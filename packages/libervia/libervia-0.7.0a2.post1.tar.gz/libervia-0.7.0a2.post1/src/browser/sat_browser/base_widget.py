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
import base_menu
from sat_frontends.quick_frontend import quick_menus


### Exceptions ###


class NoLiberviaWidgetException(Exception):
    """A Libervia widget was expected"""
    pass


### Menus ###


class WidgetMenuBar(base_menu.GenericMenuBar):

    ITEM_TPL = "<img src='media/icons/misc/%s.png' />"

    def __init__(self, parent, host, vertical=False, styles=None):
        """

        @param parent (Widget): LiberviaWidget, or instance of another class
            implementing the method addMenus
        @param host (SatWebFrontend)
        @param vertical (bool): if True, set the menu vertically
        @param styles (dict): optional styles dict
        """
        menu_styles = {'menu_bar': 'widgetHeader_buttonGroup'}
        if styles:
            menu_styles.update(styles)
        base_menu.GenericMenuBar.__init__(self, host, vertical=vertical, styles=menu_styles)

        # regroup all the dynamic menu categories in a sub-menu
        for menu_context in parent.plugin_menu_context:
            main_cont = host.menus.getMainContainer(menu_context)
            if len(main_cont)>0: # we don't add the icon if the menu is empty
                sub_menu = base_menu.GenericMenuBar(host, vertical=True, flat_level=1)
                sub_menu.update(menu_context, parent)
                menu_category = quick_menus.MenuCategory("plugins", extra={'icon':'plugins'})
                self.addCategory(menu_category, sub_menu)

    @classmethod
    def getCategoryHTML(cls, category):
        """Build the html to be used for displaying a category item.

        @param category (quick_menus.MenuCategory): category to add
        @return unicode: HTML to display
        """
        return cls.ITEM_TPL % category.icon
