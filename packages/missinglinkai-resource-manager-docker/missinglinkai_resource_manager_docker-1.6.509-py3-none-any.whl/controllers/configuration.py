import os
import yaml
import logging

WS_SERVER = os.environ.get('WS_SERVER') or 'localhost:8765'


class ConfigurationError(Exception):
    pass


class ConfigFile(object):
    @classmethod
    def load_yaml_file(cls, path):
        if os.path.isfile(path):
            with open(path) as f:
                return yaml.load(f) or {}
        return {}

    @classmethod
    def save_yaml_file(cls, path, data):
        with open(path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)

    def __init__(self, path):
        super(ConfigFile, self).__setattr__('path', path)
        super(ConfigFile, self).__setattr__('data', self.load_yaml_file(path))

    def __getattr__(self, item):
        return self.data[item]

    def __setattr__(self, key, value):
        self.data[key] = value

    def get(self, item, default=None):
        return self.data.get(item, default)

    def save(self):
        self.save_yaml_file(self.path, self.data)


class ConfigurationInstance(object):
    def __init__(self, config_path=None):
        config_path = config_path or './config'
        logging.info('Configuration path is %s', config_path)
        os.makedirs(config_path, exist_ok=True)
        self.config_path = config_path
        self.general = ConfigFile(os.path.join(config_path, 'index.yaml'))


active_config = None


def get_active_config():
    return active_config
