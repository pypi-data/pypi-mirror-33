#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from libervia.server.constants import Const as C
from twisted.words.protocols.jabber import jid
from sat.core.log import getLogger

log = getLogger("pages/ticket")
"""ticket handling pages"""

name = u"merge-requests_disco"
access = C.PAGES_ACCESS_PUBLIC
template = u"merge-request/discover.html"


def prepare_render(self, request):
    mr_handlers_config = self.host.options["mr_handlers_json"]
    if mr_handlers_config:
        handlers = request.template_data["mr_handlers"] = []
        try:
            for handler_data in mr_handlers_config:
                service = handler_data[u"service"]
                node = handler_data[u"node"]
                name = handler_data[u"name"]
                url = self.getPageByName(u"merge-requests").getURL(service, node)
                handlers.append({u"name": name, u"url": url})
        except KeyError as e:
            log.warning(u"Missing field in mr_handlers_json: {msg}".format(msg=e))
        except Exception as e:
            log.warning(u"Can't decode mr handlers: {msg}".format(msg=e))


def on_data_post(self, request):
    jid_str = self.getPostedData(request, u"jid")
    try:
        jid_ = jid.JID(jid_str)
    except RuntimeError:
        self.pageError(request, C.HTTP_BAD_REQUEST)
    # for now we just use default node
    url = self.getPageByName(u"merge-requests").getURL(jid_.full(), u"@")
    self.HTTPRedirect(request, url)
