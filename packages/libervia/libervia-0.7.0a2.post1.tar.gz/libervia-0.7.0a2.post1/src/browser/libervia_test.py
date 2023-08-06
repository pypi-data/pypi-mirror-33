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


# Just visit <root_url>/test. If you don't get any AssertError pop-up,
# everything is fine. #TODO: nicely display the results in HTML output.


### logging configuration ###
from sat_browser import logging
logging.configure()
from sat.core.log import getLogger
log = getLogger(__name__)
###

from sat_frontends.tools import jid
from sat_browser import contact_list


def test_JID():
    """Check that the JID class reproduces the Twisted behavior"""
    j1 = jid.JID("t1@test.org")
    j1b = jid.JID("t1@test.org")
    t1 = "t1@test.org"

    assert j1 == j1b
    assert j1 != t1
    assert t1 != j1
    assert hash(j1) == hash(j1b)
    assert hash(j1) != hash(t1)


def test_JIDIterable():
    """Check that our iterables reproduce the Twisted behavior"""

    j1 = jid.JID("t1@test.org")
    j1b = jid.JID("t1@test.org")
    j2 = jid.JID("t2@test.org")
    t1 = "t1@test.org"
    t2 = "t2@test.org"
    jid_set = set([j1, t2])
    jid_list = contact_list.JIDList([j1, t2])
    jid_dict = {j1: "dummy 1", t2: "dummy 2"}
    for iterable in (jid_set, jid_list, jid_dict):
        log.info("Testing %s" % type(iterable))
        assert j1 in iterable
        assert j1b in iterable
        assert j2 not in iterable
        assert t1 not in iterable
        assert t2 in iterable

    # Check that the extra JIDList class is still needed
    log.info("Testing Pyjamas native list")
    jid_native_list = ([j1, t2])
    assert j1 in jid_native_list
    assert j1b not in jid_native_list  # this is NOT Twisted's behavior
    assert j2 in jid_native_list  # this is NOT Twisted's behavior
    assert t1 in jid_native_list  # this is NOT Twisted's behavior
    assert t2 in jid_native_list

test_JID()
test_JIDIterable()
