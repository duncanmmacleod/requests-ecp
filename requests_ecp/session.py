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

"""requests.Session plugin for ECP authentication.
"""

__author__ = "Duncan Macleod <duncan.macleod@ligo.org>"

from functools import wraps
from urllib import parse as urllib_parse

from requests import Session as _Session
from requests.exceptions import HTTPError

from lxml import etree

from .auth import HTTPECPAuth

__all__ = [
    "ECPAuthSessionMixin",
    "Session",
]


def _get_xml_attribute(xdata, path):
    """Parse an attribute from an XML document
    """
    namespaces = {
        'ecp': 'urn:oasis:names:tc:SAML:2.0:profiles:SSO:ecp',
        'S': 'http://schemas.xmlsoap.org/soap/envelope/',
        'paos': 'urn:liberty:paos:2003-08'
    }
    return xdata.xpath(path, namespaces=namespaces)[0]


def _report_soap_fault(sess, url, **kwargs):
    """Report a problem with the SOAP configuration of SP/IdP pair.
    """
    return sess.post(
        url,
        headers={'Content-Type': 'application/vnd.paos+xml'},
        data="""
<S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/">
  <S:Body>
    <S:Fault>
      <faultcode>S:Server</faultcode>
      <faultstring>responseConsumerURL from SP and assertionConsumerServiceURL from IdP do not match</faultstring>
    </S:Fault>
  </S:Body>
</S:Envelope>""", # noqa
    )


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
        "SAMLRequest" in query  # redirected to IdP
        or "Shibboleth.sso" in target  # Shibboleth discovery service
    )


def is_gitlab_auth_redirect(response):
    """Return `True` if a response indicates a gitlab auth redirect
    """
    if not response.is_redirect:
        return False

    uparts = urllib_parse.urlparse(response.headers['location'])

    if not uparts.path == "/users/sign_in":
        return False

    for cookie in response.cookies:
        if (
            cookie.name == "_gitlab_session"
            and cookie.domain == uparts.netloc.split(":", 1)[0]
        ):
            return True


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
        self._idpauth = HTTPECPAuth(
            idp,
            kerberos=kerberos,
            username=username,
            password=password,
        )

    def ecp_authenticate(
            self,
            endpoint=None,
            url=None,
            cookies=None,
            **kwargs
    ):
        """Handle user authentication with ECP
        """
        endpoint = endpoint or self._idpauth.idp

        # -- step 1: initiate ECP request -----------

        resp1 = self.get(
            url or endpoint,
            headers={
                'Accept': 'text/html; application/vnd.paos+xml',
                'PAOS': 'ver="urn:liberty:paos:2003-08";'
                        '"urn:oasis:names:tc:SAML:2.0:profiles:SSO:ecp"',
            },
        )
        resp1.raise_for_status()

        # convert the SP resonse from string to etree Element object
        spetree = etree.XML(resp1.content)

        # pick out the relay state element from the SP so that it can
        # be included later in the response to the SP
        relaystate = _get_xml_attribute(
            spetree,
            "//ecp:RelayState",
        )
        rcurl = _get_xml_attribute(
            spetree,
            "/S:Envelope/S:Header/paos:Request/@responseConsumerURL",
        )

        # remote the SOAP header to create a packge for the IdP
        idpbody = spetree
        idpbody.remove(idpbody[0])

        # -- step 2: authenticate with endpoint -----

        resp2 = self.post(
            endpoint,
            auth=self._idpauth,
            data=etree.tostring(idpbody),
            headers={"Content-Type": "text/xml; charset=utf-8"},
        )
        resp2.raise_for_status()

        # -- step 3: post back to the SP ------------

        try:
            idptree = etree.XML(resp2.content)
        except etree.XMLSyntaxError:
            raise RuntimeError(
                "Failed to parse response from {}, you most "
                "likely incorrectly entered your passphrase".format(
                    endpoint,
                ),
            )
        acsurl = _get_xml_attribute(
            idptree,
            "/S:Envelope/S:Header/ecp:Response/@AssertionConsumerServiceURL",
        )

        # validate URLs between SP and IdP
        if acsurl != rcurl:
            _report_soap_fault(self, rcurl)

        # make a deep copy of the IdP response and replace its
        # header contents with the relay state initially sent by
        # the SP
        actree = idptree
        actree[0][0] = relaystate

        # POST the package to the SP
        resp3 = self.post(
            acsurl,
            data=etree.tostring(actree),
            headers={'Content-Type': 'application/vnd.paos+xml'},
        )

        # return all responses
        return resp1, resp2, resp3

    def _ecp_authenticate_gitlab(self, response, **kwargs):
        url = self.get_redirect_target(response)
        parts = urllib_parse.urlparse(url)
        callbackurl = (
            f"{parts.scheme}://{parts.netloc}/"
            "users/auth/shibboleth/callback"
        )
        self.ecp_authenticate(url=callbackurl)
        self.get(callbackurl, allow_redirects=False)

    @wraps(_Session.resolve_redirects)
    def resolve_redirects(self, resp, req, **kwargs):
        ecp_auth_success = False

        # if the redirect looks like gitlab trying to go through ECP auth,
        # attempt an ECP auth loop using the shibboleth callback
        if is_gitlab_auth_redirect(resp):
            try:
                self._ecp_authenticate_gitlab(resp)
            except HTTPError as exc:
                if exc.response.status_code != 406:
                    raise
                # host doesn't support shibboleth
                ecp_auth_success = False
            else:
                ecp_auth_success = True

        # if the redirect looks like a normal ECP auth redirect, authenticate
        elif is_ecp_auth_redirect(resp):
            self.ecp_authenticate(url=resp.url)
            ecp_auth_success = True

        # if we have authenticated,
        # hijack the redirect back to the original request so tell requests to
        # try again
        if ecp_auth_success:
            resp.headers['location'] = resp.url

        return super().resolve_redirects(resp, req, **kwargs)


class Session(ECPAuthSessionMixin, _Session):
    """A `requests.Session` with default ECP authentication
    """
