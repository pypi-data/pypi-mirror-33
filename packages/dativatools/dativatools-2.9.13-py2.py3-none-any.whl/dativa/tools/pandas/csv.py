# (c) 2012-2018 Dativa, all rights reserved
# -----------------------------------------
#  This code is licensed under MIT license (see license.txt for details)

import ast
import pandas as pd
import logging
from io import StringIO, BytesIO, TextIOWrapper
from csv import Sniffer, Error
from chardet.universaldetector import UniversalDetector
import boto3
from urllib.parse import urlparse
import s3fs

logger = logging.getLogger("dativa.tools.pandas.csv")


class FpCSVEncodingError(Exception):
    def __init__(self, message="CSV Encoding Error"):
        self.message = message


class CSVHandler():
    """
    A wrapper for pandas CSV handling to read and write dataframes
    that is provided in pandas with consistent CSV parameters and
    sniffing the CSV parameters automatically.
    Includes reading a CSV into a dataframe, and writing it out to a string.

    Parameters
    ----------
    base_path: the base path for any CSV file read, if passed as a string
    detect_parameters: whether the encoding of the CSV file should be automatically detected
    csv_encoding: the encoding of the CSV files, defaults to UTF-8
    csv_delimiter: the delimeter used in the CSV, defaults to ,
    csv_header: the index of the header row, or -1 if there is no header
    csv_skiprows: the number of rows at the beginning of file to skip
    csv_quotechar: the quoting character to use, defaults to ""

    """

    base_path = ""
    DEFAULT_ENCODING = "UTF-8"
    DEFAULT_DELIMITER = ","
    DEFAULT_HEADER = 0
    DEFAULT_QUOTECHAR = "\""
    S3_PREFIX = "s3://"

    def __init__(self,
                 detect_parameters=False,
                 csv_encoding="UTF-8",
                 csv_delimiter=",",
                 csv_header=0,
                 csv_skiprows=0,
                 csv_quotechar="\"",
                 base_path=""):
        self.auto_detect = detect_parameters
        self.csv_encoding = csv_encoding
        self.csv_delimiter = csv_delimiter
        self.csv_header = csv_header
        self.csv_skiprows = csv_skiprows
        self.csv_quotechar = csv_quotechar
        self.base_path = base_path

    def _has_header(self):
        """
        Returns whether the CSV file has a header or not
        """
        if self.csv_header == -1:
            return False
        else:
            return True

    def _get_df_from_raw(self, file, force_dtype):
        """
        Returns a dataframe from a passed file or filestream
        according to the configuration speciied in the class
        """

        if self._has_header():
            header = self.csv_header
        else:
            header = None

        full_path = self.base_path + file

        if force_dtype is not None:
            df = pd.read_csv(full_path,
                             encoding=self.csv_encoding,
                             sep=ast.literal_eval("'%s'" % self.csv_delimiter),
                             quotechar=ast.literal_eval(
                                 "'%s'" % self.csv_quotechar),
                             header=header,
                             skiprows=self.csv_skiprows,
                             skip_blank_lines=False,
                             dtype=force_dtype)
        else:
            df = pd.read_csv(full_path,
                             encoding=self.csv_encoding,
                             sep=ast.literal_eval("'%s'" % self.csv_delimiter),
                             quotechar=ast.literal_eval(
                                 "'%s'" % self.csv_quotechar),
                             header=header,
                             skiprows=self.csv_skiprows,
                             skip_blank_lines=False)

        return df

    def _get_encoding(self, sample):
        detector = UniversalDetector()
        for line in BytesIO(sample).readlines():
            detector.feed(line)
            if detector.done:
                break
        detector.close()
        return detector.result["encoding"]

    def _sniff_parameters(self, file):
        # if the mixin is using the default parameters, then attempt to guess them
        if (self.csv_encoding == self.DEFAULT_ENCODING and
            self.csv_delimiter == self.DEFAULT_DELIMITER and
            self.csv_header == self.DEFAULT_HEADER and
                self.csv_quotechar == self.DEFAULT_QUOTECHAR):
            logger.debug("sniffing file type")

            # create a sample...
            full_path = self.base_path + file
            if full_path.startswith(self.S3_PREFIX):
                # This is an S3 location
                logger.debug("s3 location")
                fs = s3fs.S3FileSystem(anon=False)
                with fs.open(full_path, "rb") as f:
                    sample = f.read(1024 * 1024)
            else:
                with open(full_path, mode="rb") as f:
                    sample = f.read(1024 * 1024)

            # get the encoding...
            self.csv_encoding = self._get_encoding(sample)
            if self.csv_encoding is None:
                self.csv_encoding = 'windows-1252'

            # now decode the sample
            try:
                sample = sample.decode(self.csv_encoding)
            except UnicodeDecodeError:
                self.csv_encoding = "windows-1252"
                try:
                    sample = sample.decode(self.csv_encoding)
                except UnicodeDecodeError as e:
                    raise FpCSVEncodingError(e)

            # use the sniffer to detect the parameters...
            sniffer = Sniffer()
            try:
                dialect = sniffer.sniff(sample)
            except Error as e:
                raise FpCSVEncodingError(e)

            self.csv_delimiter = dialect.delimiter
            if sniffer.has_header(sample):
                self.csv_header = 0
            else:
                self.csv_header = -1
            self.csv_quotechar = dialect.quotechar

            if (self.csv_encoding != self.DEFAULT_ENCODING or
                self.csv_delimiter != self.DEFAULT_DELIMITER or
                self.csv_header != self.DEFAULT_HEADER or
                    self.csv_quotechar != self.DEFAULT_QUOTECHAR):
                logger.debug("Found file type {0}, {1}, {2}".format(self.csv_encoding, self.csv_delimiter, self.csv_header))
                return True
            else:
                logger.debug("No new file type found")

        return False

    def _attempt_get_df_from_raw(self, file, force_dtype):

        try:
            return self._get_df_from_raw(file, force_dtype)
        except (UnicodeDecodeError, pd.errors.ParserError) as e:
            if self.auto_detect:
                if self._sniff_parameters(file):
                    logger.debug("second attempt to load")
                    return self._get_df_from_raw(file, force_dtype)
            raise FpCSVEncodingError(e)

    def _s3_path_to_bucket(self, url):

        s3_bucket = None
        s3_key = ""

        if url:
            parsed_s3_url = urlparse(url)
            if parsed_s3_url and parsed_s3_url.scheme.lower() == "s3":
                s3_bucket = parsed_s3_url.netloc
                if parsed_s3_url.path:
                    s3_key = parsed_s3_url.path.lstrip('/')

        return s3_bucket, s3_key

    def load_df(self, file, force_dtype=None):
        """
        Synonym for 'get_dataframe' for consistency with 'save_df'
        """
        return self.get_dataframe(file, force_dtype)

    def get_dataframe(self, file, force_dtype=None):
        """
        Opens a CSV file using the specified configuration for the class
        and raises an exception if the encoding is unparseable
        """

        df = self._attempt_get_df_from_raw(file, force_dtype)

        return df

    def save_df(self, df, file):
        """
        Writes a formatted string from a dataframe using the specified
        configuration for the class the file. Detects if base_path is
        an S3 location and saves data there if required.
        """

        if self.csv_header == -1:
            header = False
        else:
            header = True

        full_path = self.base_path + file

        if full_path.startswith(self.S3_PREFIX):
            # This is an S3 location
            s3 = boto3.client('s3')
            buffer = StringIO()
            # Stream the data via buffer
            df.to_csv(buffer,
                      index=False,
                      encoding=self.csv_encoding,
                      sep=ast.literal_eval("'%s'" % self.csv_delimiter),
                      quotechar=ast.literal_eval(
                            "'%s'" % self.csv_quotechar),
                      header=header)
            buffer.seek(0)
            # Extract bucket name from base path
            s3_bucket, s3_key = self._s3_path_to_bucket(full_path)
            # Save buffered data to file in S3 bucket
            if s3_bucket:
                s3.put_object(Bucket=s3_bucket,
                              Key=s3_key,
                              ContentEncoding=self.csv_encoding,
                              ContentType="text/csv",
                              Body=buffer.read().encode(self.csv_encoding))
        else:
            df.to_csv(full_path,
                      index=False,
                      encoding=self.csv_encoding,
                      sep=ast.literal_eval("'%s'" % self.csv_delimiter),
                      quotechar=ast.literal_eval("'%s'" % self.csv_quotechar),
                      header=header)

    def df_to_string(self, df):
        """
        Returns a formatted string from a dataframe using the specified
        configuration for the class
        """
        
        if self.csv_header == -1:
            header = False
        else:
            header = True

        buffer = StringIO()
        df.to_csv(buffer,
                  index=False,
                  encoding=self.csv_encoding,
                  sep=ast.literal_eval("'%s'" % self.csv_delimiter),
                  quotechar=ast.literal_eval("'%s'" % self.csv_quotechar),
                  header=header)
        return buffer.getvalue()
