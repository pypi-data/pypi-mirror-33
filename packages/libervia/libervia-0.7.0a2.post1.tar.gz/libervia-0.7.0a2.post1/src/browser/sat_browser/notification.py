from __pyjamas__ import JS, wnd
from sat.core.log import getLogger
log = getLogger(__name__)
from sat.core.i18n import _

from pyjamas import Window
from pyjamas.Timer import Timer
import favico.min.js

import dialog

TIMER_DELAY = 5000


class Notification(object):
    """
    If the browser supports it, the user allowed it to and the tab is in the
    background, send desktop notifications on messages.

    Requires both Web Notifications and Page Visibility API.
    """

    def __init__(self, alerts_counter):
        """

        @param alerts_counter (FaviconCounter): counter instance
        """
        self.alerts_counter = alerts_counter
        self.enabled = False
        user_agent = None
        notif_permission = None
        JS("""
        if (!('hidden' in document))
            document.hidden = false;

        user_agent = navigator.userAgent

        if (!('Notification' in window))
            return;

        notif_permission = Notification.permission

        if (Notification.permission === 'granted')
            this.enabled = true;

        else if (Notification.permission === 'default') {
            Notification.requestPermission(function(permission){
                if (permission !== 'granted')
                    return;

                self.enabled = true; //need to use self instead of this
            });
        }
        """)

        if "Chrome" in user_agent and notif_permission not in ['granted', 'denied']:
            self.user_agent = user_agent
            self._installChromiumWorkaround()

        wnd().onfocus = self.onFocus
        # wnd().onblur = self.onBlur

    def _installChromiumWorkaround(self):
        # XXX: Workaround for Chromium behaviour, it's doens't manage requestPermission on onLoad event
        # see https://code.google.com/p/chromium/issues/detail?id=274284
        # FIXME: need to be removed if Chromium behaviour changes
        try:
            version_full = [s for s in self.user_agent.split() if "Chrome" in s][0].split('/')[1]
            version = int(version_full.split('.')[0])
        except (IndexError, ValueError):
            log.warning("Can't find Chromium version")
            version = 0
        log.info("Chromium version: %d" % (version,))
        if version < 22:
            log.info("Notification use the old prefixed version or are unmanaged")
            return
        if version < 32:
            dialog.InfoDialog(_("Notifications activation for Chromium"), _('You need to activate notifications manually for your Chromium version.<br/>To activate notifications, click on the favicon on the left of the address bar')).show()
            return

        log.info("==> Installing Chromium notifications request workaround <==")
        self._old_click = wnd().onclick
        wnd().onclick = self._chromiumWorkaround

    def _chromiumWorkaround(self):
        log.info("Activating workaround")
        JS("""
            Notification.requestPermission(function(permission){
                if (permission !== 'granted')
                    return;
                self.enabled = true; //need to use self instead of this
            });
        """)
        wnd().onclick = self._old_click

    def onFocus(self, event=None):
        self.alerts_counter.update(extra=0)

    # def onBlur(self, event=None):
    #     pass

    def isHidden(self):
        JS("""return document.hidden;""")

    def _notify(self, title, body, icon):
        if not self.enabled:
            return
        notification = None
        # FIXME: icon has been removed because the notification can't display a HTTPS file
        JS("""
           notification = new Notification(title, {body: body});
           // Probably won’t work, but it doesn’t hurt to try.
           notification.addEventListener('click', function() {
               window.focus();
           });
           """)
        notification.onshow = lambda: Timer(TIMER_DELAY, lambda timer: notification.close())

    def notify(self, title, body, icon='/media/icons/apps/48/sat.png'):
        if self.isHidden():
            self._notify(title, body, icon)


class FaviconCounter(object):
    """Display numbers over the favicon to signal e.g. waiting messages"""

    def __init__(self):
        # XXX: the file favico.min.js is loaded from public/libervia.html because I get NS_ERROR_FAILURE when it's loaded with Pyjamas. It sounds like a context issue, with the favicon not being found.

        JS("""
        self.counter = new top.Favico({
            animation : 'slide',
            bgColor: '#5CB85C',
        });
        """)

        self.count = 0  # messages that are not displayed
        self.extra = 0  # messages that are displayed but the window is hidden

    def update(self, count=None, extra=None):
        """Update the favicon counter.

        @param count (int): primary counter
        @param extra (int): extra counter
        """
        if count is not None:
            self.count = count
        if extra is not None:
            self.extra = extra
        self.counter.badge(self.count + self.extra)
