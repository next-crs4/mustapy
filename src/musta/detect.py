class DetectWorkflow(object):
    def __init__(self, args=None, logger=None):
        self.logger = logger
        self.dry_run = args.dry_run
        self.force = args.force

    def run(self):
        pass

help_doc = """
Driver Gene Detection
Identification of cancer driver genes 
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

    workflow = DetectWorkflow(args=args,
                              logger=logger)
    workflow.run()


def do_register(registration_list):
    registration_list.append(('detect',
                              help_doc,
                              make_parser,
                              implementation))
