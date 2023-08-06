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
from sat_frontends.quick_frontend.quick_contact_list import QuickContactList
from pyjamas.ui.SimplePanel import SimplePanel
from pyjamas.ui.ScrollPanel import ScrollPanel
from pyjamas.ui.VerticalPanel import VerticalPanel
from pyjamas.ui.ClickListener import ClickHandler
from pyjamas.ui.Label import Label
from pyjamas import Window
from pyjamas import DOM

from constants import Const as C
from sat_frontends.tools import jid
import libervia_widget
import contact_panel
import blog
import chat

unicode = str # XXX: pyjama doesn't manage unicode


class GroupLabel(libervia_widget.DragLabel, Label, ClickHandler):
    def __init__(self, host, group):
        """

        @param host (SatWebFrontend)
        @param group (unicode): group name
        """
        self.group = group
        Label.__init__(self, group)  # , Element=DOM.createElement('div')
        self.setStyleName('group')
        libervia_widget.DragLabel.__init__(self, group, "GROUP", host)
        ClickHandler.__init__(self)
        self.addClickListener(self)

    def onClick(self, sender):
        self.host.displayWidget(blog.Blog, (self.group,))


class GroupPanel(VerticalPanel):

    def __init__(self, parent):
        VerticalPanel.__init__(self)
        self.setStyleName('groupPanel')
        self._parent = parent
        self._groups = set()

    def add(self, group):
        if group in self._groups:
            log.warning("trying to add an already existing group")
            return
        _item = GroupLabel(self._parent.host, group)
        _item.addMouseListener(self._parent)
        DOM.setStyleAttribute(_item.getElement(), "cursor", "pointer")
        index = 0
        for group_ in [child.group for child in self.getChildren()]:
            if group_ > group:
                break
            index += 1
        VerticalPanel.insert(self, _item, index)
        self._groups.add(group)

    def remove(self, group):
        for wid in self:
            if isinstance(wid, GroupLabel) and wid.group == group:
                VerticalPanel.remove(self, wid)
                self._groups.remove(group)
                return
        log.warning("Trying to remove a non existent group")

    def getGroupBox(self, group):
        """get the widget of a group

        @param group (unicode): the group
        @return: GroupLabel instance if present, else None"""
        for wid in self:
            if isinstance(wid, GroupLabel) and wid.group == group:
                return wid
        return None

    def getGroups(self):
        return self._groups


class ContactTitleLabel(libervia_widget.DragLabel, Label, ClickHandler):

    def __init__(self, host, text):
        Label.__init__(self, text)  # , Element=DOM.createElement('div')
        self.setStyleName('contactTitle')
        libervia_widget.DragLabel.__init__(self, text, "CONTACT_TITLE", host)
        ClickHandler.__init__(self)
        self.addClickListener(self)

    def onClick(self, sender):
        self.host.displayWidget(blog.Blog, ())


