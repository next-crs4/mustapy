from snakemake import snakemake
from snakedeploy.deploy import deploy

class Snakemake(object):
    def __init__(self,
                 snakefile="/musta/workflow/Snakefile",
                 report="/output/reports",
                 cores=1,
                 workdir="/output",
                 reason=True,
                 logger=None):

        self.logger = logger
        self.snakefile = snakefile
        self.report = report
        self.cores = cores
        self.workdir = workdir
        self.reason = reason

    def run(self):
        
        snakemake(snakefile = self.snakefile,
                  workdir = self.workdir,
                  report=self.report,
                  cores=self.cores,
                  printreason=self.reason,
                  use_conda=True)

    def dry_run(self):

        snakemake(snakefile=self.snakefile,
                  workdir=self.workdir,
                  report=self.report,
                  cores=self.cores,
                  printreason=self.reason,
                  use_conda=True,
                  dryrun=True)

