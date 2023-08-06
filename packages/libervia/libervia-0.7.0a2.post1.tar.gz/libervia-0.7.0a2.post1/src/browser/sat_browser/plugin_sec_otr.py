#!/usr/bin/python
# -*- coding: utf-8 -*-

# Libervia plugin for OTR encryption
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

"""
This file is adapted from sat.plugins.plugin.sec_otr. It offers browser-side OTR encryption using otr.js.
The text messages to display are mostly taken from the Pidgin OTR plugin (GPL 2.0, see http://otr.cypherpunks.ca).
"""

from sat.core.log import getLogger
log = getLogger(__name__)

from sat.core.i18n import _, D_
from sat.core import exceptions
from sat.tools import trigger

from constants import Const as C
from sat_frontends.tools import jid
import otrjs_wrapper as otr
import dialog
import chat
import uuid
import time


NS_OTR = "otr_plugin"
PRIVATE_KEY = "PRIVATE KEY"
MAIN_MENU = D_('OTR') # TODO: get this constant directly from backend's plugin
DIALOG_EOL = "<br />"

AUTH_TRUSTED = D_("Verified")
AUTH_UNTRUSTED = D_("Unverified")
AUTH_OTHER_TITLE = D_("Authentication of {jid}")
AUTH_US_TITLE = D_("Authentication to {jid}")
AUTH_TRUST_NA_TITLE = D_("Authentication requirement")
AUTH_TRUST_NA_TXT = D_("You must start an OTR conversation before authenticating your correspondent.")
AUTH_INFO_TXT = D_("Authenticating a correspondent helps ensure that the person you are talking to is who he or she claims to be.{eol}{eol}")
AUTH_FINGERPRINT_YOURS = D_("Your fingerprint is:{eol}{fingerprint}{eol}{eol}Start an OTR conversation to have your correspondent one.")
AUTH_FINGERPRINT_TXT = D_("To verify the fingerprint, contact your correspondent via some other authenticated channel (i.e. not in this chat), such as the telephone or GPG-signed email. Each of you should tell your fingerprint to the other.{eol}{eol}")
AUTH_FINGERPRINT_VERIFY = D_("Fingerprint for you, {you}:{eol}{your_fp}{eol}{eol}Purported fingerprint for {other}:{eol}{other_fp}{eol}{eol}Did you verify that this is in fact the correct fingerprint for {other}?")
AUTH_QUEST_DEFINE_TXT = D_("To authenticate using a question, pick a question whose answer is known only to you and your correspondent. Enter this question and this answer, then wait for your correspondent to enter the answer too. If the answers don't match, then you may be talking to an imposter.{eol}{eol}")
AUTH_QUEST_DEFINE = D_("Enter question here:{eol}")
AUTH_QUEST_ANSWER_TXT = D_("Your correspondent is attempting to determine if he or she is really talking to you, or if it's someone pretending to be you. Your correspondent has asked a question, indicated below. To authenticate to your correspondent, enter the answer and click OK.{eol}{eol}")
AUTH_QUEST_ANSWER = D_("This is the question asked by your correspondent:{eol}{question}")
AUTH_SECRET_INPUT = D_("{eol}{eol}Enter secret answer here: (case sensitive){eol}")
AUTH_ABORTED_TXT = D_("Authentication aborted.")
AUTH_FAILED_TXT = D_("Authentication failed.")
AUTH_OTHER_OK = D_("Authentication successful.")
AUTH_US_OK = D_("Your correspondent has successfully authenticated you.")
AUTH_OTHER_TOO = D_("You may want to authenticate your correspondent as well by asking your own question.")
AUTH_STATUS = D_("The current conversation is now {state}.")

FINISHED_CONTEXT_TITLE = D_('Finished OTR conversation with {jid}')
SEND_PLAIN_IN_FINISHED_CONTEXT = D_("Your message was not sent because your correspondent closed the OTR conversation on his/her side. Either close your own side, or refresh the session.")
RECEIVE_PLAIN_IN_ENCRYPTED_CONTEXT = D_("WARNING: received unencrypted data in a supposedly encrypted context!")

