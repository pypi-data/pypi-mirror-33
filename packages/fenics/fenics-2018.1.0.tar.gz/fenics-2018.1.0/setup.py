# -*- coding: utf-8 -*-
from __future__ import print_function

import sys

from setuptools import setup

if sys.version_info < (3, 5):
    print("Python 3.5 or higher required, please upgrade.")
    sys.exit(1)

VERSION = "2018.1.0"
RESTRICT_REQUIREMENTS = ">=2018.1.0,<2018.2"

REQUIREMENTS = [
    "fenics-ffc{}".format(RESTRICT_REQUIREMENTS),
    "fenics-fiat{}".format(RESTRICT_REQUIREMENTS),
    "fenics-ufl{}".format(RESTRICT_REQUIREMENTS),
    "fenics-dijitso{}".format(RESTRICT_REQUIREMENTS),
]

URL = "https://bitbucket.org/fenics-project"

AUTHORS = """\
The FEniCS Project contributors
"""

CLASSIFIERS = """\
Development Status :: 5 - Production/Stable
Intended Audience :: Developers
Intended Audience :: Science/Research
License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)
Operating System :: POSIX
Operating System :: POSIX :: Linux
Operating System :: MacOS :: MacOS X
Operating System :: Microsoft :: Windows
Programming Language :: Python
Programming Language :: Python :: 2
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3
Programming Language :: Python :: 3.4
Programming Language :: Python :: 3.5
Programming Language :: Python :: 3.6
Topic :: Scientific/Engineering :: Mathematics
Topic :: Software Development :: Libraries :: Python Modules
"""


def run_install():
    """Run installation"""
    # Call distutils to perform installation
    setup(name="fenics",
          description="The FEniCS Project Python Metapackage",
          version=VERSION,
          author=AUTHORS,
          classifiers=[_f for _f in CLASSIFIERS.split('\n') if _f],
          license="LGPL version 3 or later",
          author_email="fenics-dev@googlegroups.com",
          maintainer_email="fenics-dev@googlegroups.com",
          url=URL,
          platforms=["Windows", "Linux", "Solaris", "Mac OS-X", "Unix"],
          install_requires=REQUIREMENTS,
          zip_safe=False)


if __name__ == "__main__":
    run_install()
