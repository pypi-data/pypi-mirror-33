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

import pyjd  # this is dummy in pyjs
from sat.core.log import getLogger
log = getLogger(__name__)

from pyjamas.ui.HTML import HTML
from pyjamas.ui.Frame import Frame

from constants import Const as C
import file_tools
import xmlui
import chat
import dialog
import contact_group
import base_menu
from sat_browser import html_tools
from sat_browser import web_widget


unicode = str  # FIXME: pyjamas workaround


class MainMenuBar(base_menu.GenericMenuBar):
    """The main menu bar which is displayed on top of the document"""

    ITEM_TPL = "<img src='media/icons/menu/%s_menu_red.png' />%s"

    def __init__(self, host):
        styles = {'moved_popup': 'menuLastPopup', 'menu_bar': 'mainMenuBar'}
        base_menu.GenericMenuBar.__init__(self, host, vertical=False, styles=styles)

    @classmethod
    def getCategoryHTML(cls, category):
        """Build the html to be used for displaying a category item.

        @param category (quick_menus.MenuCategory): category to add
        @return unicode: HTML to display
        """
        name = html_tools.html_sanitize(category.name)
        return cls.ITEM_TPL % (category.icon, name) if category.icon is not None else name

    ## callbacks

    # General menu

    def onDisconnect(self):
        def confirm_cb(answer):
            if answer:
                self.host.disconnect(C.PROF_KEY_NONE)
        _dialog = dialog.ConfirmDialog(confirm_cb, text="Do you really want to disconnect ?")
        _dialog.show()

    #Contact menu

    def onManageContactGroups(self):
        """Open the contact groups manager."""

        def onCloseCallback():
            pass

        contact_group.ContactGroupEditor(self.host, None, onCloseCallback)

    #Group menu
    def onJoinRoom(self):

        def invite(room_jid, contacts):
            for contact in contacts:
                self.host.bridge.call('inviteMUC', None, unicode(contact), unicode(room_jid))

        def join(room_jid, contacts):
            if self.host.whoami:
                nick = self.host.whoami.node
                contact_list = self.host.contact_list
                if room_jid is None or room_jid not in contact_list.getSpecials(C.CONTACT_SPECIAL_GROUP):
                    room_jid_s = unicode(room_jid) if room_jid else ''
                    self.host.bridge.joinMUC(room_jid_s, nick, profile=C.PROF_KEY_NONE, callback=lambda room_jid: invite(room_jid, contacts), errback=self.host.onJoinMUCFailure)
                else:
                    self.host.displayWidget(chat.Chat, room_jid, type_="group")
                    invite(room_jid, contacts)

        dialog.RoomAndContactsChooser(self.host, join, ok_button="Join", visible=(True, False))


    # Help menu

    def onOfficialChatRoom(self):
        nick = self.host.whoami.node
        self.host.bridge.joinMUC(self.host.default_muc, nick, profile=C.PROF_KEY_NONE, callback=lambda dummy: None, errback=self.host.onJoinMUCFailure)

    def onSocialContract(self):
        _frame = Frame('contrat_social.html')
        _frame.setStyleName('infoFrame')
        _dialog = dialog.GenericDialog("Contrat Social", _frame)
        _dialog.setSize('80%', '80%')
        _dialog.show()

    def onAbout(self):
        def gotVersions():
            _about = HTML("""<b>Libervia</b>, a Salut &agrave; Toi project<br />
    <br />
    Libervia is a web frontend for Salut &agrave; Toi<br />
    <span style='font-style: italic;'>S&agrave;T version:</span> {sat_version}<br/>
    <span style='font-style: italic;'>Libervia version:</span> {libervia_version}<br/>
    <br />
    You can contact the authors at <a href="mailto:contact@salut-a-toi.org">contact@salut-a-toi.org</a><br />
    Blog available (mainly in french) at <a href="http://www.goffi.org" target="_blank">http://www.goffi.org</a><br />
    Project page: <a href="http://salut-a-toi.org"target="_blank">http://salut-a-toi.org</a><br />
    <br />
    Any help welcome :)
    <p style='font-size:small;text-align:center'>This project is dedicated to Roger Poisson</p>
    """.format(sat_version=self.host.sat_version, libervia_version=self.host.libervia_version))
            _dialog = dialog.GenericDialog("About", _about)
            _dialog.show()
        self.host.getVersions(gotVersions)

    #Settings menu

    def onAccount(self):
        def gotUI(xml_ui):
            if not xml_ui:
                return
            body = xmlui.create(self.host, xml_ui)
            _dialog = dialog.GenericDialog("Manage your account", body, options=['NO_CLOSE'])
            body.setCloseCb(_dialog.close)
            _dialog.show()
        self.host.bridge.call('getAccountDialogUI', gotUI)

    def onParameters(self):
        def gotParams(xml_ui):
            if not xml_ui:
                return
            body = xmlui.create(self.host, xml_ui)
            _dialog = dialog.GenericDialog("Parameters", body, options=['NO_CLOSE'])
            _dialog.addStyleName("parameters")
            body.setCloseCb(_dialog.close)
            _dialog.setSize('80%', '80%')
            _dialog.show()
        self.host.bridge.getParamsUI(profile=C.PROF_KEY_NONE, callback=gotParams)

    def removeItemParams(self):
        """Remove the Parameters item from the Settings menu bar."""
        self.menu_settings.removeItem(self.item_params)

    def onAvatarUpload(self):
        body = file_tools.AvatarUpload()
        _dialog = dialog.GenericDialog("Avatar upload", body, options=['NO_CLOSE'])
        body.setCloseCb(_dialog.close)
        _dialog.setWidth('40%')
        _dialog.show()

    def onPublicBlog(self, contact_box, data,  profile):
        # FIXME: Q&D way to check domain, need to be done in a cleaner way
        if contact_box.jid.domain != self.host._defaultDomain:
            self.host.showDialog(u"Public blogs from other domains are not managed yet", "Can't show public blog", "error")
            return

        url = '{}/blog/{}'.format(self.host.base_location, contact_box.jid.node)
        widget = self.host.displayWidget(web_widget.WebWidget, url, show_url=False)
        self.host.setSelected(widget)
