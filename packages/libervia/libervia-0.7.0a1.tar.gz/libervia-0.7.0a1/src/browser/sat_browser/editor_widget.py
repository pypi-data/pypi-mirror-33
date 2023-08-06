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
from sat_browser import strings

from pyjamas.ui.HTML import HTML
from pyjamas.ui.SimplePanel import SimplePanel
from pyjamas.ui.TextArea import TextArea
from pyjamas.ui import KeyboardListener as keyb
from pyjamas.ui.FocusListener import FocusHandler
from pyjamas.ui.ClickListener import ClickHandler
from pyjamas.ui.MouseListener import MouseHandler
from pyjamas.Timer import Timer
from pyjamas import DOM

import html_tools


class MessageBox(TextArea):
    """A basic text area for entering messages"""

    def __init__(self, host):
        TextArea.__init__(self)
        self.host = host
        self.size = (0, 0)
        self.setStyleName('messageBox')
        self.addKeyboardListener(self)
        MouseHandler.__init__(self)
        self.addMouseListener(self)

    def onBrowserEvent(self, event):
        # XXX: woraroung a pyjamas bug: self.currentEvent is not set
        #     so the TextBox's cancelKey doens't work. This is a workaround
        #     FIXME: fix the bug upstream
        self.currentEvent = event
        TextArea.onBrowserEvent(self, event)

    def onKeyPress(self, sender, keycode, modifiers):
        _txt = self.getText()

        def history_cb(text):
            self.setText(text)
            Timer(5, lambda timer: self.setCursorPos(len(text)))

        if keycode == keyb.KEY_ENTER:
            if _txt:
                self.host.selected_widget.onTextEntered(_txt)
                self.host._updateInputHistory(_txt) # FIXME: why using a global variable ?
            self.setText('')
            sender.cancelKey()
        elif keycode == keyb.KEY_UP:
            self.host._updateInputHistory(_txt, -1, history_cb)
        elif keycode == keyb.KEY_DOWN:
            self.host._updateInputHistory(_txt, +1, history_cb)
        else:
            self._onComposing()

    def _onComposing(self):
        """Callback when the user is composing a text."""
        self.host.selected_widget.chat_state_machine._onEvent("composing")

    def onMouseUp(self, sender, x, y):
        size = (self.getOffsetWidth(), self.getOffsetHeight())
        if size != self.size:
            self.size = size
            self.host.resize()

    def onSelectedChange(self, selected):
        self._selected_cache = selected


