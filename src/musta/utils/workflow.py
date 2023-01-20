import os
from . import get_cores
from .config import Config
from .pipeline import Pipeline
from .pipeline import Config as cfg
from .samples import Samples
from comoda import ensure_dir

class Workflow(object):
    def __init__(self, args=None, logger=None):
        self.logger = logger
        self.dryrun = args.dryrun
        self.force = args.force

        self.logger.info("Reading configuration file")
        self.conf = Config(config_file=args.config_file,
                           logger=self.logger)

        self.logger.info("Setting paths")
        self.io_conf = self.conf.get_io_section()
        self.workdir = args.workdir if args.workdir else self.io_conf.get('workdir_root_path')
        self.input_dir = self.io_conf.get('inputs_root_path')
        self.output_dir = os.path.join(self.workdir, self.io_conf.get('output_folder_name'))
        self.log_dir = os.path.join(self.workdir, self.io_conf.get('log_folder_name'))
        self.tmp_dir = self.io_conf.get('temp_folder_path')
        self.musta_dir = os.path.join(self.workdir, self.io_conf.get('musta_folder_name'))

        if not os.path.exists(self.output_dir):
            ensure_dir(self.output_dir)

        self.paths = dict(
            workdir=self.musta_dir,
            results_dir=self.output_dir,
            tmp_dir=self.tmp_dir,
            log_dir=self.log_dir,
            detection_folder_name=self.io_conf.get('detect_folder_name'),
            classification_folder_name=self.io_conf.get('classify_folder_name'),
            interpretation_folder_name=self.io_conf.get('interpret_folder_name'),
        )

        self.pipe_conf = self.conf.get_pipeline_section()
        self.pipe_url = self.pipe_conf.get('url')
        self.pipe_tag = self.pipe_conf.get('tag')
        self.pipe_name = self.pipe_conf.get('name')
        self.pipe_branch = self.pipe_conf.get('branch')

        self.pipe_snakefile = os.path.join(self.musta_dir,
                                           self.pipe_conf.get('workflow_folder_name'),
                                           self.pipe_conf.get('snakefile'))

        self.pipe_config_file = os.path.join(self.musta_dir,
                                             self.pipe_conf.get('config_folder_name'),
                                             self.pipe_conf.get('config_file'))

        self.pipe_samples_file = os.path.join(self.musta_dir,
                                              self.pipe_conf.get('config_folder_name'),
                                              self.pipe_conf.get('samples_file'))

        self.pipe_report_file = os.path.join(self.output_dir,
                                             self.pipe_conf.get('report_file'))

        self.pipe_stats_file = os.path.join(self.output_dir,
                                            self.pipe_conf.get('stats_file'))

        self.pipe_results_path = os.path.join(self.output_dir,
                                              self.pipe_conf.get('results_folder_name'))

        self.pipe_out_suffix = self.pipe_conf.get('out_suffix')

        self.pipe_cfg = None
        self.samples = None
        self.pipe = None

        self.cores = get_cores()

    def init_config_file(self, base=None, gatk_params=None):
        self.pipe_cfg = cfg(config_file=self.pipe_config_file,
                            logger=self.logger)
        self.pipe_cfg.reset_run_mode()
        self.pipe_cfg.set_samples_file(samples_file=self.pipe_samples_file)

        if base:
            self.pipe_cfg.set_resources_section(resources=base)

        if gatk_params:
            self.pipe_cfg.set_gatk_section(gatk_params=gatk_params)

        self.pipe_cfg.set_paths_section(paths=self.paths)
        self.pipe_cfg.write()

    def init_samples_file(self,
                          bam_path=None,
                          vcf_path=None,
                          maf_path=None,
                          results=None):
        self.samples = Samples(self.pipe_samples_file, self.logger)
        if bam_path:
            self.samples.set_bam_path(bam_path=bam_path)
        if vcf_path:
            self.samples.set_vcf_path(vcf_path=vcf_path)
        if maf_path:
            self.samples.set_maf_path(maf_path=maf_path)
        if results:
            self.samples.set_results(results=results)
        self.samples.write()

    def run(self):
        self.pipe = self.__deploy()

    def __deploy(self):
        self.logger.info('Deploying {}:{} pipeline from {}'.format(self.pipe_name,
                                                                   self.pipe_tag,
                                                                   self.pipe_url))
        return Pipeline(url=self.pipe_url,
                        name=self.pipe_name,
                        tag=self.pipe_tag,
                        branch=self.pipe_branch,
                        workdir=self.musta_dir,
                        outdir=self.output_dir,
                        report_file=self.pipe_report_file,
                        stats_file=self.pipe_stats_file,
                        force=self.force,
                        logger=self.logger)
