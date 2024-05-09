from .utils.workflow import Workflow
from .utils import overwrite


class AnalysisWorkflow(Workflow):

    def __init__(self, args=None, logger=None):
        Workflow.__init__(self, args, logger)

        self.samples_file = args.samples_file
        self.all_variants = args.all_variants

    def run(self):
        Workflow.run(self)

        overwrite(src=self.samples_file,
                  dst=self.pipe_samples_file)

        self.logger.info('Initializing  Config file')
        self.init_config_file()

        self.logger.info('Initializing  Samples file')
        self.init_samples_file(maf_path=self.input_dir)

        self.logger.info('Running')

        self.pipe_cfg.set_run_mode(run_mode='analysis')
        self.pipe_cfg.reset_variants()

        if self.all_variants:
            self.pipe_cfg.set_variants(option='all')

        self.pipe_cfg.write()

        self.pipe.run(snakefile=self.pipe_snakefile,
                      dryrun=self.dryrun,
                      cores=self.cores)

        self.logger.info("Logs in <WORKDIR>/{}".format(self.io_conf.get('log_folder_name')))
        self.logger.info("Results in <WORKDIR>/{}/{}".format(self.io_conf.get('output_folder_name'),
                                                             self.io_conf.get('interpret_folder_name')))
        self.logger.info("Report in <WORKDIR>/{}/report.html".format(self.io_conf.get('output_folder_name')))


help_doc = """Somatic Mutations Interpretation:
    1.  Identification of cancer driver genes 
    2.  Check for enrichment of known oncogenic pathways.
    3.  Infer tumor clonality by clustering variant allele frequencies.
    4.  Deconvolution of Mutational Signatures
    
"""


def make_parser(parser):
    parser.add_argument('--workdir', '-w',
                        type=str, metavar='PATH',
                        help='working folder path',
                        required=True)

    parser.add_argument('--samples-file', '-s',
                        type=str, metavar='PATH',
                        help='sample list file in YAML format',
                        required=True)

    parser.add_argument('--all-variants', '-a',
                        action='store_true', default=False,
                        help='If specified, all variants will be included in the final dataset. ' +
                             'By default, the final dataset will contain only variants that pass marked as PASS.')

    parser.add_argument('--force', '-f',
                        action='store_true', default=False,
                        help='overwrite directories and files if they exist in the destination')

    parser.add_argument('--dryrun', '-d',
                        action='store_true', default=False,
                        help='Workflow will be only described.')


def implementation(logger, args):
    logger.info(help_doc.replace('\n', ''))

    workflow = AnalysisWorkflow(args=args,
                                logger=logger)
    workflow.run()


def do_register(registration_list):
    registration_list.append(('interpret',
                              help_doc,
                              make_parser,
                              implementation))
