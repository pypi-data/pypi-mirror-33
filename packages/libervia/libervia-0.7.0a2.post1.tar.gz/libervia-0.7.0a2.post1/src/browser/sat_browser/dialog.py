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

from constants import Const as C
from sat_frontends.tools import jid

from pyjamas.ui.VerticalPanel import VerticalPanel
from pyjamas.ui.Grid import Grid
from pyjamas.ui.HorizontalPanel import HorizontalPanel
from pyjamas.ui.PopupPanel import PopupPanel
from pyjamas.ui.DialogBox import DialogBox
from pyjamas.ui.ListBox import ListBox
from pyjamas.ui.Button import Button
from pyjamas.ui.TextBox import TextBox
from pyjamas.ui.Label import Label
from pyjamas.ui.HTML import HTML
from pyjamas.ui.RadioButton import RadioButton
from pyjamas.ui import HasAlignment
from pyjamas.ui.KeyboardListener import KEY_ESCAPE, KEY_ENTER
from pyjamas.ui.MouseListener import MouseWheelHandler
from pyjamas import Window

import base_panel


# List here the patterns that are not allowed in contact group names
FORBIDDEN_PATTERNS_IN_GROUP = ()


unicode = str # XXX: pyjama doesn't manage unicode


class RoomChooser(Grid):
    """Select a room from the rooms you already joined, or create a new one"""

    GENERATE_MUC = "<use random name>"

    def __init__(self, host, room_jid_s=None):
        """

        @param host (SatWebFrontend)
        @param room_jid_s (unicode): room JID
        """
        Grid.__init__(self, 2, 2, Width='100%')
        self.host = host

        self.new_radio = RadioButton("room", "Discussion room:")
        self.new_radio.setChecked(True)
        self.box = TextBox(Width='95%')
        self.box.setText(room_jid_s if room_jid_s else self.GENERATE_MUC)
        self.exist_radio = RadioButton("room", "Already joined:")
        self.rooms_list = ListBox(Width='95%')

        self.add(self.new_radio, 0, 0)
        self.add(self.box, 0, 1)
        self.add(self.exist_radio, 1, 0)
        self.add(self.rooms_list, 1, 1)

        self.box.addFocusListener(self)
        self.rooms_list.addFocusListener(self)

        self.exist_radio.setVisible(False)
        self.rooms_list.setVisible(False)
        self.refreshOptions()

    @property
    def room(self):
        """Get the room that has been selected or entered by the user

        @return: jid.JID or None to let the backend generate a new name
        """
        if self.exist_radio.getChecked():
            values = self.rooms_list.getSelectedValues()
            return jid.JID(values[0]) if values else None
        value = self.box.getText()
        return None if value in ('', self.GENERATE_MUC) else jid.JID(value)

    def onFocus(self, sender):
        if sender == self.rooms_list:
            self.exist_radio.setChecked(True)
        elif sender == self.box:
            if self.box.getText() == self.GENERATE_MUC:
                self.box.setText("")
            self.new_radio.setChecked(True)

    def onLostFocus(self, sender):
        if sender == self.box:
            if self.box.getText() == "":
                self.box.setText(self.GENERATE_MUC)

    def refreshOptions(self):
        """Refresh the already joined room list"""
        contact_list = self.host.contact_list
        muc_rooms = contact_list.getSpecials(C.CONTACT_SPECIAL_GROUP)
        for room in muc_rooms:
            self.rooms_list.addItem(room.bare)
        if len(muc_rooms) > 0:
            self.exist_radio.setVisible(True)
            self.rooms_list.setVisible(True)
            self.exist_radio.setChecked(True)


