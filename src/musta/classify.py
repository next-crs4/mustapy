import os
from .utils.workflow import Workflow
from .utils import overwrite



class AnnotateWorkflow(Workflow):
    def __init__(self, args=None, logger=None):
        Workflow.__init__(self, args, logger)

        self.samples_file = args.samples_file
        self.reference_file = args.reference_file
        self.data_source = args.data_source
        self.ref_version = args.ref_version

        if args.tmpdir:
            self.tmp_dir = args.tmpdir

        self.resources = dict(
            base=dict(
                reference=self.reference_file,
            ),

            gatk_params=dict(
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
        self.init_samples_file(vcf_path=self.input_dir)

        self.logger.info('Running')
        self.logger.info('Variant Annotation')

        self.pipe_cfg.set_run_mode(run_mode='annotate')
        self.pipe_cfg.write()

        self.pipe.run(snakefile=self.pipe_snakefile,
                      dryrun=self.dryrun,
                      cores=self.cores,
                      report_file=os.path.join(self.output_dir,
                                               self.io_conf.get('classify_folder_name'),
                                               self.pipe_conf.get('report_file')),
                      stats_file=os.path.join(self.output_dir,
                                               self.io_conf.get('classify_folder_name'),
                                               self.pipe_conf.get('stats_file')),
                      )

        self.logger.info("Logs in <WORKDIR>/{}".format(self.io_conf.get('log_folder_name')))
        self.logger.info("Results in <WORKDIR>/{}/{}".format(self.io_conf.get('output_folder_name'), self.io_conf.get('classify_folder_name')))
        self.logger.info("Report in <WORKDIR>/{}/report.html".format(self.io_conf.get('output_folder_name')))


help_doc = """Variant Annotation
Functional annotation of called somatic variants 

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

    parser.add_argument('--tmpdir', '-t',
                        type=str, metavar='PATH',
                        help='temporary directory (large enough to hold the intermediate files)')

    parser.add_argument('--reference-file', '-r',
                        type=str, metavar='PATH',
                        help='reference FASTA file',
                        required=True)

    parser.add_argument('--data-source', '-ds',
                        type=str, metavar='PATH',
                        help='The path to a data source folder for Variant Annotations',
                        required=True)

    parser.add_argument('--ref-version', '-rf',
                        type=str, choices=['hg19', 'hg38'], default='hg19',
                        help='The version of the Human Genome reference to use.')

    parser.add_argument('--force', '-f',
                        action='store_true', default=False,
                        help='overwrite directories and files if they exist in the destination')

    parser.add_argument('--dryrun', '-d',
                        action='store_true', default=False,
                        help='Workflow will be only described.')


def implementation(logger, args):
    logger.info(help_doc.replace('\n',''))

    workflow = AnnotateWorkflow(args=args,
                                logger=logger)
    workflow.run()


def do_register(registration_list):
    registration_list.append(('classify',
                              help_doc,
                              make_parser,
                              implementation))
