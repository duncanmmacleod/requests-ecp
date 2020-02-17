# `requests-ecp`

A SAML/ECP authentication handler for python-requests.

## Development status

[![Travis](https://img.shields.io/travis/gwpy/gwpy/master.svg?label=Linux%20%28conda%29)](https://travis-ci.com/gwpy/gwpy)
[![Cirlce](https://img.shields.io/circleci/project/github/duncanmmacleod/requests-ecp/master.svg?label=Linux%20%28other%29)](https://circleci.com/gh/duncanmmacleod/requests-ecp)
[![Appveyor](https://img.shields.io/appveyor/ci/duncanmmacleod/requests-ecp/master.svg?label=Windows%20%28conda%29)](https://ci.appveyor.com/project/duncanmmacleod/requests-ecp/branch/master)  
[![codecov](https://codecov.io/gh/duncanmmacleod/requests-ecp/branch/master/graph/badge.svg)](https://codecov.io/gh/duncanmmacleod/requests-ecp)
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
