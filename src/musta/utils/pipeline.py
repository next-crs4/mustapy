import os
import shutil
from snakemake import snakemake
from .config import ConfigurationFromYamlFile

from git import Repo
from .yaml import dump as dump_config


class Pipeline(object):
    def __init__(self, url, name, tag, branch, workdir, outdir,
                 report_file, stats_file,
                 force=False, logger=None):

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

    def run(self, snakefile, dryrun, until=None, cores=1,
            stats_file=None, report_file=None):

        if until:
            snakemake(snakefile=snakefile,
                      workdir=self.workdir,
                      dryrun=dryrun,
                      forceall=self.force,
                      force_incomplete=self.force,
                      stats=stats_file if stats_file else self.stats_file,
                      use_conda=True,
                      until=[until],
                      cores=cores)
        else:
            snakemake(snakefile=snakefile,
                      workdir=self.workdir,
                      dryrun=dryrun,
                      forceall=self.force,
                      force_incomplete=self.force,
                      stats=stats_file if stats_file else self.stats_file,
                      use_conda=True,
                      cores=cores)

        if not dryrun:
            self.report(snakefile=snakefile,
                        report_file=report_file if report_file else self.report_file,)


    def report(self, snakefile, report_file=None):
        snakemake(snakefile=snakefile,
                  workdir=self.workdir,
                  report=report_file if report_file else self.report_file,
                  )

class Config(ConfigurationFromYamlFile):

    def get_run_section(self, label='run'):
        run_section = self.get_section(label)
        return run_section

    def get_callers_section(self, label='callers'):
        call_section = self.get_section(label)
        return call_section

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
            self.conf['run'][run_mode] = True

        else:
            for rm in run_section.keys():
                self.conf['run'][rm] = True

    def reset_callers(self, caller=None):
        callers_section = self.get_callers_section()
        if caller and caller in callers_section:
            self.conf['callers'][caller] = False

        else:
            for c in callers_section.keys():
                self.conf['callers'][c] = False

    def set_callers(self, caller=None):
        callers_section = self.get_callers_section()
        if caller and caller in callers_section:
            self.conf['callers'][caller] = True

        else:
            for c in callers_section.keys():
                self.conf['callers'][c] = True

    def set_samples_file(self, samples_file):

        self.set_section(section_label='samples', section_value=samples_file)

    def set_resources_section(self, resources):
        self.set_section(section_label='resources', section_value=resources)

    def set_paths_section(self, paths):
        self.set_section(section_label='paths', section_value=paths)

    def set_vep_params(self, vep_params):
        self.conf['params']['vep']


    def set_gatk_section(self, gatk_params):

        if gatk_params.get('germline'):
            self.conf['params']['gatk']['germline'] = gatk_params.get('germline')

        if gatk_params.get('exac'):
            self.conf['params']['gatk']['exac'] = gatk_params.get('exac')

        if gatk_params.get('Funcotator'):
            self.conf['params']['gatk']['Funcotator'] = gatk_params.get('Funcotator')

    def write(self):
        dump_config(self.conf, self.config_file)
