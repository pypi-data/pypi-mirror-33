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

from sat.core.i18n import _, D_
from sat_frontends.tools import host_listener
from constants import Const as C

from pyjamas.ui.VerticalPanel import VerticalPanel
from pyjamas.ui.HorizontalPanel import HorizontalPanel
from pyjamas.ui.FlexTable import FlexTable
from pyjamas.ui.FormPanel import FormPanel
from pyjamas.ui.Label import Label
from pyjamas.ui.Button import Button
from pyjamas.ui.ClickListener import ClickHandler
from pyjamas.ui.Hidden import Hidden
from pyjamas.ui.CaptionPanel import CaptionPanel
from pyjamas.media.Audio import Audio
from pyjamas import Window
from pyjamas.Timer import Timer

import html_tools
import file_tools
import dialog


unicode = str # XXX: pyjama doesn't manage unicode


class MetadataPanel(FlexTable):

    def __init__(self):
        FlexTable.__init__(self)
        title_lbl = Label("title:")
        title_lbl.setStyleName('radiocol_metadata_lbl')
        artist_lbl = Label("artist:")
        artist_lbl.setStyleName('radiocol_metadata_lbl')
        album_lbl = Label("album:")
        album_lbl.setStyleName('radiocol_metadata_lbl')
        self.title = Label("")
        self.title.setStyleName('radiocol_metadata')
        self.artist = Label("")
        self.artist.setStyleName('radiocol_metadata')
        self.album = Label("")
        self.album.setStyleName('radiocol_metadata')
        self.setWidget(0, 0, title_lbl)
        self.setWidget(1, 0, artist_lbl)
        self.setWidget(2, 0, album_lbl)
        self.setWidget(0, 1, self.title)
        self.setWidget(1, 1, self.artist)
        self.setWidget(2, 1, self.album)
        self.setStyleName("radiocol_metadata_pnl")

    def setTitle(self, title):
        self.title.setText(title)

    def setArtist(self, artist):
        self.artist.setText(artist)

    def setAlbum(self, album):
        self.album.setText(album)


