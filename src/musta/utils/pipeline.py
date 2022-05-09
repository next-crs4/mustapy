from snakemake import snakemake
from snakedeploy.deploy import deploy
from pathlib import Path
from .config import ConfigurationFromYamlFile

from git import Repo
from .yaml import dump as dump_config


class Pipeline(object):
    def __init__(self, url, name, tag, branch, workdir, force=False, logger=None):

        self.url = url
        self.name = name
        self.tag = tag
        self.branch = branch
        self.workdir = workdir
        self.force = force
        self.logger = logger

        self.repo = Repo.clone_from(self.url, self.workdir)
        # deploy(source_url=self.url,
        #        name=self.name,
        #        tag=self.tag,
        #        branch=self.branch,
        #        dest_path=Path(self.workdir),
        #        force=self.force)

    def run(self,
            snakefile,
            dryrun):

        snakemake(snakefile=snakefile,
                  workdir=self.workdir,
                  dryrun=dryrun,
                  use_conda=True)


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
