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

from sat_frontends.tools import xmltools

import nativedom
from __pyjamas__ import JS

dom = nativedom.NativeDOM()


def html_sanitize(html):
    """Naive sanitization of HTML"""
    return html.replace('<', '&lt;').replace('>', '&gt;')


def html_strip(html):
    """Strip leading/trailing white spaces, HTML line breaks and &nbsp; sequences."""
    JS("""return html.replace(/(^(<br\/?>|&nbsp;|\s)+)|((<br\/?>|&nbsp;|\s)+$)/g, "");""")

def inlineRoot(xhtml):
    """ make root element inline """
    doc = dom.parseString(xhtml)
    return xmltools.inlineRoot(doc)


def convertNewLinesToXHTML(text):
    """Replace all the \n with <br/>"""
    return text.replace('\n', '<br/>')


def XHTML2Text(xhtml):
    """Helper method to apply both html_sanitize and convertNewLinesToXHTML"""
    return convertNewLinesToXHTML(html_sanitize(xhtml))


def buildPresenceStyle(presence, base_style=None):
    """Return the CSS classname to be used for displaying the given presence information.

    @param presence (unicode): presence is a value in ('', 'chat', 'away', 'dnd', 'xa')
    @param base_style (unicode): base classname
    @return: unicode
    """
    if not base_style:
        base_style = "contactLabel"
    return '%s-%s' % (base_style, presence or 'connected')


def setPresenceStyle(widget, presence, base_style=None):
    """
    Set the CSS style of a contact's element according to its presence.

    @param widget (Widget): the UI element of the contact
    @param presence (unicode): a value in ("", "chat", "away", "dnd", "xa").
    @param base_style (unicode): the base name of the style to apply
    """
    if not hasattr(widget, 'presence_style'):
        widget.presence_style = None
    style = buildPresenceStyle(presence, base_style)
    if style == widget.presence_style:
        return
    if widget.presence_style is not None:
        widget.removeStyleName(widget.presence_style)
    widget.addStyleName(style)
    widget.presence_style = style