class ControlPanel(FormPanel):
    """Panel used to show controls to add a song, or vote for the current one"""

    def __init__(self, parent):
        FormPanel.__init__(self)
        self.setEncoding(FormPanel.ENCODING_MULTIPART)
        self.setMethod(FormPanel.METHOD_POST)
        self.setAction("upload_radiocol")
        self.timer_on = False
        self._parent = parent
        vPanel = VerticalPanel()

        types = [('audio/ogg', '*.ogg', 'Ogg Vorbis Audio'),
                 ('video/ogg', '*.ogv', 'Ogg Vorbis Video'),
                 ('application/ogg', '*.ogx', 'Ogg Vorbis Multiplex'),
                 ('audio/mpeg', '*.mp3', 'MPEG-Layer 3'),
                 ('audio/mp3', '*.mp3', 'MPEG-Layer 3'),
                 ]
        self.file_upload = file_tools.FilterFileUpload("song", 10, types)
        vPanel.add(self.file_upload)

        hPanel = HorizontalPanel()
        self.upload_btn = Button("Upload song", getattr(self, "onBtnClick"))
        hPanel.add(self.upload_btn)
        self.status = Label()
        self.updateStatus()
        hPanel.add(self.status)
        #We need to know the filename and the referee
        self.filename_field = Hidden('filename', '')
        hPanel.add(self.filename_field)
        referee_field = Hidden('referee', self._parent.referee)
        hPanel.add(self.filename_field)
        hPanel.add(referee_field)
        vPanel.add(hPanel)

        self.add(vPanel)
        self.addFormHandler(self)

    def updateStatus(self):
        if self.timer_on:
            return
        # TODO: the status should be different if a song is being played or not
        queue = self._parent.getQueueSize()
        queue_data = self._parent.queue_data
        if queue < queue_data[0]:
            left = queue_data[0] - queue
            self.status.setText("[we need %d more song%s]" % (left, "s" if left > 1 else ""))
        elif queue < queue_data[1]:
            left = queue_data[1] - queue
            self.status.setText("[%d available spot%s]" % (left, "s" if left > 1 else ""))
        elif queue >= queue_data[1]:
                self.status.setText("[The queue is currently full]")
        self.status.setStyleName('radiocol_status')

    def onBtnClick(self):
        if self.file_upload.check():
            self.status.setText('[Submitting, please wait...]')
            self.filename_field.setValue(self.file_upload.getFilename())
            if self.file_upload.getFilename().lower().endswith('.mp3'):
                self._parent._parent.host.showWarning('STATUS', 'For a better support, it is recommended to submit Ogg Vorbis file instead of MP3. You can convert your files easily, ask for help if needed!', 5000)
            self.submit()
            self.file_upload.setFilename("")

    def onSubmit(self, event):
        pass

    def blockUpload(self):
        self.file_upload.setVisible(False)
        self.upload_btn.setEnabled(False)

    def unblockUpload(self):
        self.file_upload.setVisible(True)
        self.upload_btn.setEnabled(True)

    def setTemporaryStatus(self, text, style):
        self.status.setText(text)
        self.status.setStyleName('radiocol_upload_status_%s' % style)
        self.timer_on = True

        def cb(timer):
            self.timer_on = False
            self.updateStatus()

        Timer(5000, cb)

    def onSubmitComplete(self, event):
        result = event.getResults()
        if result == C.UPLOAD_OK:
            # the song can still be rejected (not readable, full queue...)
            self.setTemporaryStatus('[Your song has been submitted to the radio]', "ok")
        elif result == C.UPLOAD_KO:
            self.setTemporaryStatus('[Something went wrong during your song upload]', "ko")
            self._parent.radiocolSongRejectedHandler(_("The uploaded file has been rejected, only Ogg Vorbis and MP3 songs are accepted."))
            # TODO: would be great to re-use the original Exception class and message
            # but it is lost in the middle of the traceback and encapsulated within
            # a DBusException instance --> extract the data from the traceback?
        else:
            Window.alert(_('Submit error: %s' % result))
            self.status.setText('')


class Player(Audio):

    def __init__(self, player_id, metadata_panel):
        Audio.__init__(self)
        self._id = player_id
        self.metadata = metadata_panel
        self.timestamp = ""
        self.title = ""
        self.artist = ""
        self.album = ""
        self.filename = None
        self.played = False  # True when the song is playing/has played, becomes False on preload
        self.setAutobuffer(True)
        self.setAutoplay(False)
        self.setVisible(False)

    def preload(self, timestamp, filename, title, artist, album):
        """preload the song but doesn't play it"""
        self.timestamp = timestamp
        self.filename = filename
        self.title = title
        self.artist = artist
        self.album = album
        self.played = False
        self.setSrc(u"radiocol/%s" % html_tools.html_sanitize(filename))
        log.debug(u"preloading %s in %s" % (title, self._id))

    def play(self, play=True):
        """Play or pause the song
        @param play: set to True to play or to False to pause
        """
        if play:
            self.played = True
            self.metadata.setTitle(self.title)
            self.metadata.setArtist(self.artist)
            self.metadata.setAlbum(self.album)
            Audio.play(self)
        else:
            self.pause()


