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
from twisted.internet import reactor
from twisted.internet import defer
from sat.core import exceptions
from sat.core.log import getLogger
import urllib

log = getLogger(__name__)


def quote(value, safe="@"):
    """shortcut to quote an unicode value for URL"""
    return urllib.quote(value.encode("utf-8"), safe=safe)


class ProgressHandler(object):
    """class to help the management of progressions"""

    handlers = {}

    def __init__(self, host, progress_id, profile):
        self.host = host
        self.progress_id = progress_id
        self.profile = profile

    @classmethod
    def _signal(cls, name, progress_id, data, profile):
        handlers = cls.handlers
        if profile in handlers and progress_id in handlers[profile]:
            handler_data = handlers[profile][progress_id]
            timeout = handler_data[u"timeout"]
            if timeout.active():
                timeout.cancel()
            cb = handler_data[name]
            if cb is not None:
                cb(data)
            if name == u"started":
                pass
            elif name == u"finished":
                handler_data[u"deferred"].callback(data)
                handler_data[u"instance"].unregister_handler()
            elif name == u"error":
                handler_data[u"deferred"].errback(Exception(data))
                handler_data[u"instance"].unregister_handler()
            else:
                log.error(u"unexpected signal: {name}".format(name=name))

    def _timeout(self):
        log.warning(
            _(
                u"No progress received, cancelling handler: {progress_id} [{profile}]"
            ).format(progress_id=self.progress_id, profile=self.profile)
        )

    def unregister_handler(self):
        """remove a previously registered handler"""
        try:
            del self.handlers[self.profile][self.progress_id]
        except KeyError:
            log.warning(
                _(u"Trying to remove unknown handler: {progress_id} [{profile}]").format(
                    progress_id=self.progress_id, profile=self.profile
                )
            )
        else:
            if not self.handlers[self.profile]:
                self.handlers[self.profile]

    def register(self, started_cb=None, finished_cb=None, error_cb=None, timeout=30):
        """register the signals to handle progression

        @param started_cb(callable, None): method to call when progressStarted signal is received
        @param finished_cb(callable, None): method to call when progressFinished signal is received
        @param error_cb(callable, None): method to call when progressError signal is received
        @param timeout(int): progress time out
            if nothing happen in this progression during this delay,
            an exception is raised
        @return (D(dict[unicode,unicode])): a deferred called when progression is finished
        """
        handler_data = self.handlers.setdefault(self.profile, {}).setdefault(
            self.progress_id, {}
        )
        if handler_data:
            raise exceptions.ConflictError(
                u"There is already one handler for this progression"
            )
        handler_data[u"instance"] = self
        deferred = handler_data[u"deferred"] = defer.Deferred()
        handler_data[u"started"] = started_cb
        handler_data[u"finished"] = finished_cb
        handler_data[u"error"] = error_cb
        handler_data[u"timeout"] = reactor.callLater(timeout, self._timeout)
        return deferred


class SubPage(unicode):
    """use to mark subpages when generating a page path"""
