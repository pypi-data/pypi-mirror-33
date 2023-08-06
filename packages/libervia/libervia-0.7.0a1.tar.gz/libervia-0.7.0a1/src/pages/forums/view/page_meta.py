#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from libervia.server.constants import Const as C
from twisted.internet import defer
from sat.core.i18n import _
from sat.core.log import getLogger

log = getLogger("pages/forums/view")

name = u"forum_view"
access = C.PAGES_ACCESS_PUBLIC
template = u"forum/view.html"


def parse_url(self, request):
    self.getPathArgs(request, ["service", "node"], 2, service=u"jid")


@defer.inlineCallbacks
def prepare_render(self, request):
    data = self.getRData(request)
    data["show_comments"] = False
    blog_page = self.getPageByName(u"blog_view")
    request.args["before"] = [""]
    request.args["reverse"] = ["1"]
    yield blog_page.prepare_render(self, request)
    request.template_data[u"login_url"] = self.getPageRedirectURL(request)


@defer.inlineCallbacks
def on_data_post(self, request):
    profile = self.getProfile(request)
    if profile is None:
        self.pageError(request, C.HTTP_UNAUTHORIZED)
    type_ = self.getPostedData(request, u"type")
    if type_ == u"comment":
        service, node, body = self.getPostedData(request, (u"service", u"node", u"body"))

        if not body:
            self.pageError(request, C.HTTP_BAD_REQUEST)
        mb_data = {u"content": body}
        try:
            yield self.host.bridgeCall(u"mbSend", service, node, mb_data, profile)
        except Exception as e:
            if u"forbidden" in unicode(e):
                self.pageError(request, 401)
            else:
                raise e
    else:
        log.warning(_(u"Unhandled data type: {}").format(type_))
