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
    Request,
    HTTPError,
)


def _get_xml_attribute(xdata, path):
    """Parse an attribute from an XML document
    """
    namespaces = {
        'ecp': 'urn:oasis:names:tc:SAML:2.0:profiles:SSO:ecp',
        'S': 'http://schemas.xmlsoap.org/soap/envelope/',
        'paos': 'urn:liberty:paos:2003-08'
    }
    return xdata.xpath(path, namespaces=namespaces)[0]


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
    request = Request(
        method="POST",
        url=url,
        headers={'Content-Type': 'application/vnd.paos+xml'},
        data=f"""
<S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/">
  <S:Body>
    <S:Fault>
      <faultcode>S:Server</faultcode>
      <faultstring>{message}</faultstring>
    </S:Fault>
  </S:Body>
</S:Envelope>""".strip(), # noqa
    ).prepare()
    return connection.send(request, **kwargs)


def authenticate(
    connection,
    auth,
    endpoint,
    url=None,
    cookies=None,
    **kwargs,
):
    """Perform an ECP authorisation round-trip.
    """
    target = url or endpoint

    # -- step 1: initiate ECP request -----------

    req1 = Request(
        method="GET",
        url=target,
        cookies=cookies,
        headers={
            'Accept': 'text/html; application/vnd.paos+xml',
            'PAOS': 'ver="urn:liberty:paos:2003-08";'
                    '"urn:oasis:names:tc:SAML:2.0:profiles:SSO:ecp"',
        },
    ).prepare()

    # request target from SP
    resp1 = connection.send(req1, **kwargs)

    # convert the SP resonse from string to etree Element object
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
    rcurl = _get_xml_attribute(
        spetree,
        "/S:Envelope/S:Header/paos:Request/@responseConsumerURL",
    )

    # remote the SOAP header to create a packge for the IdP
    idpbody = spetree
    idpbody.remove(idpbody[0])

    # -- step 2: authenticate with endpoint -----

    req2 = Request(
        method="POST",
        url=endpoint,
        auth=auth,
        cookies=cookies,
        data=etree.tostring(idpbody),
        headers={"Content-Type": "text/xml; charset=utf-8"},
    ).prepare()
    resp2 = connection.send(req2, **kwargs)

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

    # make a deep copy of the IdP response and replace its
    # header contents with the relay state initially sent by
    # the SP
    actree = idptree
    actree[0][0] = relaystate

    # POST the package to the SP
    req3 = Request(
        method="POST",
        url=acsurl,
        cookies=cookies,
        data=etree.tostring(actree),
        headers={'Content-Type': 'application/vnd.paos+xml'},
    ).prepare()
    resp3 = connection.send(req3)

    # return all responses
    return resp1, resp2, resp3
