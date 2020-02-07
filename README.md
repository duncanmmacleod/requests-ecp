# `requests-ecp`

A SAML/ECP authentication handler for python-requests.

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
