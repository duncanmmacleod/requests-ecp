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
from urllib.parse import (
    parse_qs,
    urlparse,
    urlunsplit,
)

from requests import auth as requests_auth

from .ecp import authenticate as ecp_authenticate

GITLAB_AUTH_SHIB_CALLBACK_PATH = "/users/auth/shibboleth/callback"


# -- Auth utilities ---------

def _prompt_username_password(host, username=None):
    """Prompt for a username and password from the console
    """
    if not username:
        username = input("Enter username for {0}: ".format(host))
    password = getpass(
        "Enter password for {0!r} on {1}: ".format(username, host),
    )
    return username, password


# -- Response interception --

def is_ecp_auth_redirect(response):
    """Return `True` if a response indicates a request for ECP authentication.

    Parameters
    ----------
    response : `requests.Response`
        The response object to inspect.

    Returns
    -------
    state : bool
        `True` if ``response`` looks like a redirect initiated by Shibboleth,
        otherwise `False`.
    """
    if not response.is_redirect:
        return False

    # strip out the redirect location and parse it
    target = response.headers['location']
    query = parse_qs(urlparse(target).query)

    return (
        # Identity Provider
        "SAMLRequest" in query
        # Shibboleth discovery service
        or "Shibboleth.sso" in target
    )


def is_gitlab_auth_redirect(response):
    """Return `True` if a response indicates a gitlab auth redirect.

    Parameters
    ----------
    response : `requests.Response`
        The response object to inspect.

    Returns
    -------
    state : bool
        `True` if ``response`` looks like a redirect initiated by GitLab,
        otherwise `False`.
    """
    if not response.is_redirect:
        return False

    # if the redirect cam from the callback, then the callback doesn't work
    # so let's not get stuck in an infinite loop
    if urlparse(response.url).path == GITLAB_AUTH_SHIB_CALLBACK_PATH:
        return False

    # parse the redirect target to get the gitlab host name
    uparts = urlparse(response.headers['location'])

    # if not redirecting to login, this isn't meant for us
    if not uparts.path == "/users/sign_in":
        return False

    # only redirect if there is a _gitlab_session cookie to use later
    for cookie in response.cookies:
        if (
            cookie.name == "_gitlab_session"
            and cookie.domain == uparts.hostname
        ):
            return True


# -- Auth -------------------

def _import_kerberos_auth():
    try:
        from requests_gssapi import HTTPKerberosAuth
    except ModuleNotFoundError as exc:  # pragma: no cover
        try:
            # debian doesn't have requests-gssapi
            from requests_kerberos import HTTPKerberosAuth
        except ModuleNotFoundError:
            # no kerberos interface, display a useful error message
            raise ModuleNotFoundError(
                f"{exc.msg}; you must install requests-gssapi "
                "to use Kerberos auth"
            ) from exc
    return HTTPKerberosAuth


def _kerberos_auth(url):
    """Intialise a `requests_gssapi.HTTPKerberosAuth`.
    """
    HTTPKerberosAuth = _import_kerberos_auth()
    loginhost = urlparse(url).hostname
    return HTTPKerberosAuth(
        force_preemptive=True,
        hostname_override=loginhost,
    )


class HTTPECPAuth(requests_auth.AuthBase):
    """SAML2/ECP authorisation plugin for :mod:`requests`.

    This auth plugin intercepts ``302 Found`` redirect responses
    that target a `SAMLRequest` authorisation or a `Shibboleth.sso`
    discovery service, and executes a SAML2/ECP workflow against
    the configured Identity Provider (``idp``).

    Kerberos authentication is supported via the
    `requests GSSAPI <https://github.com/pythongssapi/requests-gssapi>`__
    module.

    >>> from requests import Session
    >>> from requests_ecp import HTTPECPAuth
    >>> with Session() as sess:
    ...     sess.auth = HTTPECPAuth(idp="https://idp.example.com/SAML2/SOAP/ECP")
    ...     sess.get("https://private.example.com/data")

    """   # noqa: E501
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
        if kerberos:  # raise an ImportError early
            _import_kerberos_auth()
        self.kerberos = kerberos
        self.username = username
        self.password = password
        self._idpauth = None

        #: counter for authentication attemps for a single request
        self._num_ecp_auth = 0

    @staticmethod
    def _init_auth(idp, kerberos=False, username=None, password=None):
        if kerberos:
            return _kerberos_auth(
                kerberos if isinstance(kerberos, str) else idp,
            )
        elif username and password:
            return requests_auth.HTTPBasicAuth(username, password)
        return requests_auth.HTTPBasicAuth(*_prompt_username_password(
            urlparse(idp).hostname,
            username,
        ))

    def reset(self):
        self._num_ecp_auth = 0

    # -- auth method --------

    def _authenticate_session(
        self,
        session,
        endpoint=None,
        url=None,
        **kwargs,
    ):
        """Execute ECP authenticate for a `requests.Session`.
        """
        url = url or endpoint or self.idp
        self._authenticate(session, url=url)

    def _authenticate_response(self, response, endpoint=None, **kwargs):
        """Execute ECP authenticate based on a `requests.Response`.

        Returns
        -------
        response : `requests.Response`
            The final response from the service provider that should be
            a `302 Found` redirect back to the original resource URL.
        """
        response.raw.read()
        response.raw.release_conn()
        new = list(self._authenticate(
            response.connection,
            endpoint=endpoint,
            url=response.url,
            **kwargs,
        ))
        r = new.pop(-1)
        r.history.extend([response] + new)
        return r

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

    # -- event handling -----

    def handle_response(self, response, **kwargs):
        """Handle ECP authentication based on a transation response
        """
        # if we've already tried, don't try again,
        # otherwise we end up in an infinite loop
        if self._num_ecp_auth:
            return response

        # if the redirect looks like gitlab trying to go through ECP auth,
        # redirect to the shibboleth callback for gitlab
        if is_gitlab_auth_redirect(response):
            # redirect the redirect to the shibboleth callback URL
            parts = urlparse(response.headers['location'])
            response.headers['location'] = urlunsplit((
                parts.scheme,
                parts.netloc,
                GITLAB_AUTH_SHIB_CALLBACK_PATH,
                parts.query,
                parts.fragment,
            ))

        # if the request was redirected in a way that looks like the SP
        # is asking for ECP authentication, then handle that here:
        # (but only do that once)
        elif is_ecp_auth_redirect(response):
            # authenticate and return the final redirect
            response = self._authenticate_response(response, **kwargs)
            self._num_ecp_auth += 1

        return response

    def deregister(self, response):
        """Deregister the response handler
        """
        response.request.deregister_hook('response', self.handle_response)
        self.reset()

    def __call__(self, request):
        """Register the response handler
        """
        self.reset()
        request.register_hook('response', self.handle_response)
        return request
