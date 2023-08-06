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

from sat.core.log import getLogger
log = getLogger(__name__)
from sat.core.i18n import _

from pyjamas.ui.ClickListener import ClickHandler
from pyjamas.ui.FocusListener import FocusHandler
from pyjamas.ui.ChangeListener import ChangeHandler
from pyjamas.ui.DragHandler import DragHandler
from pyjamas.ui.KeyboardListener import KeyboardHandler, KEY_ENTER
from pyjamas.ui.DragWidget import DragWidget
from pyjamas.ui.ListBox import ListBox
from pyjamas.ui.Button import Button
from pyjamas.ui.FlowPanel import FlowPanel
from pyjamas.ui.HorizontalPanel import HorizontalPanel
from pyjamas.ui.FlexTable import FlexTable
from pyjamas.ui.AutoComplete import AutoCompleteTextBox

import base_panel
import base_widget
import libervia_widget

from sat_frontends.quick_frontend import quick_list_manager


unicode = str  # FIXME: pyjamas workaround


class ListItem(HorizontalPanel):
    """This class implements a list item with auto-completion and a delete button."""

    STYLE = {"listItem": "listItem",
             "listItem-box": "listItem-box",
             "listItem-box-invalid": "listItem-box-invalid",
             "listItem-button": "listItem-button",
             }

    VALID = 1
    INVALID = 2
    DUPLICATE = 3

    def __init__(self, listener=None, taglist=None, validate=None):
        """

        @param listener (ListItemHandler): handler for the UI events
        @param taglist (quick_list_manager.QuickTagList): list manager
        @param validate (callable): method returning a bool to validate the entry
        """
        HorizontalPanel.__init__(self)
        self.addStyleName(self.STYLE["listItem"])

        self.box = AutoCompleteTextBox(StyleName=self.STYLE["listItem-box"])
        self.remove_btn = Button('<span>x</span>', Visible=False)
        self.remove_btn.setStyleName(self.STYLE["listItem-button"])
        self.add(self.box)
        self.add(self.remove_btn)

        if listener:
            self.box.addFocusListener(listener)
            self.box.addChangeListener(listener)
            self.box.addKeyboardListener(listener)
            self.box.choices.addClickListener(listener)
            self.remove_btn.addClickListener(listener)

        self.taglist = taglist
        self.validate = validate
        self.last_checked_value = ""
        self.last_validity = self.VALID

    @property
    def text(self):
        return self.box.getText()

    def setText(self, text):
        """
        Set the text and refresh the Widget.
        
        @param text (unicode): text to set
        """
        self.box.setText(text)
        self.refresh()

    def refresh(self):
        if self.last_checked_value == self.text:
            return

        if self.taglist and self.last_checked_value:
            self.taglist.untag([self.last_checked_value])

        if self.validate:  # if None, the state is always valid
            self.last_validity = self.validate(self.text)

        if self.last_validity == self.VALID:
            self.box.removeStyleName(self.STYLE["listItem-box-invalid"])
            self.box.setVisibleLength(max(len(self.text), 10))
        elif self.last_validity == self.INVALID:
            self.box.addStyleName(self.STYLE["listItem-box-invalid"])
        elif self.last_validity == self.DUPLICATE:
            self.remove_btn.click()  # this may do more stuff then self.remove()
            return
        
        if self.taglist and self.text:
            self.taglist.tag([self.text])
        self.last_checked_value = self.text
        self.box.setSelectionRange(len(self.text), 0)  
        self.remove_btn.setVisible(len(self.text) > 0)
                     
    def setFocus(self, focused):
        self.box.setFocus(focused)

    def remove(self):
        """Remove the list item from its parent."""
        self.removeFromParent()

        if self.taglist and self.text:  # this must be done after the widget has been removed
            self.taglist.untag([self.text])