class ContactsChooser(VerticalPanel):
    """Select one or several connected contacts"""

    def __init__(self, host, nb_contact=None, ok_button=None):
        """
        @param host: SatWebFrontend instance
        @param nb_contact: number of contacts that have to be selected, None for no limit
        If a tuple is given instead of an integer, nb_contact[0] is the minimal and
        nb_contact[1] is the maximal number of contacts to be chosen.
        """
        self.host = host
        if isinstance(nb_contact, tuple):
            if len(nb_contact) == 0:
                nb_contact = None
            elif len(nb_contact) == 1:
                nb_contact = (nb_contact[0], nb_contact[0])
        elif nb_contact is not None:
            nb_contact = (nb_contact, nb_contact)
        if nb_contact is None:
            log.debug("Need to select as many contacts as you want")
        else:
            log.debug("Need to select between %d and %d contacts" % nb_contact)
        self.nb_contact = nb_contact
        self.ok_button = ok_button
        VerticalPanel.__init__(self, Width='100%')
        self.contacts_list = ListBox()
        self.contacts_list.setMultipleSelect(True)
        self.contacts_list.setWidth("95%")
        self.contacts_list.addStyleName('contactsChooser')
        self.contacts_list.addChangeListener(self.onChange)
        self.add(self.contacts_list)
        self.refreshOptions()
        self.onChange()

    @property
    def contacts(self):
        """Return the selected contacts.

        @return: list[jid.JID]
        """
        return [jid.JID(contact) for contact in self.contacts_list.getSelectedValues(True)]

    def onChange(self, sender=None):
        if self.ok_button is None:
            return
        if self.nb_contact:
            selected = len(self.contacts_list.getSelectedValues(True))
            if selected >= self.nb_contact[0] and selected <= self.nb_contact[1]:
                self.ok_button.setEnabled(True)
            else:
                self.ok_button.setEnabled(False)

    def refreshOptions(self, keep_selected=False):
        """Fill the list with the connected contacts.

        @param keep_selected (boolean): if True, keep the current selection
        """
        selection = self.contacts if keep_selected else []
        self.contacts_list.clear()
        contacts = self.host.contact_list.roster_connected
        self.contacts_list.setVisibleItemCount(10 if len(contacts) > 5 else 5)
        self.contacts_list.addItem("")
        for contact in contacts:
            self.contacts_list.addItem(contact)
        if selection:
            self.contacts_list.setItemTextSelection([unicode(contact) for contact in selection])


class RoomAndContactsChooser(DialogBox):
    """Select a room and some users to invite in"""

    def __init__(self, host, callback, nb_contact=None, ok_button="OK", title="Discussion groups",
                 title_room="Join room", title_invite="Invite contacts", visible=(True, True)):
        DialogBox.__init__(self, centered=True)
        self.host = host
        self.callback = callback
        self.title_room = title_room
        self.title_invite = title_invite

        button_panel = HorizontalPanel()
        button_panel.addStyleName("marginAuto")
        ok_button = Button("OK", self.onOK)
        button_panel.add(ok_button)
        button_panel.add(Button("Cancel", self.onCancel))

        self.room_panel = RoomChooser(host, None if visible == (False, True) else host.default_muc)
        self.contact_panel = ContactsChooser(host, nb_contact, ok_button)

        self.stack_panel = base_panel.ToggleStackPanel(Width="100%")
        self.stack_panel.add(self.room_panel, visible=visible[0])
        self.stack_panel.add(self.contact_panel, visible=visible[1])
        self.stack_panel.addStackChangeListener(self)
        self.onStackChanged(self.stack_panel, 0, visible[0])
        self.onStackChanged(self.stack_panel, 1, visible[1])

        main_panel = VerticalPanel()
        main_panel.setStyleName("room-contact-chooser")
        main_panel.add(self.stack_panel)
        main_panel.add(button_panel)

        self.setWidget(main_panel)
        self.setHTML(title)
        self.show()

        # FIXME: workaround for a pyjamas issue: calling hash on a class method always return a different value if that method is defined directly within the class (with the "def" keyword)
        self.presenceListener = self.refreshContactList
        # update the contacts list when someone logged in/out
        self.host.addListener('presence', self.presenceListener, [C.PROF_KEY_NONE])

    @property
    def room(self):
        """Get the room that has been selected or entered by the user

        @return: jid.JID or None
        """
        return self.room_panel.room

    @property
    def contacts(self):
        """Return the selected contacts.

        @return: list[jid.JID]
        """
        return self.contact_panel.contacts

    def onStackChanged(self, sender, index, visible=None):
        if visible is None:
            visible = sender.getWidget(index).getVisible()
        if index == 0:
            suffix = "" if (visible or not self.room) else ": %s" % self.room
            sender.setStackText(0, self.title_room + suffix)
        elif index == 1:
            suffix = "" if (visible or not self.contacts) else ": %s" % ", ".join([unicode(contact) for contact in self.contacts])
            sender.setStackText(1, self.title_invite + suffix)

    def refreshContactList(self, *args, **kwargs):
        """Called when someone log in/out to update the list.

        @param args: set by the event call but not used here
        """
        self.contact_panel.refreshOptions(keep_selected=True)

    def onOK(self, sender):
        room = self.room  # pyjamas issue: you need to use an intermediate variable to access a property's method
        self.hide()
        self.callback(room, self.contacts)

    def onCancel(self, sender):
        self.hide()

    def hide(self):
        self.host.removeListener('presence', self.presenceListener)
        DialogBox.hide(self, autoClosed=True)


