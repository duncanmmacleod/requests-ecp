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

"""ECP authentication wrappers for python-requests.

Basic usage:

.. code-block:: python

    >>> from request_ecp import Session
    >>> with Session(idp="https://idp.example.com/SAML/SOAP/ECP") as sess:
    ...     sess.get("https://private.example.com/data")

"""

__author__ = "Duncan Macleod <duncan.macleod@ligo.org>"
__version__ = "0.3.1"

from .auth import HTTPECPAuth
from .session import (
    ECPAuthSessionMixin,
    Session,
)
