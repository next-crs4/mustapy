
from .utils.workflow import Workflow
from .utils import overwrite


class FullWorkflow(Workflow):
    def __init__(self, args=None, logger=None):
        Workflow.__init__(self, args, logger)

        self.samples_file = args.samples_file
        self.reference_file = args.reference_file
        self.bed_file = args.bed_file
        self.germline_resource = args.germline_resource
        self.variant_file = args.variant_file
        self.data_source = args.data_source
        self.ref_version = args.ref_version

        self.resources = dict(
            base=dict(
                reference=self.reference_file,
                bed=self.bed_file,
            ),

            gatk_params=dict(
                germline=self.germline_resource,
                exac=self.variant_file,
                Funcotator=dict(
                    resources=self.data_source,
                    reference_version=self.ref_version
                )
            )
        )

    def run(self):
        Workflow.run(self)

        overwrite(src=self.samples_file,
                  dst=self.pipe_samples_file)

        self.logger.info('Initializing  Config file')
        self.init_config_file(base=self.resources.get('base'),
                              gatk_params=self.resources.get('gatk_params'))

        self.logger.info('Initializing  Samples file')
        self.init_samples_file(bam_path=self.input_dir)

        self.logger.info('Running')

        self.pipe_cfg.set_run_mode(run_mode='all')
        self.pipe_cfg.write()

        self.pipe.run(snakefile=self.pipe_snakefile,
                      dryrun=self.dryrun)

        self.logger.info("Logs in <WORKDIR>/outputs/logs")
        self.logger.info("Results in <WORKDIR>/outputs/results")
        self.logger.info("Report in <WORKDIR>/outputs/report.html")


help_doc = """
Run the whole workflow, 
from Variant Calling to Deconvolution of Mutational Signatures
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

    workflow = FullWorkflow(args=args,
                            logger=logger)
    workflow.run()


def do_register(registration_list):
    registration_list.append(('full',
                              help_doc,
                              make_parser,
                              implementation))