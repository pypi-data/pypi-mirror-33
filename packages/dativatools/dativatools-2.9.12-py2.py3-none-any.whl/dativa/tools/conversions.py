# (c) 2012-2018 Dativa, all rights reserved
# -----------------------------------------
# Usage subject to license agreement
# hello@dativa.com for more information

import json
from collections import OrderedDict


class JsonDataFrame:

    _df = None
    _json_obj = None

    @property
    def df(self):
        return self._df

    @df.setter
    def set_df(self, value):
        self._df = value
        self._json_obj = self._dataframe_to_json_obj()
        self._check_integrity()

    @df.deleter
    def delete_df(self, value):
        del self._df
        del self._json_obj

    @property
    def json_obj(self):
        return self._json_obj

    @json_obj.setter
    def set_json_obj(self, value):
        self._json_obj = value
        self._df = self._json_obj_to_dataframe()

    @json_obj.deleter
    def delete_json_obj(self, value):
        del self._df
        del self._json_obj

    def __init__(self, df=None, json_object=None):
        if df is not None:
            self.df = df
        elif json_object is not None:
            self.json = json_object

    def _compare_objects(self, new_object, original_object, ignore_list=[]):
        for key, value in self._iterate_json_obj(original_object):
            if key not in ignore_list:
                key_found = False
                for new_key, new_value in self._iterate_json_obj(new_object):
                    if key == new_key:
                        key_found = True
                        if value != new_value:
                            return value, new_value
                        break
                    if not key_found:
                        return key, None

    def compare_objects(self, new_object, original_object, ignore_list=[]):
        a, b = self._compare_objects(new_object, original_object, ignore_list)
        if a is True and b is True:
            return self._compare_objects(original_object, new_object, ignore_list)
        else:
            return a, b

    def _iterate_json_obj(self, json_object, prefix=""):
        """
        Iterates through a JSON object and returns each unique key, value.
        Nested keys are returned with dot separation
        """
        for key in json_object:
            yield "{prefix}.{key}".format(prefix=prefix, key=key), json_object[key]
            if type(json_object[key]) == dict or type(json_object[key]) == OrderedDict:
                yield from self._iterate_json_obj(json_object[key], "{prefix}.{key}".format(prefix=prefix, key=key))
            elif type(json_object[key]) == list:
                for index in range(0, len(json_object[key])):
                    yield from self._iterate_json_obj(json_object[key][index], "{prefix}.{key}".format(prefix=prefix, key=key))
            else:
                yield key, json_object[key]

    def _get_empty_row(self, header):
        row = {}
        for key in header:
            row[key] = None

    def _iterate_json_obj_rows(self, json_object, header):
        current_row = self._get_empty_row(header)
        for key, value in self._iterate_json_obj(json_object):
            if key not in current_row:
                current_row[key] = value
            else:
                yield current_row
                current_row = self._get_empty_row(header)

    def _dataframe_to_json_obj(dataframe):
        json = {}
        if json_to_dataframe(json) == dataframe:
            return json
        else:
            raise ValueError("Cannot parse this DataFrame to JSON")

    def _json_obj_to_dataframe(json_object):

        # get a unique list of keys in the JSON object
        keys = []
        for key, value in self._iterate_json_obj(json_object):
            if key not in keys:
                keys.append(key)

        with open('names.csv', 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=keys)
            writer.write_header()
            writer.write_rows(self._iterate_json_obj_rows, header)

        df = ""
        if json_to_dataframe(json) == dataframe:
            return json
        else:
            raise ValueError("Cannot parse this DataFrame to JSON")
