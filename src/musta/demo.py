import os
import sys
from .utils import gunzip
from git import Repo
from .utils.workflow import Workflow


class DemoWorkflow(Workflow):
    def __init__(self, args=None, logger=None):
        Workflow.__init__(self, args, logger)

        self.demo_conf = self.conf.get_demo_section()
        self.demo_url = self.demo_conf.get('url')
        self.demo_path = self.demo_conf.get('demo_root_path')
        self.demo_bam_path = os.path.join(self.demo_path,
                                          self.demo_conf.get('data_folder_name'),
                                          self.demo_conf.get('bam_folder_name'),
                                          )

        self.resources = dict(
            base=dict(
                reference=os.path.join(self.demo_path,
                                       self.demo_conf.get('resources_folder_name'),
                                       self.demo_conf.get('reference_filename')),
                bed=os.path.join(self.demo_path,
                                 self.demo_conf.get('resources_folder_name'),
                                 self.demo_conf.get('bed_filename')),
            ),

            gatk_params=dict(
                germline=os.path.join(self.demo_path,
                                      self.demo_conf.get('resources_folder_name'),
                                      self.demo_conf.get('germline_filename')),

                exac=os.path.join(self.demo_path,
                                  self.demo_conf.get('resources_folder_name'),
                                  self.demo_conf.get('exac_filename')),
            )
        )

    def get_demo_data(self):

        try:
            if os.path.exists(self.demo_path):
                repo = Repo(self.demo_path)
            else:
                repo = Repo.clone_from(self.demo_url, self.demo_path)
        except Exception as e:
            self.logger.error(str(e))
            sys.exit()
        return repo

    def run(self):
        Workflow.run(self)

        self.logger.info('Getting test data from {}'.format(self.demo_url))
        repo = self.get_demo_data()

        gunzip(self.resources.get('gatk_params').get('germline') + ".gz",
               self.resources.get('gatk_params').get('germline'))

        gunzip(self.resources.get('gatk_params').get('exac') + ".gz",
               self.resources.get('gatk_params').get('exac'))

        gunzip(self.resources.get('base').get('reference') + ".gz",
               self.resources.get('base').get('reference'))

        self.logger.info('Initializing  Config file')
        self.init_config_file(base=self.resources.get('base'),
                              gatk_params=self.resources.get('gatk_params'))

        self.logger.info('Initializing  Samples file')
        self.init_samples_file(bam_path=self.demo_bam_path)

        self.logger.info('Running')
        self.logger.info('Variant Calling - command: \'call\'')

        self.pipe_cfg.set_run_mode(run_mode='call')
        self.pipe_cfg.write()

        self.pipe.run(snakefile=self.pipe_snakefile,
                      dryrun=self.dryrun)


help_doc = """
Demo run on data from 
https://github.com/solida-core/test-data-somatic
"""


def make_parser(parser):

    parser.add_argument('--workdir', '-w',
                        type=str, metavar='PATH',
                        help='working folder path')

    parser.add_argument('--force', '-f',
                        action='store_true', default=False,
                        help='force all output files to be re-created')

    parser.add_argument('--dryrun', '-d',
                        action='store_true', default=False,
                        help='Workflow will be only described.')


def implementation(logger, args):
    logger.info(help_doc.replace('\n', ''))

    workflow = DemoWorkflow(args=args,
                            logger=logger)
    workflow.run()


def do_register(registration_list):
    registration_list.append(('demo',
                              help_doc,
                              make_parser,
                              implementation))
