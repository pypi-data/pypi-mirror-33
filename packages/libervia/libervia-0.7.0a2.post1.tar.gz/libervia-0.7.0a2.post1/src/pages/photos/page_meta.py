#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from libervia.server.constants import Const as C
from twisted.internet import defer

name = u"photos"
access = C.PAGES_ACCESS_PROFILE
template = u"photo/discover.html"


@defer.inlineCallbacks
def on_data_post(self, request):
    jid_ = self.getPostedData(request, u"jid")
    url = self.getPageByName(u"photos_album").getURL(jid_)
    self.HTTPRedirect(request, url)
