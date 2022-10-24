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

"""`requests.Session` mixin/wrapper for ECP requests.
"""

__author__ = "Duncan Macleod <duncan.macleod@ligo.org>"

from requests import (
    Session as _Session,
)

from .auth import HTTPECPAuth


class ECPAuthSessionMixin:
    """A mixin for `requests.Session` to add default ECP Auth
    """
    def __init__(
            self,
            idp=None,
            kerberos=False,
            username=None,
            password=None,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.auth = HTTPECPAuth(
            idp,
            kerberos=kerberos,
            username=username,
            password=password,
        )


class Session(ECPAuthSessionMixin, _Session):
    """A `requests.Session` with default ECP authentication
    """
    def ecp_authenticate(self, endpoint=None, url=None, **kwargs):
        """Manually authenticate against the endpoint

        This generates a shibboleth session cookie for the domain
        of the given URL, which defaults to the endpoint itself.
        """
        return self.auth.authenticate(
            self,
            endpoint=endpoint,
            url=url,
            **kwargs
        )
