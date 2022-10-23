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

from unittest import mock

import pytest

import requests
from requests.auth import HTTPBasicAuth

import requests_ecp
from requests_ecp.auth import HTTPKerberosAuth


class TestHTTPECPAuth(object):
    TEST_CLASS = requests_ecp.HTTPECPAuth

    @mock.patch("requests_ecp.auth.input", return_value="user")
    @mock.patch("requests_ecp.auth.getpass", return_value="passwd")
    def test_init_auth(self, input_, getpass_):
        auth = self.TEST_CLASS._init_auth("https://idp.test.com")
        assert isinstance(auth, HTTPBasicAuth)
        assert auth.username == "user"
        assert auth.password == "passwd"

    @mock.patch("requests_ecp.auth.getpass", return_value="passwd")
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

    def test_init_auth_kerberos(self):
        auth = self.TEST_CLASS._init_auth(
            "https://idp.test.com",
            kerberos=True,
        )
        assert isinstance(auth, HTTPKerberosAuth)
        assert auth.hostname_override == "idp.test.com"

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
        "requests_ecp.auth.HTTPECPAuth.is_ecp_auth_redirect",
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

    @mock.patch(
        "requests_ecp.auth.HTTPECPAuth.is_ecp_auth_redirect",
        return_value=True,
    )
    @mock.patch(
        "requests_ecp.auth.HTTPECPAuth._authenticate",
    )
    def test_handle_response_auth(self, mock_authenticate, _, requests_mock):
        requests_mock.get("https://test")
        with requests.Session() as session:
            session.auth = self.TEST_CLASS(
                idp="test",
                username="user",
                password="passwd",
            )
            response = session.get("https://test", allow_redirects=False)
        # assert that _authenticate got passed some stuff
        # devwarning: this might be a bit flaky if requests change the api
        mock_authenticate.assert_called_once_with(
            response.connection,
            endpoint=None,
            url=response.url,
            timeout=mock.ANY,
            verify=mock.ANY,
            proxies=mock.ANY,
            stream=mock.ANY,
            cert=mock.ANY,
        )
        # check that the header is hijacked properly to that requests
        # automatically retries the same URL
        assert response.headers['location'] == "https://test/"
        # make sure that we log that we did the auth loop
        assert session.auth._num_ecp_auth