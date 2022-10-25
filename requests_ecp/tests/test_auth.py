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

from requests_mock import CookieJar as MockCookieJar

import requests_ecp
from requests_ecp import auth as requests_ecp_auth


def mock_authenticate_response(url):
    """Mock the output of :meth:`requests_ecp.HTTPECPAuth._authenticate`.
    """
    responses = [requests.Response(), requests.Response(), requests.Response()]
    responses[0].status_code = 200  # SP PAOS request
    responses[1].status_code = 200  # IdP SOAP response
    responses[2].status_code = 302  # SP response
    responses[2].headers['location'] = url
    return responses


@pytest.mark.parametrize("location", [
    # IdP
    "https://idp.test.com/?SAMLRequest=12345",
    # Discovery service
    "https://example.com/Shibboleth.sso",
])
def test_is_ecp_auth_redirect(requests_mock, location):
    # configure mock
    requests_mock.get(
        "https://example.com/mydata",
        status_code=302,
        headers={"Location": location},
    )
    requests_mock.get(location)

    # execute mock request
    resp = requests.get("https://example.com/mydata", allow_redirects=False)

    # test is_ecp_auth_redirect
    assert requests_ecp_auth.is_ecp_auth_redirect(resp)


@pytest.mark.parametrize("response_kwargs", [
    # not a redirect
    {"status_code": 200},
    # redirect but without location (somehow)
    {"status_code": 302},
    # redirect with location, but not an ECP redirect
    {"status_code": 302, "headers": {"Location": "https://example.com/login"}},
])
def test_is_ecp_auth_redirect_false(requests_mock, response_kwargs):
    # configure mock
    requests_mock.get(
        "https://example.com/mydata",
        **response_kwargs
    )
    if "Location" in response_kwargs.get("headers", {}):
        requests_mock.get(response_kwargs["headers"]["Location"])

    # execute mock request
    resp = requests.get("https://example.com/mydata", allow_redirects=False)

    # test is_ecp_auth_redirect
    assert not requests_ecp_auth.is_ecp_auth_redirect(resp)


def test_is_gitlab_auth_redirect(requests_mock):
    """Test that `is_gitlab_auth_redirect` returns `True` when it should.
    """
    # configure mock
    jar = MockCookieJar()
    jar.set("_gitlab_session", "value", domain="git.example.com")
    requests_mock.get(
        "https://git.example.com/user/project",
        status_code=302,
        headers={"Location": "https://git.example.com/users/sign_in"},
        cookies=jar,
    )

    # execute mock request
    resp = requests.get(
        "https://git.example.com/user/project",
        allow_redirects=False,
    )

    # test is_gitlab_auth_redirect
    assert requests_ecp_auth.is_gitlab_auth_redirect(resp)


@pytest.mark.parametrize("response_kwargs", [
    # not a redirect
    {"status_code": 200},
    # redirect with no location
    {"status_code": 302},
    # redirect with the wrong location
    {"status_code": 302,
     "headers": {"Location": "https://git.example.com/login"},
     },
    # redirect from the callback itself (infinite loop)
    {"status_code": 302,
     "url": "https://git.example.com/users/auth/shibboleth/callback",
     "headers": {"Location": "https://git.example.com/login"},
     },
    # redirect with the right location but no cookies
    {"status_code": 302,
     "headers": {"Location": "https://git.example.com/users/sign_in"},
     "cookies": True,
     },
])
def test_is_gitlab_auth_redirect_false(requests_mock, response_kwargs):
    """Test that `is_gitlab_auth_redirect` returns `False` when it should.
    """
    url = response_kwargs.pop("url", "https://git.example.com/user/project")

    # configure mock
    if response_kwargs.get("cookies") is True:
        # insert the wrong cookie into the jar
        response_kwargs["cookies"] = jar = MockCookieJar()
        jar.set("_shib_session", "value", domain="login.ligo.org")
    requests_mock.get(url, **response_kwargs)

    # execute mock request
    resp = requests.get(url, allow_redirects=False)

    # test is_gitlab_auth_redirect
    assert not requests_ecp_auth.is_gitlab_auth_redirect(resp)


class TestHTTPECPAuth(object):
    TEST_CLASS = requests_ecp.HTTPECPAuth

    # -- test init ----------

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
        requests_gssapi = pytest.importorskip("requests_gssapi")
        auth = self.TEST_CLASS._init_auth(
            "https://idp.test.com",
            kerberos=True,
        )
        assert isinstance(auth, requests_gssapi.HTTPKerberosAuth)
        assert auth.hostname_override == "idp.test.com"

    @mock.patch.dict("sys.modules", {
        "requests_gssapi": None,
        "requests_kerberos": None,
    })
    def test_init_auth_kerberos_error(self):
        """Test that `HTTPECPAuth` raises a useful exception
        if requests-gssapi isn't available.
        """
        with pytest.raises(
            ImportError,
            match="you must install requests-gssapi",
        ):
            self.TEST_CLASS(None, kerberos=True)

    def test_init_auth_kerberos_url(self):
        requests_gssapi = pytest.importorskip("requests_gssapi")
        auth = self.TEST_CLASS._init_auth(
            "https://idp.test.com",
            kerberos="https://kerberos.test.com/idp/",
        )
        assert isinstance(auth, requests_gssapi.HTTPKerberosAuth)
        assert auth.hostname_override == "kerberos.test.com"

    # -- test handle_response

    @mock.patch(
        "requests_ecp.auth.is_ecp_auth_redirect",
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
        "requests_ecp.auth.is_ecp_auth_redirect",
        return_value=True,
    )
    @mock.patch(
        "requests_ecp.auth.HTTPECPAuth._authenticate",
        return_value=mock_authenticate_response("https://test"),
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
            requests_mock._adapter,
            endpoint=None,
            url="https://test/",
            timeout=mock.ANY,
            verify=mock.ANY,
            proxies=mock.ANY,
            stream=mock.ANY,
            cert=mock.ANY,
        )
        # check that the header is hijacked properly to that requests
        # automatically retries the same URL
        assert response.headers['location'] == "https://test"
        # make sure that we log that we did the auth loop
        assert session.auth._num_ecp_auth
