# -*- coding: utf-8 -*-
# Copyright (C) Cardiff University (2019-2020)
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

"""Tests for requests_ecp
"""

from unittest import mock

import pytest

import requests
from requests.auth import HTTPBasicAuth

from requests_kerberos import HTTPKerberosAuth

import requests_ecp


class TestHTTPECPAuth(object):
    TEST_CLASS = requests_ecp.HTTPECPAuth

    @mock.patch("requests_ecp.input", return_value="user")
    @mock.patch("requests_ecp.getpass", return_value="passwd")
    def test_init_auth(self, input_, getpass_):
        auth = self.TEST_CLASS._init_auth("https://idp.test.com")
        assert isinstance(auth, HTTPBasicAuth)
        assert auth.username == "user"
        assert auth.password == "passwd"

    @mock.patch("requests_ecp.getpass", return_value="passwd")
    def test_init_auth_username(self, getpass_):
        auth = self.TEST_CLASS._init_auth(
            "https://idp.test.com",
            username="me",
        )
        assert isinstance(auth, HTTPBasicAuth)
        assert auth.username == "me"
        assert auth.password == "passwd"

    def test_init_auth_username_password(self):
        auth = self.TEST_CLASS._init_auth(
            "https://idp.test.com",
            username="me",
            password="mypasswd",
        )
        assert isinstance(auth, HTTPBasicAuth)
        assert auth.username == "me"
        assert auth.password == "mypasswd"

    @pytest.mark.skipif(
        requests_ecp.REQUESTS_KERBEROS_VERSION < "0.9.0",
        reason="requests-kerberos-0.9.0 or later required",
        )
    def test_init_auth_kerberos(self):
        auth = self.TEST_CLASS._init_auth(
            "https://idp.test.com",
            kerberos=True,
        )
        assert isinstance(auth, HTTPKerberosAuth)
        assert auth.hostname_override == "idp.test.com"

    @pytest.mark.skipif(
        requests_ecp.REQUESTS_KERBEROS_VERSION < "0.9.0",
        reason="requests-kerberos-0.9.0 or later required",
    )
    def test_init_auth_kerberos_url(self):
        auth = self.TEST_CLASS._init_auth(
            "https://idp.test.com",
            kerberos="https://kerberos.test.com/idp/",
        )
        assert isinstance(auth, HTTPKerberosAuth)
        assert auth.hostname_override == "kerberos.test.com"

    @pytest.mark.parametrize("location", [
        "https://idp.test.com/?SAMLRequest=12345",
        "https://idp.test.com/Shibboleth.sso",
    ])
    def test_is_ecp_auth_redirect(self, requests_mock, location):
        # configure mock
        requests_mock.get(
            "https://test.domain.com",
            status_code=302,
            headers={"Location": location},
        )
        requests_mock.get(location)

        # execute mock request
        resp = requests.get("https://test.domain.com", allow_redirects=False)

        # test is_ecp_auth_redirect
        assert self.TEST_CLASS.is_ecp_auth_redirect(resp)

    @pytest.mark.parametrize("response_kwargs", [
        {"status_code": 200},
        {"status_code": 302},
        {"status_code": 302, "headers": {"Location": "https://example.com"}},
    ])
    def test_is_ecp_auth_redirect_false(self, requests_mock, response_kwargs):
        # configure mock
        requests_mock.get(
            "https://test.domain.com",
            **response_kwargs
        )
        if "Location" in response_kwargs.get("headers", {}):
            requests_mock.get(response_kwargs["headers"]["Location"])

        # execute mock request
        resp = requests.get("https://test.domain.com", allow_redirects=False)

        # test is_ecp_auth_redirect
        assert not self.TEST_CLASS.is_ecp_auth_redirect(resp)

    @mock.patch(
        "requests_ecp.HTTPECPAuth.is_ecp_auth_redirect",
        return_value=False,
    )
    def test_handle_response_noauth(self, _, requests_mock):
        requests_mock.get("https://test")
        with requests.Session() as session:
            session.auth = self.TEST_CLASS(
                idp="test",
                username="user",
                password="passwd",
            )
            session.get("https://test")
        assert session.auth._num_ecp_auth == 0
