#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from sat.core.i18n import _
from twisted.internet import defer
from sat.core.log import getLogger

log = getLogger("pages/chat")
from sat.tools.common import data_objects
from twisted.words.protocols.jabber import jid
from libervia.server.constants import Const as C
from libervia.server import session_iface

name = u"chat"
access = C.PAGES_ACCESS_PROFILE
template = u"chat/chat.html"
dynamic = True


def parse_url(self, request):
    rdata = self.getRData(request)

    try:
        target_jid_s = self.nextPath(request)
    except IndexError:
        # not chat jid, we redirect to jid selection page
        self.pageRedirect(u"chat_select", request)

    try:
        target_jid = jid.JID(target_jid_s)
        if not target_jid.user:
            raise ValueError(_(u"invalid jid for chat (no local part)"))
    except Exception as e:
        log.warning(
            _(u"bad chat jid entered: {jid} ({msg})").format(jid=target_jid, msg=e)
        )
        self.pageError(request, C.HTTP_BAD_REQUEST)
    else:
        rdata["target"] = target_jid


@defer.inlineCallbacks
def prepare_render(self, request):
    #  FIXME: bug on room filtering (currently display messages from all rooms)
    session = self.host.getSessionData(request, session_iface.ISATSession)
    template_data = request.template_data
    rdata = self.getRData(request)
    target_jid = rdata["target"]
    profile = session.profile
    profile_jid = session.jid

    disco = yield self.host.bridgeCall(u"discoInfos", target_jid.host, u"", True, profile)
    if "conference" in [i[0] for i in disco[1]]:
        chat_type = C.CHAT_GROUP
        join_ret = yield self.host.bridgeCall(
            u"mucJoin", target_jid.userhost(), "", "", profile
        )
        already_joined, room_jid_s, occupants, user_nick, room_subject, dummy = join_ret
        template_data[u"subject"] = room_subject
        own_jid = jid.JID(room_jid_s)
        own_jid.resource = user_nick
    else:
        chat_type = C.CHAT_ONE2ONE
        own_jid = profile_jid
    rdata["chat_type"] = chat_type
    template_data["own_jid"] = own_jid

    self.registerSignal(request, u"messageNew")
    history = yield self.host.bridgeCall(
        u"historyGet",
        profile_jid.userhost(),
        target_jid.userhost(),
        20,
        True,
        {},
        profile,
    )
    authors = {m[2] for m in history}
    identities = {}
    for author in authors:
        identities[author] = yield self.host.bridgeCall(u"identityGet", author, profile)

    template_data[u"messages"] = data_objects.Messages(history)
    template_data[u"identities"] = identities
    template_data[u"target_jid"] = target_jid
    template_data[u"chat_type"] = chat_type


def on_data(self, request, data):
    session = self.host.getSessionData(request, session_iface.ISATSession)
    rdata = self.getRData(request)
    target = rdata["target"]
    data_type = data.get(u"type", "")
    if data_type == "msg":
        message = data[u"body"]
        mess_type = (
            C.MESS_TYPE_GROUPCHAT
            if rdata["chat_type"] == C.CHAT_GROUP
            else C.MESS_TYPE_CHAT
        )
        log.debug(u"message received: {}".format(message))
        self.host.bridgeCall(
            u"messageSend",
            target.full(),
            {u"": message},
            {},
            mess_type,
            {},
            session.profile,
        )
    else:
        log.warning(u"unknown message type: {type}".format(type=data_type))


@defer.inlineCallbacks
def on_signal(self, request, signal, *args):
    if signal == "messageNew":
        rdata = self.getRData(request)
        template_data = request.template_data
        template_data_update = {u"msg": data_objects.Message((args))}
        target_jid = rdata["target"]
        identities = template_data["identities"]
        uid, timestamp, from_jid_s, to_jid_s, message, subject, mess_type, extra, dummy = (
            args
        )
        from_jid = jid.JID(from_jid_s)
        to_jid = jid.JID(to_jid_s)
        if (
            target_jid.userhostJID() != from_jid.userhostJID()
            and target_jid.userhostJID() != to_jid.userhostJID()
        ):
            # the message is not linked with page's room/user
            return

        if from_jid_s not in identities:
            profile = self.getProfile(request)
            identities[from_jid_s] = yield self.host.bridgeCall(
                u"identityGet", from_jid_s, profile
            )
            template_data_update["identities"] = identities
        self.renderAndUpdate(
            request, u"chat/message.html", "#messages", template_data_update
        )
    else:
        log.error(_(u"Unexpected signal: {signal}").format(signal=signal))
