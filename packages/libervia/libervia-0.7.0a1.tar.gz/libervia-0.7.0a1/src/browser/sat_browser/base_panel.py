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

from sat.core.log import getLogger
log = getLogger(__name__)
from sat.core.i18n import _

from pyjamas.ui.VerticalPanel import VerticalPanel
from pyjamas.ui.HorizontalPanel import HorizontalPanel
from pyjamas.ui.ScrollPanel import ScrollPanel
from pyjamas.ui.Button import Button
from pyjamas.ui.SimplePanel import SimplePanel
from pyjamas.ui.PopupPanel import PopupPanel
from pyjamas.ui.StackPanel import StackPanel
from pyjamas.ui.TextArea import TextArea
from pyjamas.ui.Event import BUTTON_LEFT, BUTTON_MIDDLE, BUTTON_RIGHT
from pyjamas import DOM


### Menus ###


class PopupMenuPanel(PopupPanel):
    """Popup menu (contextual menu) with common callbacks for all the items.
    
    This implementation of a popup menu allow you to assign two special methods which
    are common to all the items, in order to hide certain items and define their callbacks.
    callbacks. The menu can be bound to any button of the mouse (left, middle, right).
    """
    
    def __init__(self, entries, hide=None, callback=None, vertical=True, style=None, **kwargs):
        """
        @param entries (dict{unicode: dict{unicode: unicode}:
            - menu item keys 
            - values: dict{unicode: unicode}:
                - item data lile "title", "desc"...
                - value
        @param hide (callable): function of signature Widget, unicode: bool
            which takes the sender and the item key, and returns True if that
            item has to be hidden from the context menu.
        @param callback (callbable): function of signature Widget, unicode: None
            which takes the sender and the item key.
        @param vertical (bool): set the direction vertical or horizontal
        @param item_style (unicode): alternative CSS class for the menu items
        @param menu_style (unicode): supplementary CSS class for the sender widget
        """
        PopupPanel.__init__(self, autoHide=True, **kwargs)
        self.entries = entries
        self.hideMenu = hide
        self.callback = callback
        self.vertical = vertical
        self.style = {"selected": None, "menu": "itemKeyMenu", "item": "popupMenuItem"}
        if isinstance(style, dict):
            self.style.update(style)
        self.senders = {}

    def showMenu(self, sender):
        """Popup the menu on the screen, where it fits to the sender's position.

        @param sender (Widget): the widget that has been clicked
        """
        menu = VerticalPanel() if self.vertical is True else HorizontalPanel()
        menu.setStyleName(self.style["menu"])

        def button_cb(item):
            # XXX: you can not put that method in the loop and rely on key
            if self.callback is not None:
                self.callback(sender=sender, key=item.key)
            self.hide(autoClosed=True)

        for key, entry in self.entries.iteritems():
            if self.hideMenu is not None and self.hideMenu(sender=sender, key=key) is True:
                continue
            title = entry.get("title", key)
            item = Button(title, button_cb, StyleName=self.style["item"])
            item.key = key  # XXX: copy the key because we loop on it and it will change
            item.setTitle(entry.get("desc", title))
            menu.add(item)

        if menu.getWidgetCount() == 0:
            return  # no item to display means no menu at all
        
        self.add(menu)
        
        if self.vertical is True:
            x = sender.getAbsoluteLeft() + sender.getOffsetWidth()
            y = sender.getAbsoluteTop()
        else:
            x = sender.getAbsoluteLeft()
            y = sender.getAbsoluteTop() + sender.getOffsetHeight()
        
        self.setPopupPosition(x, y)
        self.show()
        
        if self.style["selected"]:
            sender.addStyleDependentName(self.style["selected"])

        def onHide(popup):
            if self.style["selected"]:
                sender.removeStyleDependentName(self.style["selected"])
            return PopupPanel.onHideImpl(self, popup)

        self.onHideImpl = onHide

    def registerClickSender(self, sender, button=BUTTON_LEFT):
        """Bind the menu to the specified sender.

        @param sender (Widget): bind the menu to this widget
        @param (int): BUTTON_LEFT, BUTTON_MIDDLE or BUTTON_RIGHT
        """
        self.senders.setdefault(sender, [])
        self.senders[sender].append(button)

        if button == BUTTON_RIGHT:
            # WARNING: to disable the context menu is a bit tricky...
            # The following seems to work on Firefox 24.0, but:
            # TODO: find a cleaner way to disable the context menu
            sender.getElement().setAttribute("oncontextmenu", "return false")

        def onBrowserEvent(event):
            button = DOM.eventGetButton(event)
            if DOM.eventGetType(event) == "mousedown" and button in self.senders[sender]:
                self.showMenu(sender)
            return sender.__class__.onBrowserEvent(sender, event)

        sender.onBrowserEvent = onBrowserEvent

    def registerMiddleClickSender(self, sender):
        self.registerClickSender(sender, BUTTON_MIDDLE)

    def registerRightClickSender(self, sender):
        self.registerClickSender(sender, BUTTON_RIGHT)


