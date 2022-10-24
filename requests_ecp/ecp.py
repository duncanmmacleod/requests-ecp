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

"""ECP AuthN implementation for Python requests.
"""

__author__ = "Duncan Macleod <duncan.macleod@ligo.org>"

from lxml import etree

from requests import (
    HTTPError,
    Request,
    Session,
)


# -- utilities --------------

def _get_xml_attribute(xdata, path):
    """Parse an attribute from an XML document
    """
    namespaces = {
        'ecp': 'urn:oasis:names:tc:SAML:2.0:profiles:SSO:ecp',
        'S': 'http://schemas.xmlsoap.org/soap/envelope/',
        'paos': 'urn:liberty:paos:2003-08'
    }
    return xdata.xpath(path, namespaces=namespaces)[0]


def _send(
    connection,
    method,
    url,
    **kwargs,
):
    """Format and send a request.
    """
    request_kw = {k: kwargs.pop(k) for k in (
        "auth",
        "cookies",
        "data",
        "files",
        "headers",
        "json",
    ) if k in kwargs}

    # if given a Session use it
    if isinstance(connection, Session):
        response = connection.request(
            method.lower(),
            url,
            allow_redirects=False,
            **request_kw,
        )

    # otherwise manually prepare the request
    else:
        request = Request(
            method=method,
            url=url,
            **request_kw,
        ).prepare()
        response = connection.send(request, **kwargs)

    response.raise_for_status()
    return response


def _report_soap_fault(
    connection,
    url,
    message=(
        "responseConsumerURL from SP and assertionConsumerServiceURL "
        "from IdP do not match"
    ),
    **kwargs,
):
    """Report a problem with the SOAP configuration of SP/IdP pair.
    """
    return _send(
        connection,
        "POST",
        url,
        data=f"""
<S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/">
  <S:Body>
    <S:Fault>
      <faultcode>S:Server</faultcode>
      <faultstring>{message}</faultstring>
    </S:Fault>
  </S:Body>
</S:Envelope>""".strip(), # noqa
        headers={'Content-Type': 'application/vnd.paos+xml'},
    )


# -- ECP worker -------------

def authenticate(
    connection,
    auth,
    endpoint,
    url,
    **kwargs,
):
    """Perform an ECP authorisation round-trip.

    A good description of this is round-trip is here:

    https://medium.com/@winma.15/soap-vs-paos-bindings-in-saml-9ce12a052a0f

    This function isn't really meant to be called outside of
    the `HTTPECPAuth` response handler, and is not well tested in any
    other usage.

    Parameters
    ----------
    connection : `requests.Session`, `requests.adapters.HTTPAdapter`
        The thing to use to send the request, must support a `send` method.

    auth : `requests.auth.AuthBase`
        The authentication object to use when communicating with the
        ECP Identity Provider.

    endpoint : `str`
        The URL of the Identity Provider ECP endpoint.

    url : `str`
        The URL of the resource on the Service Provider to request.

    kwargs
        Other keyword arguments are passed directly to
        :meth:`requests.Session.request` or `http.client.HTTPConnection`.

    Returns
    -------
    responses : `tuple` of `requests.Response`
        A `tuple` of three (3) `requests.Response` objects are returned
        in the order in which they were requested. The final response
        _should_ include a ``302 Found`` redirect back to the original
        requested resource.
    """
    # -- step 1: initiate ECP request -----------

    # request resource via ECP
    resp1 = _send(
        connection,
        method="GET",
        url=url,
        headers={
            'Accept': 'text/html; application/vnd.paos+xml',
            'PAOS': 'ver="urn:liberty:paos:2003-08";'
                    '"urn:oasis:names:tc:SAML:2.0:profiles:SSO:ecp"',
        },
        **kwargs,
    )

    # the response from the SP _should be_ an `<AuthnRequest>` message
    # to be relayed to the IdP.
    try:
        spetree = etree.XML(resp1.content)
    finally:
        resp1.raw.release_conn()

    # pick out the relay state element from the SP so that it can
    # be included later in the response to the SP
    relaystate = _get_xml_attribute(
        spetree,
        "//ecp:RelayState",
    )

    # pick out the responseConsumerURL to validate against the
    # AssertionConsumerServiceURL we receive later from the IdP
    rcurl = _get_xml_attribute(
        spetree,
        "/S:Envelope/S:Header/paos:Request/@responseConsumerURL",
    )

    # -- step 2: authenticate with endpoint -----

    # remove the PAOS header to create a SOAP package for the IdP
    idpbody = spetree
    idpbody.remove(idpbody[0])

    # forward <AuthnRequest> to Identity Provider using SOAP
    resp2 = _send(
        connection,
        method="POST",
        url=endpoint,
        auth=auth,
        data=etree.tostring(idpbody),
        headers={"Content-Type": "text/xml; charset=utf-8"},
        **kwargs,
    )

    try:
        idptree = etree.XML(resp2.content)
    except etree.XMLSyntaxError:
        raise RuntimeError(
            "Failed to parse response from {}, you most "
            "likely incorrectly entered your passphrase".format(
                endpoint,
            ),
        )
    finally:
        resp2.raw.release_conn()
    acsurl = _get_xml_attribute(
        idptree,
        "/S:Envelope/S:Header/ecp:Response/@AssertionConsumerServiceURL",
    )

    # validate URLs between SP and IdP
    if acsurl != rcurl:
        try:
            _report_soap_fault(connection, rcurl)
        except HTTPError:
            pass  # don't care, just doing a service

    # -- step 3: post back to the SP ------------

    # replace the IdP's <Response> with the `<RelayState>` we
    # received originally...
    actree = idptree
    actree[0][0] = relaystate

    # and post back to the SP's ECP endpoint
    resp3 = _send(
        connection,
        method="POST",
        url=acsurl,
        data=etree.tostring(actree),
        headers={'Content-Type': 'application/vnd.paos+xml'},
        **kwargs,
    )

    # The result of this _should be_ a final redirect back to the
    # resource we requested originally.

    # return the response history:
    return resp1, resp2, resp3
