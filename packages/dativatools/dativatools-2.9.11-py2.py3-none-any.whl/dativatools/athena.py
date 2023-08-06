import boto3
import logging
import sys
import time

logger = logging.Logger("dativa.comcast.ingest_data")
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


class Object(object):
    pass


class AthenaClient():

    def __init__(self, region, db, max_queries=3):
        self.glue = boto3.client(service_name='athena', region_name=region)
        self.db_name = db
        self.max_queries = max_queries
        self.queue = []
        self.aws_region = region

    @property
    def is_active(self):
        self._process_queue()
        return self.number_active + self.number_pending > 0

    @property
    def number_active(self):
        i = 0
        for query in self.queue:
            if query.is_active:
                i = i + 1
        return i

    @property
    def number_pending(self):
        i = 0
        for query in self.queue:
            if query.is_pending:
                i = i + 1
        return i

    def _get_query_status(self, query):

        logger.info("...checking status of query {0}".format(query.name))

        status = self.glue.get_query_execution(QueryExecutionId=query.id)["QueryExecution"]["Status"]

        if status["State"] == "RUNNING":
            query.is_active = True
        elif status["State"] == "SUCCEEDED":
            query.is_active = False
        else:
            logger.info("Retrying query {0} completed with state {1}".format(query.name, status["State"]))
            if "StateChangeReason" in status:
                logger.info(status["StateChangeReason"])

            query.is_active = False
            query.is_pending = True

        return query

    def _query_athena(self, query):

        logger.info("Starting query {0}".format(query.name))

        query.id = self.glue.start_query_execution(
            QueryString=query.sql,
            QueryExecutionContext={'Database': self.db_name},
            ResultConfiguration={'OutputLocation': query.output_location}
        )["QueryExecutionId"]

        query.is_active = True
        query.is_pending = False
        return query

    def _process_queue(self):
        for ix, query in enumerate(self.queue):
            if query.is_active:
                query = self._get_query_status(query)
                self.queue[ix] = query
            elif query.is_pending and self.number_active < self.max_queries:
                    self.queue[ix] = self._query_athena(query)

    def add_query(self, sql, name, output_location):
        query = Object()
        query.sql = sql
        query.name = name
        query.output_location = output_location
        query.is_active = False
        query.is_pending = True
        query.id = None

        self.queue.append(query)

        if self.number_active < self.max_queries:
            self._process_queue()

    def wait_for_completion(self):
        while self.is_active:
            time.sleep(10)

    def create_table(self,
                     crawler_target,
                     table_name,
                     columns=None,
                     schema_change_policy={'UpdateBehavior': 'UPDATE_IN_DATABASE', 'DeleteBehavior': 'DEPRECATE_IN_DATABASE'},
                     aws_role='AWSGlueServiceRoleDefault',
                     serde=None):
        """
        Creates a table in AWS Glue using a crawler.

        ## Parameters

        - region: the AWS region in which to create the table
        - db_name: the name of the Glue database in which to create the table
        - crawler_target: the definition of where the crawler should crawl

        Optional parameters
        - columns: column definitions, typically required for CSV
        - schema_change_policy: the schema change policy to use
        - aws_role: the role that Glue should use when creating it

        For more information on the crawler target and the schema change policies, go here:
        https://docs.aws.amazon.com/glue/latest/dg/aws-glue-api-crawler-crawling.html

        Columns are defined here:
        https://docs.aws.amazon.com/glue/latest/dg/aws-glue-api-catalog-tables.html

        """

        crawler_name = "{0}_{1}_crawler".format(self.db_name, table_name)

        # create a glue client...
        glue = boto3.client(service_name='glue', region_name=self.aws_region,
                            endpoint_url='https://glue.{0}.amazonaws.com'.format(self.aws_region))

        # if the glue database does not exist then create it...
        if {"Name": self.db_name} not in glue.get_databases()["DatabaseList"]:
            logger.info("creating databases {0}".format(self.db_name))
            glue.create_database(DatabaseInput={"Name": self.db_name})

        # if the crawler exists then update it:
        have_updated = False
        for crawler in glue.get_crawlers()["Crawlers"]:
            if crawler_name == crawler["Name"]:
                logger.info("updating crawler {0}".format(crawler_name))
                glue.update_crawler(Name=crawler_name,
                                    Role=aws_role,
                                    Targets=crawler_target,
                                    DatabaseName=self.db_name,
                                    Classifiers=[],
                                    SchemaChangePolicy=schema_change_policy)
                have_updated = True
                break

        # otherwise create it
        if not have_updated:
            logger.info("creating crawler {0} ".format(crawler_name))
            glue.create_crawler(Name=crawler_name,
                                Role=aws_role,
                                Targets=crawler_target,
                                DatabaseName=self.db_name,
                                Classifiers=[],
                                SchemaChangePolicy=schema_change_policy)

        # start the crawler and wait for it to complete:
        logger.info("starting crawler {0}".format(crawler_name))
        glue.start_crawler(Name=crawler_name)
        while glue.get_crawler(Name=crawler_name)["Crawler"]["State"] != "READY":
            logger.info("... waiting for crawler {0} to finish".format(crawler_name))
            time.sleep(5)

        if columns is not None or serde is not None:
            # get the table and update the column names
            logger.info("updating tables {0}".format(table_name))
            table = glue.get_table(DatabaseName=self.db_name, Name=table_name)["Table"]
            
            if columns is not None:
                table["StorageDescriptor"]["Columns"] = columns
            
            if serde is not None:
                table["StorageDescriptor"]["SerdeInfo"]["SerializationLibrary"] = serde

            glue.update_table(DatabaseName=self.db_name,
                              TableInput={'Name': table_name,
                                          'StorageDescriptor': table["StorageDescriptor"],
                                          'PartitionKeys': table["PartitionKeys"],
                                          'TableType': table["TableType"],
                                          'Parameters': table["Parameters"]})
