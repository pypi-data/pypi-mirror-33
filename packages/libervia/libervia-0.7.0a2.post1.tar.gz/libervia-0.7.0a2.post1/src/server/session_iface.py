#!/usr/bin/python
# -*- coding: utf-8 -*-

# Libervia: a SAT frontend
# Copyright (C) 2009-2018 Jérôme Poisson (goffi@goffi.org)

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
from zope.interface import Interface, Attribute, implements
from sat.tools.common import data_objects
from libervia.server.constants import Const as C
from collections import OrderedDict
import os.path
import shortuuid
import time

FLAGS_KEY = "_flags"
MAX_CACHE_AFFILIATIONS = 100  # number of nodes to keep in cache


class ISATSession(Interface):
    profile = Attribute("Sat profile")
    jid = Attribute("JID associated with the profile")
    uuid = Attribute("uuid associated with the profile session")
    identities = Attribute("Identities of XMPP entities")


class SATSession(object):
    implements(ISATSession)

    def __init__(self, session):
        self.profile = None
        self.jid = None
        self.started = time.time()
        # time when the backend session was started
        self.backend_started = None
        self.uuid = unicode(shortuuid.uuid())
        self.identities = data_objects.Identities()
        self.csrf_token = unicode(shortuuid.uuid())
        self.pages_data = {}  # used to keep data accross reloads (key is page instance)
        self.affiliations = OrderedDict()  # cache for node affiliations

    @property
    def cache_dir(self):
        if self.profile is None:
            return self.service_cache_url + u"/"
        return os.path.join(u"/", C.CACHE_DIR, self.uuid) + u"/"

    @property
    def connected(self):
        return self.profile is not None

    @property
    def guest(self):
        """True if this is a guest session"""
        if self.profile is None:
            return False
        else:
            return self.profile.startswith("guest@@")

    def getPageData(self, page, key):
        """get session data for a page

        @param page(LiberviaPage): instance of the page
        @param key(object): data key
        return (None, object): value of the key
            None if not found or page_data doesn't exist
        """
        return self.pages_data.get(page, {}).get(key)

    def popPageData(self, page, key, default=None):
        """like getPageData, but remove key once value is gotten

        @param page(LiberviaPage): instance of the page
        @param key(object): data key
        @param default(object): value to return if key is not found
        @return (object): found value or default
        """
        page_data = self.pages_data.get(page)
        if page_data is None:
            return default
        value = page_data.pop(key, default)
        if not page_data:
            # no need to keep unused page_data
            del self.pages_data[page]
        return value

    def setPageData(self, page, key, value):
        """set data to persist on reload

        @param page(LiberviaPage): instance of the page
        @param key(object): data key
        @param value(object): value to set
        @return (object): set value
        """
        page_data = self.pages_data.setdefault(page, {})
        page_data[key] = value
        return value

    def setPageFlag(self, page, flag):
        """set a flag for this page

        @param page(LiberviaPage): instance of the page
        @param flag(unicode): flag to set
        """
        flags = self.getPageData(page, FLAGS_KEY)
        if flags is None:
            flags = self.setPageData(page, FLAGS_KEY, set())
        flags.add(flag)

    def popPageFlag(self, page, flag):
        """return True if flag is set

        flag is removed if it was set
        @param page(LiberviaPage): instance of the page
        @param flag(unicode): flag to set
        @return (bool): True if flaag was set
        """
        page_data = self.pages_data.get(page, {})
        flags = page_data.get(FLAGS_KEY)
        if flags is None:
            return False
        if flag in flags:
            flags.remove(flag)
            # we remove data if they are not used anymore
            if not flags:
                del page_data[FLAGS_KEY]
            if not page_data:
                del self.pages_data[page]
            return True
        else:
            return False

    def getAffiliation(self, service, node):
        """retrieve affiliation for a pubsub node

        @param service(jid.JID): pubsub service
        @param node(unicode): pubsub node
        @return (unicode, None): affiliation, or None if it is not in cache
        """
        if service.resource:
            raise ValueError(u"Service must not have a resource")
        if not node:
            raise ValueError(u"node must be set")
        try:
            affiliation = self.affiliations.pop((service, node))
        except KeyError:
            return None
        else:
            # we replace at the top to get the most recently used on top
            # so less recently used will be removed if cache is full
            self.affiliations[(service, node)] = affiliation
            return affiliation

    def setAffiliation(self, service, node, affiliation):
        """cache affiliation for a node

        will empty cache when it become too big
        @param service(jid.JID): pubsub service
        @param node(unicode): pubsub node
        @param affiliation(unicode): affiliation to this node
        """
        if service.resource:
            raise ValueError(u"Service must not have a resource")
        if not node:
            raise ValueError(u"node must be set")
        self.affiliations[(service, node)] = affiliation
        while len(self.affiliations) > MAX_CACHE_AFFILIATIONS:
            self.affiliations.popitem(last=False)


class ISATGuestSession(Interface):
    id = Attribute("UUID of the guest")
    data = Attribute("data associated with the guest")


class SATGuestSession(object):
    implements(ISATGuestSession)

    def __init__(self, session):
        self.id = None
        self.data = None
