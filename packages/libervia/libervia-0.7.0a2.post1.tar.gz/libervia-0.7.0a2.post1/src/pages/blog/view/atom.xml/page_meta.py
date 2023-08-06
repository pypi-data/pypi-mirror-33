#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from libervia.server.constants import Const as C
from twisted.internet import defer
from sat.tools.common import uri
import time

name = u"blog_feed_atom"
access = C.PAGES_ACCESS_PUBLIC
template = u"blog/atom.xml"


@defer.inlineCallbacks
def prepare_render(self, request):
    request.setHeader("Content-Type", "application/atom+xml; charset=utf-8")
    data = self.getRData(request)
    service, node = data[u"service"], data.get(u"node")
    self.checkCache(
        request, C.CACHE_PUBSUB, service=service, node=node, short="microblog"
    )
    data["show_comments"] = False
    template_data = request.template_data
    blog_page = self.getPageByName(u"blog_view")
    yield blog_page.prepare_render(self, request)
    items = data[u"items"]

    template_data[u"request_uri"] = self.host.getExtBaseURL(
        request, request.path.decode("utf-8")
    )
    template_data[u"xmpp_uri"] = uri.buildXMPPUri(
        u"pubsub", subtype=u"microblog", path=service.full(), node=node
    )
    blog_view = self.getPageByName(u"blog_view")
    template_data[u"http_uri"] = self.host.getExtBaseURL(
        request, blog_view.getURL(service.full(), node)
    )
    if items:
        template_data[u"updated"] = items[0].updated
    else:
        template_data[u"updated"] = time.time()
