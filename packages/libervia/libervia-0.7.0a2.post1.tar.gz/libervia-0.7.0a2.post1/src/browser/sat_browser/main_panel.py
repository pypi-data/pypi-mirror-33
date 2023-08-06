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

"""Panels used as main basis"""

import pyjd  # this is dummy in pyjs
from sat.core.log import getLogger
log = getLogger(__name__)

from sat.core.i18n import _
from sat_browser import strings

from pyjamas.ui.DockPanel import DockPanel
from pyjamas.ui.HorizontalPanel import HorizontalPanel
from pyjamas.ui.VerticalPanel import VerticalPanel
from pyjamas.ui.Button import Button
from pyjamas.ui.HTML import HTML
from pyjamas.ui.ClickListener import ClickHandler
from pyjamas.Timer import Timer
from pyjamas.ui import HasVerticalAlignment


import menu
import dialog
import base_widget
import base_menu
import libervia_widget
import editor_widget
import html_tools
from constants import Const as C


### Warning notification (visibility of message, and other warning data) ###


class WarningPopup():

    def __init__(self):
        self._popup = None
        self._timer = Timer(notify=self._timeCb)
        self.timeout = None
        self._html = None
        self._last_type = None
        self._last_html = None

    def showWarning(self, type_=None, msg=None, duration=2000):
        """Display a popup information message, e.g. to notify the recipient of a message being composed.

        If type_ is None, a popup being currently displayed will be hidden.
        @type_: a type determining the CSS style to be applied (see _showWarning)
        @msg: message to be displayed
        @duration(int, None): time (in ms) to display the message
        """
        if type_ is None:
            self._removeWarning()
            return

        self.timeout = duration

        if not self._popup or self._last_type != type_ or self._last_html != msg:
            self._showWarning(type_, msg)

    def _showWarning(self, type_, msg):
        """Display a popup information message, e.g. to notify the recipient of a message being composed.

        @type_: a type determining the CSS style to be applied. For now the defined styles are
        "NONE" (will do nothing), "PUBLIC", "GROUP", "STATUS" and "ONE2ONE".
        @msg: message to be displayed
        """
        if type_ == "NONE":
            return
        if not msg:
            log.warning("no msg set")
            return
        if type_ == "PUBLIC":
            style = "targetPublic"
        elif type_ == "GROUP":
            style = "targetGroup"
        elif type_ == "STATUS":
            style = "targetStatus"
        elif type_ == "ONE2ONE":
            style = "targetOne2One"
        elif type_ == "INFO":
            style = "notifInfo"
        elif type_ == "WARNING":
            style = "notifWarning"
        else:
            log.error("unknown message type")
            return

        self._last_html = msg

        if self._popup is None:
            self._popup = dialog.PopupPanelWrapper(autoHide=False, modal=False)
            self._html = HTML(msg)
            self._popup.add(self._html)

            left = 0
            top = 0  # max(0, self.getAbsoluteTop() - contents.getOffsetHeight() - 2)
            self._popup.setPopupPosition(left, top)
            self._popup.show()
        else:
            self._html.setHTML(msg)

        if type_ != self._last_type:
            self._last_type = type_
            self._popup.setStyleName("warningPopup")
            self._popup.addStyleName(style)

        if self.timeout is not None:
            self._timer.schedule(self.timeout)

    def _timeCb(self, timer):
        if self._popup:
            self._popup.hide()
            self._popup = None

    def _removeWarning(self):
        """Remove the popup"""
        self._timer.cancel()
        self._timeCb(None)


### Status ###


class StatusPanel(editor_widget.HTMLTextEditor):

    EMPTY_STATUS = '&lt;click to set a status&gt;'
    VALIDATE_WITH_SHIFT_ENTER = False

    def __init__(self, host, status=''):
        self.host = host
        modifiedCb = lambda content: self.host.bridge.call('setStatus', None, self.host.presence_status_panel.presence, content['text']) or True
        editor_widget.HTMLTextEditor.__init__(self, {'text': status}, modifiedCb, options={'no_xhtml': True, 'listen_focus': True, 'listen_click': True})
        self.edit(False)
        self.setStyleName('marginAuto')

    @property
    def status(self):
        return self._original_content['text']

    def __cleanContent(self, content):
        status = content['text']
        if status == self.EMPTY_STATUS or status in C.PRESENCE.values():
            content['text'] = ''
        return content

    def getContent(self):
        return self.__cleanContent(editor_widget.HTMLTextEditor.getContent(self))

    def setContent(self, content):
        content = self.__cleanContent(content)
        editor_widget.BaseTextEditor.setContent(self, content)

    def setDisplayContent(self):
        status = self._original_content['text']
        try:
            presence = self.host.presence_status_panel.presence
        except AttributeError:  # during initialization
            presence = None
        if not status:
            if presence and presence in C.PRESENCE:
                status = C.PRESENCE[presence]
            else:
                status = self.EMPTY_STATUS
        self.display.setHTML(strings.addURLToText(status))


