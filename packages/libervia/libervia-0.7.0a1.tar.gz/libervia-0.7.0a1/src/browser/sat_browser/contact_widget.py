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

from sat.core import exceptions
from sat_frontends.quick_frontend import quick_menus
from pyjamas.ui.VerticalPanel import VerticalPanel
from pyjamas.ui.HTML import HTML
from pyjamas.ui.Image import Image
from pyjamas.ui.ClickListener import ClickHandler
from constants import Const as C
import html_tools
import base_widget
import libervia_widget

unicode = str # XXX: pyjama doesn't manage unicode


class ContactLabel(HTML):
    """Display a contact in HTML, selecting best display (jid/nick/etc)"""

    def __init__(self, host, jid_, display=C.CONTACT_DEFAULT_DISPLAY):
        """

        @param host (SatWebFrontend): host instance
        @param jid_ (jid.JID): contact JID
        @param display (tuple): prioritize the display methods of the contact's
            label with values in ("jid", "nick", "bare", "resource").
        """
        # TODO: add a listener for nick changes
        HTML.__init__(self)
        self.host = host
        self.jid = jid_
        self.display = display
        self.alert = False
        self.setStyleName('contactLabel')

    def update(self):
        clist = self.host.contact_list
        notifs = list(self.host.getNotifs(self.jid, exact_jid=False, profile=C.PROF_KEY_NONE))
        alerts_count = len(notifs)
        alert_html = ("<strong>(%i)</strong>&nbsp;" % alerts_count) if alerts_count else ""

        contact_raw = None
        for disp in self.display:
            if disp == "jid":
                contact_raw = unicode(self.jid)
            elif disp == "nick":
                clist = self.host.contact_list
                contact_raw = html_tools.html_sanitize(clist.getCache(self.jid, "nick"))
            elif disp == "bare":
                contact_raw = unicode(self.jid.bare)
            elif disp == "resource":
                contact_raw = self.jid.resource
            else:
                raise exceptions.InternalError(u"Unknown display argument [{}]".format(disp))
            if contact_raw:
                break
        if not contact_raw:
            log.error(u"Could not find a contact display for jid {jid} (display: {display})".format(jid=self.jid, display=self.display))
            contact_raw = "UNNAMED"
        contact_html = html_tools.html_sanitize(contact_raw)

        html = "%(alert)s%(contact)s" % {'alert': alert_html,
                                         'contact': contact_html}
        self.setHTML(html)


class ContactMenuBar(base_widget.WidgetMenuBar):
    """WidgetMenuBar displaying the contact's avatar as category."""

    def onBrowserEvent(self, event):
        base_widget.WidgetMenuBar.onBrowserEvent(self, event)
        event.stopPropagation()  # prevent opening the chat dialog

    @classmethod
    def getCategoryHTML(cls, category):
        """Return the HTML code for displaying contact's avatar.

        @param category (quick_menus.MenuCategory): ignored
        @return(unicode): HTML to display
        """
        return '<img src="%s"/>' % C.DEFAULT_AVATAR_URL

    def setUrl(self, url):
        """Set the URL of the contact avatar.

        @param url (unicode): avatar URL
        """
        if not self.items:  # the menu is empty but we've been asked to set an avatar
            self.addCategory("dummy")
        self.items[0].setHTML('<img src="%s" />' % url)


class ContactBox(VerticalPanel, ClickHandler, libervia_widget.DragLabel):

    def __init__(self, host, jid_, style_name=None, display=C.CONTACT_DEFAULT_DISPLAY, plugin_menu_context=None):
        """
        @param host (SatWebFrontend): host instance
        @param jid_ (jid.JID): contact JID
        @param style_name (unicode): CSS style name
        @param contacts_display (tuple): prioritize the display methods of the
            contact's label with values in ("jid", "nick", "bare", "resource").
        @param plugin_menu_context (iterable): contexts of menus to have (list of C.MENU_* constant)

        """
        self.plugin_menu_context = [] if plugin_menu_context is None else plugin_menu_context
        VerticalPanel.__init__(self, StyleName=style_name or 'contactBox', VerticalAlignment='middle')
        ClickHandler.__init__(self)
        libervia_widget.DragLabel.__init__(self, jid_, "CONTACT", host)
        self.jid = jid_
        self.label = ContactLabel(host, self.jid, display=display)
        self.avatar = ContactMenuBar(self, host) if plugin_menu_context else Image()
        self.states = HTML()
        self.add(self.avatar)
        self.add(self.label)
        self.add(self.states)
        self.update()
        self.addClickListener(self)

    def update(self):
        """Update the display.

        @param with_bare (bool): if True, ignore the resource and update with bare information.
        """
        self.avatar.setUrl(self.host.getAvatarURL(self.jid))

        self.label.update()
        clist = self.host.contact_list
        show = clist.getCache(self.jid, C.PRESENCE_SHOW)
        if show is None:
            show = C.PRESENCE_UNAVAILABLE
        html_tools.setPresenceStyle(self.label, show)

    def onClick(self, sender):
        try:
            self.parent.onClick(self.jid)
        except (AttributeError, TypeError):
            pass

quick_menus.QuickMenusManager.addDataCollector(C.MENU_JID_CONTEXT, lambda caller, dummy: {'jid': unicode(caller.jid.bare)})
