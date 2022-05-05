import os.path

from .config import ConfigurationFromYamlFile
from .yaml import dump as dump_config

class Samples(ConfigurationFromYamlFile):
    def __init__(self, samples_file, logger=None):
        ConfigurationFromYamlFile.__init__(self, samples_file, logger)

    def set_bam_path(self, bam_path):
        for patient in self.conf.keys():
            normal_bam = self.conf[patient]['normal_bam']
            if normal_bam:
                self.conf[patient]['normal_bam'] = [ os.path.join(bam_path,
                                                                  os.path.basename(bam))
                                                     for bam in normal_bam ]

            tumor_bam = self.conf[patient]['tumor_bam']

            if tumor_bam:
                self.conf[patient]['tumor_bam'] = [ os.path.join(bam_path,
                                                                 os.path.basename(bam))
                                                    for bam in tumor_bam ]
    def write(self):
        dump_config(self.conf, self.config_file)