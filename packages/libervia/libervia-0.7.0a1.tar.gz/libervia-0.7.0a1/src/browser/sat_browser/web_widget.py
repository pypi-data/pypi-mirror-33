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

from sat.core.i18n import D_

from pyjamas.ui.VerticalPanel import VerticalPanel
from pyjamas.ui.HorizontalPanel import HorizontalPanel
from pyjamas.ui.Button import Button
from pyjamas.ui.Frame import Frame
from pyjamas import DOM


import dialog
import libervia_widget
from constants import Const as C
from sat_frontends.quick_frontend import quick_widgets
from sat_frontends.tools import host_listener


class WebWidget(quick_widgets.QuickWidget, libervia_widget.LiberviaWidget):
    """ (mini)browser like widget """

    def __init__(self, host, target, show_url=True, profiles=None):
        """
        @param host: SatWebFrontend instance
        @param target: url to open
        """
        quick_widgets.QuickWidget.__init__(self, host, target, C.PROF_KEY_NONE)
        libervia_widget.LiberviaWidget.__init__(self, host)
        self._vpanel = VerticalPanel()
        self._vpanel.setSize('100%', '100%')
        self._url = dialog.ExtTextBox(enter_cb=self.onUrlClick)
        self._url.setText(target or "")
        self._url.setWidth('100%')
        if show_url:
            hpanel = HorizontalPanel()
            hpanel.add(self._url)
            btn = Button("Go", self.onUrlClick)
            hpanel.setCellWidth(self._url, "100%")
            hpanel.add(btn)
            self._vpanel.add(hpanel)
            self._vpanel.setCellHeight(hpanel, '20px')
        self._frame = Frame(target or "")
        self._frame.setSize('100%', '100%')
        DOM.setStyleAttribute(self._frame.getElement(), "position", "relative")
        self._vpanel.add(self._frame)
        self.setWidget(self._vpanel)

    def onUrlClick(self, sender):
        url = self._url.getText()
        scheme_end = url.find(':')
        scheme = "" if scheme_end == -1 else url[:scheme_end]
        if scheme not in C.WEB_PANEL_SCHEMES:
            url = "http://" + url
        self._frame.setUrl(url)


##  Menu

def hostReady(host):
    def onWebWidget():
        web_widget = host.displayWidget(WebWidget, C.WEB_PANEL_DEFAULT_URL)
        host.setSelected(web_widget)

    def gotMenus():
        host.menus.addMenu(C.MENU_GLOBAL, (D_(u"General"), D_(u"Web widget")), callback=onWebWidget)
    host.addListener('gotMenus', gotMenus)

host_listener.addListener(hostReady)