QUERY_ENCRYPTED = D_('Attempting to refresh the OTR conversation with {jid}...')
QUERY_NOT_ENCRYPTED = D_('Attempting to start an OTR conversation with {jid}...')
AKE_ENCRYPTED = D_(" conversation with {jid} started. Your client is not logging this conversation.")
AKE_NOT_ENCRYPTED = D_("ERROR: successfully ake'd with {jid} but the conversation is not encrypted!")
END_ENCRYPTED = D_("ERROR: the OTR session ended but the context is still supposedly encrypted!")
END_PLAIN_NO_MORE = D_("Your conversation with {jid} is no more encrypted.")
END_PLAIN_HAS_NOT = D_("Your conversation with {jid} hasn't been encrypted.")
END_FINISHED = D_("{jid} has ended his or her private conversation with you; you should do the same.")

KEY_TITLE = D_('Private key')
KEY_NA_TITLE = D_("No private key")
KEY_NA_TXT = D_("You don't have any private key yet.")
KEY_DROP_TITLE = D_('Drop your private key')
KEY_DROP_TXT = D_("You private key is used to encrypt messages for your correspondent, nobody except you must know it, if you are in doubt, you should drop it!{eol}{eol}Are you sure you want to drop your private key?")
KEY_DROPPED_TXT = D_("Your private key has been dropped.")

QUERY_TITLE = D_("Going encrypted")
QUERY_RECEIVED = D_("{jid} is willing to start with you an OTR encrypted conversation.{eol}{eol}")
QUERY_SEND = D_("You are about to start an OTR encrypted conversation with {jid}.{eol}{eol}")
QUERY_SLOWDOWN = D_("This end-to-end encryption is computed by your web browser and you may experience slowdowns.{eol}{eol}")
QUERY_NO_KEY = D_("This will take up to 10 seconds to generate your single use private key and start the conversation. In a future version of Libervia, your private key will be safely and persistently stored, so you will have to generate it only once.{eol}{eol}")
QUERY_KEY = D_("You already have a private key, but to start the conversation will still require a couple of seconds.{eol}{eol}")
QUERY_CONFIRM = D_("Press OK to start now the encryption.")

ACTION_NA_TITLE = D_("Impossible action")
ACTION_NA = D_("Your correspondent must be connected to start an OTR conversation with him.")

DEFAULT_POLICY_FLAGS = {
    'ALLOW_V2': True,
    'ALLOW_V3': True,
    'REQUIRE_ENCRYPTION': False,
    'SEND_WHITESPACE_TAG': False,  # FIXME: we need to complete sendMessageTg before turning this to True
    'WHITESPACE_START_AKE': False,  # FIXME: we need to complete newMessageTg before turning this to True
}

# list a couple of texts or htmls (untrusted, trusted) for each state
OTR_MSG_STATES = {
    otr.context.STATE_PLAINTEXT: [
        '<img src="media/icons/silk/lock_open.png" /><img src="media/icons/silk/key_delete.png" />',
        '<img src="media/icons/silk/lock_open.png" /><img src="media/icons/silk/key.png" />'
    ],
    otr.context.STATE_ENCRYPTED: [
        '<img src="media/icons/silk/lock.png" /><img src="media/icons/silk/key_delete.png" />',
        '<img src="media/icons/silk/lock.png" /><img src="media/icons/silk/key.png" />'
    ],
    otr.context.STATE_FINISHED: [
        '<img src="media/icons/silk/lock_break.png" /><img src="media/icons/silk/key_delete.png" />',
        '<img src="media/icons/silk/lock_break.png" /><img src="media/icons/silk/key.png" />'
    ]
}


unicode = str  # FIXME: pyjamas workaround


class NotConnectedEntity(Exception):
    pass


