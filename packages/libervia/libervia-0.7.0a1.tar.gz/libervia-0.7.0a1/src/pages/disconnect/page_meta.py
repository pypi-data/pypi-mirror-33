#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from libervia.server.constants import Const as C
from sat.core.log import getLogger

log = getLogger("pages/disconnect")

access = C.PAGES_ACCESS_PUBLIC
template = u"session/disconnect.html"


def parse_url(self, request):
    # TODO: disconnect profile
    request.getSession().expire()
