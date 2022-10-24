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

IDP_ECP_SOAP_RESPONSE = b"""
<soap11:Envelope
  xmlns:soap11="http://schemas.xmlsoap.org/soap/envelope/">
  <soap11:Header>
    <ecp:Response
      xmlns:ecp="urn:oasis:names:tc:SAML:2.0:profiles:SSO:ecp"
      AssertionConsumerServiceURL="https://example.com/Shibboleth.sso/SAML2/ECP"
      soap11:actor="http://schemas.xmlsoap.org/soap/actor/next"
      soap11:mustUnderstand="1"/>
    <samlec:GeneratedKey
      xmlns:samlec="urn:ietf:params:xml:ns:samlec"
      soap11:actor="http://schemas.xmlsoap.org/soap/actor/next"
    >
      srFbZAgDPKo6sBCn26u5bexUmhEZwF8mJkKUl9pMRhk=
    </samlec:GeneratedKey>
  </soap11:Header>
  <soap11:Body>
    <saml2p:Response
      xmlns:saml2p="urn:oasis:names:tc:SAML:2.0:protocol"
      Destination="https://example.com/Shibboleth.sso/SAML2/ECP"
      ID="_546b6742a3ca678b9448ca38cb7e152d"
      InResponseTo="_e78665d057736776d74e44778261fd00"
      IssueInstant="2022-10-24T08:39:28.744Z"
      Version="2.0"
    >
      <saml2:Issuer
        xmlns:saml2="urn:oasis:names:tc:SAML:2.0:assertion"
      >
        https://login.ligo.org/idp/shibboleth
      </saml2:Issuer>
      <ds:Signature
        xmlns:ds="http://www.w3.org/2000/09/xmldsig#"
      >
        <ds:SignedInfo>
          <ds:CanonicalizationMethod
            Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
          <ds:SignatureMethod
            Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"/>
          <ds:Reference URI="#_546b6742a3ca678b9448ca38cb7e152d">
            <ds:Transforms>
              <ds:Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"/>
              <ds:Transform Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
            </ds:Transforms>
            <ds:DigestMethod
              Algorithm="http://www.w3.org/2001/04/xmlenc#sha256"/>
              <ds:DigestValue>digest_value</ds:DigestValue>
            </ds:Reference>
          </ds:SignedInfo>
          <ds:SignatureValue>
            signature_value
          </ds:SignatureValue>
          <ds:KeyInfo>
            <ds:X509Data>
              <ds:X509Certificate>
                x509_certificate
              </ds:X509Certificate>
            </ds:X509Data>
          </ds:KeyInfo>
        </ds:Signature>
        <saml2p:Status>
          <saml2p:StatusCode Value="urn:oasis:names:tc:SAML:2.0:status:Success"/>
        </saml2p:Status>
        <saml2:EncryptedAssertion xmlns:saml2="urn:oasis:names:tc:SAML:2.0:assertion">
          <xenc:EncryptedData
            xmlns:xenc="http://www.w3.org/2001/04/xmlenc#"
            Id="_d5a7004ee158559a6df50abb7c53aa9b"
            Type="http://www.w3.org/2001/04/xmlenc#Element"
          >
            <xenc:EncryptionMethod
              xmlns:xenc="http://www.w3.org/2001/04/xmlenc#"
              Algorithm="http://www.w3.org/2009/xmlenc11#aes128-gcm"/>
            <ds:KeyInfo xmlns:ds="http://www.w3.org/2000/09/xmldsig#">
              <xenc:EncryptedKey
                xmlns:xenc="http://www.w3.org/2001/04/xmlenc#"
                Id="_0750a2a3345f1d2d1c8b6a064c29e6da"
                Recipient="https://example.com/shibboleth-sp"
              >
                <xenc:EncryptionMethod
                  xmlns:xenc="http://www.w3.org/2001/04/xmlenc#"
                  Algorithm="http://www.w3.org/2001/04/xmlenc#rsa-oaep-mgf1p"
                >
                  <ds:DigestMethod
                    xmlns:ds="http://www.w3.org/2000/09/xmldsig#"
                    Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>
                </xenc:EncryptionMethod>
            <ds:KeyInfo>
              <ds:X509Data>
                <ds:X509Certificate>x509_certificate</ds:X509Certificate>
              </ds:X509Data>
            </ds:KeyInfo>
            <xenc:CipherData xmlns:xenc="http://www.w3.org/2001/04/xmlenc#">
              <xenc:CipherValue>cipher_value</xenc:CipherValue>
            </xenc:CipherData>
          </xenc:EncryptedKey>
        </ds:KeyInfo>
        <xenc:CipherData xmlns:xenc="http://www.w3.org/2001/04/xmlenc#">
          <xenc:CipherValue>cipher_value</xenc:CipherValue>
          </xenc:CipherData>
        </xenc:EncryptedData>
      </saml2:EncryptedAssertion>
    </saml2p:Response>
  </soap11:Body>
</soap11:Envelope>"""  # noqa


def test_get_xml_attribute():
    """Test that `requests_ecp.auth._get_xml_attribute` works.
    """
    assert ecp._get_xml_attribute(
        etree.XML(SP_ECP_PAOS_RESPONSE),
        "//ecp:RelayState",
    ).text.strip() == "relay_state_text"
