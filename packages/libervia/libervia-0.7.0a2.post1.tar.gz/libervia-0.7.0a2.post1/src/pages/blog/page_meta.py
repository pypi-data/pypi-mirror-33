#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
from libervia.server.constants import Const as C
from twisted.words.protocols.jabber import jid
from twisted.internet import defer
from libervia.server import session_iface
from sat.core.log import getLogger

log = getLogger("pages/blog")

name = u"blog"
access = C.PAGES_ACCESS_PUBLIC
template = u"blog/discover.html"


@defer.inlineCallbacks
def prepare_render(self, request):
    profile = self.getProfile(request)
    template_data = request.template_data
    if profile is not None:
        __, entities_own, entities_roster = yield self.host.bridgeCall(
            "discoFindByFeatures",
            [],
            [(u"pubsub", u"pep")],
            True,
            False,
            True,
            True,
            True,
            profile,
        )
        entities = template_data[u"disco_entities"] = (
            entities_own.keys() + entities_roster.keys()
        )
        entities_url = template_data[u"entities_url"] = {}
        identities = template_data[u"identities"] = self.host.getSessionData(
            request, session_iface.ISATSession
        ).identities
        for entity_jid_s in entities:
            entities_url[entity_jid_s] = self.getPageByName("blog_view").getURL(
                entity_jid_s
            )
            if entity_jid_s not in identities:
                identities[entity_jid_s] = yield self.host.bridgeCall(
                    u"identityGet", entity_jid_s, profile
                )


def on_data_post(self, request):
    jid_str = self.getPostedData(request, u"jid")
    try:
        jid_ = jid.JID(jid_str)
    except RuntimeError:
        self.pageError(request, C.HTTP_BAD_REQUEST)
    url = self.getPageByName(u"blog_view").getURL(jid_.full())
    self.HTTPRedirect(request, url)
