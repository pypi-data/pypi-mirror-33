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
