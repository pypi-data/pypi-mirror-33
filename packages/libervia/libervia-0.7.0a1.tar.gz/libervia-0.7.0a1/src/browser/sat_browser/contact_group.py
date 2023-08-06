#!/usr/bin/python
# -*- coding: utf-8 -*-

# Libervia: a Salut à Toi frontend
# Copyright (C) 2013-2016 Adrien Cossa <souliane@mailoo.org>

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

from pyjamas.ui.Button import Button
from pyjamas.ui.CheckBox import CheckBox
from pyjamas.ui.Label import Label
from pyjamas.ui.HorizontalPanel import HorizontalPanel
from pyjamas.ui.VerticalPanel import VerticalPanel
from pyjamas.ui.DialogBox import DialogBox
from pyjamas.ui.ScrollPanel import ScrollPanel
from pyjamas.ui import HasAlignment

import dialog
import list_manager
import contact_panel
import contact_list
from sat_frontends.tools import jid


unicode = str  # FIXME: pyjamas workaround


class ContactGroupManager(list_manager.ListManager):

    def __init__(self, editor, data, contacts, offsets):
        """
        @param container (FlexTable): FlexTable parent widget
        @param keys (dict{unicode: dict{unicode: unicode}}): dict binding items
            keys to their display config data.
        @param contacts (list): list of contacts
        """
        self.editor = editor
        list_manager.ListManager.__init__(self, data, contacts)
        self.registerPopupMenuPanel(entries={"Remove group": {}},
                                    callback=lambda sender, key: self.removeGroup(sender))

    def removeGroup(self, sender):
        group = sender.getHTML()

        def confirm_cb(answer):
            if answer:
                list_manager.ListManager.removeList(self, group)
                self.editor.add_group_panel.groups.remove(group)

        _dialog = dialog.ConfirmDialog(confirm_cb, text="Do you really want to delete the group '%s'?" % group)
        _dialog.show()

    def tag(self, contacts):
        list_manager.ListManager.tag(self, contacts)
        self.editor.updateContactList(contacts)

    def untag(self, contacts, ignore_key=None):
        list_manager.ListManager.untag(self, contacts, ignore_key)
        self.editor.updateContactList(contacts)


