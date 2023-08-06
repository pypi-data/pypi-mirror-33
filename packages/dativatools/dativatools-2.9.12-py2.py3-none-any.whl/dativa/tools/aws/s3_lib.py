import boto3
import logging
import fnmatch
import os

logger = logging.getLogger("dativa.tools.aws.s3_lib")


class S3ClientError(Exception):
    """
    A generic class for reporting errors in the athena client
    """

    def __init__(self, reason):
        Exception.__init__(self, 'S3 Client failed: reason {}'.format(reason))
        self.reason = reason


class S3Client:
    """
    Class that provides easy access over boto s3 client
    """
    
    def __init__(self):
        self.s3_client = boto3.client(service_name='s3')

    def _files_within(self, directory_path, pattern):
        """
        Returns generator containing all the files in a directory
        """
        for dirpath, dirnames, filenames in os.walk(directory_path):
            for file_name in fnmatch.filter(filenames, pattern):
                yield os.path.join(dirpath, file_name)

    def put_folder(self, source, bucket, destination="", file_format="*"):
        """
        Copies files from a directory on local system to s3

        ## Parameters
        - source: Folder on local filesystem that must be copied to s3
        - bucket: s3 bucket in which files have to be copied
        - destination: Location on s3 bucket to which files have to be copied
        """
        if os.path.isdir(source):
            file_list = list(self._files_within(source, file_format))
            for each_file in file_list:
                part_key = os.path.relpath(each_file, source)
                key = os.path.join(destination, part_key)
                self.s3_client.upload_file(each_file, bucket, key)
        else:
            raise S3ClientError("Source must be a valid directory path")

    def _generate_keys(self, bucket, prefix, suffix="", start_after=None):

        if start_after is None:
            s3_objects = self.s3_client.list_objects_v2(Bucket=bucket,
                                                        Prefix=prefix,
                                                        MaxKeys=1000)
        else:
            s3_objects = self.s3_client.list_objects_v2(Bucket=bucket,
                                                        Prefix=prefix,
                                                        MaxKeys=1000,
                                                        StartAfter=start_after)

        if 'Contents' in s3_objects:
            for key in s3_objects["Contents"]:
                if key['Key'].endswith(suffix):
                    yield key['Key']

            # get the next keys
            yield from self._generate_keys(bucket, prefix, suffix, s3_objects["Contents"][-1]['Key'])

    def delete_files(self, bucket, prefix, suffix=""):
        keys = []
        for key in self._generate_keys(bucket, prefix, suffix):
            keys.append({'Key': key})
            if len(keys) == 1000:
                logger.info("Deleting {0} files".format(len(keys)))
                self.s3_client.delete_objects(Bucket=bucket,
                                              Delete={"Objects": keys})
                keys = []

        if len(keys) > 0:
            logger.info("Deleting {0} files".format(len(keys)))
            self.s3_client.delete_objects(Bucket=bucket,
                                          Delete={"Objects": keys})
