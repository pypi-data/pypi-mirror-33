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
from sat_frontends.tools import xmlui
from sat_browser import strings
from sat_frontends.tools import jid
from sat_browser.constants import Const as C
from sat_browser import dialog
from sat_browser import html_tools
from sat_browser import contact_panel

from pyjamas.ui.VerticalPanel import VerticalPanel
from pyjamas.ui.HorizontalPanel import HorizontalPanel
from pyjamas.ui.TabPanel import TabPanel
from pyjamas.ui.Grid import Grid
from pyjamas.ui.Label import Label
from pyjamas.ui.TextBox import TextBox
from pyjamas.ui.PasswordTextBox import PasswordTextBox
from pyjamas.ui.TextArea import TextArea
from pyjamas.ui.CheckBox import CheckBox
from pyjamas.ui.ListBox import ListBox
from pyjamas.ui.Button import Button
from pyjamas.ui.HTML import HTML

import nativedom


class EmptyWidget(xmlui.EmptyWidget, Label):

    def __init__(self, xmlui_main, xmlui_parent):
        Label.__init__(self, '')


class TextWidget(xmlui.TextWidget, Label):

    def __init__(self, xmlui_main, xmlui_parent, value):
        Label.__init__(self, value)


class LabelWidget(xmlui.LabelWidget, TextWidget):

    def __init__(self, xmlui_main, xmlui_parent, value):
        TextWidget.__init__(self, xmlui_main, xmlui_parent, value + ": ")


class JidWidget(xmlui.JidWidget, TextWidget):

    def __init__(self, xmlui_main, xmlui_parent, value):
        TextWidget.__init__(self, xmlui_main, xmlui_parent, value)


class DividerWidget(xmlui.DividerWidget, HTML):

    def __init__(self, xmlui_main, xmlui_parent, style='line'):
        """Add a divider

        @param xmlui_parent
        @param style (unicode): one of:
            - line: a simple line
            - dot: a line of dots
            - dash: a line of dashes
            - plain: a full thick line
            - blank: a blank line/space
        """
        HTML.__init__(self, "<hr/>")
        self.addStyleName(style)


class StringWidget(xmlui.StringWidget, TextBox):

    def __init__(self, xmlui_main, xmlui_parent, value, read_only=False):
        TextBox.__init__(self)
        self.setText(value)
        self.setReadonly(read_only)

    def _xmluiSetValue(self, value):
        self.setText(value)

    def _xmluiGetValue(self):
        return self.getText()

    def _xmluiOnChange(self, callback):
        self.addChangeListener(callback)


class JidInputWidget(xmlui.JidInputWidget, StringWidget):

    def __init__(self, xmlui_main, xmlui_parent, value, read_only=False):
        StringWidget.__init__(self, xmlui_main, xmlui_parent, value, read_only)


class PasswordWidget(xmlui.PasswordWidget, PasswordTextBox):

    def __init__(self, xmlui_main, xmlui_parent, value, read_only=False):
        PasswordTextBox.__init__(self)
        self.setText(value)
        self.setReadonly(read_only)

    def _xmluiSetValue(self, value):
        self.setText(value)

    def _xmluiGetValue(self):
        return self.getText()

    def _xmluiOnChange(self, callback):
        self.addChangeListener(callback)


class TextBoxWidget(xmlui.TextBoxWidget, TextArea):

    def __init__(self, xmlui_main, xmlui_parent, value, read_only=False):
        TextArea.__init__(self)
        self.setText(value)
        self.setReadonly(read_only)

    def _xmluiSetValue(self, value):
        self.setText(value)

    def _xmluiGetValue(self):
        return self.getText()

    def _xmluiOnChange(self, callback):
        self.addChangeListener(callback)


class BoolWidget(xmlui.BoolWidget, CheckBox):

    def __init__(self, xmlui_main, xmlui_parent, state, read_only=False):
        CheckBox.__init__(self)
        self.setChecked(state)
        self.setReadonly(read_only)

    def _xmluiSetValue(self, value):
        self.setChecked(value == "true")

    def _xmluiGetValue(self):
        return "true" if self.isChecked() else "false"

    def _xmluiOnChange(self, callback):
        self.addClickListener(callback)


