import sys

from .utils.workflow import Workflow
from .utils import overwrite


class RollCallWorkflow(Workflow):
    def __init__(self, args=None, logger=None):
        Workflow.__init__(self, args, logger)

        self.samples_file = args.samples_file
        self.reference_file = args.reference_file
        self.bed_file = args.bed_file
        self.dbsnp_file = args.dbsnp_file
        self.lofreq = args.lofreq
        self.varscan = args.varscan
        self.vardict = args.vardict
        self.muse = args.muse
        self.strelka = args.strelka

        if (self.lofreq or self.muse) and not self.dbsnp_file:
            self.logger.error("-db | --dbsnp-file is a mandatory argument")
            sys.exit()

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

    def run(self):
        Workflow.run(self)

        overwrite(src=self.samples_file,
                  dst=self.pipe_samples_file)

        self.logger.info('Initializing  Config file')
        self.init_config_file(base=self.resources.get('base'))

        self.logger.info('Initializing  Samples file')
        self.init_samples_file(bam_path=self.input_dir)

        self.logger.info('Running')

        self.logger.info('Extended Variant Calling - command: \'rollcall\'')
        self.pipe_cfg.set_run_mode(run_mode='rollcall')
        self.pipe_cfg.write()

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


help_doc = """
More Variant Caller.
Calls somatic SNVs and indels with:
LoFreq, VarScan, VardDict, MuSe, Strelka 
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

    parser.add_argument('--reference-file', '-r',
                        type=str, metavar='PATH',
                        help='reference FASTA file',
                        required=True)

    parser.add_argument('--bed-file', '-b',
                        type=str, metavar='PATH',
                        help='BED file listing regions to restrict analysis to',
                        required=True)

    parser.add_argument('--dbsnp-file', '-db',
                        type=str, metavar='PATH',
                        help='VCF file (bgzipped and index with tabix) containing known germline variants',
                        required=False)



    parser.add_argument('--lofreq',
                        action='store_true', default=False,
                        help='use lofreq as variant caller')

    parser.add_argument('--strelka',
                        action='store_true', default=False,
                        help='use strelka as variant caller')

    parser.add_argument('--muse',
                        action='store_true', default=False,
                        help='use muse as variant caller')

    parser.add_argument('--varscan',
                        action='store_true', default=False,
                        help='use varscan as variant caller')

    parser.add_argument('--vardict',
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

    workflow = RollCallWorkflowWorkflow(args=args,
                                        logger=logger)
    workflow.run()


def do_register(registration_list):
    registration_list.append(('rollcall',
                              help_doc,
                              make_parser,
                              implementation))
