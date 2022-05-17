"""
Utilities used by other modules.
"""
import os
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


def overwrite(src, dst):
    if os.path. exists(dst) and os.path.isfile(dst):
        os.remove(dst)
    shutil.copy(src, dst)

