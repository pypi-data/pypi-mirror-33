#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from libervia.server.constants import Const as C
from sat.core.i18n import _
from twisted.internet import defer
from twisted.words.protocols.jabber import jid
from libervia.server import session_iface
from sat.tools.common import uri
from sat.tools.common.template import safe
import time
import cgi
from sat.core.log import getLogger

log = getLogger("pages/g/e")

access = C.PAGES_ACCESS_PROFILE
template = u"event/invitation.html"


@defer.inlineCallbacks
def prepare_render(self, request):
    template_data = request.template_data
    guest_session = self.host.getSessionData(request, session_iface.ISATGuestSession)
    try:
        event_uri = guest_session.data["event_uri"]
    except KeyError:
        log.warning(_(u"event URI not found, can't render event page"))
        self.pageError(request, C.HTTP_SERVICE_UNAVAILABLE)

    data = self.getRData(request)

    ## Event ##

    event_uri_data = uri.parseXMPPUri(event_uri)
    if event_uri_data[u"type"] != u"pubsub":
        self.pageError(request, C.HTTP_SERVICE_UNAVAILABLE)

    event_service = template_data[u"event_service"] = jid.JID(event_uri_data[u"path"])
    event_node = template_data[u"event_node"] = event_uri_data[u"node"]
    event_id = template_data[u"event_id"] = event_uri_data.get(u"item", "")
    profile = self.getProfile(request)
    event_timestamp, event_data = yield self.host.bridgeCall(
        u"eventGet", event_service.userhost(), event_node, event_id, profile
    )
    try:
        background_image = event_data.pop("background-image")
    except KeyError:
        pass
    else:
        template_data["dynamic_style"] = safe(
            u"""
            html {
                background-image: url("%s");
                background-size: 15em;
            }
            """
            % cgi.escape(background_image, True)
        )
    template_data["event"] = event_data
    event_invitee_data = yield self.host.bridgeCall(
        u"eventInviteeGet",
        event_data["invitees_service"],
        event_data["invitees_node"],
        profile,
    )
    template_data["invitee"] = event_invitee_data
    template_data["days_left"] = int((event_timestamp - time.time()) / (60 * 60 * 24))

    ## Blog ##

    data[u"service"] = jid.JID(event_data[u"blog_service"])
    data[u"node"] = event_data[u"blog_node"]
    data[u"allow_commenting"] = u"simple"

    # we now need blog items, using blog common page
    # this will fill the "items" template data
    blog_page = self.getPageByName(u"blog_view")
    yield blog_page.prepare_render(self, request)


@defer.inlineCallbacks
def on_data_post(self, request):
    type_ = self.getPostedData(request, u"type")
    if type_ == u"comment":
        blog_page = self.getPageByName(u"blog_view")
        yield blog_page.on_data_post(self, request)
    elif type_ == u"attendance":
        profile = self.getProfile(request)
        service, node, attend, guests = self.getPostedData(
            request, (u"service", u"node", u"attend", u"guests")
        )
        data = {u"attend": attend, u"guests": guests}
        yield self.host.bridgeCall(u"eventInviteeSet", service, node, data, profile)
    else:
        log.warning(_(u"Unhandled data type: {}").format(type_))
