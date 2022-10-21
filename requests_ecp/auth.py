# -*- coding: utf-8 -*-
# Copyright (C) Cardiff University (2020-2022)
#
# This file is part of requests_ecp.
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

"""Auth plugin for ECP requests
"""

__author__ = "Duncan Macleod <duncan.macleod@ligo.org>"

from getpass import getpass
from urllib import parse as urllib_parse

from requests import (
    auth as requests_auth,
)

try:
    from requests_gssapi import HTTPKerberosAuth
except ModuleNotFoundError:  # pragma: no cover
    # debian doesn't have requests-gssapi
    from requests_kerberos import HTTPKerberosAuth

__all__ = [
    "HTTPECPAuth",
]


def _prompt_username_password(host, username=None):
    """Prompt for a username and password from the console
    """
    if not username:
        username = input("Enter username for {0}: ".format(host))
    password = getpass(
        "Enter password for {0!r} on {1}: ".format(username, host),
    )
    return username, password


class HTTPECPAuth(requests_auth.AuthBase):
    def __init__(
            self,
            idp,
            kerberos=False,
            username=None,
            password=None,
    ):
        #: Address of Identity Provider ECP endpoint.
        self.idp = idp

        #: Authentication object to attach to requests made directly
        #: to the IdP.
        self.kerberos = kerberos
        self.username = username
        self.password = password
        self._idpauth = None

    @staticmethod
    def _init_auth(idp, kerberos=False, username=None, password=None):
        """Intialise the Auth to use when communicating with the IdP.
        """
        if kerberos:
            url = kerberos if isinstance(kerberos, str) else idp
            loginhost = urllib_parse.urlparse(url).netloc.split(':')[0]
            return HTTPKerberosAuth(
                force_preemptive=True,
                hostname_override=loginhost,
            )
        elif username and password:
            return requests_auth.HTTPBasicAuth(username, password)
        return requests_auth.HTTPBasicAuth(*_prompt_username_password(
            urllib_parse.urlparse(idp).hostname,
            username,
        ))

    @property
    def idpauth(self):
        """The Auth object/tuple to use when communicating with the IdP.
        """
        if self._idpauth:
            return self._idpauth
        self._idpauth = self._init_auth(
            self.idp,
            kerberos=self.kerberos,
            username=self.username,
            password=self.password,
        )
        return self._idpauth

    def __call__(self, *args, **kwargs):
        return self.idpauth(*args, **kwargs)
