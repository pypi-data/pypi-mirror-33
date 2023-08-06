#!/usr/bin/python
# -*- coding: utf-8 -*-

# Libervia: a Salut à Toi frontend
# Copyright (C) 2011-2018 Jérôme Poisson <goffi@goffi.org>
# Copyright (C) 2011, 2012  Adrien Vigneron <adrienvigneron@mailoo.org>

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

#This page manage subscription and new account creation

import pyjd  # this is dummy in pyjs
from sat.core.i18n import _

from pyjamas.ui.SimplePanel import SimplePanel
from pyjamas.ui.VerticalPanel import VerticalPanel
from pyjamas.ui.HorizontalPanel import HorizontalPanel
from pyjamas.ui.StackPanel import StackPanel
from pyjamas.ui.PasswordTextBox import PasswordTextBox
from pyjamas.ui.TextBox import TextBox
from pyjamas.ui.FormPanel import FormPanel
from pyjamas.ui.Button import Button
from pyjamas.ui.Label import Label
from pyjamas.ui.HTML import HTML
from pyjamas.ui.PopupPanel import PopupPanel
from pyjamas.ui.Image import Image
from pyjamas.ui.Hidden import Hidden
from pyjamas import Window
from pyjamas.ui.KeyboardListener import KEY_ENTER
from pyjamas.Timer import Timer

from __pyjamas__ import JS

from constants import Const as C



