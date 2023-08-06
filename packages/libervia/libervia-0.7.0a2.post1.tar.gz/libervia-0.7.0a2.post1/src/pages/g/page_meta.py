#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from libervia.server.constants import Const as C
from sat.core.i18n import _
from twisted.internet import defer
from libervia.server import session_iface
from sat.core.log import getLogger

log = getLogger("pages/g")

access = C.PAGES_ACCESS_PUBLIC
template = u"invitation/welcome.html"


@defer.inlineCallbacks
def parse_url(self, request):
    """check invitation id in URL and start session if needed

    if a session already exists for an other guest/profile, it will be purged
    """
    try:
        invitation_id = self.nextPath(request)
    except IndexError:
        self.pageError(request)

    sat_session, guest_session = self.host.getSessionData(
        request, session_iface.ISATSession, session_iface.ISATGuestSession
    )
    current_id = guest_session.id

    if current_id is not None and current_id != invitation_id:
        log.info(
            _(
                u"killing guest session [{old_id}] because it is connecting with an other ID [{new_id}]"
            ).format(old_id=current_id, new_id=invitation_id)
        )
        self.host.purgeSession(request)
        sat_session, guest_session = self.host.getSessionData(
            request, session_iface.ISATSession, session_iface.ISATGuestSession
        )
        current_id = None  # FIXME: id non mis à zéro ici
        profile = None

    profile = sat_session.profile
    if profile is not None and current_id is None:
        log.info(
            _(
                u"killing current profile session [{profile}] because a guest id is used"
            ).format(profile=profile)
        )
        self.host.purgeSession(request)
        sat_session, guest_session = self.host.getSessionData(
            request, session_iface.ISATSession, session_iface.ISATGuestSession
        )
        profile = None

    if current_id is None:
        log.debug(_(u"checking invitation [{id}]").format(id=invitation_id))
        try:
            data = yield self.host.bridgeCall("invitationGet", invitation_id)
        except Exception:
            self.pageError(request, C.HTTP_UNAUTHORIZED)
        else:
            guest_session.id = invitation_id
            guest_session.data = data
    else:
        data = guest_session.data

    if profile is None:
        log.debug(_(u"connecting profile [{}]").format(profile))
        # we need to connect the profile
        profile = data["guest_profile"]
        password = data["password"]
        try:
            yield self.host.connect(request, profile, password)
        except Exception as e:
            log.warning(_(u"Can't connect profile: {msg}").format(msg=e))
            # FIXME: no good error code correspond
            #        maybe use a custom one?
            self.pageError(request, code=C.HTTP_SERVICE_UNAVAILABLE)

        log.info(
            _(
                u"guest session started, connected with profile [{profile}]".format(
                    profile=profile
                )
            )
        )

    # we copy data useful in templates
    template_data = request.template_data
    template_data["norobots"] = True
    if u"name" in data:
        template_data[u"name"] = data[u"name"]
    if u"language" in data:
        template_data[u"locale"] = data[u"language"]


def prepare_render(self, request):
    template_data = request.template_data
    guest_session = self.host.getSessionData(request, session_iface.ISATGuestSession)
    main_uri = guest_session.data.get("main_uri")
    template_data[u"include_url"] = self.getPagePathFromURI(main_uri)
