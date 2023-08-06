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

from sat_frontends.tools import composition
from sat.core.i18n import _
from sat.core.log import getLogger
log = getLogger(__name__)
from sat.tools.common import data_format

from pyjamas.ui.TextArea import TextArea
from pyjamas.ui.Button import Button
from pyjamas.ui.CheckBox import CheckBox
from pyjamas.ui.Label import Label
from pyjamas.ui.FlexTable import FlexTable
from pyjamas.ui.HorizontalPanel import HorizontalPanel
from pyjamas.ui.KeyboardListener import KeyboardHandler
from pyjamas import Window
from __pyjamas__ import doc

from constants import Const as C
import dialog
import base_panel
import editor_widget
import html_tools
import list_manager


class RichTextEditor(editor_widget.BaseTextEditor, FlexTable):
    """Panel for the rich text editor."""

    STYLE = {'main': 'richTextEditor',
             'title': 'richTextTitle',
             'toolbar': 'richTextToolbar',
             'textarea': 'richTextArea'
             }

    def __init__(self, host, content=None, modifiedCb=None, afterEditCb=None, options=None):
        """

        @param host (SatWebFrontend): host instance
        @param content (dict): dict with at least a 'text' key
        @param modifiedCb (callable): to be called when the text has been modified
        @param afterEditCb (callable): to be called when the edition is done
        @param options (list[unicode]): UI options ("read_only", "update_msg")
        """
        FlexTable.__init__(self) # FIXME
        self.host = host
        self.wysiwyg = False
        self.read_only = 'read_only' in options
        self.update_msg = 'update_msg' in options

        indices = (-1, -1, 0, -1, -1) if self.read_only else (0, 1, 2, 3, 4)
        self.title_offset, self.toolbar_offset, self.content_offset, self.tags_offset, self.command_offset = indices
        self.addStyleName(self.STYLE['main'])

        editor_widget.BaseTextEditor.__init__(self, content, None, modifiedCb, afterEditCb)

    def addEditListener(self, listener):
        """Add a method to be called whenever the text is edited.

        @param listener: method taking two arguments: sender, keycode
        """
        editor_widget.BaseTextEditor.addEditListener(self, listener)
        if hasattr(self, 'display'):
            self.display.addEditListener(listener)

    def refresh(self, edit=None):
        """Refresh the UI for edition/display mode.

        @param edit: set to True to display the edition mode
        """
        if edit is None:
            edit = hasattr(self, 'textarea') and self.textarea.getVisible()

        for widget in ['title_panel', 'tags_panel', 'command']:
            if hasattr(self, widget):
                getattr(self, widget).setVisible(edit)

        if hasattr(self, 'toolbar'):
            self.toolbar.setVisible(False)

        if not hasattr(self, 'display'):
            self.display = editor_widget.HTMLTextEditor(options={'enhance_display': False, 'listen_keyboard': False})  # for display mode
            for listener in self.edit_listeners:
                self.display.addEditListener(listener)

        if not self.read_only and not hasattr(self, 'textarea'):
            self.textarea = EditTextArea(self)  # for edition mode
            self.textarea.addStyleName(self.STYLE['textarea'])

        self.getFlexCellFormatter().setColSpan(self.content_offset, 0, 2)
        if edit and not self.wysiwyg:
            self.textarea.setWidth('100%')  # CSS width doesn't do it, don't know why
            self.setWidget(self.content_offset, 0, self.textarea)
        else:
            self.setWidget(self.content_offset, 0, self.display)
        if not edit:
            return

        if not self.read_only and not hasattr(self, 'title_panel'):
            self.title_panel = base_panel.TitlePanel()
            self.title_panel.addStyleName(self.STYLE['title'])
            self.getFlexCellFormatter().setColSpan(self.title_offset, 0, 2)
            self.setWidget(self.title_offset, 0, self.title_panel)

        if not self.read_only and not hasattr(self, 'tags_panel'):
            suggested_tags = []  # TODO: feed this list with tags suggestion
            self.tags_panel = list_manager.TagsPanel(suggested_tags)
            self.getFlexCellFormatter().setColSpan(self.tags_offset, 0, 2)
            self.setWidget(self.tags_offset, 0, self.tags_panel)

        if not self.read_only and not hasattr(self, 'command'):
            self.command = HorizontalPanel()
            self.command.addStyleName("marginAuto")
            self.command.add(Button("Cancel", lambda: self.edit(True, True)))
            self.command.add(Button("Update" if self.update_msg else "Send message", lambda: self.edit(False)))
            self.getFlexCellFormatter().setColSpan(self.command_offset, 0, 2)
            self.setWidget(self.command_offset, 0, self.command)

    def setToolBar(self, syntax):
        """This method is called asynchronously after the parameter
        holding the rich text syntax is retrieved. It is called at
        each call of self.edit(True) because the user may
        have change his setting since the last time."""
        if syntax is None or syntax not in composition.RICH_SYNTAXES.keys():
            syntax = composition.RICH_SYNTAXES.keys()[0]
        if hasattr(self, "toolbar") and self.toolbar.syntax == syntax:
            self.toolbar.setVisible(True)
            return
        self.toolbar = HorizontalPanel()
        self.toolbar.syntax = syntax
        self.toolbar.addStyleName(self.STYLE['toolbar'])
        for key in composition.RICH_SYNTAXES[syntax].keys():
            self.addToolbarButton(syntax, key)
        self.wysiwyg_button = CheckBox(_('preview'))
        wysiywgCb = lambda sender: self.setWysiwyg(sender.getChecked())
        self.wysiwyg_button.addClickListener(wysiywgCb)
        self.toolbar.add(self.wysiwyg_button)
        self.syntax_label = Label(_("Syntax: %s") % syntax)
        self.syntax_label.addStyleName("richTextSyntaxLabel")
        self.toolbar.add(self.syntax_label)
        self.toolbar.setCellWidth(self.syntax_label, "100%")
        self.getFlexCellFormatter().setColSpan(self.toolbar_offset, 0, 2)
        self.setWidget(self.toolbar_offset, 0, self.toolbar)

    def setWysiwyg(self, wysiwyg, init=False):
        """Toggle the edition mode between rich content syntax and wysiwyg.
        @param wysiwyg: boolean value
        @param init: set to True to re-init without switching the widgets."""
        def setWysiwyg():
            self.wysiwyg = wysiwyg
            try:
                self.wysiwyg_button.setChecked(wysiwyg)
            except (AttributeError, TypeError):
                pass
            try:
                if wysiwyg:
                    self.syntax_label.addStyleName('transparent')
                else:
                    self.syntax_label.removeStyleName('transparent')
            except (AttributeError, TypeError):
                pass
            if not wysiwyg:
                self.display.removeStyleName('richTextWysiwyg')

        if init:
            setWysiwyg()
            return

        self.getFlexCellFormatter().setColSpan(self.content_offset, 0, 2)
        if wysiwyg:
            def syntaxConvertCb(text):
                self.display.setContent({'text': text})
                self.textarea.removeFromParent()  # XXX: force as it is not always done...
                self.setWidget(self.content_offset, 0, self.display)
                self.display.addStyleName('richTextWysiwyg')
                self.display.edit(True)
            content = self.getContent()
            if content['text'] and content['syntax'] != C.SYNTAX_XHTML:
                self.host.bridge.call('syntaxConvert', syntaxConvertCb, content['text'], content['syntax'], C.SYNTAX_XHTML)
            else:
                syntaxConvertCb(content['text'])
        else:
            syntaxConvertCb = lambda text: self.textarea.setText(text)
            text = self.display.getContent()['text']
            if text and self.toolbar.syntax != C.SYNTAX_XHTML:
                self.host.bridge.call('syntaxConvert', syntaxConvertCb, text)
            else:
                syntaxConvertCb(text)
            self.setWidget(self.content_offset, 0, self.textarea)
            self.textarea.setWidth('100%')  # CSS width doesn't do it, don't know why

        setWysiwyg()  # do it in the end because it affects self.getContent

    def addToolbarButton(self, syntax, key):
        """Add a button with the defined parameters."""
        button = Button('<img src="%s" class="richTextIcon" />' %
                        composition.RICH_BUTTONS[key]["icon"])
        button.setTitle(composition.RICH_BUTTONS[key]["tip"])
        button.addStyleName('richTextToolButton')
        self.toolbar.add(button)

        def buttonCb():
            """Generic callback for a toolbar button."""
            text = self.textarea.getText()
            cursor_pos = self.textarea.getCursorPos()
            selection_length = self.textarea.getSelectionLength()
            data = composition.RICH_SYNTAXES[syntax][key]
            if selection_length == 0:
                middle_text = data[1]
            else:
                middle_text = text[cursor_pos:cursor_pos + selection_length]
            self.textarea.setText(text[:cursor_pos]
                                  + data[0]
                                  + middle_text
                                  + data[2]
                                  + text[cursor_pos + selection_length:])
            self.textarea.setCursorPos(cursor_pos + len(data[0]) + len(middle_text))
            self.textarea.setFocus(True)
            self.textarea.onKeyDown()

        def wysiwygCb():
            """Callback for a toolbar button while wysiwyg mode is enabled."""
            data = composition.COMMANDS[key]

            def execCommand(command, arg):
                self.display.setFocus(True)
                doc().execCommand(command, False, arg.strip() if arg else '')
            # use Window.prompt instead of dialog.PromptDialog to not loose the focus
            prompt = lambda command, text: execCommand(command, Window.prompt(text))
            if isinstance(data, tuple) or isinstance(data, list):
                if data[1]:
                    prompt(data[0], data[1])
                else:
                    execCommand(data[0], data[2])
            else:
                execCommand(data, False, '')
            self.textarea.onKeyDown()

        button.addClickListener(lambda: wysiwygCb() if self.wysiwyg else buttonCb())

    def getContent(self):
        assert(hasattr(self, 'textarea'))
        assert(hasattr(self, 'toolbar'))
        if self.wysiwyg:
            content = {'text': self.display.getContent()['text'], 'syntax': C.SYNTAX_XHTML}
        else:
            content = {'text': self.strproc(self.textarea.getText()), 'syntax': self.toolbar.syntax}
        if hasattr(self, 'title_panel'):
            content.update({'title': self.strproc(self.title_panel.getText())})
        if hasattr(self, 'tags_panel'):
            data_format.iter2dict('tag', self.tags_panel.getTags(), content)
        return content

    def edit(self, edit=False, abort=False, sync=False):
        """
        Remark: the editor must be visible before you call this method.
        @param edit: set to True to edit the content or False to only display it
        @param abort: set to True to cancel the edition and loose the changes.
        If edit and abort are both True, self.abortEdition can be used to ask for a
        confirmation. When edit is False and abort is True, abortion is actually done.
        @param sync: set to True to cancel the edition after the content has been saved somewhere else
        """
        if not (edit and abort):
            self.refresh(edit)  # not when we are asking for a confirmation
        editor_widget.BaseTextEditor.edit(self, edit, abort, sync)  # after the UI has been refreshed
        if (edit and abort):
            return  # self.abortEdition is called by editor_widget.BaseTextEditor.edit
        self.setWysiwyg(False, init=True)  # after editor_widget.BaseTextEditor (it affects self.getContent)
        if sync:
            return
        # the following must NOT be done at each UI refresh!
        content = self._original_content
        if edit:
            def getParamCb(syntax):
                # set the editable text in the current user-selected syntax
                def syntaxConvertCb(text=None):
                    if text is not None:
                        # Important: this also update self._original_content
                        content.update({'text': text})
                    content.update({'syntax': syntax})
                    self.textarea.setText(content['text'])

                    if hasattr(self, 'title_panel') and 'title' in content:
                        self.title_panel.setText(content['title'])
                        self.title_panel.setStackVisible(0, content['title'] != '')

                    if hasattr(self, 'tags_panel'):
                        tags = list(data_format.dict2iter('tag', content))
                        self.tags_panel.setTags(tags)
                        self.tags_panel.setStackVisible(0, len(tags) > 0)

                    self.setToolBar(syntax)
                if content['text'] and content['syntax'] != syntax:
                    self.host.bridge.call('syntaxConvert', syntaxConvertCb, content['text'], content['syntax'])
                else:
                    syntaxConvertCb()
            self.host.bridge.call('asyncGetParamA', getParamCb, composition.PARAM_NAME_SYNTAX, composition.PARAM_KEY_COMPOSITION)
        else:
            if not self.initialized:
                # set the display text in XHTML only during init because a new MicroblogEntry instance is created after each modification
                self.setDisplayContent()
            self.display.edit(False)

    def setDisplayContent(self):
        """Set the content of the editor_widget.HTMLTextEditor which is used for display/wysiwyg"""
        content = self._original_content
        text = content['text']
        if 'title' in content and content['title']:
            title = '<h2>%s</h2>' % html_tools.html_sanitize(content['title'])
        else:
            title = ""

        tags = ""
        for tag in data_format.dict2iter('tag', content):
            tags += "<li><a>%s</a></li>" % html_tools.html_sanitize(tag)
        if tags:
            tags = '<ul class="mblog_tags">%s</ul>' % tags

        self.display.setContent({'text': "%s%s%s" % (title, tags, text)})

    def setFocus(self, focus):
        self.textarea.setFocus(focus)

    def abortEdition(self, content):
        """Ask for confirmation before closing the dialog."""
        def confirm_cb(answer):
            if answer:
                self.edit(False, True)
        _dialog = dialog.ConfirmDialog(confirm_cb, text="Do you really want to %s?" % ("cancel your changes" if self.update_msg else "cancel this message"))
        _dialog.cancel_button.setText(_("No"))
        _dialog.show()


class EditTextArea(TextArea, KeyboardHandler):
    def __init__(self, _parent):
        TextArea.__init__(self)
        self._parent = _parent
        KeyboardHandler.__init__(self)
        self.addKeyboardListener(self)

    def onKeyDown(self, sender=None, keycode=None, modifiers=None):
        for listener in self._parent.edit_listeners:
            listener(self, keycode, modifiers) # FIXME: edit_listeners must either be removed, or send an action instead of keycode/modifiers
