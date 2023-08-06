#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from libervia.server.constants import Const as C
from sat.core.i18n import _
from twisted.internet import defer
from sat.tools.common import template_xmlui
from sat.core.log import getLogger

"""merge-requests edition"""

name = u"merge-requests_edit"
access = C.PAGES_ACCESS_PROFILE
template = u"merge-request/edit.html"
log = getLogger("pages/" + name)


def parse_url(self, request):
    try:
        item_id = self.nextPath(request)
    except IndexError:
        log.warning(_(u"no ticket id specified"))
        self.pageError(request, C.HTTP_BAD_REQUEST)

    data = self.getRData(request)
    data[u"ticket_id"] = item_id


@defer.inlineCallbacks
def prepare_render(self, request):
    data = self.getRData(request)
    template_data = request.template_data
    service, node, ticket_id = (
        data.get(u"service", u""),
        data.get(u"node", u""),
        data[u"ticket_id"],
    )
    profile = self.getProfile(request)

    ignore = (
        "publisher",
        "author",
        "author_jid",
        "author_email",
        "created",
        "updated",
        "comments_uri",
        "request_data",
        "type",
    )
    tickets = yield self.host.bridgeCall(
        "mergeRequestsGet",
        service.full() if service else u"",
        node,
        C.NO_LIMIT,
        [ticket_id],
        "",
        {},
        profile,
    )
    ticket = [template_xmlui.create(self.host, x, ignore=ignore) for x in tickets[0]][0]

    try:
        # small trick to get a one line text input instead of the big textarea
        ticket.widgets[u"labels"].type = u"string"
        ticket.widgets[u"labels"].value = ticket.widgets[u"labels"].value.replace(
            u"\n", ", "
        )
    except KeyError:
        pass
    template_data[u"new_ticket_xmlui"] = ticket


@defer.inlineCallbacks
def on_data_post(self, request):
    data = self.getRData(request)
    service = data["service"]
    node = data["node"]
    ticket_id = data["ticket_id"]
    posted_data = self.getAllPostedData(request)
    if not posted_data["title"] or not posted_data["body"]:
        self.pageError(request, C.HTTP_BAD_REQUEST)
    try:
        posted_data["labels"] = [l.strip() for l in posted_data["labels"][0].split(",")]
    except (KeyError, IndexError):
        pass
    profile = self.getProfile(request)
    yield self.host.bridgeCall(
        "mergeRequestSet",
        service.full(),
        node,
        u"",
        u"auto",
        posted_data,
        u"",
        ticket_id,
        {"update": C.BOOL_TRUE},
        profile,
    )
    # we don't want to redirect to edit page on success, but to tickets list
    data["post_redirect_page"] = (
        self.getPageByName(u"merge-requests"),
        service.full(),
        node or u"@",
    )
