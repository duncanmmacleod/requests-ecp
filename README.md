# `requests-ecp`

A SAML/ECP authentication handler for python-requests.

## Release status

[![PyPI version](https://badge.fury.io/py/requests-ecp.svg)](http://badge.fury.io/py/requests-ecp)
[![Conda version](https://img.shields.io/conda/vn/conda-forge/requests-ecp.svg)](https://anaconda.org/conda-forge/requests-ecp/)  
[![DOI](https://zenodo.org/badge/238942798.svg)](https://zenodo.org/badge/latestdoi/238942798)
[![License](https://img.shields.io/pypi/l/requests-ecp.svg)](https://choosealicense.com/licenses/gpl-3.0/)
![Supported Python versions](https://img.shields.io/pypi/pyversions/requests-ecp.svg)

## Development status

[![Travis](https://img.shields.io/travis/com/duncanmmacleod/requests-ecp/master?label=Unix%20%28conda%29&logo=travis)](https://travis-ci.com/duncanmmacleod/requests-ecp)
[![Circle](https://img.shields.io/circleci/project/github/duncanmmacleod/requests-ecp/master.svg?label=Linux%20%28other%29&logo=circleci)](https://circleci.com/gh/duncanmmacleod/requests-ecp)
[![Appveyor](https://img.shields.io/appveyor/ci/duncanmmacleod/requests-ecp/master.svg?label=Windows%20%28conda%29&logo=appveyor)](https://ci.appveyor.com/project/duncanmmacleod/requests-ecp/branch/master)  
[![Codecov](https://img.shields.io/codecov/c/gh/duncanmmacleod/requests-ecp?logo=codecov)](https://codecov.io/gh/duncanmmacleod/requests-ecp)
[![Maintainability](https://api.codeclimate.com/v1/badges/9b10bd39e588fd5a34ab/maintainability)](https://codeclimate.com/github/duncanmmacleod/requests-ecp/maintainability)
[![Documentation](https://readthedocs.org/projects/requests-ecp/badge/?version=latest)](https://requests-ecp.readthedocs.io/en/latest/?badge=latest)

## Installation

See https://requests-ecp.readthedocs.io/en/latest/#installation for installation instructions.

## Basic usage

Attach the `HTTPECPAuth` object to your [Requests](https://requests.readthedocs.io/en/master/)
Session and the relevant authentication will happen whenever required.

```python
>>> from requests import Session
>>> from requests_ecp import HTTPECPAuth
>>> with Session() as sess:
...     sess.auth = HTTPECPAuth("https://idp.university.ac.uk/idp/profile/SAML2/SOAP/ECP")
...     sess.get("https://data.university.ac.uk/mydata.dat")
```
