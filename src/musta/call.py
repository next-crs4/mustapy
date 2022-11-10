import sys

from .utils.workflow import Workflow
from .utils import overwrite


class CallWorkflow(Workflow):
    def __init__(self, args=None, logger=None):
        Workflow.__init__(self, args, logger)

        self.samples_file = args.samples_file
        self.reference_file = args.reference_file
        self.bed_file = args.bed_file
        self.germline_resource = args.germline_resource
        self.variant_file = args.variant_file
        self.dbsnp_file = args.dbsnp_file
        self.lofreq = args.lofreq

        if args.tmpdir:
            self.tmp_dir = args.tmpdir

        if self.lofreq and not self.dbsnp_file:
            self.logger.error("-db | --dbsnp-file is a mandatory argument")
            sys.exit()

        self.resources = dict(
            base=dict(
                reference=self.reference_file,
                bed=self.bed_file,
            ),

            gatk_params=dict(
                germline=self.germline_resource,
                exac=self.variant_file,
            ),

            lofreq_params=dict(
              dbsnp=self.dbsnp_file
            ) if self.dbsnp_file else None
        )

    def run(self):
        Workflow.run(self)

        overwrite(src=self.samples_file,
                  dst=self.pipe_samples_file)

        self.logger.info('Initializing  Config file')
        self.init_config_file(base=self.resources.get('base'),
                              gatk_params=self.resources.get('gatk_params'),
                              lofreq_params=self.resources.get('lofreq_params'))

        self.logger.info('Initializing  Samples file')
        self.init_samples_file(bam_path=self.input_dir)

        self.logger.info('Running')
        self.logger.info('Variant Calling - command: \'call\'')

        self.pipe_cfg.set_run_mode(run_mode='call')
        self.pipe_cfg.set_callers(caller='mutect')
        self.pipe_cfg.write()

        self.pipe.run(snakefile=self.pipe_snakefile,
                      dryrun=self.dryrun,
                      cores=self.cores)

        if self.lofreq:
            self.pipe_cfg.set_run_mode(run_mode='call')
            self.pipe_cfg.reset_callers(caller='mutect')
            self.pipe_cfg.set_callers(caller='lofreq')
            self.pipe_cfg.write()

            self.pipe.run(snakefile=self.pipe_snakefile,
                          dryrun=self.dryrun,
                          cores=self.cores)

        self.logger.info("Logs in <WORKDIR>/outputs/logs")
        self.logger.info("Results in <WORKDIR>/outputs/results")
        self.logger.info("Report in <WORKDIR>/outputs/report.html")


help_doc = """
Variant Calling.
Calls somatic SNVs and indels. 
"""


def make_parser(parser):

    parser.add_argument('--workdir', '-w',
                        type=str, metavar='PATH',
                        help='working folder path',
                        required=True)

    parser.add_argument('--tmpdir', '-t',
                        type=str, metavar='PATH',
                        help='temporary directory (large enough to hold the intermediate files)')

    parser.add_argument('--samples-file', '-s',
                        type=str, metavar='PATH',
                        help='sample list file in YAML format',
                        required=True)

    parser.add_argument('--reference-file', '-r',
                        type=str, metavar='PATH',
                        help='reference FASTA file',
                        required=True)

    parser.add_argument('--bed-file', '-b',
                        type=str, metavar='PATH',
                        help='BED file listing regions to restrict analysis to',
                        required=True)

    parser.add_argument('--variant-file', '-v',
                        type=str, metavar='PATH',
                        help='VCF file containing variants and allele frequencies',
                        required=True)

    parser.add_argument('--germline-resource', '-g',
                        type=str, metavar='PATH',
                        help='Population vcf of germline sequencing containing allele fractions.',
                        required=True)

    parser.add_argument('--force', '-f',
                        action='store_true', default=False,
                        help='force all output files to be re-created')

    parser.add_argument('--lofreq',
                        action='store_true', default=False,
                        help='use lofreq as variant caller')

    parser.add_argument('--dbsnp-file', '-db',
                        type=str, metavar='PATH',
                        help='VCF file (bgzipped and index with tabix) containing known germline variants',
                        required=False)

    parser.add_argument('--dryrun', '-d',
                        action='store_true', default=False,
                        help='Workflow will be only described.')


def implementation(logger, args):
    logger.info(help_doc.replace('\n', ''))

    workflow = CallWorkflow(args=args,
                            logger=logger)
    workflow.run()


def do_register(registration_list):
    registration_list.append(('call',
                              help_doc,
                              make_parser,
                              implementation))