### Generic panels ###


class ToggleStackPanel(StackPanel):
    """This is a pyjamas.ui.StackPanel with modified behavior. All sub-panels ca be
    visible at the same time, clicking a sub-panel header will not display it and hide
    the others but only toggle its own visibility. The argument 'visibleStack' is ignored.
    Note that the argument 'visible' has been added to listener's 'onStackChanged' method.
    """

    def __init__(self, **kwargs):
        StackPanel.__init__(self, **kwargs)

    def onBrowserEvent(self, event):
        if DOM.eventGetType(event) == "click":
            index = self.getDividerIndex(DOM.eventGetTarget(event))
            if index != -1:
                self.toggleStack(index)

    def add(self, widget, stackText="", asHTML=False, visible=False):
        StackPanel.add(self, widget, stackText, asHTML)
        self.setStackVisible(self.getWidgetCount() - 1, visible)

    def toggleStack(self, index):
        if index >= self.getWidgetCount():
            return
        visible = not self.getWidget(index).getVisible()
        self.setStackVisible(index, visible)
        for listener in self.stackListeners:
            listener.onStackChanged(self, index, visible)


class TitlePanel(ToggleStackPanel):
    """A toggle panel to set the message title"""
    
    TITLE = _("Title")

    def __init__(self, text=None):
        ToggleStackPanel.__init__(self, Width="100%")
        self.text_area = TextArea()
        self.add(self.text_area, self.TITLE)
        self.addStackChangeListener(self)
        if text:
            self.setText(text)

    def onStackChanged(self, sender, index, visible=None):
        if visible is None:
            visible = sender.getWidget(index).getVisible()
        text = self.getText()
        suffix = "" if (visible or not text) else (": %s" % text)
        sender.setStackText(index, self.TITLE + suffix)

    def getText(self):
        return self.text_area.getText()

    def setText(self, text):
        self.text_area.setText(text)


class ScrollPanelWrapper(SimplePanel):
    """Scroll Panel like component, wich use the full available space
    to work around percent size issue, it use some of the ideas found
    here: http://code.google.com/p/google-web-toolkit/issues/detail?id=316
    specially in code given at comment #46, thanks to Stefan Bachert"""

    def __init__(self, *args, **kwargs):
        SimplePanel.__init__(self)
        self.spanel = ScrollPanel(*args, **kwargs)
        SimplePanel.setWidget(self, self.spanel)
        DOM.setStyleAttribute(self.getElement(), "position", "relative")
        DOM.setStyleAttribute(self.getElement(), "top", "0px")
        DOM.setStyleAttribute(self.getElement(), "left", "0px")
        DOM.setStyleAttribute(self.getElement(), "width", "100%")
        DOM.setStyleAttribute(self.getElement(), "height", "100%")
        DOM.setStyleAttribute(self.spanel.getElement(), "position", "absolute")
        DOM.setStyleAttribute(self.spanel.getElement(), "width", "100%")
        DOM.setStyleAttribute(self.spanel.getElement(), "height", "100%")

    def setWidget(self, widget):
        self.spanel.setWidget(widget)

    def setScrollPosition(self, position):
        self.spanel.setScrollPosition(position)

    def scrollToBottom(self):
        self.setScrollPosition(self.spanel.getElement().scrollHeight)