class DraggableListItem(ListItem, DragWidget):
    """This class is like ListItem, but in addition it can be dragged."""

    def __init__(self, listener=None, taglist=None, validate=None):
        """
    
        @param listener (ListItemHandler): handler for the UI events
        @param taglist (quick_list_manager.QuickTagList): list manager
        @param validate (callable): method returning a bool to validate the entry
        """
        ListItem.__init__(self, listener, taglist, validate)
        DragWidget.__init__(self)
        self.addDragListener(listener)


    def onDragStart(self, event):
        """The user starts dragging the item."""
        dt = event.dataTransfer
        dt.setData('text/plain', "%s\n%s" % (self.text, "CONTACT_TEXTBOX"))
        dt.setDragImage(self.box.getElement(), 15, 15)


class ListItemHandler(ClickHandler, FocusHandler, KeyboardHandler, ChangeHandler):
    """Implements basic handlers for the ListItem events."""

    last_item = None  # the last item is an empty text box for user input

    def __init__(self, taglist):
        """
        
        @param taglist (quick_list_manager.QuickTagList): list manager
        """
        ClickHandler.__init__(self)
        FocusHandler.__init__(self)
        ChangeHandler.__init__(self)
        KeyboardHandler.__init__(self)
        self.taglist = taglist

    def addItem(self, item):
        raise NotImplementedError

    def removeItem(self, item):
        raise NotImplementedError

    def onClick(self, sender):
        """The remove button or a suggested completion item has been clicked."""
        #log.debug("onClick sender type: %s" % type(sender))
        if isinstance(sender, Button):
            item = sender.getParent()
            self.removeItem(item)
        elif isinstance(sender, ListBox):
            # this is called after onChange when you click a suggested item, and now we get the final value
            textbox = sender._clickListeners[0]
            self.checkValue(textbox)
        else:
            raise AssertionError

    def onFocus(self, sender):
        """The text box has the focus."""
        #log.debug("onFocus sender type:  %s" % type(sender))
        assert isinstance(sender, AutoCompleteTextBox)
        sender.setCompletionItems(self.taglist.untagged)

    def onKeyUp(self, sender, keycode, modifiers):
        """The text box is being modified - or ENTER key has been pressed."""
        # this is called after onChange when you press ENTER, and now we get the final value
        #log.debug("onKeyUp sender type:  %s" % type(sender))
        assert isinstance(sender, AutoCompleteTextBox)
        if keycode == KEY_ENTER:
            self.checkValue(sender)

    def onChange(self, sender):
        """The text box has been changed by the user."""
        # this is called before the completion when you press ENTER or click a suggest item
        #log.debug("onChange sender type:  %s" % type(sender))
        assert isinstance(sender, AutoCompleteTextBox)
        self.checkValue(sender)

    def checkValue(self, textbox):
        """Internal handler to call when a new value is submitted by the user."""
        item = textbox.getParent()
        if item.text == item.last_checked_value:
            # this method has already been called (by self.onChange) and there's nothing new
            return
        item.refresh()
        if item == self.last_item and item.last_validity == ListItem.VALID and item.text:
            self.addItem()

class DraggableListItemHandler(ListItemHandler, DragHandler):
    """Implements basic handlers for the DraggableListItem events."""

    def __init__(self, manager):
        """
        
        @param manager (ListManager): list manager
        """
        ListItemHandler.__init__(self, manager)
        DragHandler.__init__(self)

    @property
    def manager(self):
        return self.taglist

    def onDragStart(self, event):
        """The user starts dragging the item."""
        self.manager.drop_target = None

    def onDragEnd(self, event):
        """The user dropped the list item."""
        text, dummy = libervia_widget.eventGetData(event)
        target = self.manager.drop_target  # self or another ListPanel
        if text == "" or target is None:
            return
        if target != self:  # move the item from self to target
            target.addItem(text)
            self.removeItem(self.getItem(text))


