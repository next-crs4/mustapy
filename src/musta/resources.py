import os
from ftplib import FTP
from .utils import gunzip
from .utils.config import Config


class Resources(object):
    def __init__(self, args=None, logger=None):
        self.logger = logger
        self.annotation = args.annotation

        self.logger.info("Reading configuration file")
        self.conf = Config(config_file=args.config_file,
                           logger=self.logger)

        self.logger.info("Setting paths")
        self.io_conf = self.conf.get_io_section()
        self.resources_dir = args.resources_dir if args.resources_dir else self.io_conf.get('resources_root_path')

        self.ftp_conf = self.conf.get_ftp_section()
        self.dst = os.path.join(self.resources_dir,
                                self.ftp_conf.get('filename'))

    def run(self):
        ftp = FTP(host=self.ftp_conf.get('host'),
                  user=self.ftp_conf.get('user'))

        ftp.cwd(dirname=self.ftp_conf.get('path'))

        self.logger.info("Wait while downloading. It could require several minutes")
        with open(self.dst, 'wb') as fp:
            ftp.retrbinary("RETR {}".format(self.ftp_conf.get('filename')), fp.write)
        ftp.quit()
        self.logger.info("Check your <RESOURCESDIR> and decompress archive downloaded")


help_doc = """
Download resources & references.
"""


def make_parser(parser):

    parser.add_argument('--resources-dir', '-rd',
                        type=str, metavar='PATH',
                        help='resources folder path',
                        required=True)

    parser.add_argument('--annotation', '-a',
                        action='store_true', default=False,
                        help='download data source for annotation step')


def implementation(logger, args):
    logger.info(help_doc.replace('\n', ''))

    workflow = Resources(args=args,
                         logger=logger)

    workflow.run()


def do_register(registration_list):
    registration_list.append(('resources',
                              help_doc,
                              make_parser,
                              implementation))