class GenericConfirmDialog(DialogBox):

    def __init__(self, widgets, callback, title='Confirmation', prompt_widgets=None, **kwargs):
        """
        Dialog to confirm an action
        @param widgets (list[Widget]): widgets to attach
        @param callback (callable): method to call when a button is pressed,
            with the following arguments:
                - result (bool): set to True if the dialog has been confirmed
                - *args: a list of unicode (the values for the prompt_widgets)
        @param title: title of the dialog
        @param prompt_widgets (list[TextBox]): input widgets from which to retrieve
        the string value(s) to be passed to the callback when OK button is pressed.
        If None, OK button will return "True". Cancel button always returns "False".
        """
        self.callback = callback
        added_style = kwargs.pop('AddStyleName', None)
        DialogBox.__init__(self, centered=True, **kwargs)
        if added_style:
            self.addStyleName(added_style)

        if prompt_widgets is None:
            prompt_widgets = []

        content = VerticalPanel()
        content.setWidth('100%')
        for wid in widgets:
            content.add(wid)
            if wid in prompt_widgets:
                wid.setWidth('100%')
        button_panel = HorizontalPanel()
        button_panel.addStyleName("marginAuto")
        self.confirm_button = Button("OK", self.onConfirm)
        button_panel.add(self.confirm_button)
        self.cancel_button = Button("Cancel", self.onCancel)
        button_panel.add(self.cancel_button)
        content.add(button_panel)
        self.setHTML(title)
        self.setWidget(content)
        self.prompt_widgets = prompt_widgets

    def onConfirm(self, sender):
        self.hide()
        result = [True]
        result.extend([box.getText() for box in self.prompt_widgets])
        self.callback(*result)

    def onCancel(self, sender):
        self.hide()
        self.callback(False)

    def show(self):
        DialogBox.show(self)
        if self.prompt_widgets:
            self.prompt_widgets[0].setFocus(True)


class ConfirmDialog(GenericConfirmDialog):

    def __init__(self, callback, text='Are you sure ?', title='Confirmation', **kwargs):
        GenericConfirmDialog.__init__(self, [HTML(text)], callback, title, **kwargs)


class GenericDialog(DialogBox):
    """Dialog which just show a widget and a close button"""

    def __init__(self, title, main_widget, callback=None, options=None, **kwargs):
        """Simple notice dialog box
        @param title: HTML put in the header
        @param main_widget: widget put in the body
        @param callback: method to call on closing
        @param options: one or more of the following options:
                        - NO_CLOSE: don't add a close button"""
        added_style = kwargs.pop('AddStyleName', None)
        DialogBox.__init__(self, centered=True, **kwargs)
        if added_style:
            self.addStyleName(added_style)

        self.callback = callback
        if not options:
            options = []
        _body = VerticalPanel()
        _body.setSize('100%', '100%')
        _body.setSpacing(4)
        _body.add(main_widget)
        _body.setCellWidth(main_widget, '100%')
        _body.setCellHeight(main_widget, '100%')
        if 'NO_CLOSE' not in options:
            _close_button = Button("Close", self.onClose)
            _body.add(_close_button)
            _body.setCellHorizontalAlignment(_close_button, HasAlignment.ALIGN_CENTER)
        self.setHTML(title)
        self.setWidget(_body)
        self.panel.setSize('100%', '100%')  # Need this hack to have correct size in Gecko & Webkit

    def close(self):
        """Same effect as clicking the close button"""
        self.onClose(None)

    def onClose(self, sender):
        self.hide()
        if self.callback:
            self.callback()