class ListPanel(FlowPanel, DraggableListItemHandler, libervia_widget.DropCell):
    """Implements a list of items."""
    # XXX: beware that pyjamas.ui.FlowPanel is not fully implemented:
    #     - it can not be used with pyjamas.ui.Label
    #     - FlowPanel.insert doesn't work

    STYLE = {"listPanel": "listPanel"}
    ACCEPT_NEW_ENTRY = False

    def __init__(self, manager, items=None):
        """Initialization with a button for the list name (key) and a DraggableListItem.

        @param manager (ListManager): list manager
        @param items (list): items to be set
        """
        FlowPanel.__init__(self)
        DraggableListItemHandler.__init__(self, manager)
        libervia_widget.DropCell.__init__(self, None)
        self.addStyleName(self.STYLE["listPanel"])
        self.manager = manager
        self.resetItems(items)

        # FIXME: dirty magic strings '@' and '@@'
        self.drop_keys = {"GROUP": lambda host, item_s: self.addItem("@%s" % item_s),
                          "CONTACT": lambda host, item_s: self.addItem(item_s),
                          "CONTACT_TITLE": lambda host, item_s: self.addItem('@@'),
                          "CONTACT_TEXTBOX": lambda host, item_s: setattr(self.manager, "drop_target", self),
                          }

    def onDrop(self, event):
        """Something has been dropped in this ListPanel"""
        try:
            libervia_widget.DropCell.onDrop(self, event)
        except base_widget.NoLiberviaWidgetException:
            pass
    
    def getItem(self, text):
        """Get an item from its text.
        
        @param text(unicode): item text
        """
        for child in self.getChildren():
            if child.text == text:
                return child
        return None

    def getItems(self):
        """Get the non empty items.

        @return list(unicode)
        """
        return [widget.text for widget in self.getChildren() if isinstance(widget, ListItem) and widget.text]

    def validateItem(self, text):
        """Return validation code after the item has been changed.

        @param text (unicode): item text to check
        @return: int value defined by one of these constants:
            - VALID if the item is valid
            - INVALID if the item is not valid but can be displayed
            - DUPLICATE if the item is a duplicate
        """
        def count(list_, item): # XXX: list.count in not implemented by pyjamas
            return len([elt for elt in list_ if elt == item])

        if count(self.getItems(), text) > 1:
            return ListItem.DUPLICATE  # item already exists in this list so we suggest its deletion
        if self.ACCEPT_NEW_ENTRY:
            return ListItem.VALID
        return ListItem.VALID if text in self.manager.items or not text else ListItem.INVALID

    def addItem(self, text=""):
        """Add an item.

        @param text (unicode): text to be set.
        @return: True if the item has been really added or merged.
        """
        if text in self.getItems():  # avoid duplicate in the same list
            return
        
        item = DraggableListItem(self, self.manager, self.validateItem)
        self.add(item)

        if self.last_item:
            if self.last_item.last_validity == ListItem.INVALID:
                # switch the two values so that the invalid one stays in last position
                item.setText(self.last_item.text)
                self.last_item.setText(text)
            elif not self.last_item.text:
                # copy the new value to previous empty item
                self.last_item.setText(text)
        else:  # first item of the list, or previous last item has been deleted
            item.setText(text)

        self.last_item = item
        self.last_item.setFocus(True)

    def removeItem(self, item):
        """Remove an item.
        
        @param item(DraggableListItem): item to remove
        """
        if item == self.last_item:
            self.addItem("")
        item.remove()  # this also updates the taglist

    def resetItems(self, items):
        """Reset the items.
        
        @param items (list): items to be set
        """
        for child in self.getChildren():
            child.remove()

        self.addItem()
        if not items:
            return

        items.sort()
        for item in items:
            self.addItem(unicode(item))


