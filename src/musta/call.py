import sys

from .utils.workflow import Workflow
from .utils import overwrite


class CallWorkflow(Workflow):
    def __init__(self, args=None, logger=None):
        Workflow.__init__(self, args, logger)

        self.samples_file = args.samples_file
        self.reference_file = args.reference_file
        self.bed_file = args.bed_file
        self.dbsnp_file = args.dbsnp_file
        self.germline_resource = args.germline_resource
        self.variant_file = args.variant_file

        self.mutect = args.mutect
        self.lofreq = args.lofreq
        self.varscan = args.varscan
        self.vardict = args.vardict
        self.muse = args.muse
        self.strelka = args.strelka

        if not self.bed_file and not self.muse:
            self.logger.error("-b | --bed-file is a mandatory argument. Exiting...")
            sys.exit()

        if self.mutect:
            if not self.variant_file:
                self.logger.error("-v | --variant-file is a mandatory argument. Exiting...")
            if not self.germline_resource:
                self.logger.error("-g | --germline-resource is a mandatory argument. Exiting...")
            sys.exit()

        if (self.lofreq or self.muse) and not self.dbsnp_file:
            self.logger.error("-db | --dbsnp-file is a mandatory argument. Exiting...")
            sys.exit()

        if args.tmpdir:
            self.tmp_dir = args.tmpdir

        self.resources = dict(
            base=dict(
                reference=self.reference_file,
                bed=self.bed_file,
            ),
        )

        if self.dbsnp_file:
            self.resources['base'].update(dict(
                dbsnp=self.dbsnp_file,
            ))

        if self.germline_resource and self.variant_file:
            self.resources['gatk_params']=dict(
                germline=self.germline_resource,
                exac=self.variant_file,
            )


    def run(self):
        Workflow.run(self)

        overwrite(src=self.samples_file,
                  dst=self.pipe_samples_file)

        self.logger.info('Initializing  Config file')
        self.init_config_file(base=self.resources.get('base'),
                              gatk_params=self.resources.get('gatk_params'),
                              )

        self.logger.info('Initializing  Samples file')
        self.init_samples_file(bam_path=self.input_dir)

        self.logger.info('Running')
        self.logger.info('Variant Calling - command: \'call\'')
        self.pipe_cfg.set_run_mode(run_mode='call')
        self.pipe_cfg.write()

        if self.mutect:
            self.logger.info('caller:  \'mutect\'')
            self.pipe_cfg.reset_callers()
            self.pipe_cfg.set_callers(caller='mutect')
            self.pipe_cfg.write()

            self.pipe.run(snakefile=self.pipe_snakefile,
                          dryrun=self.dryrun,
                          cores=self.cores)

        if self.lofreq:
            self.logger.info('caller:  \'lofreq\'')
            self.pipe_cfg.reset_callers()
            self.pipe_cfg.set_callers(caller='lofreq')
            self.pipe_cfg.write()

            self.pipe.run(snakefile=self.pipe_snakefile,
                          dryrun=self.dryrun,
                          cores=self.cores)

        if self.varscan:
            self.logger.info('caller:  \'varscan\'')
            self.pipe_cfg.reset_callers()
            self.pipe_cfg.set_callers(caller='varscan')
            self.pipe_cfg.write()

            self.pipe.run(snakefile=self.pipe_snakefile,
                          dryrun=self.dryrun,
                          cores=self.cores)

        if self.vardict:
            self.logger.info('caller:  \'vardict\'')
            self.pipe_cfg.reset_callers()
            self.pipe_cfg.set_callers(caller='vardict')
            self.pipe_cfg.write()

            self.pipe.run(snakefile=self.pipe_snakefile,
                          dryrun=self.dryrun,
                          cores=self.cores)

        if self.muse:
            self.logger.info('caller:  \'muse\'')
            self.pipe_cfg.reset_callers()
            self.pipe_cfg.set_callers(caller='muse')
            self.pipe_cfg.write()

            self.pipe.run(snakefile=self.pipe_snakefile,
                          dryrun=self.dryrun,
                          cores=self.cores)

        if self.strelka:
            self.logger.info('caller:  \'strelka\'')
            self.pipe_cfg.reset_callers()
            self.pipe_cfg.set_callers(caller='strelka')
            self.pipe_cfg.write()

            self.pipe.run(snakefile=self.pipe_snakefile,
                          dryrun=self.dryrun,
                          cores=self.cores)

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
                        required=False)

    parser.add_argument('--variant-file', '-v',
                        type=str, metavar='PATH',
                        help='VCF file containing variants and allele frequencies (only for --mutect/-mu option)',
                        required=False)

    parser.add_argument('--germline-resource', '-g',
                        type=str, metavar='PATH',
                        help='Population vcf of germline sequencing containing allele fractions (only for --mutect/-mu option)',
                        required=False)

    parser.add_argument('--dbsnp-file', '-db',
                        type=str, metavar='PATH',
                        help='VCF file (bgzipped and index with tabix) containing known germline variants (only for --lofreq/-lf and --muse/-ms foption)',
                        required=False)

    parser.add_argument('--mutect', '-mu',
                        action='store_true', default=False,
                        help='use lofreq as variant caller')

    parser.add_argument('--lofreq', '-lf',
                        action='store_true', default=False,
                        help='use lofreq as variant caller')

    parser.add_argument('--strelka', '-sk',
                        action='store_true', default=False,
                        help='use strelka as variant caller')

    parser.add_argument('--muse', '-ms',
                        action='store_true', default=False,
                        help='use muse as variant caller')

    parser.add_argument('--varscan', '-vs',
                        action='store_true', default=False,
                        help='use varscan as variant caller')

    parser.add_argument('--vardict', '-vd',
                        action='store_true', default=False,
                        help='use vardict as variant caller')

    parser.add_argument('--force', '-f',
                        action='store_true', default=False,
                        help='force all output files to be re-created')

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
