from .utils.workflow import Workflow
from .utils import overwrite


class SignatureWorkflow(Workflow):
    def __init__(self, args=None, logger=None):
        Workflow.__init__(self, args, logger)

        self.samples_file = args.samples_file

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
        self.pipe_cfg.write()

        self.pipe.run(snakefile=self.pipe_snakefile,
                      dryrun=self.dryrun,
                      until='maftools_signatures',
                      cores=self.cores)

        self.logger.info("Logs in <WORKDIR>/outputs/logs")
        self.logger.info("Results in <WORKDIR>/outputs/results/analysis")
        self.logger.info("Report in <WORKDIR>/outputs/report.html")


help_doc = """
Deconvolution of Mutational Signatures
De-novo extraction of mutational signatures  followed  by refitting
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

    parser.add_argument('--force', '-f',
                        action='store_true', default=False,
                        help='overwrite directories and files if they exist in the destination')

    parser.add_argument('--dryrun', '-d',
                        action='store_true', default=False,
                        help='Workflow will be only described.')


def implementation(logger, args):
    logger.info(help_doc.replace('\n',''))

    workflow = SignatureWorkflow(args=args,
                                 logger=logger)
    workflow.run()


def do_register(registration_list):
    registration_list.append(('signature',
                              help_doc,
                              make_parser,
                              implementation))
