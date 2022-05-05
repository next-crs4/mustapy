import os
import sys
from .utils.config import Config
from .utils.pipeline import Pipeline
from .utils.pipeline import Config as cfg
from .utils.samples import Samples

from comoda import ensure_dir
from git import Repo

class DemoWorkflow(object):
    def __init__(self, args=None, logger=None):
        self.logger = logger
        self.dry_run = args.dry_run
        self.force = args.force

        self.logger.info("Reading configuration file")
        self.conf = Config(config_file=args.config_file,
                           logger=self.logger)

        self.logger.info("Setting paths")
        self.io_conf = self.conf.get_io_section()
        self.workdir = args.workdir if args.workdir else self.io_conf.get('workdir_root_path')
        self.input_dir = os.path.join(self.workdir, self.io_conf.get('input_folder_name'))
        self.output_dir = os.path.join(self.workdir, self.io_conf.get('output_folder_name'))
        self.tmp_dir = self.io_conf.get('temp_folder_path')

        self.demo_conf = self.conf.get_demo_section()
        self.demo_url = self.demo_conf.get('url')
        self.demo_path = self.demo_conf.get('demo_root_path')
        self.demo_bam_path = os.path.join(self.demo_path,
                                          self.demo_conf.get('data_folder_name'),
                                          self.demo_conf.get('bam_folder_name'),
                                          )

        self.resources = dict(
            reference=os.path.join(self.demo_path,
                                   self.demo_conf.get('resources_folder_name'),
                                   self.demo_conf.get('reference_filename')),
            bed=os.path.join(self.demo_path,
                             self.demo_conf.get('resources_folder_name'),
                             self.demo_conf.get('bed_filename')),

        )

        self.paths = dict(
            workdir=self.workdir,
            tmp_dir=self.tmp_dir
        )

        self.pipe_conf = self.conf.get_pipeline_section()
        self.pipe_url = self.pipe_conf.get('url')
        self.pipe_tag = self.pipe_conf.get('tag')
        self.pipe_name = self.pipe_conf.get('name')
        self.pipe_branch = self.pipe_conf.get('branch')

        self.pipe_snakefile = os.path.join(self.workdir,
                                           self.pipe_conf.get('workflow_folder_name'),
                                           self.pipe_conf.get('snakefile'))

        self.pipe_config_file = os.path.join(self.workdir,
                                             self.pipe_conf.get('config_folder_name'),
                                             self.pipe_conf.get('config_file'))

        self.pipe_samples_file = os.path.join(self.workdir,
                                              self.pipe_conf.get('config_folder_name'),
                                              self.pipe_conf.get('samples_file'))


        self.pipe_cfg = None

        self.samples = None

        if os.path.exists(self.demo_path) and not self.force:
            self.logger.error('{} already exists, aborting (use --force/-f to overwrite'.format(self.demo_path))
            sys.exit()

        ensure_dir(self.demo_path, force=self.force)

    def init_config_file(self):
        self.pipe_cfg = cfg(config_file=self.pipe_config_file,
                            logger=self.logger)
        self.pipe_cfg.reset_run_mode()
        self.pipe_cfg.set_samples_file(samples_file=self.pipe_samples_file)
        self.pipe_cfg.set_resources_section(resources=self.resources)
        self.pipe_cfg.set_paths_section(paths=self.paths)
        self.logger.info("after: {}".format(self.pipe_cfg.conf))
        self.pipe_cfg.write()

    def init_samples_file(self):
        self.samples = Samples(self.pipe_samples_file, self.logger)
        self.logger.info("before: {}".format(self.samples.conf))
        self.samples.set_bam_path(self.demo_bam_path)
        self.logger.info("after: {}".format(self.samples.conf))
        self.samples.write()

    def get_demo_data(self):

        try:
            repo = Repo.clone_from(self.demo_url, self.demo_path)
        except Exception as e:
            self.logger.error(str(e))
            sys.exit()
        return repo

    def run(self):
        self.logger.info('Deploying {}:{} pipeline from {}'.format(self.pipe_name,
                                                                   self.pipe_tag,
                                                                   self.pipe_url))
        pipe = Pipeline(url=self.pipe_url,
                        name=self.pipe_name,
                        tag=self.pipe_tag,
                        branch=self.pipe_branch,
                        workdir=self.workdir,
                        force=self.force,
                        logger=self.logger)

        self.logger.info('Getting test data from {}'.format(self.demo_url))
        repo = self.get_demo_data()

        self.init_config_file()
        self.init_samples_file()

        self.logger.info('Running')
        self.logger.info('Variant Calling - command: \'call\'')

        self.pipe_cfg.set_run_mode(run_mode='call')
        self.pipe_cfg.write()

        pipe.run(snakefile=self.pipe_snakefile,
                 dryrun=self.dry_run)



help_doc = """
Demo run on data from 
https://github.com/solida-core/test-data-somatic
"""

def make_parser(parser):

    parser.add_argument('--force', '-f',
                        action='store_true', default=False,
                        help='overwrite directories and files if they exist in the destination')

    parser.add_argument('--dry_run', '-d',
                        action='store_true', default=False,
                        help='Workflow will be only described.')

def implementation(logger, args):
    logger.info(help_doc.replace('\n',''))

    workflow = DemoWorkflow(args=args,
                            logger=logger)
    workflow.run()


def do_register(registration_list):
    registration_list.append(('demo',
                              help_doc,
                              make_parser,
                              implementation))