class InfoDialog(GenericDialog):

    def __init__(self, title, body, callback=None, options=None, **kwargs):
        GenericDialog.__init__(self, title, HTML(body), callback, options, **kwargs)


class PromptDialog(GenericConfirmDialog):

    def __init__(self, callback, textes=None, values=None, title='User input', **kwargs):
        """Prompt the user for one or more input(s).

        @param callback (callable): method to call when a button is pressed,
            with the following arguments:
                - result (bool): set to True if the dialog has been confirmed
                - *args: a list of unicode (the values entered by the user)
        @param textes (list[unicode]): HTML textes to display before the inputs
        @param values (list[unicode]): default values for each input
        @param title (unicode): dialog title
        """
        if textes is None:
            textes = ['']  # display a single input without any description
        if values is None:
            values = []
        all_widgets = []
        prompt_widgets = []
        for count in xrange(len(textes)):
            all_widgets.append(HTML(textes[count]))
            prompt = TextBox()
            if len(values) > count:
                prompt.setText(values[count])
            all_widgets.append(prompt)
            prompt_widgets.append(prompt)

        GenericConfirmDialog.__init__(self, all_widgets, callback, title, prompt_widgets, **kwargs)


class PopupPanelWrapper(PopupPanel):
    """This wrapper catch Escape event to avoid request cancellation by Firefox"""

    def onEventPreview(self, event):
        if event.type in ["keydown", "keypress", "keyup"] and event.keyCode == KEY_ESCAPE:
            # needed to prevent request cancellation in Firefox
            event.preventDefault()
        return PopupPanel.onEventPreview(self, event)


class ExtTextBox(TextBox):
    """Extended TextBox"""

    def __init__(self, *args, **kwargs):
        if 'enter_cb' in kwargs:
            self.enter_cb = kwargs['enter_cb']
            del kwargs['enter_cb']
        TextBox.__init__(self, *args, **kwargs)
        self.addKeyboardListener(self)

    def onKeyUp(self, sender, keycode, modifiers):
        pass

    def onKeyDown(self, sender, keycode, modifiers):
        pass

    def onKeyPress(self, sender, keycode, modifiers):
        if self.enter_cb and keycode == KEY_ENTER:
            self.enter_cb(self)


class GroupSelector(DialogBox):

    def __init__(self, top_widgets, initial_groups, selected_groups,
                 ok_title="OK", ok_cb=None, cancel_cb=None):
        DialogBox.__init__(self, centered=True)
        main_panel = VerticalPanel()
        self.ok_cb = ok_cb
        self.cancel_cb = cancel_cb

        for wid in top_widgets:
            main_panel.add(wid)

        main_panel.add(Label('Select in which groups your contact is:'))
        self.list_box = ListBox()
        self.list_box.setMultipleSelect(True)
        self.list_box.setVisibleItemCount(5)
        self.setAvailableGroups(initial_groups)
        self.setGroupsSelected(selected_groups)
        main_panel.add(self.list_box)

        def cb(text):
            self.list_box.addItem(text)
            self.list_box.setItemSelected(self.list_box.getItemCount() - 1, "selected")

        main_panel.add(AddGroupPanel(initial_groups, cb))

        button_panel = HorizontalPanel()
        button_panel.addStyleName("marginAuto")
        button_panel.add(Button(ok_title, self.onOK))
        button_panel.add(Button("Cancel", self.onCancel))
        main_panel.add(button_panel)

        self.setWidget(main_panel)

    def getSelectedGroups(self):
        """Return a list of selected groups"""
        return self.list_box.getSelectedValues()

    def setAvailableGroups(self, groups):
        _groups = list(set(groups))
        _groups.sort()
        self.list_box.clear()
        for group in _groups:
            self.list_box.addItem(group)

    def setGroupsSelected(self, selected_groups):
        self.list_box.setItemTextSelection(selected_groups)

    def onOK(self, sender):
        self.hide()
        if self.ok_cb:
            self.ok_cb(self)

    def onCancel(self, sender):
        self.hide()
        if self.cancel_cb:
            self.cancel_cb(self)


