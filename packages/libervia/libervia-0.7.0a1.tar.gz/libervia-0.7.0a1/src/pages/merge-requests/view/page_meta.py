#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from libervia.server.constants import Const as C
from sat.core.i18n import _
from libervia.server.utils import SubPage
from libervia.server import session_iface
from twisted.internet import defer
from twisted.words.protocols.jabber import jid
from sat.tools.common import template_xmlui
from sat.tools.common import uri
from sat.tools.common import data_objects
from sat.core.log import getLogger

name = u"merge-requests_view"
access = C.PAGES_ACCESS_PUBLIC
template = u"merge-request/item.html"
log = getLogger(u"pages/" + name)


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
    session = self.host.getSessionData(request, session_iface.ISATSession)
    service, node, ticket_id = (
        data.get(u"service", u""),
        data.get(u"node", u""),
        data[u"ticket_id"],
    )
    profile = self.getProfile(request)

    if profile is None:
        profile = C.SERVICE_PROFILE

    tickets, metadata, parsed_tickets = yield self.host.bridgeCall(
        "mergeRequestsGet",
        service.full() if service else u"",
        node,
        C.NO_LIMIT,
        [ticket_id],
        "",
        {"parse": C.BOOL_TRUE, "labels_as_list": C.BOOL_TRUE},
        profile,
    )
    ticket = template_xmlui.create(self.host, tickets[0], ignore=["request_data", "type"])
    template_data[u"item"] = ticket
    template_data["patches"] = parsed_tickets[0]
    comments_uri = ticket.widgets["comments_uri"].value
    if comments_uri:
        uri_data = uri.parseXMPPUri(comments_uri)
        template_data["comments_node"] = comments_node = uri_data["node"]
        template_data["comments_service"] = comments_service = uri_data["path"]
        comments = yield self.host.bridgeCall(
            "mbGet", comments_service, comments_node, C.NO_LIMIT, [], {}, profile
        )

        template_data[u"comments"] = data_objects.BlogItems(comments)
        template_data[u"login_url"] = self.getPageRedirectURL(request)

    if session.connected:
        # we set edition URL only if user is the publisher or the node owner
        publisher = jid.JID(ticket.widgets["publisher"].value)
        is_publisher = publisher.userhostJID() == session.jid.userhostJID()
        affiliation = None
        if not is_publisher:
            node = node or self.host.ns_map["merge_requests"]
            affiliation = yield self.host.getAffiliation(request, service, node)
        if is_publisher or affiliation == "owner":
            template_data[u"url_ticket_edit"] = self.getURLByPath(
                SubPage("merge-requests"),
                service.full(),
                node or u"@",
                SubPage("merge-requests_edit"),
                ticket_id,
            )


@defer.inlineCallbacks
def on_data_post(self, request):
    type_ = self.getPostedData(request, u"type")
    if type_ == u"comment":
        blog_page = self.getPageByName(u"blog_view")
        yield blog_page.on_data_post(self, request)
    else:
        log.warning(_(u"Unhandled data type: {}").format(type_))
