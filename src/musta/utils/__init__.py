"""
Utilities used by other modules.
"""
import os
import multiprocessing
import tarfile
import shutil


def gunzip(src, dst):
    with tarfile.open(src) as f_in:
        f_in.extractall(dst)


def get_cores(reserve_cores=1, max_cores=5):
    cores = max_cores if multiprocessing.cpu_count() > max_cores else multiprocessing.cpu_count()
    return max(cores - reserve_cores, 1)


def overwrite(src, dst):
    if os.path.exists(dst) and os.path.isfile(dst):
        os.remove(dst)
    shutil.copy(src, dst)


def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