class AddGroupPanel(HorizontalPanel):
    def __init__(self, groups, cb=None):
        """
        @param groups: list of the already existing groups
        """
        HorizontalPanel.__init__(self)
        self.groups = groups
        self.add(Label('New group:'))
        self.textbox = ExtTextBox(enter_cb=self.onGroupInput)
        self.add(self.textbox)
        self.add(Button("Add", lambda sender: self.onGroupInput(self.textbox)))
        self.cb = cb

    def onGroupInput(self, sender):
        text = sender.getText()
        if text == "":
            return
        for group in self.groups:
            if text == group:
                Window.alert("The group '%s' already exists." % text)
                return
        for pattern in FORBIDDEN_PATTERNS_IN_GROUP:
            if pattern in text:
                Window.alert("The pattern '%s' is not allowed in group names." % pattern)
                return
        sender.setText('')
        self.groups.append(text)
        if self.cb is not None:
            self.cb(text)


class WheelTextBox(TextBox, MouseWheelHandler):

    def __init__(self, *args, **kwargs):
        TextBox.__init__(self, *args, **kwargs)
        MouseWheelHandler.__init__(self)


class IntSetter(HorizontalPanel):
    """This class show a bar with button to set an int value"""

    def __init__(self, label, value=0, value_max=None, visible_len=3):
        """initialize the intSetter
        @param label: text shown in front of the setter
        @param value: initial value
        @param value_max: limit value, None or 0 for unlimited"""
        HorizontalPanel.__init__(self)
        self.value = value
        self.value_max = value_max
        _label = Label(label)
        self.add(_label)
        self.setCellWidth(_label, "100%")
        minus_button = Button("-", self.onMinus)
        self.box = WheelTextBox()
        self.box.setVisibleLength(visible_len)
        self.box.setText(unicode(value))
        self.box.addInputListener(self)
        self.box.addMouseWheelListener(self)
        plus_button = Button("+", self.onPlus)
        self.add(minus_button)
        self.add(self.box)
        self.add(plus_button)
        self.valueChangedListener = []

    def addValueChangeListener(self, listener):
        self.valueChangedListener.append(listener)

    def removeValueChangeListener(self, listener):
        if listener in self.valueChangedListener:
            self.valueChangedListener.remove(listener)

    def _callListeners(self):
        for listener in self.valueChangedListener:
            listener(self.value)

    def setValue(self, value):
        """Change the value and fire valueChange listeners"""
        self.value = value
        self.box.setText(unicode(value))
        self._callListeners()

    def onMinus(self, sender, step=1):
        self.value = max(0, self.value - step)
        self.box.setText(unicode(self.value))
        self._callListeners()

    def onPlus(self, sender, step=1):
        self.value += step
        if self.value_max:
            self.value = min(self.value, self.value_max)
        self.box.setText(unicode(self.value))
        self._callListeners()

    def onInput(self, sender):
        """Accept only valid integer && normalize print (no leading 0)"""
        try:
            self.value = int(self.box.getText()) if self.box.getText() else 0
        except ValueError:
            pass
        if self.value_max:
            self.value = min(self.value, self.value_max)
        self.box.setText(unicode(self.value))
        self._callListeners()

    def onMouseWheel(self, sender, velocity):
        if velocity > 0:
            self.onMinus(sender, 10)
        else:
            self.onPlus(sender, 10)
