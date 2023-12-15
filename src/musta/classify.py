import os
from .utils.workflow import Workflow
from .utils import overwrite, ensure_directory_exists
from .utils.summary import generate_classification_summary


class ClassifyWorkflow(Workflow):
    def __init__(self, args=None, logger=None):
        Workflow.__init__(self, args, logger)

        self.samples_file = args.samples_file
        self.reference_file = args.reference_file
        self.data_source = args.data_source
        self.ref_version = args.ref_version
        self.cache_version = args.cache_version

        self.funcotator = args.also_funcotator or args.only_funcotator
        self.vep = not args.only_funcotator

        if args.tmpdir:
            self.tmp_dir = args.tmpdir

        self.resources = dict(
            base=dict(
                reference=self.reference_file,
            ),

            gatk_params=dict(
                Funcotator=dict(
                    resources=os.path.join(self.data_source, self.io_conf.get('funcotator_folder_name')),
                    reference_version=self.ref_version
                )
            ),

            vep_params=dict(
                resources=os.path.join(self.data_source, self.io_conf.get('vep_folder_name')),
                reference_version=self.ref_version,
                cache_version=self.cache_version,
            )
        )

    def run(self):
        Workflow.run(self)

        overwrite(src=self.samples_file,
                  dst=self.pipe_samples_file)

        self.logger.info('Initializing  Config file')
        self.init_config_file(base=self.resources.get('base'),
                              gatk_params=self.resources.get('gatk_params'),
                              vep_params=self.resources.get('vep_params'))

        self.logger.info('Initializing  Samples file')
        self.init_samples_file(vcf_path=self.input_dir)

        self.logger.info('Running')
        self.logger.info('Variant Annotation')

        self.pipe_cfg.reset_run_mode()
        self.pipe_cfg.set_run_mode(run_mode='annotate')

        if self.vep:
            self.logger.info('Variant Annotator:  \'vep\'')
            self.pipe_cfg.reset_annotators()
            self.pipe_cfg.set_annotators(annotator="vep")
            self.pipe_cfg.write()

            self.pipe.run(snakefile=self.pipe_snakefile,
                          dryrun=self.dryrun,
                          cores=self.cores,
                          report_file=self._get_report_file('vep'),
                          stats_file=self._get_stats_file('vep')
                          )

        if self.funcotator:
            self.logger.info('Variant Annotator:  \'funcotator\'')
            self.pipe_cfg.reset_annotators()
            self.pipe_cfg.set_annotators(annotator="funcotator")
            self.pipe_cfg.write()

            self.pipe.run(snakefile=self.pipe_snakefile,
                          dryrun=self.dryrun,
                          cores=self.cores,
                          report_file=self._get_report_file('funcotator'),
                          stats_file=self._get_stats_file('funcotator')
                          )

        self.pipe.report(snakefile=self.pipe_snakefile,
                         report_file=self.get_report_file())

        ensure_directory_exists(self.summary_paths.get('classification').get('summary_directory'))
        generate_classification_summary(
            main_directory=self.summary_paths.get('classification').get('main_directory'),
            maf_directory=self.summary_paths.get('classification').get('maf_directory'),
            out_files=self.summary_files.get('classification'),
            plots=self.plot_conf,
        )

        self.logger.info("Logs in <WORKDIR>/{}/<VARIANT ANNOTATOR>".format(self.io_conf.get('log_folder_name')))

        self.logger.info("Outputs in <WORKDIR>/{}/{}/<VARIANT ANNOTATOR>".format(self.io_conf.get('output_folder_name'),
                                                                                 self.io_conf.get(
                                                                                     'classify_folder_name')))

        self.logger.info("Report in <WORKDIR>/{}/<VARIANT ANNOTATOR>/{}".format(self.io_conf.get('output_folder_name'),
                                                                                self.pipe_conf.get('report_file')))

        self.logger.info("VCFs/MAFs in <WORKDIR>/{}/{}/results/{}".format(self.io_conf.get('output_folder_name'),
                                                                          self.io_conf.get('classify_folder_name'),
                                                                          self.summary_conf.get('folder_name')))

    def _get_report_file(self, annotator):
        return os.path.join(self.output_dir,
                            self.io_conf.get('classify_folder_name'),
                            annotator,
                            self.pipe_conf.get('report_file'))

    def _get_stats_file(self, annotator):
        return os.path.join(self.output_dir,
                            self.io_conf.get('classify_folder_name'),
                            annotator,
                            self.pipe_conf.get('stats_file'))


help_doc = """Somatic Mutations Classification.
    Functional annotation of called somatic variants.
    VEP and/or GATK Funcotator
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
                        help='The version of the Human Genome reference to use. [default=hg19]')

    parser.add_argument('--cache-version', '-cv',
                        type=str, default='106',
                        help='Version of offline cache to use with VEP (e.g. 75, 91, 102, 105, 106). [default=106]')

    parser.add_argument('--also-funcotator', '-af',
                        action='store_true', default=False,
                        help='also run gatk funcotator')

    parser.add_argument('--only-funcotator', '-of',
                        action='store_true', default=False,
                        help='only run gatk funcotator')

    parser.add_argument('--force', '-f',
                        action='store_true', default=False,
                        help='overwrite directories and files if they exist in the destination')

    parser.add_argument('--dryrun', '-d',
                        action='store_true', default=False,
                        help='Workflow will be only described.')


def implementation(logger, args):
    logger.info(help_doc.replace('\n', ''))

    workflow = ClassifyWorkflow(args=args,
                                logger=logger)
    workflow.run()


def do_register(registration_list):
    registration_list.append(('classify',
                              help_doc,
                              make_parser,
                              implementation))
