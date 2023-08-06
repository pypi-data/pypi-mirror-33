#!/usr/bin/python
# -*- coding: utf-8 -*-

# SAT plugin for Chat State Notifications Protocol (xep-0085)
# Copyright (C) 2013-2016 Adrien Cossa (souliane@mailoo.org)

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

from pyjamas.Timer import Timer


# Copy of the map from sat/src/plugins/plugin_xep_0085
TRANSITIONS = {"active": {"next_state": "inactive", "delay": 120},
               "inactive": {"next_state": "gone", "delay": 480},
               "gone": {"next_state": "", "delay": 0},
               "composing": {"next_state": "paused", "delay": 30},
               "paused": {"next_state": "inactive", "delay": 450}
               }


class ChatStateMachine:
    """This is an adapted version of the ChatStateMachine from sat/src/plugins/plugin_xep_0085
    which manage a timer on the web browser and keep it synchronized with the timer that runs
    on the backend. This is only needed to avoid calling the bridge method chatStateComposing
    too often ; accuracy is not needed so we can ignore the delay of the communication between
    the web browser and the backend (the timer on the web browser always starts a bit before).
    /!\ Keep this file up to date if you modify the one in the sat plugins directory.
    """
    def __init__(self, host, target_s):

        self.host = host
        self.target_s = target_s
        self.started = False
        self.state = None
        self.timer = None

    def _onEvent(self, state):
        # Pyjamas callback takes no extra argument so we need this trick

        # Here we should check the value of the parameter "Send chat state notifications"
        # but this costs two messages. It's even better to call chatStateComposing
        # with a doubt, it will be checked by the back-end anyway before sending
        # the actual notifications to the other client.
        if state == "composing" and not self.started:
            return
        self.started = True
        self.next_state = state
        self.__onEvent(None)

    def __onEvent(self, timer):
        state = self.next_state

        assert(state in TRANSITIONS)
        transition = TRANSITIONS[state]
        assert("next_state" in transition and "delay" in transition)

        if state != self.state and state == "composing":
            self.host.bridge.call('chatStateComposing', None, self.target_s)

        self.state = state
        if self.timer is not None:
            self.timer.cancel()

        if transition["next_state"] and transition["delay"] > 0:
            self.next_state = transition["next_state"]
            self.timer = Timer(transition["delay"] * 1000, self.__onEvent)  # pyjamas timer is in milliseconds