class Context(otr.context.Context):

    def __init__(self, host, account, other_jid):
        """

        @param host (satWebFrontend)
        @param account (Account)
        @param other_jid (jid.JID): JID of the person your chat correspondent
        """
        super(Context, self).__init__(account, other_jid)
        self.host = host

    def getPolicy(self, key):
        """Get the value of the specified policy

        @param key (unicode): a value in:
            - ALLOW_V1 (apriori removed from otr.js)
            - ALLOW_V2
            - ALLOW_V3
            - REQUIRE_ENCRYPTION
            - SEND_WHITESPACE_TAG
            - WHITESPACE_START_AKE
            - ERROR_START_AKE
        @return: unicode
        """
        if key in DEFAULT_POLICY_FLAGS:
            return DEFAULT_POLICY_FLAGS[key]
        else:
            return False

    def receiveMessageCb(self, msg, encrypted):
        assert isinstance(self.peer, jid.JID)
        if not encrypted:
            log.warning(u"A plain-text message has been handled by otr.js")
        log.debug(u"message received (was %s): %s" % ('encrypted' if encrypted else 'plain', msg))
        uuid_ = str(uuid.uuid4())  # FIXME
        if not encrypted:
            if self.state == otr.context.STATE_ENCRYPTED:
                log.warning(u"Received unencrypted message in an encrypted context (from %(jid)s)" % {'jid': self.peer})
                self.host.newMessageHandler(uuid_, time.time(), unicode(self.peer), unicode(self.host.whoami), {'': RECEIVE_PLAIN_IN_ENCRYPTED_CONTEXT}, {}, C.MESS_TYPE_INFO, {})
        self.host.newMessageHandler(uuid_, time.time(), unicode(self.peer), unicode(self.host.whoami), {'': msg}, {}, C.MESS_TYPE_CHAT, {})

    def sendMessageCb(self, msg, meta=None):
        assert isinstance(self.peer, jid.JID)
        log.debug(u"message to send%s: %s" % ((' (attached meta data: %s)' % meta) if meta else '', msg))
        self.host.bridge.call('sendMessage', (None, self.host.sendError), unicode(self.peer), msg, '', C.MESS_TYPE_CHAT, {'send_only': 'true'})

    def messageErrorCb(self, error):
        log.error(u'error occured: %s' % error)

    def setStateCb(self, msg_state, status):
        if status == otr.context.STATUS_AKE_INIT:
            return

        other_jid_s = self.peer
        feedback = _(u"Error: the state of the conversation with %s is unknown!")
        trust = self.getCurrentTrust()

        if status == otr.context.STATUS_SEND_QUERY:
            feedback = QUERY_ENCRYPTED if msg_state == otr.context.STATE_ENCRYPTED else QUERY_NOT_ENCRYPTED

        elif status == otr.context.STATUS_AKE_SUCCESS:
            trusted_str = AUTH_TRUSTED if trust else AUTH_UNTRUSTED
            feedback = (trusted_str + AKE_ENCRYPTED) if msg_state == otr.context.STATE_ENCRYPTED else AKE_NOT_ENCRYPTED

        elif status == otr.context.STATUS_END_OTR:
            if msg_state == otr.context.STATE_PLAINTEXT:
                feedback = END_PLAIN_NO_MORE
            elif msg_state == otr.context.STATE_ENCRYPTED:
                log.error(END_ENCRYPTED)
            elif msg_state == otr.context.STATE_FINISHED:
                feedback = END_FINISHED

        uuid_ = str(uuid.uuid4())  # FIXME
        self.host.newMessageHandler(uuid_, time.time(), unicode(self.peer), unicode(self.host.whoami), {'': feedback.format(jid=other_jid_s)}, {}, C.MESS_TYPE_INFO, {'header_info': OTR.getInfoText(msg_state, trust)})

    def setCurrentTrust(self, new_trust='', act='asked', type_='trust'):
        log.debug(u"setCurrentTrust: trust={trust}, act={act}, type={type}".format(type=type_, trust=new_trust, act=act))
        title = (AUTH_OTHER_TITLE if act == "asked" else AUTH_US_TITLE).format(jid=self.peer)
        old_trust = self.getCurrentTrust()
        if type_ == 'abort':
            msg = AUTH_ABORTED_TXT
        elif new_trust:
            if act == "asked":
                msg = AUTH_OTHER_OK
            else:
                msg = AUTH_US_OK
                if not old_trust:
                    msg += " " + AUTH_OTHER_TOO
        else:
            msg = AUTH_FAILED_TXT
        dialog.InfoDialog(title, msg, AddStyleName="maxWidthLimit").show()
        if act != "asked":
            return
        otr.context.Context.setCurrentTrust(self, new_trust)
        if old_trust != new_trust:
            feedback = AUTH_STATUS.format(state=(AUTH_TRUSTED if new_trust else AUTH_UNTRUSTED).lower())
            uuid_ = str(uuid.uuid4())  # FIXME
            self.host.newMessageHandler(uuid_, time.time(), unicode(self.peer), unicode(self.host.whoami), {'': feedback}, {}, C.MESS_TYPE_INFO, {'header_info': OTR.getInfoText(self.state, new_trust)})

    def fingerprintAuthCb(self):
        """OTR v2 authentication using manual fingerprint comparison"""
        priv_key = self.user.privkey

        if priv_key is None:  # OTR._authenticate should not let us arrive here
            raise exceptions.InternalError
            return

        other_key = self.getCurrentKey()
        if other_key is None:
            # we have a private key, but not the fingerprint of our correspondent
            msg = (AUTH_INFO_TXT + AUTH_FINGERPRINT_YOURS).format(fingerprint=priv_key.fingerprint(), eol=DIALOG_EOL)
            dialog.InfoDialog(_("Fingerprint"), msg, AddStyleName="maxWidthLimit").show()
            return

        def setTrust(confirm):
            self.setCurrentTrust('fingerprint' if confirm else '')

        text = (AUTH_INFO_TXT + "<i>" + AUTH_FINGERPRINT_TXT + "</i>" + AUTH_FINGERPRINT_VERIFY).format(you=self.host.whoami, your_fp=priv_key.fingerprint(), other=self.peer, other_fp=other_key.fingerprint(), eol=DIALOG_EOL)
        title = AUTH_OTHER_TITLE.format(jid=self.peer)
        dialog.ConfirmDialog(setTrust, text, title, AddStyleName="maxWidthLimit").show()

    def smpAuthCb(self, type_, data, act=None):
        """OTR v3 authentication using the socialist millionaire protocol.

        @param type_ (unicode): a value in ('question', 'trust', 'abort')
        @param data (unicode, bool): this could be:
            - a string containing the question if type_ is 'question'
            - a boolean value telling if the authentication succeed when type_ is 'trust'
        @param act (unicode): a value in ('asked', 'answered')
        """
        log.debug(u"smpAuthCb: type={type}, data={data}, act={act}".format(type=type_, data=data, act=act))
        if act is None:
            if type_ == 'question':
                act = 'answered'  # OTR._authenticate calls this method with act="asked"
            elif type_ == 'abort':
                act = 'asked'  # smpAuthAbort triggers this method with act='answered' when needed

                # FIXME upstream: if the correspondent uses Pidgin and authenticate us via
                # fingerprints, we will reach this code... that's wrong, this method is for SMP!
                # There's probably a bug to fix in otr.js. Do it together with the issue that
                # make us need the dirty self.smpAuthAbort.
            else:
                log.error("FIXME: unmanaged ambiguous 'act' value in Context.smpAuthCb!")
        title = (AUTH_OTHER_TITLE if act == "asked" else AUTH_US_TITLE).format(jid=self.peer)
        if type_ == 'question':
            if act == 'asked':
                def cb(result, question, answer=None):
                    if not result or not answer:  # dialog cancelled or the answer is empty
                        return
                    self.smpAuthSecret(answer, question)
                text = (AUTH_INFO_TXT + "<i>" + AUTH_QUEST_DEFINE_TXT + "</i>" + AUTH_QUEST_DEFINE).format(eol=DIALOG_EOL)
                dialog.PromptDialog(cb, [text, AUTH_SECRET_INPUT.format(eol=DIALOG_EOL)], title=title, AddStyleName="maxWidthLimit").show()
            else:
                def cb(result, answer):
                    if not result or not answer:  # dialog cancelled or the answer is empty
                        self.smpAuthAbort('answered')
                        return
                    self.smpAuthSecret(answer)
                text = (AUTH_INFO_TXT + "<i>" + AUTH_QUEST_ANSWER_TXT + "</i>" + AUTH_QUEST_ANSWER).format(eol=DIALOG_EOL, question=data)
                dialog.PromptDialog(cb, [text + AUTH_SECRET_INPUT.format(eol=DIALOG_EOL)], title=title, AddStyleName="maxWidthLimit").show()
        elif type_ == 'trust':
            self.setCurrentTrust('smp' if data else '', act)
        elif type_ == 'abort':
            self.setCurrentTrust('', act, 'abort')

    def disconnect(self):
        """Disconnect the session."""
        if self.state != otr.context.STATE_PLAINTEXT:
            super(Context, self).disconnect()

    def finish(self):
        """Finish the session - avoid to send any message but the user still has to end the session himself."""
        if self.state == otr.context.STATE_ENCRYPTED:
            super(Context, self).finish()


