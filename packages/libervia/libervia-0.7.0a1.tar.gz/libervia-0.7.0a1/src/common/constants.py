#!/usr/bin/python
# -*- coding: utf-8 -*-

# Libervia: a SAT frontend
# Copyright (C) 2009-2018 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from sat_frontends.quick_frontend import constants
import os.path


class Const(constants.Const):

    # XXX: we don't want to use the APP_VERSION inherited from sat.core.constants version
    #      as we use this version to check that there is not a mismatch with backend
    APP_VERSION = u"0.7.0a1"  # Please add 'D' at the end for dev versions
    LIBERVIA_MAIN_PAGE = "libervia.html"

    # REGISTRATION
    # XXX: for now libervia forces the creation to lower case
    # XXX: Regex patterns must be compatible with both Python and JS
    REG_LOGIN_RE = r"^[a-z0-9_-]+$"
    REG_EMAIL_RE = r"^.+@.+\..+"
    PASSWORD_MIN_LENGTH = 6

    # HTTP REQUEST RESULT VALUES
    PROFILE_AUTH_ERROR = "PROFILE AUTH ERROR"
    XMPP_AUTH_ERROR = "XMPP AUTH ERROR"
    ALREADY_WAITING = "ALREADY WAITING"
    SESSION_ACTIVE = "SESSION ACTIVE"
    NOT_CONNECTED = "NOT CONNECTED"
    PROFILE_LOGGED = "LOGGED"
    PROFILE_LOGGED_EXT_JID = "LOGGED (REGISTERED WITH EXTERNAL JID)"
    ALREADY_EXISTS = "ALREADY EXISTS"
    REGISTRATION_SUCCEED = "REGISTRATION"
    INTERNAL_ERROR = "INTERNAL ERROR"
    INVALID_INPUT = "INVALID INPUT"
    BAD_REQUEST = "BAD REQUEST"
    NO_REPLY = "NO REPLY"
    NOT_ALLOWED = "NOT ALLOWED"
    UPLOAD_OK = "UPLOAD OK"
    UPLOAD_KO = "UPLOAD KO"

    # directories
    MEDIA_DIR = "media/"
    CACHE_DIR = "cache"

    # avatars
    DEFAULT_AVATAR_FILE = "default_avatar.png"
    DEFAULT_AVATAR_URL = os.path.join(MEDIA_DIR, "misc", DEFAULT_AVATAR_FILE)
    EMPTY_AVATAR_FILE = "empty_avatar"
    EMPTY_AVATAR_URL = os.path.join(MEDIA_DIR, "misc", EMPTY_AVATAR_FILE)

    # blog
    MAM_FILTER_CATEGORY = "http://salut-a-toi.org/protocols/mam_filter_category"
