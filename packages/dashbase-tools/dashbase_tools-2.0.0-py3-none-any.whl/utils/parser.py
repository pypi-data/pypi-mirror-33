import yaml
import os
import argparse


# https://stackoverflow.com/questions/27973988/python-how-to-remove-all-empty-fields-in-a-nested-dict
def clean_empty(d):
    if not isinstance(d, (dict, list)):
        return d
    if isinstance(d, list):
        return [v for v in (clean_empty(v) for v in d) if v]
    return {k: v for k, v in ((k, clean_empty(v)) for k, v in d.items()) if v}


class ConfigParser(object):
    def __init__(self,
                 parser,
                 config_file,
                 ):
        self.parser = parser
        self._config_file = config_file

    @staticmethod
    def get_object_keys(obj):
        return [i for i in dir(obj) if not i.startswith("_")]

    def get_args(self):
        file_namespace = None
        if os.path.exists(self.config_file):
            file_namespace = self.get_config_file_namespace()

        data = self.parser.parse_args(namespace=file_namespace)

        return data

    @property
    def config_file(self):
        if self._config_file.startswith("~"):
            return os.path.expanduser(self._config_file)
        return os.path.abspath(self._config_file)

    def get_config_file_namespace(self):
        with open(self.config_file, 'r') as f:
            try:
                data = yaml.safe_load(f)
                assert isinstance(data, dict)
            except (yaml.YAMLError, AssertionError):
                print("[warning] parse config-file:{} failed".format(self.config_file))
                return None
            return argparse.Namespace(**data)
