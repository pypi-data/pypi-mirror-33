import os

from yaml import load

_instance = None


class Singleton(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance


class RuntimeConfiguration(Singleton):
    """
    Runtime configuration helper
    """
    DEFAULT_CONFIGURATION = {
        'CLI': {
            'TYPE': ['SSH',
                     'TELNET'],
            'PORTS': {
                'SSH': 22,
                'TELNET': 23
            }
        },
        'LOGGING': {
            'LEVEL': 'INFO'
        }
    }

    def __init__(self, config_path=None):
        if not hasattr(self, '_configuration'):
            self._configuration = self._read_configuration(config_path)

    @property
    def configuration(self):
        """
        Configuration property
        :return: 
        :rtype: dict
        """
        return self._configuration

    def _read_configuration(self, config_path):
        """Read configuration from file if exists or use default"""
        if config_path and os.path.isfile(config_path) and os.access(config_path, os.R_OK):
            with open(config_path, 'r') as config:
                loaded_configuration = load(config)
                return self._merge_configs(self.DEFAULT_CONFIGURATION, loaded_configuration)
        else:
            return self.DEFAULT_CONFIGURATION

    def _merge_configs(self, config_a, config_b):
        return config_b

    def read_key(self, complex_key, default_value=None):
        """
        Value for complex key like CLI.PORTS
        :param complex_key:
        :param default_value: Default value
        :return:
        """
        value = self.configuration
        for key in complex_key.split('.'):
            if isinstance(value, dict):
                value = value.get(key)
            else:
                value = None
                break

        return value or default_value