class Account(otr.context.Account):

    def __init__(self, host):
        log.debug(u"new account: %s" % host.whoami)
        if not host.whoami.resource:
            log.warning("Account created without resource")
        super(Account, self).__init__(host.whoami)
        self.host = host

    def loadPrivkey(self):
        return self.privkey

    def savePrivkey(self):
        # TODO: serialize and encrypt the private key and save it to a HTML5 persistent storage
        # We need to ask the user before saving the key (e.g. if he's not on his private machine)
        # self.privkey.serializePrivateKey() --> encrypt --> store
        if self.privkey is None:
            raise exceptions.InternalError(_("Save is called but privkey is None !"))
        pass

    def saveTrusts(self):
        # TODO save the trusts as it would be done for the private key
        pass


class ContextManager(object):

    def __init__(self, host):
        self.host = host
        self.account = Account(host)
        self.contexts = {}

    def startContext(self, other_jid):
        assert isinstance(other_jid, jid.JID)  # never start an OTR session with a bare JID
        # FIXME upstream: apparently pyjamas doesn't implement setdefault well, it ignores JID.__hash__ redefinition
        #context = self.contexts.setdefault(other_jid, Context(self.host, self.account, other_jid))
        if other_jid not in self.contexts:
            self.contexts[other_jid] = Context(self.host, self.account, other_jid)
        return self.contexts[other_jid]

    def getContextForUser(self, other_jid, start=True):
        """Get the context for the given JID

        @param other_jid (jid.JID): your correspondent
        @param start (bool): start non-existing context if True
        @return: Context
        """
        try:
            other_jid = self.fixResource(other_jid)
        except NotConnectedEntity:
            log.debug(u"getContextForUser [%s]: not connected!" % other_jid)
            return None
        log.debug(u"getContextForUser [%s]" % other_jid)
        if start:
            return self.startContext(other_jid)
        else:
            return self.contexts.get(other_jid, None)

    def getContextsForBareUser(self, bare_jid):
        """Get all the contexts for the users sharing the given bare JID.

        @param bare_jid (jid.JID): bare JID
        @return: list[Context]
        """
        return [context for other_jid, context in self.contexts.iteritems() if other_jid.bare == bare_jid]

    def fixResource(self, other_jid):
        """Return the full JID in case the resource of the given JID is missing.

        @param other_jid (jid.JID): JID to check
        @return jid.JID
        """
        if other_jid.resource:
            return other_jid
        clist = self.host.contact_list
        if clist.getCache(other_jid.bare, C.PRESENCE_SHOW) is None:
            raise NotConnectedEntity
        return clist.getFullJid(other_jid)


