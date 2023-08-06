#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from libervia.server.constants import Const as C
from sat.core.log import getLogger

log = getLogger("pages/ticket")
"""ticket handling pages"""

name = u"merge-requests_new"
access = C.PAGES_ACCESS_PUBLIC
template = u"merge-request/create.html"