class BaseTextEditor(object):
    """Basic definition of a text editor. The method edit gets a boolean parameter which
    should be set to True when you want to edit the text and False to only display it."""

    def __init__(self, content=None, strproc=None, modifiedCb=None, afterEditCb=None):
        """
        Remark when inheriting this class: since the setContent method could be
        overwritten by the child class, you should consider calling this __init__
        after all the parameters affecting this setContent method have been set.
        @param content: dict with at least a 'text' key
        @param strproc: method to be applied on strings to clean the content
        @param modifiedCb: method to be called when the text has been modified.
            This method can return:
                - True: the modification will be saved and afterEditCb called;
                - False: the modification won't be saved and afterEditCb called;
                - None: the modification won't be saved and afterEditCb not called.
        @param afterEditCb: method to be called when the edition is done
        """
        if content is None:
            content = {'text': ''}
        assert 'text' in content
        if strproc is None:
            def strproc(text):
                try:
                    return text.strip()
                except (TypeError, AttributeError):
                    return text
        self.strproc = strproc
        self._modifiedCb = modifiedCb
        self._afterEditCb = afterEditCb
        self.initialized = False
        self.edit_listeners = []
        self.setContent(content)

    def setContent(self, content=None):
        """Set the editable content.
        The displayed content, which is set from the child class, could differ.

        @param content (dict): content data, need at least a 'text' key
        """
        if content is None:
            content = {'text': ''}
        elif not isinstance(content, dict):
            content = {'text': content}
        assert 'text' in content
        self._original_content = {}
        for key in content:
            self._original_content[key] = self.strproc(content[key])

    def getContent(self):
        """Get the current edited or editable content.
        @return: dict with at least a 'text' key
        """
        raise NotImplementedError

    def setOriginalContent(self, content):
        """Use this method with care! Content initialization should normally be
        done with self.setContent. This method exists to let you trick the editor,
        e.g. for self.modified to return True also when nothing has been modified.
        @param content: dict
        """
        self._original_content = content

    def getOriginalContent(self):
        """
        @return (dict): the original content before modification (i.e. content given in __init__)
        """
        return self._original_content

    def modified(self, content=None):
        """Check if the content has been modified.
        Remark: we don't use the direct comparison because we want to ignore empty elements
        @content: content to be check against the original content or None to use the current content
        @return: True if the content has been modified.
        """
        if content is None:
            content = self.getContent()
        # the following method returns True if one non empty element exists in a but not in b
        diff1 = lambda a, b: [a[key] for key in set(a.keys()).difference(b.keys()) if a[key]] != []
        # the following method returns True if the values for the common keys are not equals
        diff2 = lambda a, b: [1 for key in set(a.keys()).intersection(b.keys()) if a[key] != b[key]] != []
        # finally the combination of both to return True if a difference is found
        diff = lambda a, b: diff1(a, b) or diff1(b, a) or diff2(a, b)

        return diff(content, self._original_content)

    def edit(self, edit, abort=False):
        """
        Remark: the editor must be visible before you call this method.
        @param edit: set to True to edit the content or False to only display it
        @param abort: set to True to cancel the edition and loose the changes.
        If edit and abort are both True, self.abortEdition can be used to ask for a
        confirmation. When edit is False and abort is True, abortion is actually done.
        """
        if edit:
            self.setFocus(True)
            if abort:
                content = self.getContent()
                if not self.modified(content) or self.abortEdition(content):  # e.g: ask for confirmation
                    self.edit(False, True)
                    return
        else:
            if not self.initialized:
                return
            content = self.getContent()
            if abort:
                self._afterEditCb(content)
                return
            if self._modifiedCb and self.modified(content):
                result = self._modifiedCb(content)  # e.g.: send a message or update something
                if result is not None:
                    if self._afterEditCb:
                        self._afterEditCb(content)  # e.g.: restore the display mode
                    if result is True:
                        self.setContent(content)
            elif self._afterEditCb:
                self._afterEditCb(content)

        self.initialized = True

    def setFocus(self, focus):
        """
        @param focus: set to True to focus the editor
        """
        raise NotImplementedError

    def abortEdition(self, content):
        return True

    def addEditListener(self, listener):
        """Add a method to be called whenever the text is edited.
        @param listener: method taking two arguments: sender, keycode"""
        self.edit_listeners.append(listener)


