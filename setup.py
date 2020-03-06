# -*- coding: utf-8 -*-
# Copyright (C) Cardiff University (2019-2020)
#
# This file is part of requests_ecp
#
# requests_ecp is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# requests_ecp is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with requests_ecp.  If not, see <http://www.gnu.org/licenses/>.

"""Build configuration for requests_ecp
"""

import re

from setuptools import setup

__author__ = "Duncan Macleod <duncan.macleod@ligo.org>"


def find_version(path, varname="__version__"):
    """Parse the version metadata in the given file.
    """
    with open(path, 'r') as fobj:
        version_file = fobj.read()
    version_match = re.search(
        r"^{0} = ['\"]([^'\"]*)['\"]".format(varname),
        version_file,
        re.M,
    )
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


def read(path):
    """Read the long description out of a file
    """
    with open(path, "r") as fobj:
        return fobj.read()


TESTS_REQUIRE = [
    "pytest >= 2.9.2",
    "pytest-cov",
    "requests-mock >= 1.5.0",
]

setup(
    # distribution metadata
    name="requests-ecp",
    version=find_version("requests_ecp.py"),
    author="Duncan Macleod",
    author_email="duncan.macleod@ligo.org",
    license="GPL-3.0-or-later",
    description="SAML/ECP authentication handler for python-requests",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/requests-ecp/",
    project_urls={
        "Bug Tracker": "https://github.com/duncanmmacleod/requests-ecp/issues",
        "Documentation": "https://requests-ecp.readthedocs.io/",
        "Source Code": "https://github.com/duncanmmacleod/requests-ecp/",
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Scientific/Engineering',
    ],
    # contents
    py_modules=[
        "requests_ecp",
    ],
    # dependencies
    python_requires=">=3.5",
    setup_requires=[
        "setuptools",  # MIT
    ],
    install_requires=[
        "lxml",  # BSD
        "requests",  # Apache-2.0
        "requests-kerberos",  # ISC
    ],
    tests_require=TESTS_REQUIRE,
    extras_require={
        "test": TESTS_REQUIRE,
        "docs": [
            "sphinx",
            "sphinx-argparse",
            "sphinx_automodapi",
            "sphinx_rtd_theme",
            "sphinx_tabs",
        ],
    },
)
