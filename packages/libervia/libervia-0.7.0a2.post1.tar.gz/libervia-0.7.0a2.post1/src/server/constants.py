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

from ..common import constants


class Const(constants.Const):

    APP_NAME = "Libervia"
    APP_NAME_FILE = "libervia"
    SERVICE_PROFILE = "libervia"  # the SàT profile that is used for exporting the service

    SESSION_TIMEOUT = 7200  # Session's timeout, after that the user will be disconnected
    HTML_DIR = "html/"
    THEMES_DIR = "themes/"
    THEMES_URL = "themes"
    MEDIA_DIR = "media/"
    CARDS_DIR = "games/cards/tarot"
    PAGES_DIR = u"pages"

    ERRNUM_BRIDGE_ERRBACK = 0  # FIXME
    ERRNUM_LIBERVIA = 0  # FIXME

    # Security limit for Libervia (get/set params)
    SECURITY_LIMIT = 5

    # Security limit for Libervia server_side
    SERVER_SECURITY_LIMIT = constants.Const.NO_SECURITY_LIMIT

    # keys for cache values we can get from browser
    ALLOWED_ENTITY_DATA = {"avatar", "nick"}

    STATIC_RSM_MAX_LIMIT = 100
    STATIC_RSM_MAX_DEFAULT = 10
    STATIC_RSM_MAX_COMMENTS_DEFAULT = 10

    ## Libervia pages ##
    PAGES_META_FILE = u"page_meta.py"
    PAGES_ACCESS_NONE = (
        u"none"
    )  #  no access to this page (using its path will return a 404 error)
    PAGES_ACCESS_PUBLIC = u"public"
    PAGES_ACCESS_PROFILE = (
        u"profile"
    )  # a session with an existing profile must be started
    PAGES_ACCESS_ADMIN = u"admin"  #  only profiles set in admins_list can access the page
    PAGES_ACCESS_ALL = (
        PAGES_ACCESS_NONE,
        PAGES_ACCESS_PUBLIC,
        PAGES_ACCESS_PROFILE,
        PAGES_ACCESS_ADMIN,
    )
    # names of the page to use for menu
    DEFAULT_MENU = [
        "login",
        "chat",
        "blog",
        "forums",
        "photos",
        "files",
        "events",
        "tickets",
        "merge-requests",
        "app",
    ]

    ## Session flags ##
    FLAG_CONFIRM = u"CONFIRM"

    ## Data post ##
    POST_NO_CONFIRM = u"POST_NO_CONFIRM"

    ## HTTP methods ##
    HTTP_METHOD_GET = u"GET"
    HTTP_METHOD_POST = u"POST"

    ## HTTP codes ##
    HTTP_SEE_OTHER = 303
    HTTP_NOT_MODIFIED = 304
    HTTP_BAD_REQUEST = 400
    HTTP_UNAUTHORIZED = 401
    HTTP_NOT_FOUND = 404
    HTTP_INTERNAL_ERROR = 500
    HTTP_SERVICE_UNAVAILABLE = 503

    ## Cache ##
    CACHE_PUBSUB = 0

    ## Date/Time ##
    HTTP_DAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
    HTTP_MONTH = (
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    )
