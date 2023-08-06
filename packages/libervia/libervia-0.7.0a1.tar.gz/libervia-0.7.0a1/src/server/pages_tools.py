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

"""Helper methods for common operations on pages"""

from sat.core.i18n import _
from libervia.server.constants import Const as C
from twisted.internet import defer
from sat.core.log import getLogger

log = getLogger(__name__)
from sat.tools.common import data_objects


def commentsDataToObjects(comments_data):
    return data_objects.BlogItems(comments_data)


def retrieveComments(self, service, node, profile, pass_exceptions=True):
    """Retrieve comments from server and convert them to data objects

    @param service(unicode): service holding the comments
    @param node(unicode): node to retrieve
    @param profile(unicode): profile of the user willing to find comments
    @param pass_exceptions(bool): if True bridge exceptions will be ignored but logged
        else exception will be raised
    """
    try:
        d = self.host.bridgeCall(u"mbGet", service, node, C.NO_LIMIT, [], {}, profile)
    except Exception as e:
        if not pass_exceptions:
            raise e
        else:
            log.warning(
                _(u"Can't get comments at {node} (service: {service}): {msg}").format(
                    service=service, node=node, msg=e
                )
            )
            return defer.succeed([])

    d.addCallback(commentsDataToObjects)
    return d