class OTR(object):

    def __init__(self, host):
        log.info(_(u"OTR plugin initialization"))
        self.host = host
        self.context_manager = None
        self.host.bridge._registerMethods(["skipOTR"])
        self.host.trigger.add("messageNewTrigger", self.newMessageTg, priority=trigger.TriggerManager.MAX_PRIORITY)
        self.host.trigger.add("messageSendTrigger", self.sendMessageTg, priority=trigger.TriggerManager.MAX_PRIORITY)

        # FIXME: workaround for a pyjamas issue: calling hash on a class method always return a different value if that method is defined directly within the class (with the "def" keyword)
        self._profilePluggedListener = self.profilePluggedListener
        self._gotMenusListener = self.gotMenusListener
        # FIXME: these listeners are never removed, can't be removed by themselves (it modifies the list while looping), maybe need a 'one_shot' argument
        self.host.addListener('profilePlugged', self._profilePluggedListener)
        self.host.addListener('gotMenus', self._gotMenusListener)

    @classmethod
    def getInfoText(self, state=otr.context.STATE_PLAINTEXT, trust=''):
        """Get the widget info text for a certain message state and trust.

        @param state (unicode): message state
        @param trust (unicode): trust
        @return: unicode
        """
        if not state:
            state = OTR_MSG_STATES.keys()[0]
        return OTR_MSG_STATES[state][1 if trust else 0]

    def getInfoTextForUser(self, other_jid):
        """Get the current info text for a conversation.

        @param other_jid (jid.JID): JID of the correspondant
        """
        otrctx = self.context_manager.getContextForUser(other_jid, start=False)
        if otrctx is None:
            return OTR.getInfoText()
        else:
            return OTR.getInfoText(otrctx.state, otrctx.getCurrentTrust())

    def gotMenusListener(self,):
        # TODO: get menus paths to hook directly from backend's OTR plugin
        self.host.menus.addMenuHook(C.MENU_SINGLE, (MAIN_MENU, D_(u"Start/Refresh")), callback=self._startRefresh)
        self.host.menus.addMenuHook(C.MENU_SINGLE, (MAIN_MENU, D_(u"End session")), callback=self._endSession)
        self.host.menus.addMenuHook(C.MENU_SINGLE, (MAIN_MENU, D_(u"Authenticate")), callback=self._authenticate)
        self.host.menus.addMenuHook(C.MENU_SINGLE, (MAIN_MENU, D_(u"Drop private key")), callback=self._dropPrivkey)

    def profilePluggedListener(self, profile):
        # FIXME: workaround for a pyjamas issue: calling hash on a class method always return a different value if that method is defined directly within the class (with the "def" keyword)
        self._presenceListener = self.presenceListener
        self._disconnectListener = self.disconnectListener
        self.host.addListener('presence', self._presenceListener, [C.PROF_KEY_NONE])
        # FIXME: this listener is never removed, can't be removed by itself (it modifies the list while looping), maybe need a 'one_shot' argument
        self.host.addListener('disconnect', self._disconnectListener, [C.PROF_KEY_NONE])

        self.host.bridge.call('skipOTR', None)
        self.context_manager = ContextManager(self.host)
        # TODO: retrieve the encrypted private key from a HTML5 persistent storage,
        # decrypt it, parse it with otr.crypt.PK.parsePrivateKey(privkey) and
        # assign it to self.context_manager.account.privkey

    def disconnectListener(self, profile):
        """Things to do just before the profile disconnection"""
        self.host.removeListener('presence', self._presenceListener)

        for context in self.context_manager.contexts.values():
            context.disconnect()  # FIXME: no time to send the message before the profile has been disconnected

    def presenceListener(self, entity, show, priority, statuses, profile):
        if show == C.PRESENCE_UNAVAILABLE:
            self.endSession(entity, disconnect=False)

    def newMessageTg(self, uid, timestamp, from_jid, to_jid, msg, subject, msg_type, extra, profile):
        if msg_type != C.MESS_TYPE_CHAT:
            return True

        try:
            msg = msg.values()[0]  # FIXME: Q&D fix for message refactoring, message is now a dict
        except IndexError:
            return True
        tag = otr.proto.checkForOTR(msg)
        if tag is None or (tag == otr.context.WHITESPACE_TAG and not DEFAULT_POLICY_FLAGS['WHITESPACE_START_AKE']):
            return True

        other_jid = to_jid if from_jid.bare == self.host.whoami.bare else from_jid
        otrctx = self.context_manager.getContextForUser(other_jid, start=False)
        if otrctx is None:
            def confirm(confirm):
                if confirm:
                    self.host.displayWidget(chat.Chat, other_jid)
                    self.context_manager.startContext(other_jid).receiveMessage(msg)
                else:
                    # FIXME: plain text messages with whitespaces would be lost here when WHITESPACE_START_AKE is True
                    pass
            key = self.context_manager.account.privkey
            question = QUERY_RECEIVED + QUERY_SLOWDOWN + (QUERY_KEY if key else QUERY_NO_KEY) + QUERY_CONFIRM
            dialog.ConfirmDialog(confirm, question.format(jid=other_jid, eol=DIALOG_EOL), QUERY_TITLE, AddStyleName="maxWidthLimit").show()
        else:  # do not ask for user confirmation if the context exist
            otrctx.receiveMessage(msg)

        return False  # interrupt the main process

    def sendMessageTg(self, to_jid, message, subject, mess_type, extra, callback, errback, profile_key):
        if mess_type != C.MESS_TYPE_CHAT:
            return True

        otrctx = self.context_manager.getContextForUser(to_jid, start=False)
        if otrctx is not None and otrctx.state != otr.context.STATE_PLAINTEXT:
            if otrctx.state == otr.context.STATE_ENCRYPTED:
                log.debug(u"encrypting message")
                otrctx.sendMessage(message)
                uuid_ = str(uuid.uuid4())  # FIXME
                self.host.newMessageHandler(uuid_, time.time(), unicode(self.host.whoami), unicode(to_jid), {'': message}, {}, mess_type,  extra)
            else:
                feedback = SEND_PLAIN_IN_FINISHED_CONTEXT
                dialog.InfoDialog(FINISHED_CONTEXT_TITLE.format(jid=to_jid), feedback, AddStyleName="maxWidthLimit").show()
            return False  # interrupt the main process

        log.debug(u"sending message unencrypted")
        return True

    def endSession(self, other_jid, disconnect=True):
        """Finish or disconnect an OTR session

        @param other_jid (jid.JID): other JID
        @param disconnect (bool): if False, finish the session but do not disconnect it
        """
        # checking for private key existence is not needed, context checking is enough
        if other_jid.resource:
            contexts = [self.context_manager.getContextForUser(other_jid, start=False)]
        else:  # contact disconnected itself so we need to terminate the OTR session but the Chat panel lost its resource
            contexts = self.context_manager.getContextsForBareUser(other_jid)
        for otrctx in contexts:
            if otrctx is None or otrctx.state == otr.context.STATE_PLAINTEXT:
                if disconnect:
                    uuid_ = str(uuid.uuid4())  # FIXME
                    self.host.newMessageHandler(uuid_, time.time(), unicode(other_jid), unicode(self.host.whoami), {'': END_PLAIN_HAS_NOT.format(jid=other_jid)}, {}, C.MESS_TYPE_INFO, {})
                return
            if disconnect:
                otrctx.disconnect()
            else:
                otrctx.finish()

    # Menu callbacks

    def _startRefresh(self, caller, menu_data, profile):
        """Start or refresh an OTR session

        @param menu_data: %(menu_data)s
        """
        def query(other_jid):
            otrctx = self.context_manager.getContextForUser(other_jid)
            if otrctx:
                otrctx.sendQueryMessage()

        other_jid = jid.JID(menu_data['jid'])
        clist = self.host.contact_list
        if clist.getCache(other_jid.bare, C.PRESENCE_SHOW) is None:
            dialog.InfoDialog(ACTION_NA_TITLE, ACTION_NA, AddStyleName="maxWidthLimit").show()
            return

        key = self.context_manager.account.privkey
        if key is None:
            def confirm(confirm):
                if confirm:
                    query(other_jid)
            msg = QUERY_SEND + QUERY_SLOWDOWN + QUERY_NO_KEY + QUERY_CONFIRM
            dialog.ConfirmDialog(confirm, msg.format(jid=other_jid, eol=DIALOG_EOL), QUERY_TITLE, AddStyleName="maxWidthLimit").show()
        else:  # on query reception we ask always, if we initiate we just ask the first time
            query(other_jid)

    def _endSession(self, caller, menu_data, profile):
        """End an OTR session

        @param menu_data: %(menu_data)s
        """
        self.endSession(jid.JID(menu_data['jid']))

    def _authenticate(self, caller, menu_data, profile):
        """Authenticate other user and see our own fingerprint

        @param menu_data: %(menu_data)s
        @param profile: %(doc_profile)s
        """
        def not_available():
            dialog.InfoDialog(AUTH_TRUST_NA_TITLE, AUTH_TRUST_NA_TXT, AddStyleName="maxWidthLimit").show()

        to_jid = jid.JID(menu_data['jid'])

        # checking for private key existence is not needed, context checking is enough
        otrctx = self.context_manager.getContextForUser(to_jid, start=False)
        if otrctx is None or otrctx.state != otr.context.STATE_ENCRYPTED:
            not_available()
            return
        otr_version = otrctx.getUsedVersion()
        if otr_version == otr.context.OTR_VERSION_2:
            otrctx.fingerprintAuthCb()
        elif otr_version == otr.context.OTR_VERSION_3:
            otrctx.smpAuthCb('question', None, 'asked')
        else:
            not_available()

    def _dropPrivkey(self, caller, menu_data, profile):
        """Drop our private Key

        @param menu_data: %(menu_data)s
        @param profile: %(doc_profile)s
        """
        priv_key = self.context_manager.account.privkey
        if priv_key is None:
            # we have no private key yet
            dialog.InfoDialog(KEY_NA_TITLE, KEY_NA_TXT, AddStyleName="maxWidthLimit").show()
            return

        def dropKey(confirm):
            if confirm:
                # we end all sessions
                for context in self.context_manager.contexts.values():
                    context.disconnect()
                self.context_manager.contexts.clear()
                self.context_manager.account.privkey = None
                dialog.InfoDialog(KEY_TITLE, KEY_DROPPED_TXT, AddStyleName="maxWidthLimit").show()

        dialog.ConfirmDialog(dropKey, KEY_DROP_TXT.format(eol=DIALOG_EOL), KEY_DROP_TITLE, AddStyleName="maxWidthLimit").show()
