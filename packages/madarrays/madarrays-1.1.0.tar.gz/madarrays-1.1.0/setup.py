#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ######### COPYRIGHT #########
#
# Copyright(c) 2018
# -----------------
#
# * Laboratoire d'Informatique et Systèmes <http://www.lis-lab.fr/>
# * Université d'Aix-Marseille <http://www.univ-amu.fr/>
# * Centre National de la Recherche Scientifique <http://www.cnrs.fr/>
# * Université de Toulon <http://www.univ-tln.fr/>
#
# Contributors
# ------------
#
# * Ronan Hamon <firstname.lastname_AT_lis-lab.fr>
# * Valentin Emiya <firstname.lastname_AT_lis-lab.fr>
# * Florent Jaillet <firstname.lastname_AT_lis-lab.fr>
#
# Description
# -----------
#
# Python package for audio data structures with missing entries
#
# Licence
# -------
# This file is part of madarrays.
#
# madarrays is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ######### COPYRIGHT #########
import os
from setuptools import setup, find_packages
import sys

NAME = 'madarrays'
DESCRIPTION = 'Python package for audio data structures with missing entries'
LICENSE = 'GNU General Public License v3 (GPLv3)'
URL = 'https://gitlab.lis-lab.fr/skmad-suite/{}'.format(NAME)
AUTHOR = 'Ronan Hamon, Valentin Emiya, and Florent Jaillet'
AUTHOR_EMAIL = ('ronan.hamon@lis-lab.fr, valentin.emiya@lis-lab.fr, '
                'florent.jaillet@lis-lab.fr')
INSTALL_REQUIRES = ['matplotlib',
                    'numpy',
                    'scipy',
                    'simpleaudio',
                    'resampy']
CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Intended Audience :: End Users/Desktop',
    'Intended Audience :: Science/Research',
    'Topic :: Multimedia :: Sound/Audio :: Analysis',
    'Topic :: Scientific/Engineering :: Artificial Intelligence',
    'Topic :: Scientific/Engineering :: Mathematics',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Natural Language :: English',
    'Operating System :: MacOS :: MacOS X ',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6']
PYTHON_REQUIRES = '>=3.5'
EXTRAS_REQUIRE = {
    'dev': ['coverage', 'pytest', 'pytest-cov', 'pytest-randomly', 'ipython'],
    'doc': ['sphinx', 'nbsphinx', 'numpydoc']}
PROJECT_URLS = {'Bug Reports': URL + '/issues',
                'Source': URL}
KEYWORDS = 'audio, data structures, missing data'

###############################################################################
if sys.argv[-1] == 'setup.py':
    print("To install, run 'python setup.py install'\n")

if sys.version_info[:2] < (3, 5):
    errmsg = '{} requires Python 3.5 or later ({[0]:d}.{[1]:d} detected).'
    print(errmsg.format(NAME, sys.version_info[:2]))
    sys.exit(-1)


def get_version():
    v_text = open('VERSION').read().strip()
    v_text_formted = '{"' + v_text.replace('\n', '","').replace(':', '":"')
    v_text_formted += '"}'
    v_dict = eval(v_text_formted)
    return v_dict[NAME]


def set_version(path, VERSION):
    filename = os.path.join(path, '__init__.py')
    buf = ""
    for line in open(filename, "rb"):
        if not line.decode("utf8").startswith("__version__ ="):
            buf += line.decode("utf8")
    f = open(filename, "wb")
    f.write(buf.encode("utf8"))
    f.write(('__version__ = "%s"\n' % VERSION).encode("utf8"))


def setup_package():
    """Setup function"""
    # set version
    VERSION = get_version()

    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
        long_description = f.read()

    mod_dir = NAME
    set_version(mod_dir, get_version())
    setup(name=NAME,
          version=VERSION,
          description=DESCRIPTION,
          long_description=long_description,
          url=URL,
          author=AUTHOR,
          author_email=AUTHOR_EMAIL,
          license=LICENSE,
          classifiers=CLASSIFIERS,
          keywords=KEYWORDS,
          packages=find_packages(exclude=['doc', 'dev']),
          install_requires=INSTALL_REQUIRES,
          python_requires=PYTHON_REQUIRES,
          extras_require=EXTRAS_REQUIRE,
          project_urls=PROJECT_URLS)


if __name__ == "__main__":
    setup_package()
