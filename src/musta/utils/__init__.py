"""
Utilities used by other modules.
"""

import subprocess
import multiprocessing
import gzip
import shutil


def gunzip(src, dst):
    with gzip.open(src, 'rb') as f_in:
        with open(dst, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)


def get_cores():
    return multiprocessing.cpu_count()


def runJob(cmd, logger, timeout=None):

    try:
        process = subprocess.Popen(cmd,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        out = process.communicate()[0]
        logger.info("command output: {}".format(out))

        ret = process.wait()
        logger.info("command return-code:".format(ret))

        return True

    except subprocess.CalledProcessError as e:
        process.kill()

        if e.output:
            logger.info("command output: {}".format(e.output))
        else:
            logger.info("no command output available")

        logger.info("command return-code: {}".format(e.returncode))
        logger.info("command error: {}".format(e.stderr))

        return False

