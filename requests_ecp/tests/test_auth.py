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

from requests.auth import HTTPBasicAuth

from .. import auth as recp_auth


class TestHTTPECPAuth(object):
    TEST_CLASS = recp_auth.HTTPECPAuth

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
        assert isinstance(auth, recp_auth.HTTPKerberosAuth)
        assert auth.hostname_override == "idp.test.com"

    def test_init_auth_kerberos_url(self):
        auth = self.TEST_CLASS._init_auth(
            "https://idp.test.com",
            kerberos="https://kerberos.test.com/idp/",
        )
        assert isinstance(auth, recp_auth.HTTPKerberosAuth)
        assert auth.hostname_override == "kerberos.test.com"
