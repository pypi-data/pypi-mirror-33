#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Author: Olivier Watté <user>
# @Date:   2018-06-29T06:30:53-04:00
# @Email:  owatte@ipeos.com
# @Last modified by:   user
# @Last modified time: 2018-07-02T10:52:41-04:00
# @License: GPLv3
# @Copyright: IPEOS I-Solutions

from setuptools import setup, find_packages

import vigimeteo_cli

setup(
    name='vigimeteo_cli',
    version=vigimeteo_cli.__version__,
    packages=find_packages(),
    author="Olivier Watte - IPEOS",
    author_email="owatte@ipeos.com",
    description="Get current French West Indies weather awareness level "
    "(Vigilance Meteo)",
    long_description=open('README.md').read(),
    include_package_data=True,
    url='https://work.ipeos.com/gitlab/vigimeteo/vigimeteo-cli',
    classifiers=[
        "Programming Language :: Python",
        "Environment :: Console",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 "
        "or later (GPLv3+)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.5",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    install_requires=[
        'certifi==2018.4.16',
        'chardet==3.0.4',
        'docopt==0.6.2',
        'fake-useragent==0.1.10',
        'idna==2.7',
        'pdfminer.six==20170720',
        'pycryptodome==3.6.3',
        'requests==2.19.1',
        'six==1.11.0',
        'urllib3==1.23'
    ],
    entry_points={
        'console_scripts': [
            'vigimeteo = vigimeteo_cli.cli:main',
        ],

    },
)
