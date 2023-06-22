import os.path
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

        check = int(args.fast) + int(args.strict) + int(args.soft)
        if check == 0:
            self.mutect = not args.exclude_mutect
            self.lofreq = not args.exclude_lofreq
            self.varscan = not args.exclude_varscan
            self.vardict = not args.exclude_vardict
            self.muse = not args.exclude_muse
            self.strelka = not args.exclude_strelka
        elif check == 1:
            self.mutect = not args.exclude_mutect and args.strict
            self.lofreq = not args.exclude_lofreq and (args.strict or args.fast)
            self.varscan = not args.exclude_varscan and (args.soft or args.fast)
            self.vardict = not args.exclude_vardict and args.soft
            self.muse = not args.exclude_muse and (args.soft or args.fast)
            self.strelka = not args.exclude_strelka and (args.strict or args.fast)
        else:
            self.logger.error("choose only one of these arguments: --fast / --soft / --strict . Exiting...")
            sys.exit()


        if not self.bed_file and not self.muse:
            self.logger.error("-b | --bed-file is a mandatory argument. Exiting...")
            sys.exit()

        if self.mutect:
            if not self.variant_file:
                self.logger.error("-v | --variant-file is a mandatory argument. Exiting...")
                sys.exit()
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
        self.logger.info('Variant Calling')
        self.pipe_cfg.reset_run_mode()
        self.pipe_cfg.set_run_mode(run_mode='call')

        if self.mutect:
            self.logger.info('Variant Caller:  \'mutect\'')
            self.pipe_cfg.reset_callers()
            self.pipe_cfg.set_callers(caller='mutect')
            self.pipe_cfg.write()

            self.pipe.run(snakefile=self.pipe_snakefile,
                          dryrun=self.dryrun,
                          cores=self.cores,
                          report_file=self._get_report_file('mutect'),
                          stats_file=self._get_stats_file('mutect'),
                          )

        if self.lofreq:
            self.logger.info('Variant Caller:  \'lofreq\'')
            self.pipe_cfg.reset_callers()
            self.pipe_cfg.set_callers(caller='lofreq')
            self.pipe_cfg.write()

            self.pipe.run(snakefile=self.pipe_snakefile,
                          dryrun=self.dryrun,
                          cores=self.cores,
                          report_file=self._get_report_file('lofreq'),
                          stats_file=self._get_stats_file('lofreq'),
                          )

        if self.varscan:
            self.logger.info('Variant Caller:  \'varscan\'')
            self.pipe_cfg.reset_callers()
            self.pipe_cfg.set_callers(caller='varscan')
            self.pipe_cfg.write()

            self.pipe.run(snakefile=self.pipe_snakefile,
                          dryrun=self.dryrun,
                          cores=self.cores,
                          report_file=self._get_report_file('varscan'),
                          stats_file=self._get_stats_file('varscan'),
                          )

        if self.vardict:
            self.logger.info('Variant Caller:  \'vardict\'')
            self.pipe_cfg.reset_callers()
            self.pipe_cfg.set_callers(caller='vardict')
            self.pipe_cfg.write()

            self.pipe.run(snakefile=self.pipe_snakefile,
                          dryrun=self.dryrun,
                          cores=self.cores,
                          report_file=self._get_report_file('vardict'),
                          stats_file=self._get_stats_file('vardict'),
                          )

        if self.muse:
            self.logger.info('Variant Caller:  \'muse\'')
            self.pipe_cfg.reset_callers()
            self.pipe_cfg.set_callers(caller='muse')
            self.pipe_cfg.write()

            self.pipe.run(snakefile=self.pipe_snakefile,
                          dryrun=self.dryrun,
                          cores=self.cores,
                          report_file = self._get_report_file('muse'),
                          stats_file = self._get_stats_file('muse'),
            )

        if self.strelka:
            self.logger.info('caller:  \'strelka\'')
            self.pipe_cfg.reset_callers()
            self.pipe_cfg.set_callers(caller='strelka')
            self.pipe_cfg.write()

            self.pipe.run(snakefile=self.pipe_snakefile,
                          dryrun=self.dryrun,
                          cores=self.cores,
                          report_file=self._get_report_file('strelka'),
                          stats_file=self._get_stats_file('strelka'),
            )

        self.pipe_cfg.reset_callers()
        self.pipe_cfg.reset_run_mode()
        self.pipe_cfg.reset_callers()
        if self.mutect:
            self.pipe_cfg.set_callers(caller='mutect')
        if self.lofreq:
            self.pipe_cfg.set_callers(caller='lofreq')
        if self.varscan:
            self.pipe_cfg.set_callers(caller='varscan')
        if self.vardict:
            self.pipe_cfg.set_callers(caller='vardict')
        if self.muse:
            self.pipe_cfg.set_callers(caller='muse')
        if self.strelka:
            self.pipe_cfg.set_callers(caller='strelka')
        self.pipe_cfg.set_run_mode(run_mode='combine')
        self.pipe_cfg.write()

        self.pipe.run(snakefile=self.pipe_snakefile,
                      dryrun=self.dryrun,
                      cores=self.cores,
                      report_file=self._get_report_file('somaticseq'),
                      stats_file=self._get_stats_file('somaticseq'),
        )

        self.pipe.report(snakefile=self.pipe_snakefile,
                         report_file=self.pipe_report_file)

        self.logger.info("Logs in <WORKDIR>/{}/<VARIANT CALLER>".format(self.io_conf.get('log_folder_name')))
        self.logger.info("Outputs in <WORKDIR>/{}/{}/<VARIANT CALLER>".format(self.io_conf.get('output_folder_name'),
                                                                              self.io_conf.get('detect_folder_name')))

        self.logger.info("Report in <WORKDIR>/{}/<VARIANT CALLER>/{}".format(self.io_conf.get('output_folder_name'),
                                                                             self.pipe_conf.get('report_file')))

        self.logger.info("VCFs in <WORKDIR>/{}/{}/results".format(self.io_conf.get('output_folder_name'),
                                                                  self.io_conf.get('detect_folder_name')))

    def _get_report_file(self, caller=""):
        return os.path.join(self.output_dir,
                            self.io_conf.get('detect_folder_name'),
                            caller,
                            self.pipe_conf.get('report_file'))

    def _get_stats_file(self, caller):
        return os.path.join(self.output_dir,
                            self.io_conf.get('detect_folder_name'),
                            caller,
                            self.pipe_conf.get('stats_file'))


