#!/usr/bin/python
# -*- coding: utf-8 -*-

# Libervia wrapper for otr.js
# Copyright (C) 2009-2018 Jérôme Poisson (goffi@goffi.org)
# Copyright (C) 2013-2016 Adrien Cossa (souliane@mailoo.org)

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

"""This file is a wrapper for otr.js. It partially reproduces the usage
(modules, classes and attributes names) and behavior of potr, so you
can easily adapt some code based on potr to Pyjamas applications.

potr is released under the GNU LESSER GENERAL PUBLIC LICENSE Version 3
    - https://github.com/python-otr/pure-python-otr/blob/master/LICENSE

otr.js is released under the Mozilla Public Licence Version 2.0
    - https://github.com/arlolra/otr/blob/master/license
"""

from __pyjamas__ import JS

# should you re-use this class outside SàT, you can import __pyjamas__.console as log instead
from sat.core.log import getLogger
log = getLogger(__name__)


# XXX: pyjamas can't probably import more than one JS file, it messes the order.
# XXX: pyjamas needs the file to be in the compilation directory - no submodule.
# XXX: pyjamas needs the imported file to end with a empty line or semi-column.
# FIXME: fix these bugs upstream in Pyjamas
import otr.min.js


def isSupported():
    JS("""return (typeof OTR !== 'undefined');""")


if not isSupported():
    # see https://developer.mozilla.org/en-US/docs/Web/API/window.crypto.getRandomValues#Browser_Compatibility
    log.error('Your browser is not implementing CSPRNG: OTR has been disabled.')
    raise ImportError('CSPRNG is not supported by your browser')


