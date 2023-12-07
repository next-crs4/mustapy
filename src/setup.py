import glob
import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'APPNAME')) as f:
    __appname__ = f.read().strip()

with open(os.path.join(here, 'VERSION')) as f:
    __version__ = f.read().strip()

with open(os.path.join(here, 'DESCRIPTION')) as f:
    __description__ = f.read().strip()

with open(os.path.join(here, 'requirements.txt')) as f:
    required = f.read().splitlines()

extra_files = [os.path.join(here, 'APPNAME'),
               os.path.join(here, 'VERSION'),
               os.path.join(here, 'DESCRIPTION'),
               os.path.join(here, 'requirements.txt'),
               ]

AUTHOR_INFO = [
    ("Rossano Atzeni", "ratzeni@crs4.it"),
    ("Matteo Massidda", "mmassidda@crs4.it"),
]
MAINTAINER_INFO = [
    ("Rossano Atzeni", "ratzeni@crs4.it"),
    ("Matteo Massidda", "mmassidda@crs4.it"),
]
AUTHOR = ", ".join(t[0] for t in AUTHOR_INFO)
AUTHOR_EMAIL = ", ".join("<%s>" % t[1] for t in AUTHOR_INFO)
MAINTAINER = ", ".join(t[0] for t in MAINTAINER_INFO)
MAINTAINER_EMAIL = ", ".join("<%s>" % t[1] for t in MAINTAINER_INFO)

setup(name=__appname__,
      version=__version__,
      description=__description__,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      maintainer=MAINTAINER,
      maintainer_email=MAINTAINER_EMAIL,
      install_requires=required,
      scripts=glob.glob('scripts/*'),
      packages=find_packages(),
      include_package_data=True,
      package_data={'': extra_files},
      zip_safe=False,
      license='MIT',
      platforms="Posix; MacOS X; Windows",
      classifiers=["Development Status :: 4 - Beta",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: MIT License",
                   "Operating System :: OS Independent",
                   "Topic :: Utilities",
                   "Programming Language :: Python :: 3.8"],
      # entry_points={'console_scripts': ['musta=musta.main:main',],},
      )