class IntWidget(xmlui.IntWidget, TextBox):

    def __init__(self, xmlui_main, xmlui_parent, value, read_only=False):
        TextBox.__init__(self)
        self.setText(value)
        self.setReadonly(read_only)

    def _xmluiSetValue(self, value):
        self.setText(value)

    def _xmluiGetValue(self):
        return self.getText()

    def _xmluiOnChange(self, callback):
        self.addChangeListener(callback)


class ButtonWidget(xmlui.ButtonWidget, Button):

    def __init__(self, xmlui_main, xmlui_parent, value, click_callback):
        Button.__init__(self, value, click_callback)

    def _xmluiOnClick(self, callback):
        self.addClickListener(callback)


class ListWidget(xmlui.ListWidget, ListBox):

    def __init__(self, xmlui_main, xmlui_parent, options, selected, flags):
        ListBox.__init__(self)
        multi_selection = 'single' not in flags
        self.setMultipleSelect(multi_selection)
        if multi_selection:
            self.setVisibleItemCount(5)
        for option in options:
            self.addItem(option[1])
        self._xmlui_attr_map = {label: value for value, label in options}
        self._xmluiSelectValues(selected)

    def _xmluiSelectValue(self, value):
        """Select a value checking its item"""
        try:
            label = [label for label, _value in self._xmlui_attr_map.items() if _value == value][0]
        except IndexError:
            log.warning(u"Can't find value [%s] to select" % value)
            return
        self.selectItem(label)

    def _xmluiSelectValues(self, values):
        """Select multiple values, ignore the items"""
        self.setValueSelection(values)

    def _xmluiGetSelectedValues(self):
        ret = []
        for label in self.getSelectedItemText():
            ret.append(self._xmlui_attr_map[label])
        return ret

    def _xmluiOnChange(self, callback):
        self.addChangeListener(callback)

    def _xmluiAddValues(self, values, select=True):
        selected = self._xmluiGetSelectedValues()
        for value in values:
            if value not in self._xmlui_attr_map.values():
                self.addItem(value)
                self._xmlui_attr_map[value] = value
            if value not in selected:
                selected.append(value)
        self._xmluiSelectValues(selected)


class JidsListWidget(contact_panel.ContactsPanel, xmlui.JidsListWidget):

    def __init__(self, xmlui_main, xmlui_parent, jids, styles):
        contact_panel.ContactsPanel.__init__(self, xmlui_main.host, merge_resources=False)
        self.addStyleName("xmlui-JidsListWidget")
        self.setList([jid.JID(jid_) for jid_ in jids])

    def _xmluiGetSelectedValues(self):
        # XXX: there is not selection in this list, so we return all non empty values
        return self.getJids()



class LiberviaContainer(object):

    def _xmluiAppend(self, widget):
        self.append(widget)


class AdvancedListContainer(xmlui.AdvancedListContainer, Grid):

    def __init__(self, xmlui_main, xmlui_parent, columns, selectable='no'):
        Grid.__init__(self, 0, columns)
        self.columns = columns
        self.row = -1
        self.col = 0
        self._xmlui_rows_idx = []
        self._xmlui_selectable = selectable != 'no'
        self._xmlui_selected_row = None
        self.addTableListener(self)
        if self._xmlui_selectable:
            self.addStyleName('AdvancedListSelectable')

    def onCellClicked(self, grid, row, col):
        if not self._xmlui_selectable:
            return
        self._xmlui_selected_row = row
        try:
            self._xmlui_select_cb(self)
        except AttributeError:
            log.warning("no select callback set")

    def _xmluiAppend(self, widget):
        self.setWidget(self.row, self.col, widget)
        self.col += 1

    def _xmluiAddRow(self, idx):
        self.row += 1
        self.col = 0
        self._xmlui_rows_idx.insert(self.row, idx)
        self.resizeRows(self.row + 1)

    def _xmluiGetSelectedWidgets(self):
        return [self.getWidget(self._xmlui_selected_row, col) for col in range(self.columns)]

    def _xmluiGetSelectedIndex(self):
        try:
            return self._xmlui_rows_idx[self._xmlui_selected_row]
        except TypeError:
            return None

    def _xmluiOnSelect(self, callback):
        self._xmlui_select_cb = callback