class RadioColPanel(HorizontalPanel, ClickHandler):

    def __init__(self, parent, referee, players, queue_data):
        """
        @param parent
        @param referee
        @param players
        @param queue_data: list of integers (queue to start, queue limit)
        """
        # We need to set it here and not in the CSS :(
        HorizontalPanel.__init__(self, Height="90px")
        ClickHandler.__init__(self)
        self._parent = parent
        self.referee = referee
        self.queue_data = queue_data
        self.setStyleName("radiocolPanel")

        # Now we set up the layout
        self.metadata_panel = MetadataPanel()
        self.add(CaptionPanel("Now playing", self.metadata_panel))
        self.playlist_panel = VerticalPanel()
        self.add(CaptionPanel("Songs queue", self.playlist_panel))
        self.control_panel = ControlPanel(self)
        self.add(CaptionPanel("Controls", self.control_panel))

        self.next_songs = []
        self.players = [Player("player_%d" % i, self.metadata_panel) for i in xrange(queue_data[1] + 1)]
        self.current_player = None
        for player in self.players:
            self.add(player)
        self.addClickListener(self)

        help_msg = """Accepted file formats: Ogg Vorbis (recommended), MP3.<br />
        Please do not submit files that are protected by copyright.<br />
        Click <a style="color: red;">here</a> if you need some support :)"""
        link_cb = lambda: self._parent.host.bridge.joinMUC(self._parent.host.default_muc, self._parent.nick, profile=C.PROF_KEY_NONE, callback=lambda dummy: None, errback=self._parent.host.onJoinMUCFailure)
        # FIXME: printInfo disabled after refactoring
        # self._parent.printInfo(help_msg, type_='link', link_cb=link_cb)

    def pushNextSong(self, title):
        """Add a song to the left panel's next songs queue"""
        next_song = Label(title)
        next_song.setStyleName("radiocol_next_song")
        self.next_songs.append(next_song)
        self.playlist_panel.append(next_song)
        self.control_panel.updateStatus()

    def popNextSong(self):
        """Remove the first song of next songs list
        should be called when the song is played"""
        #FIXME: should check that the song we remove is the one we play
        next_song = self.next_songs.pop(0)
        self.playlist_panel.remove(next_song)
        self.control_panel.updateStatus()

    def getQueueSize(self):
        return len(self.playlist_panel.getChildren())

    def radiocolCheckPreload(self, timestamp):
        for player in self.players:
            if player.timestamp == timestamp:
                return False
        return True

    def radiocolPreloadHandler(self, timestamp, filename, title, artist, album, sender):
        if not self.radiocolCheckPreload(timestamp):
            return  # song already preloaded
        preloaded = False
        for player in self.players:
            if not player.filename or \
               (player.played and player != self.current_player):
                #if player has no file loaded, or it has already played its song
                #we use it to preload the next one
                player.preload(timestamp, filename, title, artist, album)
                preloaded = True
                break
        if not preloaded:
            log.warning("Can't preload song, we are getting too many songs to preload, we shouldn't have more than %d at once" % self.queue_data[1])
        else:
            self.pushNextSong(title)
            # FIXME: printInfo disabled after refactoring
            # self._parent.printInfo(_('%(user)s uploaded %(artist)s - %(title)s') % {'user': sender, 'artist': artist, 'title': title})

    def radiocolPlayHandler(self, filename):
        found = False
        for player in self.players:
            if not found and player.filename == filename:
                player.play()
                self.popNextSong()
                self.current_player = player
                found = True
            else:
                player.play(False)  # in case the previous player was not sync
        if not found:
            log.error("Song not found in queue, can't play it. This should not happen")

    def radiocolNoUploadHandler(self):
        self.control_panel.blockUpload()

    def radiocolUploadOkHandler(self):
        self.control_panel.unblockUpload()

    def radiocolSongRejectedHandler(self, reason):
        Window.alert("Song rejected: %s" % reason)


##  Menu

def hostReady(host):
    def onCollectiveRadio(self):
        def callback(room_jid, contacts):
            contacts = [unicode(contact) for contact in contacts]
            room_jid_s = unicode(room_jid) if room_jid else ''
            host.bridge.launchRadioCollective(contacts, room_jid_s, profile=C.PROF_KEY_NONE, callback=lambda dummy: None, errback=host.onJoinMUCFailure)
        dialog.RoomAndContactsChooser(host, callback, ok_button="Choose", title="Collective Radio", visible=(False, True))


    def gotMenus():
        host.menus.addMenu(C.MENU_GLOBAL, (D_(u"Groups"), D_(u"Collective radio")), callback=onCollectiveRadio)

    host.addListener('gotMenus', gotMenus)

host_listener.addListener(hostReady)
