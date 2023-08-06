#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from libervia.server.constants import Const as C
from twisted.internet import defer
from twisted.words.protocols.jabber import jid
from sat.tools.common.template import safe
from sat.core.i18n import _
from sat.core.log import getLogger
import time
import cgi
import math
import re

name = u"event_admin"
access = C.PAGES_ACCESS_PROFILE
template = u"event/admin.html"
log = getLogger(u"pages/" + name)
REG_EMAIL_RE = re.compile(C.REG_EMAIL_RE, re.IGNORECASE)


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
    data = self.getRData(request)
    template_data = request.template_data

    ## Event ##

    event_service = template_data[u"event_service"] = data["event_service"]
    event_node = template_data[u"event_node"] = data["event_node"]
    event_id = template_data[u"event_id"] = data["event_id"]
    profile = self.getProfile(request)
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
    invitees = yield self.host.bridgeCall(
        u"eventInviteesList",
        event_data["invitees_service"],
        event_data["invitees_node"],
        profile,
    )
    template_data["invitees"] = invitees
    invitees_guests = 0
    for invitee_data in invitees.itervalues():
        if invitee_data.get("attend", "no") == "no":
            continue
        try:
            invitees_guests += int(invitee_data.get("guests", 0))
        except ValueError:
            log.warning(
                _(u"guests value is not valid: {invitee}").format(invitee=invitee_data)
            )
    template_data["invitees_guests"] = invitees_guests
    template_data["days_left"] = int(
        math.ceil((event_timestamp - time.time()) / (60 * 60 * 24))
    )

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
    profile = self.getProfile(request)
    if not profile:
        log.error(u"got post data without profile")
        self.pageError(request, C.HTTP_INTERNAL_ERROR)
    type_ = self.getPostedData(request, "type")
    if type_ == "blog":
        service, node, title, body, lang = self.getPostedData(
            request, (u"service", u"node", u"title", u"body", u"language")
        )

        if not body.strip():
            self.pageError(request, C.HTTP_BAD_REQUEST)
        data = {u"content": body}
        if title:
            data[u"title"] = title
        if lang:
            data[u"language"] = lang
        try:
            comments = bool(self.getPostedData(request, u"comments").strip())
        except KeyError:
            pass
        else:
            if comments:
                data[u"allow_comments"] = C.BOOL_TRUE

        try:
            yield self.host.bridgeCall(u"mbSend", service, node, data, profile)
        except Exception as e:
            if u"forbidden" in unicode(e):
                self.pageError(request, C.HTTP_UNAUTHORIZED)
            else:
                raise e
    elif type_ == "event":
        service, node, event_id, jids, emails = self.getPostedData(
            request, (u"service", u"node", u"event_id", u"jids", u"emails")
        )
        for invitee_jid_s in jids.split():
            try:
                invitee_jid = jid.JID(invitee_jid_s)
            except RuntimeError as e:
                log.warning(
                    _(u"this is not a valid jid: {jid}").format(jid=invitee_jid_s)
                )
                continue
            yield self.host.bridgeCall(
                "eventInvite", invitee_jid.userhost(), service, node, event_id, profile
            )
        for email_addr in emails.split():
            if not REG_EMAIL_RE.match(email_addr):
                log.warning(
                    _(u"this is not a valid email address: {email}").format(
                        email=email_addr
                    )
                )
                continue
            yield self.host.bridgeCall(
                "eventInviteByEmail",
                service,
                node,
                event_id,
                email_addr,
                {},
                u"",
                u"",
                u"",
                u"",
                u"",
                u"",
                profile,
            )

    else:
        log.warning(_(u"Unhandled data type: {}").format(type_))
