import yaml


class Config():
    def __init__(self):
        self.config = {}

    def load_file(self, path='/srv/config.yml'):
        with open(path) as config_file:
            self.config = yaml.load(config_file)

    def load(self, yaml_string):
        self.config = yaml.load(yaml_string)

    def set_config(self, config):
        self.config = config

    def get_config(self):
        return self.config


CONFIG = Config()