class ContactGroupEditor(VerticalPanel):
    """A big panel including a ContactGroupManager and other UI stuff."""

    def __init__(self, host, container=None, onCloseCallback=None):
        """

        @param host (SatWebFrontend)
        @param container (PanelBase): parent panel or None to display in a popup
        @param onCloseCallback (callable)
        """
        VerticalPanel.__init__(self, StyleName="contactGroupEditor")
        self.host = host

        # eventually display in a popup
        if container is None:
            container = DialogBox(autoHide=False, centered=True)
            container.setHTML("Manage contact groups")
        self.container = container
        self._on_close_callback = onCloseCallback

        self.all_contacts = contact_list.JIDList(self.host.contact_list.roster)
        roster_entities_by_group = self.host.contact_list.roster_entities_by_group
        del roster_entities_by_group[None]  # remove the empty group
        roster_groups = roster_entities_by_group.keys()
        roster_groups.sort()

        # groups on the left
        manager = self.initContactGroupManager(roster_entities_by_group)
        self.add_group_panel = self.initAddGroupPanel(roster_groups)
        left_container = VerticalPanel(Width="100%")
        left_container.add(manager)
        left_container.add(self.add_group_panel)
        left_container.setCellHorizontalAlignment(self.add_group_panel, HasAlignment.ALIGN_CENTER)
        left_panel = ScrollPanel(left_container, StyleName="contactGroupManager")
        left_panel.setAlwaysShowScrollBars(True)

        # contact list on the right
        east_panel = ScrollPanel(self.initContactList(), StyleName="contactGroupRoster")
        east_panel.setAlwaysShowScrollBars(True)

        south_panel = self.initCloseSaveButtons()

        main_panel = HorizontalPanel()
        main_panel.add(left_panel)
        main_panel.add(east_panel)
        self.add(Label("You get here an over whole view of your contact groups. There are two ways to assign your contacts to an existing group: write them into auto-completed textboxes or use the right panel to drag and drop them into the group."))
        self.add(main_panel)
        self.add(south_panel)

        self.setCellHorizontalAlignment(south_panel, HasAlignment.ALIGN_CENTER)

        # need to be done after the contact list has been initialized
        self.updateContactList()

        # Hide the contacts list from the main panel to not confuse the user
        self.restore_contact_panel = False
        clist = self.host.contact_list_widget
        if clist.getVisible():
            self.restore_contact_panel = True
            self.host.panel._contactsSwitch()

        container.add(self)
        container.setVisible(True)
        if isinstance(container, DialogBox):
            container.center()

    def initContactGroupManager(self, data):
        """Initialise the contact group manager.

        @param groups (list[unicode]): contact groups
        """
        self.groups = ContactGroupManager(self, data, self.all_contacts)
        return self.groups

    def initAddGroupPanel(self, groups):
        """Initialise the 'Add group' panel.

        @param groups (list[unicode]): contact groups
        """

        def add_group_cb(key):
            self.groups.addList(key)
            self.add_group_panel.textbox.setFocus(True)

        add_group_panel = dialog.AddGroupPanel(groups, add_group_cb)
        add_group_panel.addStyleName("addContactGroupPanel")
        return add_group_panel

    def initCloseSaveButtons(self):
        """Add the buttons to close the dialog and save the groups."""
        buttons = HorizontalPanel()
        buttons.addStyleName("marginAuto")
        buttons.add(Button("Cancel", listener=self.cancelWithoutSaving))
        buttons.add(Button("Save", listener=self.closeAndSave))
        return buttons

    def initContactList(self):
        """Add the contact list to the DockPanel."""

        self.toggle = CheckBox("Hide assigned contacts")
        self.toggle.addClickListener(lambda dummy: self.updateContactList())
        self.toggle.addStyleName("toggleAssignedContacts")
        self.contacts = contact_panel.ContactsPanel(self.host)
        for contact in self.all_contacts:
            self.contacts.updateContactBox(contact)
        panel = VerticalPanel()
        panel.add(self.toggle)
        panel.add(self.contacts)
        return panel

    def updateContactList(self, contacts=None):
        """Update the contact list's items visibility, depending of the toggle
        checkbox and the "contacts" attribute.

        @param contacts (list): contacts to be updated, or None to update all.
        """
        if not hasattr(self, "toggle"):
            return
        if contacts is not None:
            contacts = [jid.JID(contact) for contact in contacts]
            contacts = set(contacts).intersection(self.all_contacts)
        else:
            contacts = self.all_contacts

        for contact in contacts:
            if not self.toggle.getChecked():  # show all contacts
                self.contacts.updateContactBox(contact).setVisible(True)
            else:  # show only non-assigned contacts
                if contact in self.groups.untagged:
                    self.contacts.updateContactBox(contact).setVisible(True)
                else:
                    self.contacts.updateContactBox(contact).setVisible(False)

    def __close(self):
        """Remove the widget from parent or close the popup."""
        if isinstance(self.container, DialogBox):
            self.container.hide()
        self.container.remove(self)
        if self._on_close_callback is not None:
            self._on_close_callback()
        if self.restore_contact_panel:
            self.host.panel._contactsSwitch()

    def cancelWithoutSaving(self):
        """Ask for confirmation before closing the dialog."""
        def confirm_cb(answer):
            if answer:
                self.__close()

        _dialog = dialog.ConfirmDialog(confirm_cb, text="Do you really want to cancel without saving?")
        _dialog.show()

    def closeAndSave(self):
        """Call bridge methods to save the changes and close the dialog"""
        old_groups_by_entity = contact_list.JIDDict(self.host.contact_list.roster_groups_by_entity)
        old_entities = old_groups_by_entity.keys()
        result = {jid.JID(item): keys for item, keys in self.groups.getKeysByItem().iteritems()}
        groups_by_entity = contact_list.JIDDict(result)
        entities = groups_by_entity.keys()

        for invalid in entities.difference(self.all_contacts):
            dialog.InfoDialog("Invalid contact(s)",
                              "The contact '%s' is not in your contact list but has been assigned to: '%s'." % (invalid, "', '".join(groups_by_entity[invalid])) +
                              "Your changes could not be saved: please check your assignments and save again.", Width="400px").center()
            return

        for entity in old_entities.difference(entities):
            self.host.bridge.call('updateContact', None, unicode(entity), '', [])

        for entity, groups in groups_by_entity.iteritems():
            if entity not in old_groups_by_entity or groups != old_groups_by_entity[entity]:
                self.host.bridge.call('updateContact', None, unicode(entity), '', list(groups))
        self.__close()
