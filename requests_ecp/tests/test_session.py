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

"""Tests for requests_ecp.session.
"""

import requests_ecp
from .test_ecp import (
    IDP_ECP_SOAP_RESPONSE,
    SP_ECP_PAOS_RESPONSE,
)


class TestSession:
    """Tests for :class:`requests_ecp.Session`.
    """
    TEST_CLASS = requests_ecp.Session

    def test_init(self):
        """Test that basic `requests_ecp.Session()` init works.
        """
        sess = self.TEST_CLASS(idp="test")
        assert isinstance(sess.auth, requests_ecp.HTTPECPAuth)
        assert sess.auth.idp == "test"
        assert sess.auth._idpauth is None

    # -- test ECP auth round-trip

    def test_ecp_authenticate(self, requests_mock):
        # SP response
        requests_mock.get(
            "https://example.com/data",
            content=SP_ECP_PAOS_RESPONSE,
        )
        # ECP response
        requests_mock.post(
            "https://idp.example.com/profile/SAML2/SOAP/ECP",
            content=IDP_ECP_SOAP_RESPONSE
        )
        # SP response 2
        requests_mock.post(
            "https://example.com/Shibboleth.sso/SAML2/ECP",
            status_code=302,
            headers={"location": "https://example.com/data"},
        )

        # make the call
        with self.TEST_CLASS(
            idp="https://idp.example.com/profile/SAML2/SOAP/ECP",
            kerberos=False,
            username="user",
            password="passwd",
        ) as sess:
            sess.ecp_authenticate("https://example.com/data")

        assert requests_mock.call_count == 3
