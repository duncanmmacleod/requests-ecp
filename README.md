# `requests-ecp`

A SAML/ECP authentication handler for python-requests.

## Release status

[![PyPI version](https://img.shields.io/pypi/v/requests-ecp.svg)](https://pypi.python.org/pypi/requests-ecp)
[![Conda version](https://img.shields.io/conda/vn/conda-forge/requests-ecp.svg)](https://anaconda.org/conda-forge/requests-ecp/)  
[![License](https://img.shields.io/pypi/l/requests-ecp.svg)](https://choosealicense.com/licenses/gpl-3.0/)
![Supported Python versions](https://img.shields.io/pypi/pyversions/requests-ecp.svg)

## Development status

[![Build status](https://git.ligo.org/computing/software/requests-ecp/badges/main/pipeline.svg)](https://git.ligo.org/computing/software/requests-ecp/-/pipelines)
![Code coverage](https://git.ligo.org/computing/software/requests-ecp/badges/main/coverage.svg)
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
