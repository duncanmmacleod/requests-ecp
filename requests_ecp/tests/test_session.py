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
from requests.exceptions import HTTPError

from requests_mock import CookieJar as MockCookieJar

from .. import session as recp_session


@pytest.mark.parametrize("location", [
    "https://idp.test.com/?SAMLRequest=12345",
    "https://idp.test.com/Shibboleth.sso",
])
def test_is_ecp_auth_redirect(requests_mock, location):
    """Test that `is_ecp_auth_redirect` returns `True` when it should.
    """
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
    assert recp_session.is_ecp_auth_redirect(resp)


@pytest.mark.parametrize("response_kwargs", [
    {"status_code": 200},
    {"status_code": 302},
    {"status_code": 302, "headers": {"Location": "https://example.com"}},
])
def test_is_ecp_auth_redirect_false(requests_mock, response_kwargs):
    """Test that `is_ecp_auth_redirect` returns `True` when it should.
    """
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
    assert not recp_session.is_ecp_auth_redirect(resp)


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
    assert recp_session.is_gitlab_auth_redirect(resp)


@pytest.mark.parametrize("response_kwargs", [
    # not a redirect
    {"status_code": 200},
    # redirect with no location
    {"status_code": 302},
    # redirect with the wrong location
    {"status_code": 302,
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
    # configure mock
    if response_kwargs.get("cookies") is True:
        # insert the wrong cookie into the jar
        response_kwargs["cookies"] = jar = MockCookieJar()
        jar.set("_shib_session", "value", domain="login.ligo.org")

    requests_mock.get(
        "https://git.example.com/user/project",
        **response_kwargs,
    )

    # execute mock request
    resp = requests.get(
        "https://git.example.com/user/project",
        allow_redirects=False,
    )

    # test is_gitlab_auth_redirect
    assert not recp_session.is_gitlab_auth_redirect(resp)


class TestSession:
    TEST_CLASS = recp_session.Session

    def test_init(self):
        sess = self.TEST_CLASS(idp="test")
        assert isinstance(sess._idpauth, recp_session.HTTPECPAuth)
        assert sess._idpauth.idp == "test"
        assert sess._idpauth._idpauth is None

    @mock.patch(
        "requests_ecp.session.Session.ecp_authenticate",
        return_value=True,
    )
    def test_resolve_redirects(self, ecp_auth, requests_mock):
        requests_mock.get("https://private.example.com/data", [
            # first reponse is the redirect
            {
                "status_code": 302,
                "headers": {
                    "Location": "https://private.example.com/Shibboleth.sso",
                },
            },
            # second reponse is authenticated and works
            {"status_code": 200, "text": "HELLO"}
        ])

        with self.TEST_CLASS(idp="test") as sess:
            resp = sess.get("https://private.example.com/data")
            ecp_auth.assert_called_with(url="https://private.example.com/data")
            assert resp.text == "HELLO"

    def test_resolve_redirects_fail(self, requests_mock):
        requests_mock.get("https://private.example.com/data", [
            # first reponse is the redirect
            {
                "status_code": 302,
                "headers": {
                    "Location": "https://private.example.com/Shibboleth.sso",
                },
            },
            # second reponse is the first hit of the auth loop
            {"status_code": 404}
        ])

        with pytest.raises(HTTPError):
            with self.TEST_CLASS(idp="test") as sess:
                sess.get("https://private.example.com/data")

    @mock.patch(
        "requests_ecp.session.Session.ecp_authenticate",
        return_value=True,
    )
    def test_resolve_redirects_gitlab(self, ecp_auth, requests_mock):
        jar = MockCookieJar()
        jar.set("_gitlab_session", "value", domain="git.example.com")
        requests_mock.get("https://git.example.com/data", [
            # first reponse is the redirect
            {
                "status_code": 302,
                "headers": {
                    "Location": "https://git.example.com/users/sign_in",
                },
                "cookies": jar,
            },
            # second reponse is authenticated and works
            {"status_code": 200, "text": "HELLO"}
        ])
        requests_mock.get(
            "https://git.example.com/users/auth/shibboleth/callback",
        )

        with self.TEST_CLASS(idp="test") as sess:
            resp = sess.get("https://git.example.com/data")
            ecp_auth.assert_called_with(
                url="https://git.example.com/users/auth/shibboleth/callback",
            )
            assert resp.text == "HELLO"
