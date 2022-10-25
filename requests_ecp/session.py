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
    """A mixin for `requests.Session` to add default ECP Auth.

    This creates a default `~requests.Session.auth` attribute on created
    `~requests.Session` objects as an instance of the
    `~requests_ecp.HTTPECPAuth` authorisation plugin:

    .. code-block:: python

       from requests import Session
       from requests_ecp import ECPAuthSessionMixin
       class MySession(ECPAuthSessionMixin, Session):
           pass

    This can be mixed with any other `~requests.Session` mixins, but beware
    of the inheritance order that may impact which mixin preserves the final
    `~requests.Session.auth` attribute.

    See also
    --------
    requests_ecp.Session
        For a ready-made wrapped `~requests.Session`.
    """
    def __init__(
            self,
            idp=None,
            kerberos=False,
            username=None,
            password=None,
            **kwargs,
    ):
        super().__init__(**kwargs)
        self.auth = HTTPECPAuth(
            idp,
            kerberos=kerberos,
            username=username,
            password=password,
        )


class Session(ECPAuthSessionMixin, _Session):
    """A `requests.Session` wrapper with default SAML/ECP authentication.

    To start a `~requests.Session` to handle ECP authentication with a
    particular Identity Provider (IdP) pass the ``idp`` argument with the
    URL of the ECP endpoint or the IdP.
    For any individual requests in this `~requests.Session`
    that are redirected to a SAML/Shibboleth authentication page/app the
    `~requests_ecp.HTTPECPAuth` authorisation plugin will automatically
    intercept the redirect and invoke a SAML/ECP authorisation workflow:

    >>> from requests_ecp import Session
    >>> with Session(idp="https://idp.example.com/SAML/SOAP/ECP") as sess:
    ...     sess.get("https://private.example.com/data")

    """
    def ecp_authenticate(self, url, endpoint=None, **kwargs):
        """Manually authenticate against the endpoint.

        This generates a shibboleth session cookie for the domain
        of the given URL, which defaults to the endpoint itself.

        Parameters
        ----------
        url : `str`
            The URL of the resource (on the Service Provider) to request.

        endpoint : `str`
            The URL of the ECP endpoint on the Identity Provider.
            If not given it will be taken from the ``auth`` attribute.

        kwargs
            Other keyword arguments are passed directly to
            :func:`requests_ecp.ecp.authenticate`.

        See also
        --------
        requests_ecp.ecp.authenticate
            For details of the ECP authentication workflow.
        """
        if not isinstance(self.auth, HTTPECPAuth):
            raise ValueError(
                f"Cannot execute ECP authentication with {type(self.auth)}",
            )
        return self.auth._authenticate_session(
            self,
            endpoint=endpoint,
            url=url,
            **kwargs
        )