class ContactList(SimplePanel, QuickContactList):
    """Manage the contacts and groups"""

    def __init__(self, host, target, on_click=None, on_change=None, user_data=None, profiles=None):
        QuickContactList.__init__(self, host, C.PROF_KEY_NONE)
        self.contact_list = self.host.contact_list
        SimplePanel.__init__(self)
        self.host = host
        self.scroll_panel = ScrollPanel()
        self.scroll_panel.addStyleName("gwt-ScrollPanel")  # XXX: no class is set by Pyjamas
        self.vPanel = VerticalPanel()
        _title = ContactTitleLabel(host, 'Contacts')
        DOM.setStyleAttribute(_title.getElement(), "cursor", "pointer")

        def on_click(contact_jid):
            self.host.displayWidget(chat.Chat, contact_jid, type_=C.CHAT_ONE2ONE)
            self.removeAlerts(contact_jid, True)

        self._contacts_panel = contact_panel.ContactsPanel(host, contacts_click=on_click, contacts_menus=(C.MENU_JID_CONTEXT, C.MENU_ROSTER_JID_CONTEXT))
        self._group_panel = GroupPanel(self)

        self.vPanel.add(_title)
        self.vPanel.add(self._group_panel)
        self.vPanel.add(self._contacts_panel)
        self.scroll_panel.add(self.vPanel)
        self.add(self.scroll_panel)
        self.setStyleName('contactList')
        Window.addWindowResizeListener(self)

        # FIXME: workaround for a pyjamas issue: calling hash on a class method always return a different value if that method is defined directly within the class (with the "def" keyword)
        self.avatarListener = self.onAvatarUpdate
        host.addListener('avatar', self.avatarListener, [C.PROF_KEY_NONE])
        self.postInit()

    @property
    def profile(self):
        return C.PROF_KEY_NONE

    def onDelete(self):
        QuickContactList.onDelete(self)
        self.host.removeListener('avatar', self.avatarListener)

    def update(self, entities=None, type_=None, profile=None):
        # XXX: as update is slow, we avoid many updates on profile plugs
        # and do them all at once at the end
        if not self.host._profile_plugged:  # FIXME: should not be necessary anymore (done in QuickFrontend)
            return
        ### GROUPS ###
        _keys = self.contact_list._groups.keys()
        try:
            # XXX: Pyjamas doesn't do the set casting if None is present
            _keys.remove(None)
        except (KeyError, ValueError): # XXX: error raised depend on pyjama's compilation options
            pass
        current_groups = set(_keys)
        shown_groups = self._group_panel.getGroups()
        new_groups = current_groups.difference(shown_groups)
        removed_groups = shown_groups.difference(current_groups)
        for group in new_groups:
            self._group_panel.add(group)
        for group in removed_groups:
            self._group_panel.remove(group)

        ### JIDS ###
        to_show = [jid_ for jid_ in self.contact_list.roster if self.contact_list.entityVisible(jid_) and jid_ != self.contact_list.whoami.bare]
        to_show.sort()

        self._contacts_panel.setList(to_show)

    def onWindowResized(self, width, height):
        ideal_height = height - DOM.getAbsoluteTop(self.getElement()) - 5
        tab_panel = self.host.panel.tab_panel
        if tab_panel.getWidgetCount() > 1:
            ideal_height -= tab_panel.getTabBar().getOffsetHeight()
        self.scroll_panel.setHeight("%s%s" % (ideal_height, "px"))

    def isContactInRoster(self, contact_jid):
        """Test if the contact is in our roster list"""
        for contact_box in self._contacts_panel:
            if contact_jid == contact_box.jid:
                return True
        return False

    def getGroups(self):
        return set([g for g in self._groups if g is not None])

    def onMouseMove(self, sender, x, y):
        pass

    def onMouseDown(self, sender, x, y):
        pass

    def onMouseUp(self, sender, x, y):
        pass

    def onMouseEnter(self, sender):
        if isinstance(sender, GroupLabel):
            jids = self.contact_list.getGroupData(sender.group, "jids")
            for contact in self._contacts_panel.getBoxes():
                if contact.jid in jids:
                    contact.label.addStyleName("selected")

    def onMouseLeave(self, sender):
        if isinstance(sender, GroupLabel):
            jids = self.contact_list.getGroupData(sender.group, "jids")
            for contact in self._contacts_panel.getBoxes():
                if contact.jid in jids:
                    contact.label.removeStyleName("selected")

    def onAvatarUpdate(self, jid_, hash_, profile):
        """Called on avatar update events

        @param jid_: jid of the entity with updated avatar
        @param hash_: hash of the avatar
        @param profile: %(doc_profile)s
        """
        box = self._contacts_panel.getContactBox(jid_)
        if box:
            box.update()

    def onNickUpdate(self, jid_, new_nick, profile):
        box = self._contacts_panel.getContactBox(jid_)
        if box:
            box.update()

    def offlineContactsToShow(self):
        """Tell if offline contacts should be visible according to the user settings

        @return: boolean
        """
        return C.bool(self.host.getCachedParam('General', C.SHOW_OFFLINE_CONTACTS))

    def emtyGroupsToShow(self):
        """Tell if empty groups should be visible according to the user settings

        @return: boolean
        """
        return C.bool(self.host.getCachedParam('General', C.SHOW_EMPTY_GROUPS))

    def onPresenceUpdate(self, entity, show, priority, statuses, profile):
        QuickContactList.onPresenceUpdate(self, entity, show, priority, statuses, profile)
        box = self._contacts_panel.getContactBox(entity)
        if box:  # box doesn't exist for MUC bare entity, don't create it
            box.update()


class JIDList(list):
    """JID-friendly list implementation for Pyjamas"""

    def __contains__(self, item):
        """Tells if the list contains the given item.

        @param item (object): element to check
        @return: bool
        """
        # Since our JID doesn't inherit from str/unicode, without this method
        # the test would return True only when the objects references are the
        # same. Tests have shown that the other iterable "set" and "dict" don't
        # need this hack to reproduce the Twisted's behavior.
        for other in self:
            if other == item:
                return True
        return False

    def index(self, item):
        i = 0
        for other in self:
            if other == item:
                return i
            i += 1
        raise ValueError("JIDList.index(%(item)s): %(item)s not in list" % {"item": item})

class JIDSet(set):
    """JID set implementation for Pyjamas"""

    def __contains__(self, item):
        return __containsJID(self, item)


class JIDDict(dict):
    """JID dict implementation for Pyjamas (a dict with JID keys)"""

    def __contains__(self, item):
        return __containsJID(self, item)

    def keys(self):
        return JIDSet(dict.keys(self))


def __containsJID(iterable, item):
    """Tells if the given item is in the iterable, works with JID.

    @param iterable(object): list, set or another iterable object
    @param item (object): element
    @return: bool
    """
    # Pyjamas JID-friendly implementation of the "in" operator. Since our JID
    # doesn't inherit from str, without this method the test would return True
    # only when the objects references are the same.
    if isinstance(item, jid.JID):
        return hash(item) in [hash(other) for other in iterable if isinstance(other, jid.JID)]
    return super(type(iterable), iterable).__contains__(iterable, item)