class PairsContainer(xmlui.PairsContainer, Grid):

    def __init__(self, xmlui_main, xmlui_parent):
        Grid.__init__(self, 0, 0)
        self.row = 0
        self.col = 0

    def _xmluiAppend(self, widget):
        if self.col == 0:
            self.resize(self.row + 1, 2)
        self.setWidget(self.row, self.col, widget)
        self.col += 1
        if self.col == 2:
            self.row += 1
            self.col = 0


class LabelContainer(PairsContainer, xmlui.LabelContainer):
    pass


class TabsContainer(LiberviaContainer, xmlui.TabsContainer, TabPanel):

    def __init__(self, xmlui_main, xmlui_parent):
        TabPanel.__init__(self)
        self.setStyleName('liberviaTabPanel')

    def _xmluiAddTab(self, label, selected):
        tab_panel = VerticalContainer(self)
        self.add(tab_panel, label)
        count = len(self.getChildren())
        if count == 1 or selected:
            self.selectTab(count - 1)
        return tab_panel


class VerticalContainer(LiberviaContainer, xmlui.VerticalContainer, VerticalPanel):
    __bases__ = (LiberviaContainer, xmlui.VerticalContainer, VerticalPanel)

    def __init__(self, xmlui_main, xmlui_parent):
        VerticalPanel.__init__(self)


## Dialogs ##


class Dlg(object):

    def _xmluiShow(self):
        self.show()

    def _xmluiClose(self):
        pass


class MessageDialog(Dlg, xmlui.MessageDialog, dialog.InfoDialog):

    def __init__(self, xmlui_main, xmlui_parent, title, message, level):
        #TODO: level is not managed
        title = html_tools.html_sanitize(title)
        message = strings.addURLToText(html_tools.XHTML2Text(message))
        Dlg.__init__(self)
        xmlui.MessageDialog.__init__(self, xmlui_main, xmlui_parent)
        dialog.InfoDialog.__init__(self, title, message, self._xmluiValidated())


class NoteDialog(xmlui.NoteDialog, MessageDialog):
    # TODO: separate NoteDialog

    def __init__(self, xmlui_main, xmlui_parent, title, message, level):
        xmlui.NoteDialog.__init__(self, xmlui_main, xmlui_parent)
        MessageDialog.__init__(self, xmlui_main, xmlui_parent, title, message, level)


class ConfirmDialog(xmlui.ConfirmDialog, Dlg, dialog.ConfirmDialog):

    def __init__(self, xmlui_main, xmlui_parent, title, message, level):
        #TODO: level is not managed
        title = html_tools.html_sanitize(title)
        message = strings.addURLToText(html_tools.XHTML2Text(message))
        xmlui.ConfirmDialog.__init__(self, xmlui_main, xmlui_parent)
        Dlg.__init__(self)
        dialog.ConfirmDialog.__init__(self, self.answered, message, title)

    def answered(self, validated):
        if validated:
            self._xmluiValidated()
        else:
            self._xmluiCancelled()


class FileDialog(xmlui.FileDialog, Dlg):
    #TODO:

    def __init__(self, xmlui_main, xmlui_parent, title, message, level, filetype):
        raise NotImplementedError("FileDialog is not implemented in Libervia yet")


