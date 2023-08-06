#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from libervia.server.constants import Const as C
from twisted.internet import defer
from sat.core.i18n import _
from sat.core.log import getLogger
from sat.tools.common import uri as xmpp_uri

log = getLogger("pages/forums/topics")

name = u"forum_topics"
access = C.PAGES_ACCESS_PUBLIC
template = u"forum/view_topics.html"


def parse_url(self, request):
    self.getPathArgs(request, ["service", "node"], 2, service=u"jid")


@defer.inlineCallbacks
def prepare_render(self, request):
    profile = self.getProfile(request) or C.SERVICE_PROFILE
    data = self.getRData(request)
    service, node = data[u"service"], data[u"node"]
    request.template_data.update({u"service": service, u"node": node})
    template_data = request.template_data
    topics, metadata = yield self.host.bridgeCall(
        u"forumTopicsGet", service.full(), node, {}, profile
    )
    template_data[u"identities"] = identities = {}
    for topic in topics:
        parsed_uri = xmpp_uri.parseXMPPUri(topic[u"uri"])
        author = topic[u"author"]
        topic[u"http_uri"] = self.getPageByName(u"forum_view").getURL(
            parsed_uri[u"path"], parsed_uri[u"node"]
        )
        if author not in identities:
            identities[topic[u"author"]] = yield self.host.bridgeCall(
                u"identityGet", author, profile
            )
    template_data[u"topics"] = topics


@defer.inlineCallbacks
def on_data_post(self, request):
    profile = self.getProfile(request)
    if profile is None:
        self.pageError(request, C.HTTP_UNAUTHORIZED)
    type_ = self.getPostedData(request, u"type")
    if type_ == u"new_topic":
        service, node, title, body = self.getPostedData(
            request, (u"service", u"node", u"title", u"body")
        )

        if not title or not body:
            self.pageError(request, C.HTTP_BAD_REQUEST)
        topic_data = {u"title": title, u"content": body}
        try:
            yield self.host.bridgeCall(
                u"forumTopicCreate", service, node, topic_data, profile
            )
        except Exception as e:
            if u"forbidden" in unicode(e):
                self.pageError(request, 401)
            else:
                raise e
    else:
        log.warning(_(u"Unhandled data type: {}").format(type_))
