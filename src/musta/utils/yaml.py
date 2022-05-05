import os
import sys
from ruamel.yaml import YAML

def dump(data, filename, mode='w'):
    yaml = YAML()
    yaml.default_flow_style = False
    with open(filename, mode) as fn:
        yaml.dump(data, fn)

def load(filename):
    """
    Load a yaml file into a dictionary if exists, otherwise return an empty one
    :param filename: path tot the file
    :return: dictionary
    """
    yaml = YAML()
    conf = dict()
    if os.path.isfile(filename):
        with open(filename) as fn:
            conf = yaml.load(fn)
    return conf


class ObjectView:
    def __init__(self, d):
        self.__dict__ = d

    @property
    def keys(self):
        return [k for k, v in self.__dict__.items()]


class DetailsFromYamlFile:
    """
    Retrieve details from a yaml file
    """
    def __init__(self, yaml_file, logger):
        self.logger = logger
        if os.path.isfile(yaml_file):
            self.conf = load(yaml_file)
        else:
            self.logger.critical('{} not exists'.format(yaml_file))
            sys.exit()

    def section(self, section_label):
        if self.is_section_present(section_label):
            return ObjectView(self.conf[section_label])
        else:
            self.logger.warning('section {} not found'.format(section_label))
            return ''

    def is_section_present(self, section_label):
        if section_label in self.conf:
            return True
        else:
            return False
