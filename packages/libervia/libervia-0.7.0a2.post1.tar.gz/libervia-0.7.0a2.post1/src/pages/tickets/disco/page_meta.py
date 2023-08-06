#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from libervia.server.constants import Const as C
from twisted.words.protocols.jabber import jid
from sat.core.log import getLogger

log = getLogger("pages/ticket")
"""ticket handling pages"""

name = u"tickets_disco"
access = C.PAGES_ACCESS_PUBLIC
template = u"ticket/discover.html"


def prepare_render(self, request):
    tickets_trackers_config = self.host.options["tickets_trackers_json"]
    if tickets_trackers_config:
        trackers = request.template_data["tickets_trackers"] = []
        try:
            for tracker_data in tickets_trackers_config:
                service = tracker_data[u"service"]
                node = tracker_data[u"node"]
                name = tracker_data[u"name"]
                url = self.getPageByName(u"tickets").getURL(service, node)
                trackers.append({u"name": name, u"url": url})
        except KeyError as e:
            log.warning(u"Missing field in tickets_trackers_json: {msg}".format(msg=e))
        except Exception as e:
            log.warning(u"Can't decode tickets trackers: {msg}".format(msg=e))


def on_data_post(self, request):
    jid_str = self.getPostedData(request, u"jid")
    try:
        jid_ = jid.JID(jid_str)
    except RuntimeError:
        self.pageError(request, C.HTTP_BAD_REQUEST)
    # for now we just use default node
    url = self.getPageByName(u"tickets").getURL(jid_.full(), u"@")
    self.HTTPRedirect(request, url)
