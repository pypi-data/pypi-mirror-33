#!/usr/bin/python
# -*- coding: utf-8 -*-

# Libervia: a Salut à Toi frontend
# Copyright (C) 2011-2018 Jérôme Poisson <goffi@goffi.org>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


### logging configuration ###
from sat.core.log import getLogger
log = getLogger(__name__)
###

from pyjamas.Timer import Timer
from pyjamas import Window
from pyjamas import JSONService
import time
from sat_browser import main_panel

from sat_browser.constants import Const as C
import random


class LiberviaMethodProxy(object):
    """This class manage calling for one method"""

    def __init__(self, parent, method):
        self._parent = parent
        self._method = method

    def call(self, *args, **kwargs):
        """Method called when self._method attribue is used in JSON_PROXY_PARENT

        This method manage callback/errback in kwargs, and profile(_key) removing
        @param *args: positional arguments of self._method
        @param **kwargs: keyword arguments of self._method
        """
        callback=kwargs.pop('callback', None)
        errback=kwargs.pop('errback', None)

        # as profile is linked to browser session and managed server side, we remove them
        profile_removed = False
        try:
            kwargs['profile'] # FIXME: workaround for pyjamas bug: KeyError is not raised with del
            del kwargs['profile']
            profile_removed = True
        except KeyError:
            pass

        try:
            kwargs['profile_key'] # FIXME: workaround for pyjamas bug: KeyError is not raised iwith del
            del kwargs['profile_key']
            profile_removed = True
        except KeyError:
            pass

        if not profile_removed and args:
            # if profile was not in kwargs, there is most probably one in args
            args = list(args)
            assert isinstance(args[-1], basestring) # Detect when we want to remove a callback (or something else) instead of the profile
            del args[-1]

        if kwargs:
            # kwargs should be empty here, we don't manage keyword arguments on bridge calls
            log.error(u"kwargs is not empty after treatment on method call: kwargs={}".format(kwargs))

        id_ = self._parent.callMethod(self._method, args)

        # callback or errback are managed in parent LiberviaJsonProxy with call id
        if callback is not None:
            self._parent.cb[id_] = callback
        if errback is not None:
            self._parent.eb[id_] = errback


class LiberviaJsonProxy(JSONService.JSONService):

    def __init__(self, url, methods):
        self._serviceURL = url
        self.methods = methods
        JSONService.JSONService.__init__(self, url, self)
        self.cb = {}
        self.eb = {}
        self._registerMethods(methods)

    def _registerMethods(self, methods):
        if methods:
            for method in methods:
                log.debug(u"Registering JSON method call [{}]".format(method))
                setattr(self,
                        method,
                        getattr(LiberviaMethodProxy(self, method), 'call')
                       )

    def callMethod(self, method, params, handler = None):
        ret = super(LiberviaJsonProxy, self).callMethod(method, params, handler)
        return ret

    def call(self, method, cb, *args):
        # FIXME: deprecated call method, must be removed once it's not used anymore
        id_ = self.callMethod(method, args)
        log.debug(u"call: method={} [id={}], args={}".format(method, id_, args))
        if cb:
            if isinstance(cb, tuple):
                if len(cb) != 2:
                    log.error("tuple syntax for bridge.call is (callback, errback), aborting")
                    return
                if cb[0] is not None:
                    self.cb[id_] = cb[0]
                self.eb[id_] = cb[1]
            else:
                self.cb[id_] = cb

    def onRemoteResponse(self, response, request_info):
        try:
            _cb = self.cb[request_info.id]
        except KeyError:
            pass
        else:
            _cb(response)
            del self.cb[request_info.id]

        try:
            del self.eb[request_info.id]
        except KeyError:
            pass

    def onRemoteError(self, code, errobj, request_info):
        """def dump(obj):
            print "\n\nDUMPING %s\n\n" % obj
            for i in dir(obj):
                print "%s: %s" % (i, getattr(obj,i))"""
        try:
            _eb = self.eb[request_info.id]
        except KeyError:
            if code != 0:
                log.error("Internal server error")
                """for o in code, error, request_info:
                    dump(o)"""
            else:
                if isinstance(errobj['message'], dict):
                    log.error(u"Error %s: %s" % (errobj['message']['faultCode'], errobj['message']['faultString']))
                else:
                    log.error(u"%s" % errobj['message'])
        else:
            _eb((code, errobj))
            del self.eb[request_info.id]

        try:
            del self.cb[request_info.id]
        except KeyError:
            pass


class RegisterCall(LiberviaJsonProxy):
    def __init__(self):
        LiberviaJsonProxy.__init__(self, "/register_api",
                        ["getSessionMetadata", "isConnected", "connect", "registerParams", "menusGet"])


