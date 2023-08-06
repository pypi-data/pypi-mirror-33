#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from libervia.server.constants import Const as C

"""pages needing a profile session"""

name = u"profile"
access = C.PAGES_ACCESS_PROFILE
template = u"error/404.html"  # FIXME: do a listing or default activity
