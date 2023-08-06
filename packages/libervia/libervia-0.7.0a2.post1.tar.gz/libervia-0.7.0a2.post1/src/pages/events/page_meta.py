#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from libervia.server.constants import Const as C
from twisted.internet import defer
from sat.core.i18n import _
from sat.core.log import getLogger

log = getLogger("pages/ticket")
"""ticket handling pages"""

name = u"events"
access = C.PAGES_ACCESS_PUBLIC
template = u"event/overview.html"


@defer.inlineCallbacks
def parse_url(self, request):
    profile = self.getProfile(request)
    template_data = request.template_data
    template_data[u"url_event_new"] = self.getSubPageURL(request, "event_new")
    if profile is not None:
        try:
            events = yield self.host.bridgeCall("eventsList", "", "", profile)
        except Exception:
            log.warning(_(u"Can't get events list for {profile}").format(profile=profile))
        else:
            own_events = []
            other_events = []
            for event in events:
                if C.bool(event.get("creator", C.BOOL_FALSE)):
                    own_events.append(event)
                    event["url"] = self.getSubPageURL(
                        request,
                        u"event_admin",
                        event.get("service", ""),
                        event.get("node", ""),
                        event.get("item"),
                    )
                else:
                    other_events.append(event)
                    event["url"] = self.getSubPageURL(
                        request,
                        u"event_rsvp",
                        event.get("service", ""),
                        event.get("node", ""),
                        event.get("item"),
                    )

            template_data[u"events"] = own_events + other_events
