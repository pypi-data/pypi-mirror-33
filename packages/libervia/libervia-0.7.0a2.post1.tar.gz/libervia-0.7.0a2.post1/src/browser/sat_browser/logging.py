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
"""This module configure logs for Libervia browser side"""

from __pyjamas__ import console
from constants import Const as C
from sat.core import log  # XXX: we don't use core.log_config here to avoid the impossible imports in pyjamas


class LiberviaLogger(log.Logger):

    def out(self, message, level=None):
        try:
            console
        except:
            # XXX: for older Firefox version, the displayed error is "libervia_main ReferenceError: console is not defined"
            # but none of the following exception class is working: ReferenceError, TypeError, NameError, Exception...
            # it works when you don't explicit a class, tested with Firefox 3.0.4
            print message
            return
        if level == C.LOG_LVL_DEBUG:
            console.debug(message)
        elif level == C.LOG_LVL_INFO:
            console.info(message)
        elif level == C.LOG_LVL_WARNING:
            console.warn(message)
        else:
            console.error(message)


def configure():
    fmt = '[%(name)s] %(message)s'
    log.configure(C.LOG_BACKEND_CUSTOM,
                  logger_class = LiberviaLogger,
                  level = C.LOG_LVL_DEBUG,
                  fmt = fmt,
                  output = None,
                  logger = None,
                  colors = False,
                  force_colors = False)
    # FIXME: workaround for Pyjamas, need to be removed when Pyjamas is fixed
    LiberviaLogger.fmt = fmt
