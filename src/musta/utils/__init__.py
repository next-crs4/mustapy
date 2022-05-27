"""
Utilities used by other modules.
"""
import os
import subprocess
import multiprocessing
import tarfile
import shutil


def gunzip(src, dst):
    with tarfile.open(src) as f_in:
        f_in.extractall(dst)


def get_cores():
    return multiprocessing.cpu_count()


def overwrite(src, dst):
    if os.path. exists(dst) and os.path.isfile(dst):
        os.remove(dst)
    shutil.copy(src, dst)

