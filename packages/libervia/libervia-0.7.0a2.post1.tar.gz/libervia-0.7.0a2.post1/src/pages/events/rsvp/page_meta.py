#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from libervia.server.constants import Const as C
from sat.core.i18n import _
from twisted.internet import defer
from twisted.words.protocols.jabber import jid
from sat.core.log import getLogger
from sat.tools.common.template import safe
import time
import cgi

"""creation of new events"""

name = u"event_rsvp"
access = C.PAGES_ACCESS_PROFILE
template = u"event/invitation.html"
log = getLogger(u"pages/" + name)


def parse_url(self, request):
    self.getPathArgs(
        request,
        ("event_service", "event_node", "event_id"),
        min_args=2,
        event_service="@jid",
        event_id="",
    )


@defer.inlineCallbacks
def prepare_render(self, request):
    template_data = request.template_data
    data = self.getRData(request)
    profile = self.getProfile(request)

    ## Event ##

    event_service = data["event_service"]
    event_node = data[u"event_node"]
    event_id = data[u"event_id"]
    event_timestamp, event_data = yield self.host.bridgeCall(
        u"eventGet",
        event_service.userhost() if event_service else "",
        event_node,
        event_id,
        profile,
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