class BridgeCall(LiberviaJsonProxy):
    def __init__(self):
        LiberviaJsonProxy.__init__(self, "/json_api",
                        ["getContacts", "addContact", "messageSend",
                         "psNodeDelete", "psRetractItem", "psRetractItems",
                         "mbSend", "mbRetract", "mbGet", "mbGetFromMany", "mbGetFromManyRTResult",
                         "mbGetFromManyWithComments", "mbGetFromManyWithCommentsRTResult",
                         "historyGet", "getPresenceStatuses", "joinMUC", "mucLeave", "mucGetRoomsJoined",
                         "inviteMUC", "launchTarotGame", "getTarotCardsPaths", "tarotGameReady",
                         "tarotGamePlayCards", "launchRadioCollective",
                         "getWaitingSub", "subscription", "delContact", "updateContact", "avatarGet",
                         "getEntityData", "getParamsUI", "asyncGetParamA", "setParam", "launchAction",
                         "disconnect", "chatStateComposing", "getNewAccountDomain",
                         "syntaxConvert", "getAccountDialogUI", "getMainResource", "getEntitiesData",
                         "getVersion", "getLiberviaVersion", "mucGetDefaultService", "getFeatures",
                         "namespacesGet",
                        ])

    def __call__(self, *args, **kwargs):
        return LiberviaJsonProxy.__call__(self, *args, **kwargs)

    def getConfig(self, dummy1, dummy2): # FIXME
        log.warning("getConfig is not implemeted in Libervia yet")
        return ''

    def isConnected(self, dummy, callback): # FIXME
        log.warning("isConnected is not implemeted in Libervia as for now profile is connected if session is opened")
        callback(True)

    def bridgeConnect(self, callback, errback):
        callback()


class BridgeSignals(LiberviaJsonProxy):

    def __init__(self, host):
        self.host = host
        self.retry_time = None
        self.retry_nb = 0
        self.retry_warning = None
        self.retry_timer = None
        LiberviaJsonProxy.__init__(self, "/json_signal_api",
                        ["getSignals"])
        self._signals = {} # key: signal name, value: callback

    def onRemoteResponse(self, response, request_info):
        if self.retry_time:
            log.info("Connection with server restablished")
            self.retry_nb = 0
            self.retry_time = None
        LiberviaJsonProxy.onRemoteResponse(self, response, request_info)

    def onRemoteError(self, code, errobj, request_info):
        if errobj['message'] == 'Empty Response':
            log.warning(u"Empty reponse bridgeSignal\ncode={}\nrequest_info: id={} method={} handler={}".format(code, request_info.id, request_info.method, request_info.handler))
            # FIXME: to check/replace by a proper session end on disconnected signal
            # Window.getLocation().reload()  # XXX: reset page in case of session ended.
                                           # FIXME: Should be done more properly without hard reload
        LiberviaJsonProxy.onRemoteError(self, code, errobj, request_info)
        #we now try to reconnect
        if isinstance(errobj['message'], dict) and errobj['message']['faultCode'] == 0:
            Window.alert('You are not allowed to connect to server')
        else:
            def _timerCb(dummy):
                current = time.time()
                if current > self.retry_time:
                    msg = "Trying to reconnect to server..."
                    log.info(msg)
                    self.retry_warning.showWarning("INFO", msg)
                    self.retry_timer.cancel()
                    self.retry_warning = self.retry_timer = None
                    self.getSignals(callback=self.signalHandler, profile=None)
                else:
                    remaining = int(self.retry_time - current)
                    msg_html = u"Connection with server lost. Retrying in <strong>{}</strong> s".format(remaining)
                    self.retry_warning.showWarning("WARNING", msg_html, None)

            if self.retry_nb < 3:
                retry_delay = 1
            elif self.retry_nb < 10:
                retry_delay = random.randint(1,10)
            else:
                retry_delay = random.randint(1,60)
            self.retry_nb += 1
            log.warning(u"Lost connection, trying to reconnect in {} s (try #{})".format(retry_delay, self.retry_nb))
            self.retry_time = time.time() + retry_delay
            self.retry_warning = main_panel.WarningPopup()
            self.retry_timer = Timer(notify=_timerCb)
            self.retry_timer.scheduleRepeating(1000)
            _timerCb(None)

    def register_signal(self, name, callback, with_profile=True):
        """Register a signal

        @param: name of the signal to register
        @param callback: method to call
        @param with_profile: True if the original bridge method need a profile
        """
        log.debug(u"Registering signal {}".format(name))
        if name in self._signals:
            log.error(u"Trying to register and already registered signal ({})".format(name))
        else:
            self._signals[name] = (callback, with_profile)

    def signalHandler(self,  signal_data):
        self.getSignals(callback=self.signalHandler, profile=None)
        if len(signal_data) == 1:
            signal_data.append([])
        log.debug(u"Got signal ==> name: %s, params: %s" % (signal_data[0], signal_data[1]))
        name, args = signal_data
        try:
            callback, with_profile = self._signals[name]
        except KeyError:
            log.warning(u"Ignoring {} signal: no handler registered !".format(name))
            return
        if with_profile:
            args.append(C.PROF_KEY_NONE)
        if not self.host._profile_plugged:
            log.debug("Profile is not plugged, we cache the signal")
            self.host.signals_cache[C.PROF_KEY_NONE].append((name, callback, args, {}))
        else:
            callback(*args)
