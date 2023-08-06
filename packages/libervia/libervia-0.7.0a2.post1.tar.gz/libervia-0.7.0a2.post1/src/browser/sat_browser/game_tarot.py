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
from sat_frontends.tools.games import TarotCard
from sat_frontends.tools import host_listener

from pyjamas.ui.AbsolutePanel import AbsolutePanel
from pyjamas.ui.DockPanel import DockPanel
from pyjamas.ui.SimplePanel import SimplePanel
from pyjamas.ui.Image import Image
from pyjamas.ui.Label import Label
from pyjamas.ui.ClickListener import ClickHandler
from pyjamas.ui.MouseListener import MouseHandler
from pyjamas.ui import HasAlignment
from pyjamas import Window
from pyjamas import DOM
from constants import Const as C

import dialog
import xmlui


CARD_WIDTH = 74
CARD_HEIGHT = 136
CARD_DELTA_Y = 30
MIN_WIDTH = 950  # Minimum size of the panel
MIN_HEIGHT = 500


unicode = str  # XXX: pyjama doesn't manage unicode


class CardWidget(TarotCard, Image, MouseHandler):
    """This class is used to represent a card, graphically and logically"""

    def __init__(self, parent, file_):
        """@param file: path of the PNG file"""
        self._parent = parent
        Image.__init__(self, file_)
        root_name = file_[file_.rfind("/") + 1:-4]
        suit, value = root_name.split('_')
        TarotCard.__init__(self, (suit, value))
        MouseHandler.__init__(self)
        self.addMouseListener(self)

    def onMouseEnter(self, sender):
        if self._parent.state == "ecart" or self._parent.state == "play":
            DOM.setStyleAttribute(self.getElement(), "top", "0px")

    def onMouseLeave(self, sender):
        if not self in self._parent.hand:
            return
        if not self in list(self._parent.selected):  # FIXME: Workaround pyjs bug, must report it
            DOM.setStyleAttribute(self.getElement(), "top", "%dpx" % CARD_DELTA_Y)

    def onMouseUp(self, sender, x, y):
        if self._parent.state == "ecart":
            if self not in list(self._parent.selected):
                self._parent.addToSelection(self)
            else:
                self._parent.removeFromSelection(self)
        elif self._parent.state == "play":
            self._parent.playCard(self)


