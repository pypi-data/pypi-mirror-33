#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from libervia.server import session_iface
from sat.core.log import getLogger

log = getLogger("pages/login")

"""SàT log-in page, with link to create an account"""

template = u"login/logged.html"


def prepare_render(self, request):
    template_data = request.template_data
    session_data = self.host.getSessionData(request, session_iface.ISATSession)
    template_data["guest_session"] = session_data.guest
    template_data["session_started"] = session_data.started