class SimpleTextEditor(BaseTextEditor, FocusHandler, keyb.KeyboardHandler, ClickHandler):
    """Base class for manage a simple text editor."""

    CONVERT_NEW_LINES = True
    VALIDATE_WITH_SHIFT_ENTER = True

    def __init__(self, content=None, modifiedCb=None, afterEditCb=None, options=None):
        """
        @param content
        @param modifiedCb
        @param afterEditCb
        @param options (dict): can have the following value:
            - no_xhtml: set to True to clean any xhtml content.
            - enhance_display: if True, the display text will be enhanced with strings.addURLToText
            - listen_keyboard: set to True to terminate the edition with <enter> or <escape>.
            - listen_focus: set to True to terminate the edition when the focus is lost.
            - listen_click: set to True to start the edition when you click on the widget.
        """
        self.options = {'no_xhtml': False,
                        'enhance_display': True,
                        'listen_keyboard': True,
                        'listen_focus': False,
                        'listen_click': False
                        }
        if options:
            self.options.update(options)
        if self.options['listen_focus']:
            FocusHandler.__init__(self)
        if self.options['listen_click']:
            ClickHandler.__init__(self)
        keyb.KeyboardHandler.__init__(self)
        strproc = lambda text: html_tools.html_sanitize(html_tools.html_strip(text)) if self.options['no_xhtml'] else html_tools.html_strip(text)
        BaseTextEditor.__init__(self, content, strproc, modifiedCb, afterEditCb)
        self.textarea = self.display = None

    def setContent(self, content=None):
        BaseTextEditor.setContent(self, content)

    def getContent(self):
        raise NotImplementedError

    def edit(self, edit, abort=False):
        BaseTextEditor.edit(self, edit)
        if edit:
            if self.options['listen_focus'] and self not in self.textarea._focusListeners:
                self.textarea.addFocusListener(self)
            if self.options['listen_click']:
                self.display.clearClickListener()
            if self not in self.textarea._keyboardListeners:
                self.textarea.addKeyboardListener(self)
        else:
            self.setDisplayContent()
            if self.options['listen_focus']:
                try:
                    self.textarea.removeFocusListener(self)
                except ValueError:
                    pass
            if self.options['listen_click'] and self not in self.display._clickListeners:
                self.display.addClickListener(self)
            try:
                self.textarea.removeKeyboardListener(self)
            except ValueError:
                pass

    def setDisplayContent(self):
        text = self._original_content['text']
        if not self.options['no_xhtml']:
            text = strings.addURLToImage(text)
        if self.options['enhance_display']:
            text = strings.addURLToText(text)
        if self.CONVERT_NEW_LINES:
            text = html_tools.convertNewLinesToXHTML(text)
        text = strings.fixXHTMLLinks(text)
        self.display.setHTML(text)

    def setFocus(self, focus):
        raise NotImplementedError

    def onKeyDown(self, sender, keycode, modifiers):
        for listener in self.edit_listeners:
            listener(self.textarea, keycode, modifiers) # FIXME: edit_listeners must either be removed, or send an action instead of keycode/modifiers
        if not self.options['listen_keyboard']:
            return
        if keycode == keyb.KEY_ENTER and (not self.VALIDATE_WITH_SHIFT_ENTER or modifiers & keyb.MODIFIER_SHIFT):
            self.textarea.setFocus(False)
            if not self.options['listen_focus']:
                self.edit(False)

    def onLostFocus(self, sender):
        """Finish the edition when focus is lost"""
        if self.options['listen_focus']:
            self.edit(False)

    def onClick(self, sender=None):
        """Start the edition when the widget is clicked"""
        if self.options['listen_click']:
            self.edit(True)

    def onBrowserEvent(self, event):
        if self.options['listen_focus']:
            FocusHandler.onBrowserEvent(self, event)
        if self.options['listen_click']:
            ClickHandler.onBrowserEvent(self, event)
        keyb.KeyboardHandler.onBrowserEvent(self, event)


class HTMLTextEditor(SimpleTextEditor, HTML, FocusHandler, keyb.KeyboardHandler):
    """Manage a simple text editor with the HTML 5 "contenteditable" property."""

    CONVERT_NEW_LINES = False  # overwrite definition in SimpleTextEditor

    def __init__(self, content=None, modifiedCb=None, afterEditCb=None, options=None):
        HTML.__init__(self)
        SimpleTextEditor.__init__(self, content, modifiedCb, afterEditCb, options)
        self.textarea = self.display = self

    def getContent(self):
        text = DOM.getInnerHTML(self.getElement())
        return {'text': self.strproc(text) if text else ''}

    def edit(self, edit, abort=False):
        if edit:
            self.textarea.setHTML(self._original_content['text'])
        self.getElement().setAttribute('contenteditable', 'true' if edit else 'false')
        SimpleTextEditor.edit(self, edit, abort)

    def setFocus(self, focus):
        if focus:
            self.getElement().focus()
        else:
            self.getElement().blur()


class LightTextEditor(SimpleTextEditor, SimplePanel, FocusHandler, keyb.KeyboardHandler):
    """Manage a simple text editor with a TextArea for editing, HTML for display."""

    def __init__(self, content=None, modifiedCb=None, afterEditCb=None, options=None):
        SimplePanel.__init__(self)
        SimpleTextEditor.__init__(self, content, modifiedCb, afterEditCb, options)
        self.textarea = TextArea()
        self.display = HTML()

    def getContent(self):
        text = self.textarea.getText()
        return {'text': self.strproc(text) if text else ''}

    def edit(self, edit, abort=False):
        if edit:
            self.textarea.setText(self._original_content['text'])
        self.setWidget(self.textarea if edit else self.display)
        SimpleTextEditor.edit(self, edit, abort)

    def setFocus(self, focus):
        if focus and self.isAttached():
            self.textarea.setCursorPos(len(self.textarea.getText()))
        self.textarea.setFocus(focus)