class TarotPanel(DockPanel, ClickHandler):

    def __init__(self, parent, referee, players):
        DockPanel.__init__(self)
        ClickHandler.__init__(self)
        self._parent = parent
        self._autoplay = None  # XXX: use 0 to activate fake play, None else
        self.referee = referee
        self.players = players
        self.player_nick = parent.nick
        self.bottom_nick = self.player_nick
        idx = self.players.index(self.player_nick)
        idx = (idx + 1) % len(self.players)
        self.right_nick = self.players[idx]
        idx = (idx + 1) % len(self.players)
        self.top_nick = self.players[idx]
        idx = (idx + 1) % len(self.players)
        self.left_nick = self.players[idx]
        self.bottom_nick = self.player_nick
        self.selected = set()  # Card choosed by the player (e.g. during ecart)
        self.hand_size = 13  # number of cards in a hand
        self.hand = []
        self.to_show = []
        self.state = None
        self.setSize("%dpx" % MIN_WIDTH, "%dpx" % MIN_HEIGHT)
        self.setStyleName("cardPanel")

        # Now we set up the layout
        _label = Label(self.top_nick)
        _label.setStyleName('cardGamePlayerNick')
        self.add(_label, DockPanel.NORTH)
        self.setCellWidth(_label, '100%')
        self.setCellHorizontalAlignment(_label, HasAlignment.ALIGN_CENTER)

        self.hand_panel = AbsolutePanel()
        self.add(self.hand_panel, DockPanel.SOUTH)
        self.setCellWidth(self.hand_panel, '100%')
        self.setCellHorizontalAlignment(self.hand_panel, HasAlignment.ALIGN_CENTER)

        _label = Label(self.left_nick)
        _label.setStyleName('cardGamePlayerNick')
        self.add(_label, DockPanel.WEST)
        self.setCellHeight(_label, '100%')
        self.setCellVerticalAlignment(_label, HasAlignment.ALIGN_MIDDLE)

        _label = Label(self.right_nick)
        _label.setStyleName('cardGamePlayerNick')
        self.add(_label, DockPanel.EAST)
        self.setCellHeight(_label, '100%')
        self.setCellHorizontalAlignment(_label, HasAlignment.ALIGN_RIGHT)
        self.setCellVerticalAlignment(_label, HasAlignment.ALIGN_MIDDLE)

        self.center_panel = DockPanel()
        self.inner_left = SimplePanel()
        self.inner_left.setSize("%dpx" % CARD_WIDTH, "%dpx" % CARD_HEIGHT)
        self.center_panel.add(self.inner_left, DockPanel.WEST)
        self.center_panel.setCellHeight(self.inner_left, '100%')
        self.center_panel.setCellHorizontalAlignment(self.inner_left, HasAlignment.ALIGN_RIGHT)
        self.center_panel.setCellVerticalAlignment(self.inner_left, HasAlignment.ALIGN_MIDDLE)

        self.inner_right = SimplePanel()
        self.inner_right.setSize("%dpx" % CARD_WIDTH, "%dpx" % CARD_HEIGHT)
        self.center_panel.add(self.inner_right, DockPanel.EAST)
        self.center_panel.setCellHeight(self.inner_right, '100%')
        self.center_panel.setCellVerticalAlignment(self.inner_right, HasAlignment.ALIGN_MIDDLE)

        self.inner_top = SimplePanel()
        self.inner_top.setSize("%dpx" % CARD_WIDTH, "%dpx" % CARD_HEIGHT)
        self.center_panel.add(self.inner_top, DockPanel.NORTH)
        self.center_panel.setCellHorizontalAlignment(self.inner_top, HasAlignment.ALIGN_CENTER)
        self.center_panel.setCellVerticalAlignment(self.inner_top, HasAlignment.ALIGN_BOTTOM)

        self.inner_bottom = SimplePanel()
        self.inner_bottom.setSize("%dpx" % CARD_WIDTH, "%dpx" % CARD_HEIGHT)
        self.center_panel.add(self.inner_bottom, DockPanel.SOUTH)
        self.center_panel.setCellHorizontalAlignment(self.inner_bottom, HasAlignment.ALIGN_CENTER)
        self.center_panel.setCellVerticalAlignment(self.inner_bottom, HasAlignment.ALIGN_TOP)

        self.inner_center = SimplePanel()
        self.center_panel.add(self.inner_center, DockPanel.CENTER)
        self.center_panel.setCellHorizontalAlignment(self.inner_center, HasAlignment.ALIGN_CENTER)
        self.center_panel.setCellVerticalAlignment(self.inner_center, HasAlignment.ALIGN_MIDDLE)

        self.add(self.center_panel, DockPanel.CENTER)
        self.setCellWidth(self.center_panel, '100%')
        self.setCellHeight(self.center_panel, '100%')
        self.setCellVerticalAlignment(self.center_panel, HasAlignment.ALIGN_MIDDLE)
        self.setCellHorizontalAlignment(self.center_panel, HasAlignment.ALIGN_CENTER)

        self.loadCards()
        self.mouse_over_card = None  # contain the card to highlight
        self.visible_size = CARD_WIDTH / 2  # number of pixels visible for cards
        self.addClickListener(self)

    def loadCards(self):
        """Load all the cards in memory"""
        def _getTarotCardsPathsCb(paths):
            log.debug("_getTarotCardsPathsCb")
            for file_ in paths:
                log.debug(u"path: %s" % file_)
                card = CardWidget(self, file_)
                log.debug(u"card: %s" % card)
                self.cards[(card.suit, card.value)] = card
                self.deck.append(card)
            self._parent.host.bridge.call('tarotGameReady', None, self.player_nick, self.referee)
        self.cards = {}
        self.deck = []
        self.cards["atout"] = {}  # As Tarot is a french game, it's more handy & logical to keep french names
        self.cards["pique"] = {}  # spade
        self.cards["coeur"] = {}  # heart
        self.cards["carreau"] = {}  # diamond
        self.cards["trefle"] = {}  # club
        self._parent.host.bridge.call('getTarotCardsPaths', _getTarotCardsPathsCb)

    def onClick(self, sender):
        if self.state == "chien":
            self.to_show = []
            self.state = "wait"
            self.updateToShow()
        elif self.state == "wait_for_ecart":
            self.state = "ecart"
            self.hand.extend(self.to_show)
            self.hand.sort()
            self.to_show = []
            self.updateToShow()
            self.updateHand()

    def tarotGameNewHandler(self, hand):
        """Start a new game, with given hand"""
        if hand is []:  # reset the display after the scores have been showed
            self.selected.clear()
            del self.hand[:]
            del self.to_show[:]
            self.state = None
            #empty hand
            self.updateHand()
            #nothing on the table
            self.updateToShow()
            for pos in ['top', 'left', 'bottom', 'right']:
                getattr(self, "inner_%s" % pos).setWidget(None)
            self._parent.host.bridge.call('tarotGameReady', None, self.player_nick, self.referee)
            return
        for suit, value in hand:
            self.hand.append(self.cards[(suit, value)])
        self.hand.sort()
        self.state = "init"
        self.updateHand()

    def updateHand(self):
        """Show the cards in the hand in the hand_panel (SOUTH panel)"""
        self.hand_panel.clear()
        self.hand_panel.setSize("%dpx" % (self.visible_size * (len(self.hand) + 1)), "%dpx" % (CARD_HEIGHT + CARD_DELTA_Y + 10))
        x_pos = 0
        y_pos = CARD_DELTA_Y
        for card in self.hand:
            self.hand_panel.add(card, x_pos, y_pos)
            x_pos += self.visible_size

    def updateToShow(self):
        """Show cards in the center panel"""
        if not self.to_show:
            _widget = self.inner_center.getWidget()
            if _widget:
                self.inner_center.remove(_widget)
            return
        panel = AbsolutePanel()
        panel.setSize("%dpx" % ((CARD_WIDTH + 5) * len(self.to_show) - 5), "%dpx" % (CARD_HEIGHT))
        x_pos = 0
        y_pos = 0
        for card in self.to_show:
            panel.add(card, x_pos, y_pos)
            x_pos += CARD_WIDTH + 5
        self.inner_center.setWidget(panel)

    def _ecartConfirm(self, confirm):
        if not confirm:
            return
        ecart = []
        for card in self.selected:
            ecart.append((card.suit, card.value))
            self.hand.remove(card)
        self.selected.clear()
        self._parent.host.bridge.call('tarotGamePlayCards', None, self.player_nick, self.referee, ecart)
        self.state = "wait"
        self.updateHand()

    def addToSelection(self, card):
        self.selected.add(card)
        if len(self.selected) == 6:
            dialog.ConfirmDialog(self._ecartConfirm, "Put these cards into chien ?").show()

    def tarotGameInvalidCardsHandler(self, phase, played_cards, invalid_cards):
        """Invalid cards have been played
        @param phase: phase of the game
        @param played_cards: all the cards played
        @param invalid_cards: cards which are invalid"""

        if phase == "play":
            self.state = "play"
        elif phase == "ecart":
            self.state = "ecart"
        else:
            log.error("INTERNAL ERROR: unmanaged game phase")  # FIXME: raise an exception here

        for suit, value in played_cards:
            self.hand.append(self.cards[(suit, value)])

        self.hand.sort()
        self.updateHand()
        if self._autoplay == None:  # No dialog if there is autoplay
            Window.alert('Cards played are invalid !')
        self.__fakePlay()

    def removeFromSelection(self, card):
        self.selected.remove(card)
        if len(self.selected) == 6:
            dialog.ConfirmDialog(self._ecartConfirm, "Put these cards into chien ?").show()

    def tarotGameChooseContratHandler(self, xml_data):
        """Called when the player has to select his contrat
        @param xml_data: SàT xml representation of the form"""
        body = xmlui.create(self._parent.host, xml_data, flags=['NO_CANCEL'])
        _dialog = dialog.GenericDialog(_('Please choose your contrat'), body, options=['NO_CLOSE'])
        body.setCloseCb(_dialog.close)
        _dialog.show()

    def tarotGameShowCardsHandler(self, game_stage, cards, data):
        """Display cards in the middle of the game (to show for e.g. chien ou poignée)"""
        self.to_show = []
        for suit, value in cards:
            self.to_show.append(self.cards[(suit, value)])
        self.updateToShow()
        if game_stage == "chien" and data['attaquant'] == self.player_nick:
            self.state = "wait_for_ecart"
        else:
            self.state = "chien"

    def getPlayerLocation(self, nick):
        """return player location (top,bottom,left or right)"""
        for location in ['top', 'left', 'bottom', 'right']:
            if getattr(self, '%s_nick' % location) == nick:
                return location
        log.error("This line should not be reached")

    def tarotGameCardsPlayedHandler(self, player, cards):
        """A card has been played by player"""
        if not len(cards):
            log.warning("cards should not be empty")
            return
        if len(cards) > 1:
            log.error("can't manage several cards played")
        if self.to_show:
            self.to_show = []
            self.updateToShow()
        suit, value = cards[0]
        player_pos = self.getPlayerLocation(player)
        player_panel = getattr(self, "inner_%s" % player_pos)

        if player_panel.getWidget() != None:
            #We have already cards on the table, we remove them
            for pos in ['top', 'left', 'bottom', 'right']:
                getattr(self, "inner_%s" % pos).setWidget(None)

        card = self.cards[(suit, value)]
        DOM.setElemAttribute(card.getElement(), "style", "")
        player_panel.setWidget(card)

    def tarotGameYourTurnHandler(self):
        """Called when we have to play :)"""
        if self.state == "chien":
            self.to_show = []
            self.updateToShow()
        self.state = "play"
        self.__fakePlay()

    def __fakePlay(self):
        """Convenience method for stupid autoplay
        /!\ don't forgot to comment any interactive dialog for invalid card"""
        if self._autoplay == None:
            return
        if self._autoplay >= len(self.hand):
            self._autoplay = 0
        card = self.hand[self._autoplay]
        self._parent.host.bridge.call('tarotGamePlayCards', None, self.player_nick, self.referee, [(card.suit, card.value)])
        del self.hand[self._autoplay]
        self.state = "wait"
        self._autoplay += 1

    def playCard(self, card):
        self.hand.remove(card)
        self._parent.host.bridge.call('tarotGamePlayCards', None, self.player_nick, self.referee, [(card.suit, card.value)])
        self.state = "wait"
        self.updateHand()

    def tarotGameScoreHandler(self, xml_data, winners, loosers):
        """Show score at the end of a round"""
        if not winners and not loosers:
            title = "Draw game"
        else:
            if self.player_nick in winners:
                title = "You <b>win</b> !"
            else:
                title = "You <b>loose</b> :("
        body = xmlui.create(self._parent.host, xml_data, title=title, flags=['NO_CANCEL'])
        _dialog = dialog.GenericDialog(title, body, options=['NO_CLOSE'])
        body.setCloseCb(_dialog.close)
        _dialog.show()


##  Menu

def hostReady(host):
    def onTarotGame():
        def onPlayersSelected(room_jid, other_players):
            other_players = [unicode(contact) for contact in other_players]
            room_jid_s = unicode(room_jid) if room_jid else ''
            host.bridge.launchTarotGame(other_players, room_jid_s, profile=C.PROF_KEY_NONE, callback=lambda dummy: None, errback=host.onJoinMUCFailure)
        dialog.RoomAndContactsChooser(host, onPlayersSelected, 3, title="Tarot", title_invite=_(u"Please select 3 other players"), visible=(False, True))

    def gotMenus():
        host.menus.addMenu(C.MENU_GLOBAL, (D_(u"Groups"), D_(u"Tarot")), callback=onTarotGame)
    host.addListener('gotMenus', gotMenus)

host_listener.addListener(hostReady)
