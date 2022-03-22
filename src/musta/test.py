from .utils.snakemake import Snakemake

class TestWorkflow(object):
    def __init__(self, args=None, logger=None):
        self.logger = logger

    def run(self):
        snk = Snakemake(logger=self.logger)
        snk.dry_run()

help_doc = """
Perform a DryRun test on data from 
https://github.com/solida-core/test-data-somatic
"""

def make_parser(parser):
    pass

def implementation(logger, args):
    workflow = TestWorkflow(args=args,
                            logger=logger)
    workflow.run()


def do_register(registration_list):
    registration_list.append(('test',
                              help_doc,
                              make_parser,
                              implementation))
