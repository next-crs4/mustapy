import os
import shutil
from snakemake import snakemake
from .config import ConfigurationFromYamlFile

from git import Repo
from .yaml import dump as dump_config


class Pipeline(object):
    def __init__(self, url, name, tag, branch, workdir, outdir, report_file, stats_file, force=False, logger=None):

        self.url = url
        self.name = name
        self.tag = tag
        self.branch = branch
        self.workdir = workdir
        self.force = force
        self.outdir = outdir
        self.report_file = report_file
        self.stats_file = stats_file
        self.logger = logger

        if os.path.exists(self.workdir):
            shutil.rmtree(self.workdir)

        self.repo = Repo.clone_from(self.url, self.workdir)

    def run(self, snakefile, dryrun):

        snakemake(snakefile=snakefile,
                  workdir=self.workdir,
                  dryrun=dryrun,
                  forceall=self.force,
                  force_incomplete=self.force,
                  stats=self.stats_file,
                  use_conda=True)

        if not dryrun:
            snakemake(snakefile=snakefile,
                      workdir=self.workdir,
                      report=self.report_file,
                      )


class Config(ConfigurationFromYamlFile):

    def get_run_section(self, label='run'):
        run_section = self.get_section(label)
        return run_section

    def get_samples_section(self, label='samples'):
        samples_section = self.get_section(label)
        return samples_section

    def get_resources_section(self, label='resources'):
        resources_section = self.get_section(label)
        return resources_section

    def get_params_section(self, label='params'):
        params_section = self.get_section(label)
        return params_section

    def get_paths_section(self, label='paths'):
        paths_section = self.get_section(label)
        return paths_section

    def reset_run_mode(self, run_mode=None):
        run_section = self.get_run_section()
        if run_mode and run_mode in run_section:
            self.conf['run'][run_mode] = False

        else:
            for rm in run_section.keys():
                self.conf['run'][rm] = False

    def set_run_mode(self, run_mode=None):
        run_section = self.get_run_section()
        if run_mode and run_mode in run_section:
            self.conf['run'][run_mode] = str(True)

        else:
            for rm in run_section.keys():
                self.conf['run'][rm] = str(True)

    def set_samples_file(self, samples_file):

        self.set_section(section_label='samples', section_value=samples_file)

    def set_resources_section(self, resources):
        self.set_section(section_label='resources', section_value=resources)

    def set_paths_section(self, paths):
        self.set_section(section_label='paths', section_value=paths)

    def set_gatk_section(self, gatk_params):

        if gatk_params.get('germline'):
            self.conf['params']['gatk']['germline'] = gatk_params.get('germline')

        if gatk_params.get('exac'):
            self.conf['params']['gatk']['exac'] = gatk_params.get('exac')

    def write(self):
        dump_config(self.conf, self.config_file)
