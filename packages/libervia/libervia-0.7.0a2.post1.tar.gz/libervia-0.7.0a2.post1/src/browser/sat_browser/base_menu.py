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


"""Base classes for building a menu.

These classes have been moved here from menu.py because they are also used
by base_widget.py, and the import sequence caused a JS runtime error."""


from sat.core.log import getLogger
log = getLogger(__name__)

from pyjamas.ui.MenuBar import MenuBar
from pyjamas.ui.MenuItem import MenuItem
from pyjamas import Window
from sat_frontends.quick_frontend import quick_menus
from sat_browser import html_tools


unicode = str  # FIXME: pyjamas workaround


class MenuCmd(object):
    """Return an object with an "execute" method that can be set to a menu item callback"""

    def __init__(self, menu_item, caller=None):
        """
        @param menu_item(quick_menu.MenuItem): instance of a callbable MenuItem
        @param caller: menu caller
        """
        self.item = menu_item
        self._caller = caller

    def execute(self):
        self.item.call(self._caller)


class SimpleCmd(object):
    """Return an object with an "executre" method that launch a callback"""

    def __init__(self, callback):
        """
        @param callback: method to call when menu is selected
        """
        self.callback = callback

    def execute(self):
        self.callback()


class GenericMenuBar(MenuBar):
    """A menu bar with sub-categories and items"""

    def __init__(self, host, vertical=False, styles=None, flat_level=0, **kwargs):
        """
        @param host (SatWebFrontend): host instance
        @param vertical (bool): True to display the popup menu vertically
        @param styles (dict): specific styles to be applied:
            - key: a value in ('moved_popup', 'menu_bar')
            - value: a CSS class name
        @param flat_level (int): sub-menus until that level see their items
        displayed in the parent menu bar instead of in a callback popup.
        """
        MenuBar.__init__(self, vertical, **kwargs)
        self.host = host
        self.styles = {}
        if styles:
            self.styles.update(styles)
        try:
            self.setStyleName(self.styles['menu_bar'])
        except KeyError:
            pass
        self.menus_container = None
        self.flat_level = flat_level

    def update(self, type_, caller=None):
        """Method to call when menus have changed

        @param type_: menu type like in sat.core.sat_main.importMenu
        @param caller: instance linked to the menus
        """
        self.menus_container = self.host.menus.getMainContainer(type_)
        self._caller=caller
        self.createMenus()

    @classmethod
    def getCategoryHTML(cls, category):
        """Build the html to be used for displaying a category item.

        Inheriting classes may overwrite this method.
        @param category (quick_menus.MenuCategory): category to add
        @return unicode: HTML to display
        """
        return html_tools.html_sanitize(category.name)

    def _buildMenus(self, container, flat_level, caller=None):
        """Recursively build menus of the container

        @param container: a quick_menus.MenuContainer instance
        @param caller: instance linked to the menus
        """
        for child in container.getActiveMenus():
            if isinstance(child, quick_menus.MenuContainer):
                item = self.addCategory(child, flat=bool(flat_level))
                submenu = item.getSubMenu()
                if submenu is None:
                    submenu = self
                submenu._buildMenus(child, flat_level-1 if flat_level else 0, caller)
            elif isinstance(child, quick_menus.MenuSeparator):
                item = MenuItem(text='', asHTML=None, StyleName="menuSeparator")
                self.addItem(item)
            elif isinstance(child, quick_menus.MenuItem):
                self.addItem(child.name, False, MenuCmd(child, caller) if child.CALLABLE else None)
            else:
                log.error(u"Unknown child type: {}".format(child))

    def createMenus(self):
        self.clearItems()
        if self.menus_container is None:
            log.debug("Menu is empty")
            return
        self._buildMenus(self.menus_container, self.flat_level, self._caller)

    def doItemAction(self, item, fireCommand):
        """Overwrites the default behavior for the popup menu to fit in the screen"""
        MenuBar.doItemAction(self, item, fireCommand)
        if not self.popup:
            return
        if self.vertical:
            # move the popup if it would go over the screen's viewport
            max_left = Window.getClientWidth() - self.getOffsetWidth() + 1 - self.popup.getOffsetWidth()
            new_left = self.getAbsoluteLeft() - self.popup.getOffsetWidth() + 1
            top = item.getAbsoluteTop()
        else:
            # move the popup if it would go over the menu bar right extremity
            max_left = self.getAbsoluteLeft() + self.getOffsetWidth() - self.popup.getOffsetWidth()
            new_left = max_left
            top = self.getAbsoluteTop() + self.getOffsetHeight() - 1
        if item.getAbsoluteLeft() > max_left:
            self.popup.setPopupPosition(new_left, top)
            # eventually smooth the popup edges to fit the menu own style
            try:
                self.popup.addStyleName(self.styles['moved_popup'])
            except KeyError:
                pass

    def addCategory(self, category, menu_bar=None, flat=False):
        """Add a new category.

        @param category (quick_menus.MenuCategory): category to add
        @param menu_bar (GenericMenuBar): instance to popup as the category sub-menu.
        """
        html = self.getCategoryHTML(category)

        if menu_bar is not None:
            assert not flat # can't have a menu_bar and be flat at the same time
            sub_menu = menu_bar
        elif not flat:
            sub_menu = GenericMenuBar(self.host, vertical=True)
        else:
            sub_menu = None

        item = self.addItem(html, True, sub_menu)
        if flat:
            item.setStyleName("menuFlattenedCategory")
        return item
