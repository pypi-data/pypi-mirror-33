#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from sat.core.i18n import _
from sat.core import exceptions
from libervia.server.constants import Const as C
from libervia.server import session_iface
from twisted.internet import defer
from sat.core.log import getLogger

log = getLogger("pages/login")

"""SàT log-in page, with link to create an account"""

name = u"login"
access = C.PAGES_ACCESS_PUBLIC
template = u"login/login.html"


def prepare_render(self, request):
    template_data = request.template_data

    #  we redirect to logged page if a session is active
    profile = self.getProfile(request)
    if profile is not None:
        self.pageRedirect("/login/logged", request)

    # login error message
    session_data = self.host.getSessionData(request, session_iface.ISATSession)
    login_error = session_data.popPageData(self, "login_error")
    if login_error is not None:
        template_data["S_C"] = C  # we need server constants in template
        template_data["login_error"] = login_error
    template_data["empty_password_allowed"] = bool(
        self.host.options["empty_password_allowed_warning_dangerous_list"]
    )

    # register page url
    template_data["register_url"] = self.getPageRedirectURL(request, "register")

    #  if login is set, we put it in template to prefill field
    template_data["login"] = session_data.popPageData(self, "login")


def login_error(self, request, error_const):
    """set login_error in page data

    @param error_const(unicode): one of login error constant
    @return C.POST_NO_CONFIRM: avoid confirm message
    """
    session_data = self.host.getSessionData(request, session_iface.ISATSession)
    session_data.setPageData(self, "login_error", error_const)
    return C.POST_NO_CONFIRM


@defer.inlineCallbacks
def on_data_post(self, request):
    profile = self.getProfile(request)
    type_ = self.getPostedData(request, "type")
    if type_ == "disconnect":
        if profile is None:
            log.warning(_(u"Disconnect called when no profile is logged"))
            self.pageError(request, C.HTTP_BAD_REQUEST)
        else:
            self.host.purgeSession(request)
            defer.returnValue(C.POST_NO_CONFIRM)
    elif type_ == "login":
        login, password = self.getPostedData(request, (u"login", u"password"))
        try:
            status = yield self.host.connect(request, login, password)
        except ValueError as e:
            if e.message in (C.XMPP_AUTH_ERROR, C.PROFILE_AUTH_ERROR):
                defer.returnValue(login_error(self, request, e.message))
            else:
                # this error was not expected!
                raise e
        except exceptions.TimeOutError:
            defer.returnValue(login_error(self, request, C.NO_REPLY))
        else:
            if status in (C.PROFILE_LOGGED, C.PROFILE_LOGGED_EXT_JID, C.SESSION_ACTIVE):
                # Profile has been logged correctly
                self.redirectOrContinue(request)
            else:
                log.error(_(u"Unhandled status: {status}".format(status=status)))
    else:
        self.pageError(request, C.HTTP_BAD_REQUEST)
