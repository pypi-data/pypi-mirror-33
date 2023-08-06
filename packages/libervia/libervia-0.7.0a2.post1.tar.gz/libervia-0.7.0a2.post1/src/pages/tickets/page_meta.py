#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from libervia.server.constants import Const as C
from twisted.internet import defer
from sat.tools.common import template_xmlui
from sat.tools.common import data_objects
from sat.core.log import getLogger

log = getLogger("pages/ticket")
"""ticket handling pages"""

name = u"tickets"
access = C.PAGES_ACCESS_PUBLIC
template = u"ticket/overview.html"


def parse_url(self, request):
    self.getPathArgs(request, ["service", "node"], service="jid")
    data = self.getRData(request)
    service, node = data[u"service"], data[u"node"]
    if node is None:
        self.pageRedirect(u"tickets_disco", request)
    if node == u"@":
        node = data[u"node"] = u""
    template_data = request.template_data
    template_data[u"url_tickets_list"] = self.getURL(service.full(), node or u"@")
    template_data[u"url_tickets_new"] = self.getSubPageURL(request, "tickets_new")


@defer.inlineCallbacks
def prepare_render(self, request):
    data = self.getRData(request)
    template_data = request.template_data
    service, node = data[u"service"], data[u"node"]
    profile = self.getProfile(request) or C.SERVICE_PROFILE

    self.checkCache(request, C.CACHE_PUBSUB, service=service, node=node, short="tickets")

    tickets = yield self.host.bridgeCall(
        "ticketsGet",
        service.full() if service else u"",
        node,
        C.NO_LIMIT,
        [],
        "",
        {"labels_as_list": C.BOOL_TRUE},
        profile,
    )
    template_data[u"tickets"] = [template_xmlui.create(self.host, x) for x in tickets[0]]
    template_data[u"on_ticket_click"] = data_objects.OnClick(
        url=self.getSubPageURL(request, u"tickets_view") + u"/{item.id}"
    )
