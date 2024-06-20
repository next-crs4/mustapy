"""
Utilities used by other modules.
"""
import os
import multiprocessing
import tarfile
import shutil


def gunzip(src, dst):
    with tarfile.open(src) as f_in:
        def is_within_directory(directory, target):
            
            abs_directory = os.path.abspath(directory)
            abs_target = os.path.abspath(target)
        
            prefix = os.path.commonprefix([abs_directory, abs_target])
            
            return prefix == abs_directory
        
        def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
        
            for member in tar.getmembers():
                member_path = os.path.join(path, member.name)
                if not is_within_directory(path, member_path):
                    raise Exception("Attempted Path Traversal in Tar File")
        
            tar.extractall(path, members, numeric_owner=numeric_owner) 
            
        
        safe_extract(f_in, dst)


def get_cores(reserve_cores=1, max_cores=5):
    cores = max_cores if multiprocessing.cpu_count() > max_cores else multiprocessing.cpu_count()
    return max(cores - reserve_cores, 1)


def overwrite(src, dst):
    if os.path.exists(dst) and os.path.isfile(dst):
        os.remove(dst)
    shutil.copy(src, dst)


