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
from sat.core.i18n import _, D_
from pyjamas.ui.FileUpload import FileUpload
from pyjamas.ui.FormPanel import FormPanel
from pyjamas import Window
from pyjamas import DOM
from pyjamas.ui.VerticalPanel import VerticalPanel
from pyjamas.ui.HTML import HTML
from pyjamas.ui.HorizontalPanel import HorizontalPanel
from pyjamas.ui.Button import Button
from pyjamas.ui.Label import Label


class FilterFileUpload(FileUpload):

    def __init__(self, name, max_size, types=None):
        """
        @param name: the input element name and id
        @param max_size: maximum file size in MB
        @param types: allowed types as a list of couples (x, y, z):
        - x: MIME content type e.g. "audio/ogg"
        - y: file extension e.g. "*.ogg"
        - z: description for the user e.g. "Ogg Vorbis Audio"
        If types is None, all file format are accepted
        """
        FileUpload.__init__(self)
        self.setName(name)
        while DOM.getElementById(name):
            name = "%s_" % name
        self.setID(name)
        self._id = name
        self.max_size = max_size
        self.types = types

    def getFileInfo(self):
        from __pyjamas__ import JS
        JS("var file = top.document.getElementById(this._id).files[0]; return [file.size, file.type]")

    def check(self):
        if self.getFilename() == "":
            return False
        (size, filetype) = self.getFileInfo()
        if self.types and filetype not in [x for (x, y, z) in self.types]:
            types = []
            for type_ in ["- %s (%s)" % (z, y) for (x, y, z) in self.types]:
                if type_ not in types:
                    types.append(type_)
            Window.alert('This file type is not accepted.\nAccepted file types are:\n\n%s' % "\n".join(types))
            return False
        if size > self.max_size * pow(2, 20):
            Window.alert('This file is too big!\nMaximum file size: %d MB.' % self.max_size)
            return False
        return True


class FileUploadPanel(FormPanel):

    def __init__(self, action_url, input_id, max_size, texts=None, close_cb=None):
        """Build a form panel to upload a file.
        @param action_url: the form action URL
        @param input_id: the input element name and id
        @param max_size: maximum file size in MB
        @param texts: a dict to ovewrite the default textual values
        @param close_cb: the close button callback method
        """
        FormPanel.__init__(self)
        self.texts = {'ok_button': D_('Upload file'),
                     'cancel_button': D_('Cancel'),
                     'body': D_('Please select a file.'),
                     'submitting': D_('<strong>Submitting, please wait...</strong>'),
                     'errback': D_("Your file has been rejected..."),
                     'body_errback': D_('Please select another file.'),
                     'callback': D_("Your file has been accepted!")}
        if isinstance(texts, dict):
            self.texts.update(texts)
        self.close_cb = close_cb
        self.setEncoding(FormPanel.ENCODING_MULTIPART)
        self.setMethod(FormPanel.METHOD_POST)
        self.setAction(action_url)
        self.vPanel = VerticalPanel()
        self.message = HTML(self.texts['body'])
        self.vPanel.add(self.message)

        hPanel = HorizontalPanel()
        hPanel.setSpacing(5)
        hPanel.setStyleName('marginAuto')
        self.file_upload = FilterFileUpload(input_id, max_size)
        self.vPanel.add(self.file_upload)

        self.upload_btn = Button(self.texts['ok_button'], getattr(self, "onSubmitBtnClick"))
        hPanel.add(self.upload_btn)
        hPanel.add(Button(self.texts['cancel_button'], getattr(self, "onCloseBtnClick")))

        self.status = Label()
        hPanel.add(self.status)

        self.vPanel.add(hPanel)

        self.add(self.vPanel)
        self.addFormHandler(self)

    def setCloseCb(self, close_cb):
        self.close_cb = close_cb

    def onCloseBtnClick(self):
        if self.close_cb:
            self.close_cb()
        else:
            log.warning("no close method defined")

    def onSubmitBtnClick(self):
        if not self.file_upload.check():
            return
        self.message.setHTML(self.texts['submitting'])
        self.upload_btn.setEnabled(False)
        self.submit()

    def onSubmit(self, event):
        pass

    def onSubmitComplete(self, event):
        result = event.getResults()
        if result == C.UPLOAD_KO:
            Window.alert(self.texts['errback'])
            self.message.setHTML(self.texts['body_errback'])
            self.upload_btn.setEnabled(True)
        elif result == C.UPLOAD_OK:
            Window.alert(self.texts['callback'])
            self.close_cb()
        else:
            Window.alert(_('Submit error: %s' % result))
            self.upload_btn.setEnabled(True)


class AvatarUpload(FileUploadPanel):
    def __init__(self):
        texts = {'ok_button': 'Upload avatar',
                 'body': 'Please select an image to show as your avatar...<br>Your picture must be a square and will be resized to 64x64 pixels if necessary.',
                 'errback': "Can't open image... did you actually submit an image?",
                 'body_errback': 'Please select another image file.',
                 'callback': "Your new profile picture has been set!"}
        FileUploadPanel.__init__(self, 'upload_avatar', 'avatar_path', 2, texts)