class GenericFactory(object):
    # XXX: __getattr__ doens't work here with pyjamas for an unknown reason
    #      so an introspection workaround is used

    def __init__(self, xmlui_main):
        self.xmlui_main = xmlui_main
        for name, cls in globals().items():
            if name.endswith("Widget") or name.endswith("Container") or name.endswith("Dialog"):
                log.info("registering: %s" % name)
                def createCreater(cls):
                    return lambda *args, **kwargs: self._genericCreate(cls, *args, **kwargs)
                setattr(self, "create%s" % name, createCreater(cls))

    def _genericCreate(self, cls, *args, **kwargs):
        instance = cls(self.xmlui_main, *args, **kwargs)
        return instance

    # def __getattr__(self, attr):
    #     if attr.startswith("create"):
    #         cls = globals()[attr[6:]]
    #         cls._xmlui_main = self._xmlui_main
    #         return cls


class WidgetFactory(GenericFactory):

    def _genericCreate(self, cls, *args, **kwargs):
        instance = GenericFactory._genericCreate(self, cls, *args, **kwargs)
        return instance

class LiberviaXMLUIBase(object):

    def _xmluiLaunchAction(self, action_id, data):
        self.host.launchAction(action_id, data, callback=self._defaultCb)


class XMLUIPanel(LiberviaXMLUIBase, xmlui.XMLUIPanel, VerticalPanel):

    def __init__(self, host, parsed_xml, title=None, flags=None, callback=None, ignore=None, whitelist=None, profile=C.PROF_KEY_NONE):
        self.widget_factory = WidgetFactory(self)
        self.host = host
        VerticalPanel.__init__(self)
        self.setSize('100%', '100%')
        xmlui.XMLUIPanel.__init__(self,
                                  host,
                                  parsed_xml,
                                  title = title,
                                  flags = flags,
                                  callback = callback,
                                  profile = profile)

    def setCloseCb(self, close_cb):
        self.close_cb = close_cb

    def _xmluiClose(self):
        if self.close_cb:
            self.close_cb()
        else:
            log.warning("no close method defined")

    def _xmluiSetParam(self, name, value, category):
        self.host.bridge.call('setParam', None, name, value, category)

    def constructUI(self, parsed_dom):
        super(XMLUIPanel, self).constructUI(parsed_dom)
        self.add(self.main_cont)
        self.setCellHeight(self.main_cont, '100%')
        if self.type == 'form':
            hpanel = HorizontalPanel()
            hpanel.setStyleName('marginAuto')
            hpanel.add(Button('Submit', self.onFormSubmitted))
            if not 'NO_CANCEL' in self.flags:
                hpanel.add(Button('Cancel', self.onFormCancelled))
            self.add(hpanel)
        elif self.type == 'param':
            assert(isinstance(self.children[0][0], TabPanel))
            hpanel = HorizontalPanel()
            hpanel.setStyleName('marginAuto')
            hpanel.add(Button('Save', self.onSaveParams))
            hpanel.add(Button('Cancel', lambda ignore: self._xmluiClose()))
            self.add(hpanel)

    def show(self):
        options = ['NO_CLOSE'] if self.type == C.XMLUI_FORM else []
        _dialog = dialog.GenericDialog(self.xmlui_title, self, options=options)
        self.setCloseCb(_dialog.close)
        _dialog.show()


class XMLUIDialog(LiberviaXMLUIBase, xmlui.XMLUIDialog):
    dialog_factory = GenericFactory()

    def __init__(self, host, parsed_dom, title=None, flags=None, callback=None, ignore=None, whitelist=None, profile=C.PROF_KEY_NONE):
        self.dialog_factory = GenericFactory(self)
        xmlui.XMLUIDialog.__init__(self,
                                   host,
                                   parsed_dom,
                                   title=title,
                                   flags=flags,
                                   callback=callback,
                                   ignore=ignore,
                                   profile=profile)
        self.host = host

xmlui.registerClass(xmlui.CLASS_PANEL, XMLUIPanel)
xmlui.registerClass(xmlui.CLASS_DIALOG, XMLUIDialog)

def create(*args, **kwargs):
    dom = nativedom.NativeDOM()
    kwargs['dom_parse'] = lambda xml_data: dom.parseString(xml_data)
    return xmlui.create(*args, **kwargs)
