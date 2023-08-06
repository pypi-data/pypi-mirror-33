#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from libervia.server.constants import Const as C
from twisted.internet import defer
from twisted.words.protocols.jabber import jid

"""page used to target a user profile, e.g. for public blog"""

name = u"user"
access = C.PAGES_ACCESS_PUBLIC  # can be a callable
template = u"blog/articles.html"
url_cache = True


@defer.inlineCallbacks
def parse_url(self, request):
    try:
        prof_requested = self.nextPath(request)
    except IndexError:
        self.pageError(request)

    data = self.getRData(request)

    target_profile = yield self.host.bridgeCall("profileNameGet", prof_requested)
    request.template_data[u"target_profile"] = target_profile
    target_jid = yield self.host.bridgeCall(
        "asyncGetParamA", "JabberID", "Connection", "value", profile_key=target_profile
    )
    target_jid = jid.JID(target_jid)
    data[u"service"] = target_jid


@defer.inlineCallbacks
def prepare_render(self, request):
    data = self.getRData(request)
    self.checkCache(
        request, C.CACHE_PUBSUB, service=data[u"service"], node=None, short="microblog"
    )
    self.pageRedirect(u"blog_view", request)
