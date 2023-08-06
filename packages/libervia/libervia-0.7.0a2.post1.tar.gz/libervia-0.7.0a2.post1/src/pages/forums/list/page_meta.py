#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from libervia.server.constants import Const as C
from twisted.internet import defer
from sat.core.log import getLogger
from sat.core.i18n import _
from sat.tools.common import uri as xmpp_uri

log = getLogger("pages/forum")
import json

"""forum handling pages"""

name = u"forums"
access = C.PAGES_ACCESS_PUBLIC
template = u"forum/overview.html"


def parse_url(self, request):
    self.getPathArgs(
        request,
        ["service", "node", "forum_key"],
        service=u"@jid",
        node=u"@",
        forum_key=u"",
    )


def getLinks(self, forums):
    for forum in forums:
        try:
            uri = forum["uri"]
        except KeyError:
            pass
        else:
            uri = xmpp_uri.parseXMPPUri(uri)
            service = uri[u"path"]
            node = uri[u"node"]
            forum["http_url"] = self.getPageByName(u"forum_topics").getURL(service, node)
        if u"sub-forums" in forum:
            getLinks(self, forum[u"sub-forums"])


@defer.inlineCallbacks
def prepare_render(self, request):
    data = self.getRData(request)
    template_data = request.template_data
    service, node, key = data[u"service"], data[u"node"], data[u"forum_key"]
    profile = self.getProfile(request) or C.SERVICE_PROFILE

    try:
        forums_raw = yield self.host.bridgeCall(
            "forumsGet", service.full() if service else u"", node, key, profile
        )
    except Exception as e:
        log.warning(_(u"Can't retrieve forums: {msg}").format(msg=e))
        forums = []
    else:
        forums = json.loads(forums_raw)
    getLinks(self, forums)

    template_data[u"forums"] = forums