class context(object):

    # Pre-declare these attributes to avoid the pylint "undefined variable" errors
    STATUS_SEND_QUERY = None
    STATUS_AKE_INIT = None
    STATUS_AKE_SUCCESS = None
    STATUS_END_OTR = None
    STATE_PLAINTEXT = None
    STATE_ENCRYPTED = None
    STATE_FINISHED = None
    OTR_TAG = None
    OTR_VERSION_2 = None
    OTR_VERSION_3 = None
    WHITESPACE_TAG = None
    WHITESPACE_TAG_V2 = None
    WHITESPACE_TAG_V3 = None

    JS("""
    $cls_definition['STATUS_SEND_QUERY'] = OTR.CONST.STATUS_SEND_QUERY;
    $cls_definition['STATUS_AKE_INIT'] = OTR.CONST.STATUS_AKE_INIT;
    $cls_definition['STATUS_AKE_SUCCESS'] = OTR.CONST.STATUS_AKE_SUCCESS;
    $cls_definition['STATUS_END_OTR'] = OTR.CONST.STATUS_END_OTR;
    $cls_definition['STATE_PLAINTEXT'] = OTR.CONST.MSGSTATE_PLAINTEXT;
    $cls_definition['STATE_ENCRYPTED'] = OTR.CONST.MSGSTATE_ENCRYPTED;
    $cls_definition['STATE_FINISHED'] = OTR.CONST.MSGSTATE_FINISHED;
    $cls_definition['OTR_TAG'] = OTR.CONST.OTR_TAG;
    $cls_definition['OTR_VERSION_2'] = OTR.CONST.OTR_VERSION_2;
    $cls_definition['OTR_VERSION_3'] = OTR.CONST.OTR_VERSION_3;
    $cls_definition['WHITESPACE_TAG'] = OTR.CONST.WHITESPACE_TAG;
    $cls_definition['WHITESPACE_TAG_V2'] = OTR.CONST.WHITESPACE_TAG_V2;
    $cls_definition['WHITESPACE_TAG_V3'] = OTR.CONST.WHITESPACE_TAG_V3;
    """)

    class UnencryptedMessage(Exception):
        pass

    class Context(object):

        def __init__(self, account, peername):
            self.user = account
            self.peer = peername
            self.trustName = self.peer
            options = {'fragment_size': 140,
                       'send_interval': 200,
                       'priv': account.getPrivkey(),  # this would generate the account key if it hasn't been done yet
                       'debug': False,
                       }
            JS("""self.otr = new OTR(options);""")

            for policy in ('ALLOW_V2', 'ALLOW_V3', 'REQUIRE_ENCRYPTION'):
                setattr(self.otr, policy, self.getPolicy(policy))

            self.otr.on('ui', self.receiveMessageCb)
            self.otr.on('io', self.sendMessageCb)
            self.otr.on('error', self.messageErrorCb)
            self.otr.on('status', lambda status: self.setStateCb(self.otr.msgstate, status))
            self.otr.on('smp', self.smpAuthCb)

        @property
        def state(self):
            return self.otr.msgstate

        @state.setter
        def state(self, state):
            self.otr.msgstate = state

        def getCurrentKey(self):
            return self.otr.their_priv_pk

        def setTrust(self, fingerprint, trustLevel):
            self.user.setTrust(self.trustName, fingerprint, trustLevel)

        def setCurrentTrust(self, trustLevel):
            self.setTrust(self.otr.their_priv_pk.fingerprint(), trustLevel)

        def getTrust(self, fingerprint, default=None):
            return self.user.getTrust(self.trustName, fingerprint, default)

        def getCurrentTrust(self):
            # XXX: the docstring of potr for the return value of this method is incorrect
            if self.otr.their_priv_pk is None:
                return None
            return self.getTrust(self.otr.their_priv_pk.fingerprint(), None)

        def getUsedVersion(self):
            """Return the otr version that is beeing used"""
            # this method doesn't exist in potr, it has been added for convenience
            try:
                return self.otr.ake.otr_version
            except AttributeError:
                return None

        def disconnect(self):
            self.otr.endOtr()

        def finish(self):
            """Finish the session - avoid to send any message and the user has to manually disconnect"""
            # it means TLV of type 1 (two first bytes), message length 0 (2 last bytes)
            self.otr.handleTLVs('\x00\x01\x00\x00')

        def receiveMessage(self, msg):
            """Received a message, ask otr.js to (try to) decrypt it"""
            self.otr.receiveMsg(msg)

        def sendMessage(self, msg):
            """Ask otr.js to encrypt a message for sending"""
            self.otr.sendMsg(msg)

        def sendQueryMessage(self):
            """Start or refresh an encryption communication"""
            # otr.js offers this method, with potr you have to build the query message yourself
            self.otr.sendQueryMsg()

        def inject(self, msg, appdata=None):
            return self.sendMessageCb(msg, appdata)

        def getPolicy(self, key):
            raise NotImplementedError

        def smpAuthSecret(self, secret, question=None):
            return self.otr.smpSecret(secret, question)

        def smpAuthAbort(self, act=None):
            # XXX: dirty hack to let the triggered method know who aborted the
            # authentication. We need it to display the proper feedback and,
            # if the correspondent aborted, set the conversation 'unverified'.
            self.otr.sm.init()
            JS("""self.otr.sm.sendMsg(OTR.HLP.packTLV(6, ''))""")
            self.smpAuthCb('abort', '', act)

        def sendMessageCb(self, msg, meta):
            """Actually send the message after it's been encrypted"""
            raise NotImplementedError

        def receiveMessageCb(self, msg, encrypted):
            """Display the message after it's been eventually decrypted"""
            raise NotImplementedError

        def messageErrorCb(self, error):
            """Message error callback"""
            raise NotImplementedError

        def setStateCb(self, newstate):
            raise NotImplementedError

        def smpAuthCb(self, newstate):
            raise NotImplementedError

    class Account(object):

        def __init__(self, host):
            self.host = host
            self.privkey = None
            self.trusts = {}

        def getPrivkey(self):
            # the return value must have a method serializePrivateKey()
            # if the key is not saved yet, call savePrivkey to generate it
            if self.privkey is None:
                self.privkey = self.loadPrivkey()
            if self.privkey is None:
                JS("""self.privkey = new DSA();""")
                self.savePrivkey()
            return self.privkey

        def setTrust(self, key, fingerprint, trustLevel):
            if key not in self.trusts:
                self.trusts[key] = {}
            self.trusts[key][fingerprint] = trustLevel
            self.saveTrusts()

        def getTrust(self, key, fingerprint, default=None):
            if key not in self.trusts:
                return default
            return self.trusts[key].get(fingerprint, default)

        def loadPrivkey(self):
            raise NotImplementedError

        def savePrivkey(self):
            raise NotImplementedError

        def saveTrusts(self):
            raise NotImplementedError


class crypt(object):

    class PK(object):

        def parsePrivateKey(self, key):
            JS("""return DSA.parsePrivate(key);""")


class proto(object):

    @classmethod
    def checkForOTR(cls, body):
        """Helper method to check if the message contains OTR starting tag or whitespace

        @return:
            - context.OTR_TAG if the message starts with it
            - context.WHITESPACE_TAG if the message contains OTR whitespaces
            - None otherwise
        """
        if body.startswith(context.OTR_TAG):
            return context.OTR_TAG
        index = body.find(context.WHITESPACE_TAG)
        if index < 0:
            return False
        tags = [body[i:i + 8] for i in range(index, len(body), 8)]
        if [True for tag in tags if tag in (context.WHITESPACE_TAG_V2, context.WHITESPACE_TAG_V3)]:
            return context.WHITESPACE_TAG
        return None


# serialazePrivateKey is the method name in potr
JS("""DSA.serializePrivateKey = DSA.packPrivate;""")