class RegisterPanel(FormPanel):

    def __init__(self, callback, session_data):
        """
        @param callback(callable): method to call if login successful
        @param session_data(dict): session metadata
        """
        FormPanel.__init__(self)
        self.setSize('600px', '350px')
        self.callback = callback
        self.setMethod(FormPanel.METHOD_POST)
        main_panel = HorizontalPanel()
        main_panel.setStyleName('registerPanel_main')
        left_side = Image("media/libervia/register_left.png")
        main_panel.add(left_side)

        ##StackPanel##
        self.right_side = StackPanel(StyleName='registerPanel_right_side')
        main_panel.add(self.right_side)
        main_panel.setCellWidth(self.right_side, '100%')

        ##Login stack##
        login_stack = SimplePanel()
        login_stack.setStyleName('registerPanel_content')
        login_vpanel = VerticalPanel()
        login_stack.setWidget(login_vpanel)

        self.login_warning_msg = HTML('')
        self.login_warning_msg.setStyleName('formWarning')
        login_vpanel.add(self.login_warning_msg)

        login_label = Label('Login:')
        self.login_box = TextBox()
        self.login_box.setName("login")
        self.login_box.addKeyboardListener(self)
        login_pass_label = Label('Password:')
        self.login_pass_box = PasswordTextBox()
        self.login_pass_box.setName("login_password")
        self.login_pass_box.addKeyboardListener(self)

        login_vpanel.add(login_label)
        login_vpanel.add(self.login_box)
        login_vpanel.add(login_pass_label)
        login_vpanel.add(self.login_pass_box)
        login_but = Button("Log in", getattr(self, "onLogin"))
        login_but.setStyleName('button')
        login_but.addStyleName('red')
        login_vpanel.add(login_but)
        self.right_side.add(login_stack, 'Return to the login screen')

        #The hidden submit_type field
        self.submit_type = Hidden('submit_type')
        login_vpanel.add(self.submit_type)

        ##Register stack##
        if session_data["allow_registration"]:
            register_stack = SimplePanel()
            register_stack.setStyleName('registerPanel_content')
            register_vpanel = VerticalPanel()
            register_stack.setWidget(register_vpanel)

            self.register_warning_msg = HTML('')
            self.register_warning_msg.setStyleName('formWarning')
            register_vpanel.add(self.register_warning_msg)

            register_login_label = Label('Login:')
            self.register_login_box = TextBox()
            self.register_login_box.setName("register_login")
            self.register_login_box.addKeyboardListener(self)
            email_label = Label('E-mail:')
            self.email_box = TextBox()
            self.email_box.setName("email")
            self.email_box.addKeyboardListener(self)
            register_pass_label = Label('Password:')
            self.register_pass_box = PasswordTextBox()
            self.register_pass_box.setName("register_password")
            self.register_pass_box.addKeyboardListener(self)
            register_vpanel.add(register_login_label)
            register_vpanel.add(self.register_login_box)
            register_vpanel.add(email_label)
            register_vpanel.add(self.email_box)
            register_vpanel.add(register_pass_label)
            register_vpanel.add(self.register_pass_box)

            register_but = Button("Register a new account", getattr(self, "onRegister"))
            register_but.setStyleName('button')
            register_but.addStyleName('red')
            register_vpanel.add(register_but)

            self.right_side.add(register_stack, 'No account yet? Create a new one!')
            self.right_side.addStackChangeListener(self)
            register_stack.setWidth(None)
        login_stack.setWidth(None)

        self.add(main_panel)
        self.addFormHandler(self)
        self.setAction('register_api/login')

    def onStackChanged(self, sender, index):
        if index == 0:
            self.login_box.setFocus(True)
        elif index == 1:
            self.register_login_box.setFocus(True)

    def onKeyPress(self, sender, keycode, modifiers):
        # XXX: this is triggered before the textbox value has changed
        if keycode == KEY_ENTER:
            # Browsers offer an auto-completion feature to any
            # text box, but the selected value is not set when
            # the widget looses the focus. Using a timer with
            # any delay value > 0 would do the trick.
            if sender == self.login_box:
                Timer(5, lambda timer: self.login_pass_box.setFocus(True))
            elif sender == self.login_pass_box:
                self.onLogin(None)
            elif sender == self.register_login_box:
                Timer(5, lambda timer: self.email_box.setFocus(True))
            elif sender == self.email_box:
                Timer(5, lambda timer: self.register_pass_box.setFocus(True))
            elif sender == self.register_pass_box:
                self.onRegister(None)

    def onKeyUp(self, sender, keycode, modifiers):
        # XXX: this is triggered after the textbox value has changed
        if sender == self.login_box:
            if "@" in self.login_box.getText():
                self.login_warning_msg.setHTML(_('<span class="formInfo">Entering a full JID is only needed to connect with an external XMPP account.</span>'))
            else:
                self.login_warning_msg.setHTML("")

    def onKeyDown(self, sender, keycode, modifiers):
        pass

    def onLogin(self, button):
        if not self.checkJID(self.login_box.getText()):
            self.login_warning_msg.setHTML('Invalid login, valid characters<br>are a-z A-Z 0-9 _ - or a bare JID')
        else:
            self.submit_type.setValue('login')
            self.submit(None)

    def onRegister(self, button):
        # XXX: for now libervia forces the creation to lower case
        self.register_login_box.setText(self.register_login_box.getText().lower())
        if not self.checkLogin(self.register_login_box.getText()):
            self.register_warning_msg.setHTML(_('Invalid login, valid characters<br>are a-z A-Z 0-9 _ -'))
        elif not self.checkEmail(self.email_box.getText()):
            self.register_warning_msg.setHTML(_('Invalid email address<br>(or not accepted yet)'))
        elif len(self.register_pass_box.getText()) < C.PASSWORD_MIN_LENGTH:
            self.register_warning_msg.setHTML(_('Your password must contain<br>at least %d characters.') % C.PASSWORD_MIN_LENGTH)
        else:
            self.register_warning_msg.setHTML("")
            self.submit_type.setValue('register')
            self.submit(None)

    def onSubmit(self, event):
        pass

    def onSubmitComplete(self, event):
        result = event.getResults()
        if result == C.PROFILE_AUTH_ERROR:
            self.login_warning_msg.setHTML(_('Your login and/or password is incorrect. Please try again.'))
        elif result == C.XMPP_AUTH_ERROR:
            # TODO: call stdui action CHANGE_XMPP_PASSWD_ID as it's done in primitivus
            Window.alert(_(u'Your XMPP account failed to connect. Did you enter the good password? If you have changed your XMPP password since your last connection on Libervia, please use another SàT frontend to update your profile.'))
        elif result == C.PROFILE_LOGGED_EXT_JID:
            self.callback()
            Window.alert(_('A profile has been created on this Libervia service using your existing XMPP account. Since you are not using our XMPP server, we can not guaranty that all the extra features (blog, directory...) will fully work.'))
        elif result == C.PROFILE_LOGGED:
            self.callback()
        elif result == C.SESSION_ACTIVE:
            Window.alert(_('Session already active, this should not happen, please contact the author to fix it.'))
        elif result == C.NO_REPLY:
            Window.alert(_("Did not receive a reply (the timeout expired or the connection is broken)."))
        elif result == C.ALREADY_EXISTS:
            self.register_warning_msg.setHTML(_('This login already exists,<br>please choose another one.'))
        elif result == C.INTERNAL_ERROR:
            self.register_warning_msg.setHTML(_('An registration error occurred, please contact the server administrator.'))
        elif result == C.REGISTRATION_SUCCEED:
            self.login_warning_msg.setHTML("")
            self.register_warning_msg.setHTML("")
            self.login_box.setText(self.register_login_box.getText())
            self.login_pass_box.setText('')
            self.register_login_box.setText('')
            self.register_pass_box.setText('')
            self.email_box.setText('')
            self.right_side.showStack(0)
            self.login_pass_box.setFocus(True)
            Window.alert(_('An email has been sent to you with your login informations\nPlease remember that this is ONLY A TECHNICAL DEMO.'))
        else:
            Window.alert(_("An error occurred and we couldn't process your request. Please report the following error name to the administrators of your network: '%s'" % result))

    def checkLogin(self, text):
        """Check if the given text is a valid login

        @param text (unicode)
        @return bool
        """
        # FIXME: Pyjamas re module is not stable so we use pure JS instead
        # FIXME: login is restricted to this regex until we fix the account creation
        JS("""return /^(\w|-)+$/.test(text);""")

    def checkEmail(self, text):
        """Check if the given text is a valid email address.

        @param text (unicode)
        @return bool
        """
        # FIXME: Pyjamas re module is not stable so we use pure JS instead
        # FIXME: send a message to validate the email instead of using a bad regex
        JS("""return /^(\w|-|\.|\+)+@(\w|-)+\.(\w|-)+$/.test(text);""")

    def checkJID(self, text):
        """Check if the given text is a valid JID.

        @param text (unicode)
        @return bool
        """
        # FIXME: Pyjamas re module is not stable so we use pure JS instead
        # FIXME: this regex is too restrictive for people using external XMPP account
        JS("""return /^(\w|-|\.|\+)+(@(\w|-)+\.(\w|-)+)?$/.test(text);""")


class RegisterBox(PopupPanel):

    def __init__(self, callback, session_data, *args, **kwargs):
        PopupPanel.__init__(self, *args, **kwargs)
        self._form = RegisterPanel(callback, session_data)
        self.setWidget(self._form)

    def onWindowResized(self, width, height):
        super(RegisterBox, self).onWindowResized(width, height)
        self.centerBox()

    def show(self):
        super(RegisterBox, self).show()
        self.centerBox()
        self._form.login_box.setFocus(True)
