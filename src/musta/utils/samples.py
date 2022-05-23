import os.path

from .config import ConfigurationFromYamlFile
from .yaml import dump as dump_config


class Samples(ConfigurationFromYamlFile):
    def __init__(self, samples_file, logger=None):
        ConfigurationFromYamlFile.__init__(self, samples_file, logger)

    def set_bam_path(self, bam_path):
        for patient in self.get_patients():
            normal_bam = self.conf[patient]['normal_bam']
            if normal_bam:
                self.conf[patient]['normal_bam'] = [os.path.join(bam_path,
                                                                 os.path.basename(bam))
                                                    for bam in normal_bam]

            tumor_bam = self.conf[patient]['tumor_bam']

            if tumor_bam:
                self.conf[patient]['tumor_bam'] = [os.path.join(bam_path,
                                                                os.path.basename(bam))
                                                   for bam in tumor_bam]

    def set_vcf_path(self, vcf_path):
        for patient in self.get_patients():
            vcfs = self.conf[patient]['vcf']
            if vcfs:
                self.conf[patient]['vcf'] = [os.path.join(vcf_path,
                                                          os.path.basename(vcf))
                                             for vcf in vcfs]

    def set_results(self, results):
        for patient in self.get_patients():
            if 'call' in results:
                self.conf[patient]['vcf'] = [self.__build_result_path(patient, results.get('call'))]

    def get_patients(self):
        return self.conf.keys()

    def __build_result_path(self, patient, result):
        return os.path.join(result.get('dirpath'),
                            "{}{}".format(patient,
                                          result.get('out_suffix')))

    def write(self):
        dump_config(self.conf, self.config_file)