class ListManager(FlexTable, quick_list_manager.QuickTagList):
    """Implements a table to manage one or several lists of items."""

    STYLE = {"listManager-button": "group",
             "listManager-button-cell": "listManager-button-cell",
             }

    def __init__(self, data=None, items=None):
        """
        @param data (dict{unicode: list}): dict binding keys to tagged items.
        @param items (list): full list of items (tagged and untagged)
        """
        FlexTable.__init__(self, Width="100%")
        quick_list_manager.QuickTagList.__init__(self, [unicode(item) for item in items])
        self.lists = {}

        if data:
            for key, items in data.iteritems():
                self.addList(key, [unicode(item) for item in items])

    def addList(self, key, items=None):
        """Add a Button and ListPanel for a new list.

        @param key (unicode): list name
        @param items (list): items to append to the new list
        """
        if key in self.lists:
            return

        if items is None:
            items = []

        self.lists[key] = {"button": Button(key, Title=key, StyleName=self.STYLE["listManager-button"]),
                           "panel": ListPanel(self, items)}

        y, x = len(self.lists), 0
        self.insertRow(y)
        self.setWidget(y, x, self.lists[key]["button"])
        self.setWidget(y, x + 1, self.lists[key]["panel"])
        self.getCellFormatter().setStyleName(y, x, self.STYLE["listManager-button-cell"])

        try:
            self.popup_menu.registerClickSender(self.lists[key]["button"])
        except (AttributeError, TypeError):  # self.registerPopupMenuPanel hasn't been called yet
            pass

    def removeList(self, key):
        """Remove a ListPanel from this manager.

        @param key (unicode): list name
        """
        items = self.lists[key]["panel"].getItems()
        (y, x) = self.getIndex(self.lists[key]["button"])
        self.removeRow(y)
        del self.lists[key]
        self.untag(items)

    def untag(self, items):
        """Untag some items.
        
        Check first if the items are not used in any panel.

        @param items (list): items to be removed
        """
        items_assigned = set()
        for values in self.getItemsByKey().itervalues():
            items_assigned.update(values)
        quick_list_manager.QuickTagList.untag(self, [item for item in items if item not in items_assigned])

    def getItemsByKey(self):
        """Get the items grouped by list name.

        @return dict{unicode: list}
        """
        return {key: self.lists[key]["panel"].getItems() for key in self.lists}

    def getKeysByItem(self):
        """Get the keys groups by item.

        @return dict{object: set(unicode)}
        """
        result = {}
        for key in self.lists:
            for item in self.lists[key]["panel"].getItems():
                result.setdefault(item, set()).add(key)
        return result

    def registerPopupMenuPanel(self, entries, callback):
        """Register a popup menu panel for the list names' buttons.

        @param entries (dict{unicode: dict{unicode: unicode}}): menu entries
        @param callback (callable): common callback for all menu items, arguments are:
            - button widget
            - list name (item key)
        """
        self.popup_menu = base_panel.PopupMenuPanel(entries, callback=callback)
        for key in self.lists:  # register click sender for already existing lists
            self.popup_menu.registerClickSender(self.lists[key]["button"])


class TagsPanel(base_panel.ToggleStackPanel):
    """A toggle panel to set the tags"""

    TAGS = _("Tags")
    
    STYLE = {"main": "tagsPanel-main",
             "tags": "tagsPanel-tags"}

    def __init__(self, suggested_tags, tags=None):
        """
        
        @param suggested_tags (list[unicode]): list of all suggested tags
        @param tags (list[unicode]): already assigned tags
        """
        base_panel.ToggleStackPanel.__init__(self, Width="100%")
        self.addStyleName(self.STYLE["main"])
        
        if tags is None:
            tags = []

        self.tags = ListPanel(quick_list_manager.QuickTagList(suggested_tags), tags)
        self.tags.addStyleName(self.STYLE["tags"])
        self.tags.ACCEPT_NEW_ENTRY = True
        self.add(self.tags, self.TAGS)
        self.addStackChangeListener(self)

    def onStackChanged(self, sender, index, visible=None):
        if visible is None:
            visible = sender.getWidget(index).getVisible()
        text = ", ".join(self.getTags())
        suffix = "" if (visible or not text) else (": %s" % text)
        sender.setStackText(index, self.TAGS + suffix)

    def getTags(self):
        return self.tags.getItems()

    def setTags(self, items):
        self.tags.resetItems(items)

