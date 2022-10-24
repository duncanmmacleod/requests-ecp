# -*- coding: utf-8 -*-
# Copyright (C) Cardiff University (2020-2022)
#
# This file is part of requests_ecp
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

"""Tests for requests_ecp.auth.
"""

from lxml import etree

from requests_ecp import ecp


SP_ECP_PAOS_RESPONSE = b"""
<S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/">
  <S:Header>
    <paos:Request
      xmlns:paos="urn:liberty:paos:2003-08"
      S:actor="http://schemas.xmlsoap.org/soap/actor/next"
      S:mustUnderstand="1"
      responseConsumerURL="https://example.com/Shibboleth.sso/SAML2/ECP"
      service="urn:oasis:names:tc:SAML:2.0:profiles:SSO:ecp"
    />
    <ecp:Request
      xmlns:ecp="urn:oasis:names:tc:SAML:2.0:profiles:SSO:ecp"
      IsPassive="0"
      S:actor="http://schemas.xmlsoap.org/soap/actor/next"
      S:mustUnderstand="1"
    >
      <saml:Issuer xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">
        https://example.com/shibboleth-sp
      </saml:Issuer>
    </ecp:Request>
    <ecp:RelayState
      xmlns:ecp="urn:oasis:names:tc:SAML:2.0:profiles:SSO:ecp"
      S:actor="http://schemas.xmlsoap.org/soap/actor/next"
      S:mustUnderstand="1"
    >
      relay_state_text
    </ecp:RelayState>
  </S:Header>
  <S:Body>
    <samlp:AuthnRequest
      xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
      AssertionConsumerServiceURL="https://example.com/Shibboleth.sso/SAML2/ECP"
      ID="_209874385ad739b88d6e1504a9e88c43"
      IssueInstant="2022-10-24T08:22:40Z"
      ProtocolBinding="urn:oasis:names:tc:SAML:2.0:bindings:PAOS"
      Version="2.0"
    >
      <saml:Issuer xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">
        https://example.com/shibboleth-sp
      </saml:Issuer>
      <samlp:NameIDPolicy AllowCreate="1"/>
    </samlp:AuthnRequest>
  </S:Body>
</S:Envelope>
"""


def test_get_xml_attribute():
    """Test that `requests_ecp.auth._get_xml_attribute` works.
    """
    assert ecp._get_xml_attribute(
        etree.XML(SP_ECP_PAOS_RESPONSE),
        "//ecp:RelayState",
    ).text.strip() == "relay_state_text"
