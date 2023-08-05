# (c) 2012-2018 Dativa, all rights reserved
# -----------------------------------------
#  This code is licensed under MIT license (see license.txt for details)

import ast
import pandas as pd
import logging
from io import StringIO, BytesIO
from csv import Sniffer, Error
from chardet.universaldetector import UniversalDetector


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

    def __init__(self,
                 detect_parameters=False,
                 csv_encoding="UTF-8",
                 csv_delimiter=",",
                 csv_header=0,
                 csv_skiprows=0,
                 csv_quotechar="\"",
                 base_path="."):
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

        if force_dtype is not None:
            df = pd.read_csv(self.base_path + file,
                             encoding=self.csv_encoding,
                             sep=ast.literal_eval("'%s'" % self.csv_delimiter),
                             quotechar=ast.literal_eval(
                                 "'%s'" % self.csv_quotechar),
                             header=header,
                             skiprows=self.csv_skiprows,
                             skip_blank_lines=False,
                             dtype=force_dtype)
        else:
            df = pd.read_csv(self.base_path + file,
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

            # create a sample and get the encoding...
            with open(self.base_path + file, mode="rb") as f:
                sample = f.read(1024 * 1024)
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
                    self.save()
                    logger.debug("second attempt to load")
                    return self._get_df_from_raw(file, force_dtype)
            raise FpCSVEncodingError(e)

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
        configuration for the class the file
        """

        if self.csv_header == -1:
            header = False
        else:
            header = True
        file = df.to_csv(file,
                         index=False,
                         encoding=self.csv_encoding,
                         sep=ast.literal_eval("'%s'" % self.csv_delimiter),
                         quotechar=ast.literal_eval(
                             "'%s'" % self.csv_quotechar),
                         header=header)

    def df_to_string(self, df):
        """
        Returns a formatted string from a dataframe using the specified
        configuration for the class
        """

        buffer = StringIO()
        self.save_df(df, buffer)
        return buffer.getvalue()