help_doc = """Somatic Mutations Detection.
    1.  Multiple Variant Calling: mutect, lofreq, varscan, vardict, muse, strelka.
    2.  Ensemble consensus approach to combine results and to improve the performance of variant calling

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
                        help='compressed and indexed BED file listing regions to restrict analysis to',
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
                        help='compressed and indexed VCF file containing known germline variants (only for --lofreq/-lf and --muse/-ms foption)',
                        required=False)

    parser.add_argument('--exclude-mutect', '-emu',
                        action='store_true', default=False,
                        help="do NOT run MUTECT variant caller")

    parser.add_argument('--exclude-lofreq', '-elf',
                        action='store_true', default=False,
                        help='do NOT run LOFREQ variant caller')

    parser.add_argument('--exclude-strelka', '-esk',
                        action='store_true', default=False,
                        help='do NOT run STRELKA variant caller')

    parser.add_argument('--exclude-muse', '-ems',
                        action='store_true', default=False,
                        help='do NOT run MUSE variant caller')

    parser.add_argument('--exclude-varscan', '-evs',
                        action='store_true', default=False,
                        help='do NOT run VARSCAN variant caller')

    parser.add_argument('--exclude-vardict', '-evd',
                        action='store_true', default=False,
                        help='do NOT run VARDICT variant caller')

    parser.add_argument('--strict',
                        action='store_true', default=False,
                        help='run only restrictive variant callers: mutect, lofreq, strelka')

    parser.add_argument('--soft',
                        action='store_true', default=False,
                        help='run only permissive variant callers: varscan, vardict, muse')

    parser.add_argument('--fast',
                        action='store_true', default=False,
                        help='run only fast variant callers: lofreq, varscan, strelka, muse')

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
    registration_list.append(('detect',
                              help_doc,
                              make_parser,
                              implementation))
