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

from sat.core.i18n import _
from sat.core.log import getLogger

log = getLogger(__name__)
from sat.core import exceptions

from autobahn.twisted import websocket
from autobahn.twisted import resource as resource
from autobahn.websocket import types

import json

LIBERVIA_PROTOCOL = "libervia_page"


class LiberviaPageWSProtocol(websocket.WebSocketServerProtocol):
    host = None
    tokens_map = {}

    def onConnect(self, request):
        prefix = LIBERVIA_PROTOCOL + u"_"
        for protocol in request.protocols:
            if protocol.startswith(prefix):
                token = protocol[len(prefix) :].strip()
                if token:
                    break
        else:
            raise types.ConnectionDeny(
                types.ConnectionDeny.NOT_IMPLEMENTED, u"Can't use this subprotocol"
            )

        if token not in self.tokens_map:
            log.warning(_(u"Can't activate page socket: unknown token"))
            raise types.ConnectionDeny(
                types.ConnectionDeny.FORBIDDEN, u"Bad token, please reload page"
            )
        self.token = token
        self.page = self.tokens_map[token]["page"]
        self.request = self.tokens_map[token]["request"]
        return protocol

    def onOpen(self):
        log.debug(
            _(
                u"Websocket opened for {page} (token: {token})".format(
                    page=self.page, token=self.token
                )
            )
        )
        self.request.sendData = self.sendJSONData
        self.page.onSocketOpen(self.request)

    def onMessage(self, payload, isBinary):
        try:
            data_json = json.loads(payload.decode("utf8"))
        except ValueError as e:
            log.warning(
                _(u"Not valid JSON, ignoring data: {msg}\n{data}").format(
                    msg=e, data=payload
                )
            )
            return
        #  we request page first, to raise an AttributeError
        # if it is not set (which should never happen)
        page = self.page
        try:
            cb = page.on_data
        except AttributeError:
            log.warning(
                _(
                    u'No "on_data" method set on dynamic page, ignoring data:\n{data}'
                ).format(data=data_json)
            )
        else:
            cb(page, self.request, data_json)

    def onClose(self, wasClean, code, reason):
        try:
            token = self.token
        except AttributeError:
            log.warning(_(u"Websocket closed but no token is associated"))
            return

        self.page.onSocketClose(self.request)

        try:
            del self.tokens_map[token]
            del self.request.sendData
        except (KeyError, AttributeError):
            raise exceptions.InternalError(
                _(u"Token or sendData doesn't exist, this should never happen!")
            )
        log.debug(
            _(
                u"Websocket closed for {page} (token: {token}). {reason}".format(
                    page=self.page,
                    token=self.token,
                    reason=u""
                    if wasClean
                    else _(u"Reason: {reason}").format(reason=reason),
                )
            )
        )

    def sendJSONData(self, type_, **data):
        assert "type" not in data
        data["type"] = type_
        self.sendMessage(json.dumps(data, ensure_ascii=False).encode("utf8"))

    @classmethod
    def getBaseURL(cls, host, secure):
        return u"ws{sec}://localhost:{port}".format(
            sec="s" if secure else "",
            port=cls.host.options["port_https" if secure else "port"],
        )

    @classmethod
    def getResource(cls, host, secure):
        if cls.host is None:
            cls.host = host
        factory = websocket.WebSocketServerFactory(cls.getBaseURL(host, secure))
        factory.protocol = cls
        return resource.WebSocketResource(factory)

    @classmethod
    def registerToken(cls, token, page, request):
        if token in cls.tokens_map:
            raise exceptions.ConflictError(_(u"This token is already registered"))
        cls.tokens_map[token] = {"page": page, "request": request}
