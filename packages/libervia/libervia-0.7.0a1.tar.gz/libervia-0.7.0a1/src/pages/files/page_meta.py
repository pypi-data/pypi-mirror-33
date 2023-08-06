#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from libervia.server.constants import Const as C
from twisted.internet import defer
from twisted.words.protocols.jabber import jid
from sat.core.log import getLogger

log = getLogger("pages/files")
"""files handling pages"""

name = u"files"
access = C.PAGES_ACCESS_PROFILE
template = u"file/discover.html"


@defer.inlineCallbacks
def prepare_render(self, request):
    profile = self.getProfile(request)
    template_data = request.template_data
    namespace = self.host.ns_map["fis"]
    entities_services, entities_own, entities_roster = yield self.host.bridgeCall(
        "discoFindByFeatures", [namespace], [], False, True, True, True, False, profile
    )
    tpl_service_entities = template_data["disco_service_entities"] = {}
    tpl_own_entities = template_data["disco_own_entities"] = {}
    tpl_roster_entities = template_data["disco_roster_entities"] = {}
    entities_url = template_data["entities_url"] = {}

    # we store identities in dict of dict using category and type as keys
    # this way it's easier to test category in the template
    for tpl_entities, entities_map in (
        (tpl_service_entities, entities_services),
        (tpl_own_entities, entities_own),
        (tpl_roster_entities, entities_roster),
    ):
        for entity_str, entity_ids in entities_map.iteritems():
            entity_jid = jid.JID(entity_str)
            tpl_entities[entity_jid] = identities = {}
            for cat, type_, name in entity_ids:
                identities.setdefault(cat, {}).setdefault(type_, []).append(name)
            entities_url[entity_jid] = self.getPageByName("files_list").getURL(
                entity_jid.full()
            )


def on_data_post(self, request):
    jid_str = self.getPostedData(request, u"jid")
    try:
        jid_ = jid.JID(jid_str)
    except RuntimeError:
        self.pageError(request, C.HTTP_BAD_REQUEST)
    url = self.getPageByName(u"files_list").getURL(jid_.full())
    self.HTTPRedirect(request, url)
