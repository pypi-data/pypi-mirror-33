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

""" Contacts / jids related panels """

import pyjd  # this is dummy in pyjs
from sat.core.log import getLogger
log = getLogger(__name__)
from sat_frontends.tools import jid

from pyjamas.ui.ScrollPanel import ScrollPanel
from pyjamas.ui.VerticalPanel import VerticalPanel

import contact_widget
from constants import Const as C


class ContactsPanel(ScrollPanel):
    """ContactList graphic representation

    Special features like popup menu panel or changing the contact states must be done in a sub-class.
    """

    def __init__(self, host, merge_resources=True, contacts_click=None,
                 contacts_style=None, contacts_menus=None,
                 contacts_display=C.CONTACT_DEFAULT_DISPLAY):
        """

        @param host (SatWebFrontend): host instance
        @param merge_resources (bool): if True, the entities sharing the same
            bare JID will also share the same contact box.
        @param contacts_click (callable): click callback for the contact boxes
        @param contacts_style (unicode): CSS style name for the contact boxes
        @param contacts_menus (tuple): define the menu types that fit this
            contact panel, with values from the menus type constants.
        @param contacts_display (tuple): prioritize the display methods of the
            contact's label with values in ("jid", "nick", "bare", "resource")
        """
        self.panel = VerticalPanel()
        ScrollPanel.__init__(self, self.panel)
        self.addStyleName("gwt-ScrollPanel")  # XXX: no class is set by Pyjamas

        self.host = host
        self.merge_resources = merge_resources
        self._contacts = {}  # entity jid to ContactBox map
        self.panel.click_listener = None

        if contacts_click is not None:
            self.panel.onClick = contacts_click

        self.contacts_style = contacts_style
        self.contacts_menus = contacts_menus
        self.contacts_display = contacts_display

    def _key(self, contact_jid):
        """Return internal key for this contact.

        @param contact_jid (jid.JID): contact JID
        @return: jid.JID
        """
        return contact_jid.bare if self.merge_resources else contact_jid

    def getJids(self):
        """Return jids present in the panel

        @return (list[jid.JID]): full jids or bare jids if self.merge_resources is True
        """
        return self._contacts.keys()

    def getBoxes(self):
        """Return ContactBox present in the panel

        @return (list[ContactBox]): boxes of the contacts
        """
        return self._contacts.itervalues()

    def clear(self):
        """Clear all contacts."""
        self._contacts.clear()
        VerticalPanel.clear(self.panel)

    def setList(self, jids):
        """set all contacts in the list in one shot.

        @param jids (list[jid.JID]): jids to display (the order is kept)
        @param name (unicode): optional name of the contact
        """
        current_jids = [box.jid for box in self.panel.children if isinstance(box, contact_widget.ContactBox)]
        if current_jids == jids:
            # the display doesn't change
            return
        for contact_jid in set(current_jids).difference(jids):
            self.removeContactBox(contact_jid)
        count = 0
        for contact_jid in jids:
            assert isinstance(contact_jid, jid.JID)
            self.updateContactBox(contact_jid, count)
            count += 1

    def getContactBox(self, contact_jid):
        """Get the contact box for the given contact.

        @param contact_jid (jid.JID): contact JID
        @return: ContactBox or None
        """
        try:
            return self._contacts[self._key(contact_jid)]
        except KeyError:
            return None

    def updateContactBox(self, contact_jid, index=None):
        """Add a contact or update it if it already exists.

        @param contact_jid (jid.JID): contact JID
        @param index (int): insertion index if the contact is added
        @return: ContactBox
        """
        box = self.getContactBox(contact_jid)
        if box:
            box.update()
        else:
            entity = contact_jid.bare if self.merge_resources else contact_jid
            box = contact_widget.ContactBox(self.host, entity,
                                            style_name=self.contacts_style,
                                            display=self.contacts_display,
                                            plugin_menu_context=self.contacts_menus)
            self._contacts[self._key(contact_jid)] = box
            if index:
                VerticalPanel.insert(self.panel, box, index)
            else:
                VerticalPanel.append(self.panel, box)
        return box

    def removeContactBox(self, contact_jid):
        """Remove a contact.

        @param contact_jid (jid.JID): contact JID
        """
        box = self._contacts.pop(self._key(contact_jid), None)
        if box:
            VerticalPanel.remove(self.panel, box)
