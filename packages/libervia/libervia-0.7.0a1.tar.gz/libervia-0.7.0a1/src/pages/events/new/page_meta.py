#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from libervia.server.constants import Const as C
from twisted.internet import defer
from sat.core.log import getLogger
from sat.tools.common import date_utils

"""creation of new events"""

name = u"event_new"
access = C.PAGES_ACCESS_PROFILE
template = u"event/create.html"
log = getLogger(u"pages/" + name)


@defer.inlineCallbacks
def on_data_post(self, request):
    request_data = self.getRData(request)
    profile = self.getProfile(request)
    title, location, body, date, main_img, bg_img = self.getPostedData(
        request, ("name", "location", "body", "date", "main_image", "bg_image")
    )
    timestamp = date_utils.date_parse(date)
    data = {"name": title, "description": body, "location": location}

    for value, var in ((main_img, "image"), (bg_img, "background-image")):
        value = value.strip()
        if not value:
            continue
        if not value.startswith("http"):
            self.pageError(request, C.HTTP_BAD_REQUEST)
        data[var] = value
    data[u"register"] = C.BOOL_TRUE
    node = yield self.host.bridgeCall("eventCreate", timestamp, data, "", "", "", profile)
    log.info(u"Event node created at {node}".format(node=node))

    request_data["post_redirect_page"] = (self.getPageByName(u"event_admin"), "@", node)
    defer.returnValue(C.POST_NO_CONFIRM)
