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

"""Auth plugin for ECP requests.
"""

__author__ = "Duncan Macleod <duncan.macleod@ligo.org>"

from getpass import getpass
from urllib import parse as urllib_parse

from requests import auth as requests_auth
from requests.cookies import extract_cookies_to_jar

try:
    from requests_gssapi import HTTPKerberosAuth
except ModuleNotFoundError:  # pragma: no cover
    # debian doesn't have requests-gssapi
    from requests_kerberos import HTTPKerberosAuth

from .ecp import authenticate as ecp_authenticate


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

        #: counter for authentication attemps for a single request
        self._num_ecp_auth = 0

    @staticmethod
    def _init_auth(idp, kerberos=False, username=None, password=None):
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

    # -- auth method --------

    def authenticate(self, session, endpoint=None, url=None, **kwargs):
        url = url or endpoint or self.idp
        adapter = session.get_adapter(url=url)
        # authenticate and store cookies
        for resp in self._authenticate(adapter, url=url):
            extract_cookies_to_jar(session.cookies, resp.request, resp.raw)

    def _authenticate_response(self, response, endpoint=None, **kwargs):
        response.raw.read()
        response.raw.release_conn()
        return self._authenticate(
            response.connection,
            endpoint=endpoint,
            url=response.url,
            **kwargs
        )

    def _authenticate(
            self,
            connection,
            endpoint=None,
            url=None,
            **kwargs
    ):
        """Handle user authentication with ECP.
        """
        if self._idpauth is None:  # init auth now
            self._idpauth = self._init_auth(
                self.idp,
                kerberos=self.kerberos,
                username=self.username,
                password=self.password,
            )

        # authenticate
        return ecp_authenticate(
            connection,
            self._idpauth,
            endpoint or self.idp,
            url=url,
            **kwargs,
        )

    # -- auth discovery -----

    @staticmethod
    def is_ecp_auth_redirect(response):
        """Return `True` if a response indicates a request for authentication
        """
        if not response.is_redirect:
            return False

        # strip out the redirect location and parse it
        target = response.headers['location']
        if isinstance(target, bytes):
            target = target.decode("utf-8")
        query = urllib_parse.parse_qs(urllib_parse.urlparse(target).query)

        return (
                "SAMLRequest" in query or  # redirected to IdP
                "Shibboleth.sso" in target  # Shibboleth discovery service
        )

    # -- event handling -----

    def handle_response(self, response, **kwargs):
        """Handle ECP authentication based on a transation response
        """
        # if the request was redirected in a way that looks like the SP
        # is asking for ECP authentication, then handle that here:
        # (but only do that once)
        if self.is_ecp_auth_redirect(response) and not self._num_ecp_auth:
            # authenticate (preserving the history)
            response.history.extend(
                self._authenticate_response(response, **kwargs),
            )

            # and hijack the redirect back to itself
            response.headers['location'] = response.url
            self._num_ecp_auth += 1
        else:
            self._num_ecp_auth = 0

        return response

    def deregister(self, response):
        """Deregister the response handler
        """
        response.request.deregister_hook('response', self.handle_response)

    def __call__(self, request):
        """Register the response handler
        """
        request.register_hook('response', self.handle_response)
        return request
