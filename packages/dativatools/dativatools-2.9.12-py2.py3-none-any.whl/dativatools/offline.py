import requests
import datetime
import pandas as pd
import io
import json
from collections import namedtuple
from spotless.file_processing import FileProcessor, CSVHandler, FileProcessingError, FpMaximumValueExpectedError, FpTooManyRecordsError, FpInvalidSourceFieldError, FpCSVEncodingError
from pyspotless import SpotlessClient, SpotlessError


class JobLogger():
    job = None
    csv_reader = None

    def __init__(self, client, job, csv_reader):
        self.client = client
        self.job = job
        self.csv_reader = csv_reader

    def log_history(self,
                    rule,
                    column,
                    df,
                    category,
                    description
                    ):
        # log the history on the current job
        if isinstance(df, pd.Series):
            df = df.to_frame()

        requests.post(
            "%s/api/history/" % self.client.url,
            headers={"Authorization": "Token " + self.client.token},
            data={"job": self.job["url"],
                  "rule": rule,
                  "column": column,
                  "date": datetime.datetime.now(),
                  "category": category,
                  "description": description,
                  "number_records": df.shape[0]},
            files={"records": io.StringIO(self.csv_reader.df_to_string(df))},

        )

    def get_report(self):
        return None

class SpotlessProfile():
    maximum_records = 2000000
    maximum_records_reference_rule = 500000
    maximum_records_closest_matches = 5000
    lookalike_number_records = 5
    maximum_records_lookalike = 5000
    maximum_file_records_lookalike = 500000


class SpotlessOfflineClient(SpotlessClient):

    # job limits
    profile = SpotlessProfile()

    def _get_csv_reader(self, plan):
        return CSVHandler(
            csv_encoding=plan["csv_encoding"],
            csv_delimiter=plan["csv_delimiter"],
            csv_header=plan["csv_header"],
            csv_skiprows=plan["csv_skiprows"],
            csv_quotechar=plan["csv_quotechar"])

    def df_to_string(self, plan, df):
        plan = self._get_object("{0}/api/plans/{1}/".format(self.url, self._get_id(plan)), "plan")
        return self._get_csv_reader(plan).df_to_string(df)

    def run_job(self, plan_url, df, *args):
        """

        Process a spotless job offline. The dataframe that is passed will be cleaned inplace.

        :type plan_url: string
        :param plan_url: the URL of the plan on spotlessdata.com that you want to process the file against
        :type df: dataframe
        :param file: The path to the file to be processed
        :type callback: function
        :param callback: The optional function you wish to have called once the job has been processed.
            The callback will receive a two parameters:
            - job - an object containingq the following fields:
                - url - the URL of the job
                - plan - the plan that was used to process the job
                - processing_complete - set to True if the processing is complete
                - history - details of the records that have been cleansed and links to quarantined records
            - df - containing the dataframe that was passed to be processed and has been modified inplace

        """

        # create a job on the server...
        response = requests.post(
            "%s/api/jobs/" % self.url,
            headers={"Authorization": "Token " + self.token},
            data={"plan": self._get_id(plan_url),
                  "run_offline": True}
        )

        job = self._decode_object_response(response, "creating", "offline job")

        # get the plan and set up the csv_reader...
        plan = self._get_object("{0}/api/plans/{1}/".format(self.url, job["plan"]), "plan")
        csv = self._get_csv_reader(plan)

        # set up the job for the logger...
        logger = JobLogger(self, job, csv)

        # run the job...
        config = plan["config"]
        try:
            file_processor = FileProcessor(logger, self.profile)
            file_processor.run(df, config)
        except FileProcessingError as e:
            raise SpotlessError(reason=e.message)
        except FpMaximumValueExpectedError as e:
            raise SpotlessError(reason=e.message)
        except FpTooManyRecordsError as e:
            raise SpotlessError(reason=e.message)
        except FpInvalidSourceFieldError as e:
            raise SpotlessError(reason=e.message)
        except FpCSVEncodingError as e:
            raise SpotlessError(reason=e.message)

        # either call the callback or return the job
        if len(args) > 0:
            callback = args[0]
            new_args = [a for a in args if a != callback]
            callback(job, self, df, *new_args)
        else:
            return job
