#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from twisted.internet import defer
from sat.core.log import getLogger

log = getLogger("pages/login")

"""SàT log-in page, with link to create an account"""

template = u"login/logged.html"


@defer.inlineCallbacks
def on_data_post(self, request):
    import ipdb

    ipdb.set_trace()
