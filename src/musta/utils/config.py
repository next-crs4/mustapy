import os
import sys
from .yaml import load as load_config

class ConfigurationFromYamlFile(object):
    """
    Retrieve infrastructure configuration's details from a yaml file
    """

    def __init__(self, config_file, logger):
        self.config_file = config_file
        self.logger = logger
        if os.path.isfile(self.config_file):
            self.conf = load_config(self.config_file)
        else:
            self.logger.critical('{} not exists'.format(self.config_file))
            sys.exit()

    def get_section(self, section_label):
        if self.is_section_present(section_label):
            return self.conf[section_label]
        else:
            self.logger.warning('section {} not found'.format(section_label))
            return ''

    def set_section(self, section_label, section_value):

        if self.is_section_present(section_label):
            if isinstance(section_value, dict):
                for k,v in section_value.items():

                    if k in self.conf.get(section_label):
                        self.conf[section_label][k] = v
            else:
                self.conf[section_label] = section_value
        else:
            self.logger.warning('section {} not found'.format(section_label))

    def is_section_present(self, section_label):
        if section_label in self.conf:
            return True
        else:
            return False


class Config(ConfigurationFromYamlFile):

    def get_io_section(self, label='io'):
        io_section = self.get_section(label)
        return io_section

    def get_pipeline_section(self, label='pipeline'):
        pipeline_section = self.get_section(label)
        return pipeline_section

    def get_demo_section(self, label='demo'):
        demo_section = self.get_section(label)
        return demo_section

    def get_resources_section(self, label='resources'):
        resources_section = self.get_section(label)
        return resources_section

    def get_ftp_section(self, label='ftp'):
        resources_section = self.get_resources_section()
        ftp_section = resources_section.get(label)
        return ftp_section

    def get_stats_section(self, label='stats'):
        stats_section = self.get_section(label)
        return stats_section