class PresenceStatusMenuBar(base_widget.WidgetMenuBar):
    def __init__(self, parent):
        styles = {'menu_bar': 'presence-button'}
        base_widget.WidgetMenuBar.__init__(self, parent, parent.host, styles=styles)
        self.button = self.addCategory(u"◉")
        presence_menu = self.button.getSubMenu()
        for presence, presence_i18n in C.PRESENCE.items():
            html = u'<span class="%s">◉</span> %s' % (html_tools.buildPresenceStyle(presence), presence_i18n)
            presence_menu.addItem(html, True, base_menu.SimpleCmd(lambda presence=presence: self.changePresenceCb(presence)))
        self.parent_panel = parent

    def changePresenceCb(self, presence=''):
        """Callback to notice the backend of a new presence set by the user.
        @param presence (unicode): the new presence is a value in ('', 'chat', 'away', 'dnd', 'xa')
        """
        self.host.bridge.call('setStatus', None, presence, self.parent_panel.status_panel.status)

    @classmethod
    def getCategoryHTML(cls, category):
        """Build the html to be used for displaying a category item.

        @param category (quick_menus.MenuCategory): category to add
        @return unicode: HTML to display
        """
        return category


class PresenceStatusPanel(HorizontalPanel, ClickHandler):

    def __init__(self, host, presence="", status=""):
        self.host = host
        self.plugin_menu_context = []
        HorizontalPanel.__init__(self, Width='100%')
        self.presence_bar = PresenceStatusMenuBar(self)
        self.status_panel = StatusPanel(host, status=status)
        self.setPresence(presence)

        panel = HorizontalPanel()
        panel.add(self.presence_bar)
        panel.add(self.status_panel)
        panel.setCellVerticalAlignment(self.presence_bar, 'baseline')
        panel.setCellVerticalAlignment(self.status_panel, 'baseline')
        panel.setStyleName("presenceStatusPanel")
        self.add(panel)

        self.status_panel.edit(False)

        ClickHandler.__init__(self)
        self.addClickListener(self)

    @property
    def presence(self):
        return self._presence

    @property
    def status(self):
        return self.status_panel._original_content['text']

    def setPresence(self, presence):
        self._presence = presence
        html_tools.setPresenceStyle(self.presence_bar.button, self._presence)

    def setStatus(self, status):
        self.status_panel.setContent({'text': status})
        self.status_panel.setDisplayContent()

    def onClick(self, sender):
        # As status is the default target of uniBar, we don't want to select anything if click on it
        self.host.setSelected(None)


### Panels managing the main area ###


class MainPanel(DockPanel):
    """The panel which take the whole screen"""

    def __init__(self, host):
        self.host = host
        DockPanel.__init__(self, StyleName="mainPanel liberviaTabPanel")

        # menu and status panel
        self.header = VerticalPanel(StyleName="header")
        self.menu = menu.MainMenuBar(host)
        self.header.add(self.menu)

        # contacts
        self.contacts_switch = Button(u'«', self._contactsSwitch)
        self.contacts_switch.addStyleName('contactsSwitch')

        # tab panel
        self.tab_panel = libervia_widget.MainTabPanel(host)
        self.tab_panel.addWidgetsTab(_(u"Discussions"), select=True, locked=True)

        # XXX: widget's addition order is important!
        self.add(self.header, DockPanel.NORTH)
        self.add(self.tab_panel, DockPanel.CENTER)
        self.setCellWidth(self.tab_panel, '100%')
        self.setCellHeight(self.tab_panel, '100%')
        self.add(self.tab_panel.getTabBar(), DockPanel.SOUTH)

    def addContactList(self, contact_list):
        self.add(self.contacts_switch, DockPanel.WEST)
        self.add(contact_list, DockPanel.WEST)

    def addPresenceStatusPanel(self, panel):
        self.header.add(panel)
        self.header.setCellHeight(panel, '100%')
        self.header.setCellVerticalAlignment(panel, HasVerticalAlignment.ALIGN_BOTTOM)

    def _contactsSwitch(self, btn=None):
        """ (Un)hide contacts panel """
        if btn is None:
            btn = self.contacts_switch
        clist = self.host.contact_list_widget
        clist.setVisible(not clist.getVisible())
        btn.setText(u"«" if clist.getVisible() else u"»")
        self.host.resize()

    def _contactsMove(self, parent):
        """Move the contacts container (containing the contact list and
        the "hide/show" button) to another parent, but always as the
        first child position (insert at index 0).
        """
        if self._contacts.getParent():
            if self._contacts.getParent() == parent:
                return
            self._contacts.removeFromParent()
        parent.insert(self._contacts, 0)
