# `requests-ecp`

A SAML/ECP authentication handler for python-requests.

## Release status

[![PyPI version](https://img.shields.io/pypi/v/requests-ecp.svg)](https://pypi.python.org/pypi/requests-ecp)
[![Conda version](https://img.shields.io/conda/vn/conda-forge/requests-ecp.svg)](https://anaconda.org/conda-forge/requests-ecp/)  
[![DOI](https://zenodo.org/badge/238942798.svg)](https://zenodo.org/badge/latestdoi/238942798)
[![License](https://img.shields.io/pypi/l/requests-ecp.svg)](https://choosealicense.com/licenses/gpl-3.0/)
![Supported Python versions](https://img.shields.io/pypi/pyversions/requests-ecp.svg)

## Development status

[![Build status](https://github.com/duncanmmacleod/requests-ecp/actions/workflows/build.yml/badge.svg?branch=main)](https://github.com/duncanmmacleod/requests-ecp/actions/workflows/build.yml)
[![Codecov](https://codecov.io/gh/duncanmmacleod/requests-ecp/branch/main/graph/badge.svg?token=PO7lRIPpTm)](https://codecov.io/gh/duncanmmacleod/requests-ecp)
[![Maintainability](https://api.codeclimate.com/v1/badges/9b10bd39e588fd5a34ab/maintainability)](https://codeclimate.com/github/duncanmmacleod/requests-ecp/maintainability)
[![Documentation](https://readthedocs.org/projects/requests-ecp/badge/?version=latest)](https://requests-ecp.readthedocs.io/en/latest/?badge=latest)

## Installation

See https://requests-ecp.readthedocs.io/en/latest/#installation for installation instructions.

## Basic usage

Attach the `HTTPECPAuth` object to your [Requests](https://requests.readthedocs.io/)
Session and the relevant authentication will happen whenever required.

```python
>>> from requests import Session
>>> from requests_ecp import HTTPECPAuth
>>> with Session() as sess:
...     sess.auth = HTTPECPAuth("https://idp.university.ac.uk/idp/profile/SAML2/SOAP/ECP")
...     sess.get("https://data.university.ac.uk/mydata.dat")
```
