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


### logging configuration ###
from sat_browser import logging
logging.configure()
from sat.core.log import getLogger
log = getLogger(__name__)
###

from sat.core.i18n import D_

from sat_frontends.quick_frontend.quick_app import QuickApp
from sat_frontends.quick_frontend import quick_widgets
from sat_frontends.quick_frontend import quick_menus

from sat_frontends.tools.misc import InputHistory
from sat_browser import strings
from sat_frontends.tools import jid
from sat_frontends.tools import host_listener
from sat.core.i18n import _

from pyjamas.ui.RootPanel import RootPanel
# from pyjamas.ui.HTML import HTML
from pyjamas.ui.KeyboardListener import KEY_ESCAPE
from pyjamas.Timer import Timer
from pyjamas import Window, DOM

from sat_browser import json
from sat_browser import register
from sat_browser.contact_list import ContactList
from sat_browser import main_panel
# from sat_browser import chat
from sat_browser import blog
from sat_browser import xmlui
from sat_browser import dialog
from sat_browser import html_tools
from sat_browser import notification
from sat_browser import libervia_widget
from sat_browser import web_widget
assert web_widget # XXX: just here to avoid pyflakes warning

from sat_browser.constants import Const as C


try:
    # FIXME: import plugin dynamically
    from sat_browser import plugin_sec_otr
except ImportError:
    pass


unicode = str  # FIXME: pyjamas workaround


# MAX_MBLOG_CACHE = 500  # Max microblog entries kept in memories # FIXME


class SatWebFrontend(InputHistory, QuickApp):

    def onModuleLoad(self):
        log.info("============ onModuleLoad ==============")
        self.bridge_signals = json.BridgeSignals(self)
        QuickApp.__init__(self, json.BridgeCall, xmlui=xmlui, connect_bridge=False)
        self.connectBridge()
        self._profile_plugged = False
        self.signals_cache[C.PROF_KEY_NONE] = []
        self.panel = main_panel.MainPanel(self)
        self.tab_panel = self.panel.tab_panel
        self.tab_panel.addTabListener(self)
        self._register_box = None
        RootPanel().add(self.panel)

        self.alerts_counter = notification.FaviconCounter()
        self.notification = notification.Notification(self.alerts_counter)
        DOM.addEventPreview(self)
        self.importPlugins()
        self._register = json.RegisterCall()
        self._register.call('menusGet', self.gotMenus)
        self._register.call('registerParams', None)
        self._register.call('getSessionMetadata', self._getSessionMetadataCB)
        self.initialised = False
        self.init_cache = []  # used to cache events until initialisation is done
        self.cached_params = {}
        self.next_rsm_index = 0

        #FIXME: microblog cache should be managed directly in blog module
        self.mblog_cache = []  # used to keep our own blog entries in memory, to show them in new mblog panel

        self._versions={} # SàT and Libervia versions cache

    @property
    def whoami(self):
        # XXX: works because Libervia is mono-profile
        #      if one day Libervia manage several profiles at once, this must be deleted
        return self.profiles[C.PROF_KEY_NONE].whoami

    @property
    def contact_list(self):
        return self.contact_lists[C.PROF_KEY_NONE]

    @property
    def visible_widgets(self):
        widgets_panel = self.tab_panel.getCurrentPanel()
        return [wid for wid in widgets_panel.widgets if isinstance(wid, quick_widgets.QuickWidget)]

    @property
    def base_location(self):
        """Return absolute base url of this Libervia instance"""
        url = Window.getLocation().getHref()
        if url.endswith(C.LIBERVIA_MAIN_PAGE):
            url = url[:-len(C.LIBERVIA_MAIN_PAGE)]
        if url.endswith("/"):
            url = url[:-1]
        return url

    @property
    def sat_version(self):
        return self._versions["sat"]

    @property
    def libervia_version(self):
        return self._versions["libervia"]

    def getVersions(self, callback=None):
        """Ask libervia server for SàT and Libervia version and fill local cache

        @param callback: method to call when both versions have been received
        """
        def gotVersion():
            if len(self._versions) == 2 and callback is not None:
                callback()

        if len(self._versions) == 2:
            # we already have versions in cache
            gotVersion()
            return

        def gotSat(version):
            self._versions["sat"] = version
            gotVersion()

        def gotLibervia(version):
            self._versions["libervia"] = version
            gotVersion()

        self.bridge.getVersion(callback=gotSat, profile=None)
        self.bridge.getLiberviaVersion(callback=gotLibervia, profile=None) # XXX: bridge direct call expect a profile, even for method with no profile needed

    def registerSignal(self, functionName, handler=None, iface="core", with_profile=True):
        if handler is None:
            callback = getattr(self, "{}{}".format(functionName, "Handler"))
        else:
            callback = handler

        self.bridge_signals.register_signal(functionName, callback, with_profile=with_profile)

    def importPlugins(self):
        self.plugins = {}
        try:
            self.plugins['otr'] = plugin_sec_otr.OTR(self)
        except TypeError:  # plugin_sec_otr has not been imported
            pass

    def getSelected(self):
        wid = self.tab_panel.getCurrentPanel()
        if not isinstance(wid, libervia_widget.WidgetsPanel):
            log.error("Tab widget is not a WidgetsPanel, can't get selected widget")
            return None
        return wid.selected

    def setSelected(self, widget):
        """Define the selected widget"""
        widgets_panel = self.tab_panel.getCurrentPanel()
        if not isinstance(widgets_panel, libervia_widget.WidgetsPanel):
            return

        selected = widgets_panel.selected

        if selected == widget:
            return

        if selected:
            selected.removeStyleName('selected_widget')

        # FIXME: check that widget is in the current WidgetsPanel
        widgets_panel.selected = widget
        self.selected_widget = widget

        if widget:
            widgets_panel.selected.addStyleName('selected_widget')

    def resize(self):
        """Resize elements"""
        Window.onResize()

    def onBeforeTabSelected(self, sender, tab_index):
        return True

    def onTabSelected(self, sender, tab_index):
        pass
    # def onTabSelected(self, sender, tab_index):
    #     for widget in self.tab_panel.getCurrentPanel().widgets:
    #         if isinstance(widget, chat.Chat):
    #             clist = self.contact_list
    #             clist.removeAlerts(widget.current_target, True)

    def onEventPreview(self, event):
        if event.type in ["keydown", "keypress", "keyup"] and event.keyCode == KEY_ESCAPE:
            #needed to prevent request cancellation in Firefox
            event.preventDefault()
        return True

    def getAvatarURL(self, jid_):
        """Return avatar of a jid if in cache, else ask for it.

        @param jid_ (jid.JID): JID of the contact
        @return: the URL to the avatar (unicode)
        """
        return self.getAvatar(jid_) or self.getDefaultAvatar()

    def getDefaultAvatar(self):
        return C.DEFAULT_AVATAR_URL

    def registerWidget(self, wid):
        log.debug(u"Registering %s" % wid.getDebugName())
        self.libervia_widgets.add(wid)

    def unregisterWidget(self, wid):
        try:
            self.libervia_widgets.remove(wid)
        except KeyError:
            log.warning(u'trying to remove a non registered Widget: %s' % wid.getDebugName())

    def refresh(self):
        """Refresh the general display."""
        self.contact_list.refresh()
        for lib_wid in self.libervia_widgets:
            lib_wid.refresh()
        self.resize()

    def addWidget(self, wid, tab_index=None):
        """ Add a widget at the bottom of the current or specified tab

        @param wid: LiberviaWidget to add
        @param tab_index: index of the tab to add the widget to
        """
        if tab_index is None or tab_index < 0 or tab_index >= self.tab_panel.getWidgetCount():
            panel = self.tab_panel.getCurrentPanel()
        else:
            panel = self.tab_panel.deck.getWidget(tab_index)
        panel.addWidget(wid)

    def gotMenus(self, backend_menus):
        """Put the menus data in cache and build the main menu bar

        @param backend_menus (list[tuple]): menu data from backend
        """
        main_menu = self.panel.menu # most of global menu callbacks are in main_menu

        # Categories (with icons)
        self.menus.addCategory(C.MENU_GLOBAL, [D_(u"General")], extra={'icon': 'home'})
        self.menus.addCategory(C.MENU_GLOBAL, [D_(u"Contacts")], extra={'icon': 'social'})
        self.menus.addCategory(C.MENU_GLOBAL, [D_(u"Groups")], extra={'icon': 'social'})
        #self.menus.addCategory(C.MENU_GLOBAL, [D_(u"Games")], extra={'icon': 'games'})

        # menus to have before backend menus
        self.menus.addMenu(C.MENU_GLOBAL, (D_(u"Groups"), D_(u"Discussion")), callback=main_menu.onJoinRoom)

        # menus added by the backend/plugins (include other types than C.MENU_GLOBAL)
        self.menus.addMenus(backend_menus, top_extra={'icon': 'plugins'})

        # menus to have under backend menus
        self.menus.addMenu(C.MENU_GLOBAL, (D_(u"Contacts"), D_(u"Manage contact groups")), callback=main_menu.onManageContactGroups)

        # separator and right hand menus
        self.menus.addMenuItem(C.MENU_GLOBAL, [], quick_menus.MenuSeparator())

        self.menus.addMenu(C.MENU_GLOBAL, (D_(u"Help"), D_("Official chat room")), top_extra={'icon': 'help'}, callback=main_menu.onOfficialChatRoom)
        self.menus.addMenu(C.MENU_GLOBAL, (D_(u"Help"), D_("Social contract")), top_extra={'icon': 'help'}, callback=main_menu.onSocialContract)
        self.menus.addMenu(C.MENU_GLOBAL, (D_(u"Help"), D_("About")), callback=main_menu.onAbout)
        self.menus.addMenu(C.MENU_GLOBAL, (D_(u"Settings"), D_("Account")), top_extra={'icon': 'settings'}, callback=main_menu.onAccount)
        self.menus.addMenu(C.MENU_GLOBAL, (D_(u"Settings"), D_("Parameters")), callback=main_menu.onParameters)
        # XXX: temporary, will change when a full profile will be managed in SàT
        self.menus.addMenu(C.MENU_GLOBAL, (D_(u"Settings"), D_("Upload avatar")), callback=main_menu.onAvatarUpload)

        # we call listener to have menu added by local classes/plugins
        self.callListeners('gotMenus')  # FIXME: to be done another way or moved to quick_app

        # and finally the menus which must appear at the bottom
        self.menus.addMenu(C.MENU_GLOBAL, (D_(u"General"), D_(u"Disconnect")), callback=main_menu.onDisconnect)

        # we can now display all the menus
        main_menu.update(C.MENU_GLOBAL)

        # XXX: temp, will be reworked in the backed static blog plugin
        self.menus.addMenu(C.MENU_JID_CONTEXT, (D_(u"User"), D_("Public blog")), callback=main_menu.onPublicBlog)

    def removeListener(self, type_, callback):
        """Remove a callback from listeners

        @param type_: same as for [addListener]
        @param callback: callback to remove
        """
        # FIXME: workaround for pyjamas
        #        check KeyError issue
        assert type_ in C.LISTENERS
        try:
            self._listeners[type_].pop(callback)
        except KeyError:
            pass

    def _getSessionMetadataCB(self, metadata):
        if not metadata['plugged']:
            warning = metadata.get("warning")
            self.panel.setStyleAttribute("opacity", "0.25")  # set background transparency
            self._register_box = register.RegisterBox(self.logged, metadata)
            self._register_box.centerBox()
            self._register_box.show()
            if warning:
                dialog.InfoDialog(_('Security warning'), warning).show()
            self._tryAutoConnect(skip_validation=not not warning)
        else:
            self._register.call('isConnected', self._isConnectedCB)

    def _isConnectedCB(self, connected):
        if not connected:
            self._register.call('connect', lambda x: self.logged())
        else:
            self.logged()

    def logged(self):
        self.panel.setStyleAttribute("opacity", "1")  # background becomes foreground
        if self._register_box:
            self._register_box.hide()
            del self._register_box  # don't work if self._register_box is None

        # display the presence status panel and tab bar
        self.presence_status_panel = main_panel.PresenceStatusPanel(self)
        self.panel.addPresenceStatusPanel(self.presence_status_panel)
        self.panel.tab_panel.getTabBar().setVisible(True)

        self.bridge_signals.getSignals(callback=self.bridge_signals.signalHandler, profile=None)

        def domain_cb(value):
            self._defaultDomain = value
            log.info(u"new account domain: %s" % value)

        def domain_eb(value):
            self._defaultDomain = "libervia.org"

        self.bridge.getNewAccountDomain(callback=domain_cb, errback=domain_eb)
        self.plug_profiles([C.PROF_KEY_NONE]) # XXX: None was used intitially, but pyjamas bug when using variable arguments and None is the only arg.

    def profilePlugged(self, dummy):
        self._profile_plugged = True
        QuickApp.profilePlugged(self, C.PROF_KEY_NONE)
        contact_list = self.widgets.getOrCreateWidget(ContactList, None, on_new_widget=None, profile=C.PROF_KEY_NONE)
        self.contact_list_widget = contact_list
        self.panel.addContactList(contact_list)

        # FIXME: the contact list height has to be set manually the first time
        self.resize()

        # XXX: as contact_list.update() is slow and it's called a lot of time
        #      during profile plugging, we prevent it before it's plugged
        #      and do all at once now
        contact_list.update()

        try:
            self.mblog_available = C.bool(self.features['XEP-0277']['available'])
        except KeyError:
            self.mblog_available = False

        try:
            self.groupblog_available = C.bool(self.features['GROUPBLOG']['available'])
        except KeyError:
            self.groupblog_available = False

        blog_widget = self.displayWidget(blog.Blog, ())
        self.setSelected(blog_widget)

        if self.mblog_available:
            if not self.groupblog_available:
                dialog.InfoDialog(_(u"Group blogging not available"), _(u"Your server can manage (micro)blogging, but not fine permissions.<br />You'll only be able to blog publicly.")).show()

        else:
            dialog.InfoDialog(_(u"Blogging not available"), _(u"Your server can't handle (micro)blogging.<br />You'll be able to see your contacts (micro)blogs, but not to post yourself.")).show()

        # we fill the panels already here
        # for wid in self.widgets.getWidgets(blog.MicroblogPanel):
        #     if wid.accept_all():
        #         self.bridge.getMassiveMblogs('ALL', (), None, profile=C.PROF_KEY_NONE, callback=wid.massiveInsert)
        #     else:
        #         self.bridge.getMassiveMblogs('GROUP', list(wid.accepted_groups), None, profile=C.PROF_KEY_NONE, callback=wid.massiveInsert)

        #we ask for our own microblogs:
        # self.loadOurMainEntries()

        def gotDefaultMUC(default_muc):
            self.default_muc = default_muc
        self.bridge.mucGetDefaultService(profile=None, callback=gotDefaultMUC)

    def newWidget(self, wid):
        log.debug(u"newWidget: {}".format(wid))
        self.addWidget(wid)

    def newMessageHandler(self, from_jid_s, msg, type_, to_jid_s, extra, profile=C.PROF_KEY_NONE):
        if type_ == C.MESS_TYPE_HEADLINE:
            from_jid = jid.JID(from_jid_s)
            if from_jid.domain == self._defaultDomain:
                # we display announcement from the server in a dialog for better visibility
                try:
                    title = extra['subject']
                except KeyError:
                    title = _('Announcement from %s') % from_jid
                msg = strings.addURLToText(html_tools.XHTML2Text(msg))
                dialog.InfoDialog(title, msg).show()
                return
        QuickApp.newMessageHandler(self, from_jid_s, msg, type_, to_jid_s, extra, profile)

    def disconnectedHandler(self, profile):
        QuickApp.disconnectedHandler(self, profile)
        Window.getLocation().reload()

    def setPresenceStatus(self, show='', status=None, profile=C.PROF_KEY_NONE):
        self.presence_status_panel.setPresence(show)
        if status is not None:
            self.presence_status_panel.setStatus(status)

    def _tryAutoConnect(self, skip_validation=False):
        """This method retrieve the eventual URL parameters to auto-connect the user.
        @param skip_validation: if True, set the form values but do not validate it
        """
        params = strings.getURLParams(Window.getLocation().getSearch())
        if "login" in params:
            self._register_box._form.right_side.showStack(0)
            self._register_box._form.login_box.setText(params["login"])
            self._register_box._form.login_pass_box.setFocus(True)
            if "passwd" in params:
                # try to connect
                self._register_box._form.login_pass_box.setText(params["passwd"])
                if not skip_validation:
                    self._register_box._form.onLogin(None)
                return True
            else:
                # this would eventually set the browser saved password
                Timer(5, lambda: self._register_box._form.login_pass_box.setFocus(True))

    def _actionManagerUnknownError(self):
        dialog.InfoDialog("Error",
                          "Unmanaged action result", Width="400px").center()

    # def _ownBlogsFills(self, mblogs, mblog_panel=None):
    #     """Put our own microblogs in cache, then fill the panels with them.

    #     @param mblogs (dict): dictionary mapping a publisher JID to blogs data.
    #     @param mblog_panel (MicroblogPanel): the panel to fill, or all if None.
    #     """
    #     cache = []
    #     for publisher in mblogs:
    #         for mblog in mblogs[publisher][0]:
    #             if 'content' not in mblog:
    #                 log.warning(u"No content found in microblog [%s]" % mblog)
    #                 continue
    #             if 'groups' in mblog:
    #                 _groups = set(mblog['groups'].split() if mblog['groups'] else [])
    #             else:
    #                 _groups = None
    #             mblog_entry = blog.MicroblogItem(mblog)
    #             cache.append((_groups, mblog_entry))

    #     self.mblog_cache.extend(cache)
    #     if len(self.mblog_cache) > MAX_MBLOG_CACHE:
    #         del self.mblog_cache[0:len(self.mblog_cache - MAX_MBLOG_CACHE)]

    #     widget_list = [mblog_panel] if mblog_panel else self.widgets.getWidgets(blog.MicroblogPanel)

    #     for wid in widget_list:
    #         self.fillMicroblogPanel(wid, cache)

    #     # FIXME

    #     if self.initialised:
    #         return
    #     self.initialised = True  # initialisation phase is finished here
    #     for event_data in self.init_cache:  # so we have to send all the cached events
    #         self.personalEventHandler(*event_data)
    #     del self.init_cache

    # def loadOurMainEntries(self, index=0, mblog_panel=None):
    #     """Load a page of our own blogs from the cache or ask them to the
    #     backend. Then fill the panels with them.

    #     @param index (int): starting index of the blog page to retrieve.
    #     @param mblog_panel (MicroblogPanel): the panel to fill, or all if None.
    #     """
    #     delta = index - self.next_rsm_index
    #     if delta < 0:
    #         assert mblog_panel is not None
    #         self.fillMicroblogPanel(mblog_panel, self.mblog_cache[index:index + C.RSM_MAX_ITEMS])
    #         return

    #     def cb(result):
    #         self._ownBlogsFills(result, mblog_panel)

    #     rsm = {'max_': str(delta + C.RSM_MAX_ITEMS), 'index': str(self.next_rsm_index)}
    #     self.bridge.getMassiveMblogs('JID', [unicode(self.whoami.bare)], rsm, callback=cb, profile=C.PROF_KEY_NONE)
    #     self.next_rsm_index = index + C.RSM_MAX_ITEMS

    ## Signals callbacks ##

    # def personalEventHandler(self, sender, event_type, data):
        # elif event_type == 'MICROBLOG_DELETE':
        #     for wid in self.widgets.getWidgets(blog.MicroblogPanel):
        #         wid.removeEntry(data['type'], data['id'])

        #     if sender == self.whoami.bare and data['type'] == 'main_item':
        #         for index in xrange(0, len(self.mblog_cache)):
        #             entry = self.mblog_cache[index]
        #             if entry[1].id == data['id']:
        #                 self.mblog_cache.remove(entry)
        #                 break

    # def fillMicroblogPanel(self, mblog_panel, mblogs):
    #     """Fill a microblog panel with entries in cache

    #     @param mblog_panel: MicroblogPanel instance
    #     """
    #     #XXX: only our own entries are cached
    #     for cache_entry in mblogs:
    #         _groups, mblog_entry = cache_entry
    #         mblog_panel.addEntryIfAccepted(self.whoami.bare, *cache_entry)

    # def getEntityMBlog(self, entity):
    #     # FIXME: call this after a contact has been added to roster
    #     log.info(u"geting mblog for entity [%s]" % (entity,))
    #     for lib_wid in self.libervia_widgets:
    #         if isinstance(lib_wid, blog.MicroblogPanel):
    #             if lib_wid.isJidAccepted(entity):
    #                 self.bridge.call('getMassiveMblogs', lib_wid.massiveInsert, 'JID', [unicode(entity)])

    def displayWidget(self, class_, target, dropped=False, new_tab=None, *args, **kwargs):
        """Get or create a LiberviaWidget and select it. When the user dropped
        something, a new widget is always created, otherwise we look for an
        existing widget and re-use it if it's in the current tab.

        @arg class_(class): see quick_widgets.getOrCreateWidget
        @arg target: see quick_widgets.getOrCreateWidget
        @arg dropped(bool): if True, assume the widget has been dropped
        @arg new_tab(unicode): if not None, it holds the name of a new tab to
            open for the widget. If None, use the default behavior.
        @param args(list): optional args to create a new instance of class_
        @param kwargs(list): optional kwargs to create a new instance of class_
        @return: the widget
        """
        kwargs['profile'] = C.PROF_KEY_NONE

        if dropped:
            kwargs['on_new_widget'] = None
            kwargs['on_existing_widget'] = C.WIDGET_RECREATE
            wid = self.widgets.getOrCreateWidget(class_, target, *args, **kwargs)
            self.setSelected(wid)
            return wid

        if new_tab:
            kwargs['on_new_widget'] = None
            kwargs['on_existing_widget'] = C.WIDGET_RECREATE
            wid = self.widgets.getOrCreateWidget(class_, target, *args, **kwargs)
            self.tab_panel.addWidgetsTab(new_tab)
            self.addWidget(wid, tab_index=self.tab_panel.getWidgetCount() - 1)
            return wid

        kwargs['on_existing_widget'] = C.WIDGET_RAISE
        try:
            wid = self.widgets.getOrCreateWidget(class_, target, *args, **kwargs)
        except quick_widgets.WidgetAlreadyExistsError:
            kwargs['on_existing_widget'] = C.WIDGET_KEEP
            wid = self.widgets.getOrCreateWidget(class_, target, *args, **kwargs)
            widgets_panel = wid.getParent(libervia_widget.WidgetsPanel, expect=False)
            if widgets_panel is None:
                # The widget exists but is hidden
                self.addWidget(wid)
            elif widgets_panel != self.tab_panel.getCurrentPanel():
                # the widget is on an other tab, so we add a new one here
                kwargs['on_existing_widget'] = C.WIDGET_RECREATE
                wid = self.widgets.getOrCreateWidget(class_, target, *args, **kwargs)
                self.addWidget(wid)
        self.setSelected(wid)
        return wid

    def isHidden(self):
        """Tells if the frontend window is hidden.

        @return bool
        """
        return self.notification.isHidden()

    def updateAlertsCounter(self, extra_inc=0):
        """Update the over whole alerts counter

        @param extra_inc (int): extra counter
        """
        extra = self.alerts_counter.extra + extra_inc
        self.alerts_counter.update(self.alerts_count, extra=extra)

    def _paramUpdate(self, name, value, category, refresh=True):
        """This is called when the paramUpdate signal is received, but also
        during initialization when the UI parameters values are retrieved.
        @param refresh: set to True to refresh the general UI
        """
        for param_cat, param_name in C.CACHED_PARAMS:
            if name == param_name and category == param_cat:
                self.cached_params[(category, name)] = value
                if refresh:
                    self.refresh()
                break

    def getCachedParam(self, category, name):
        """Return a parameter cached value (e.g for refreshing the UI)

        @param category (unicode): the parameter category
        @pram name (unicode): the parameter name
        """
        return self.cached_params[(category, name)] if (category, name) in self.cached_params else None

    def sendError(self, errorData):
        dialog.InfoDialog("Error while sending message",
                          "Your message can't be sent", Width="400px").center()
        log.error("sendError: %s" % unicode(errorData))

    def showWarning(self, type_=None, msg=None):
        """Display a popup information message, e.g. to notify the recipient of a message being composed.
        If type_ is None, a popup being currently displayed will be hidden.
        @type_: a type determining the CSS style to be applied (see WarningPopup.showWarning)
        @msg: message to be displayed
        """
        if not hasattr(self, "warning_popup"):
            self.warning_popup = main_panel.WarningPopup()
        self.warning_popup.showWarning(type_, msg)

    def showDialog(self, message, title="", type_="info", answer_cb=None, answer_data=None):
        if type_ == 'info':
            popup = dialog.InfoDialog(unicode(title), unicode(message), callback=answer_cb)
        elif type_ == 'error':
            popup = dialog.InfoDialog(unicode(title), unicode(message), callback=answer_cb)
        elif type_ == 'yes/no':
            popup = dialog.ConfirmDialog(lambda answer: answer_cb(answer, answer_data),
                                         text=unicode(message), title=unicode(title))
            popup.cancel_button.setText(_("No"))
        else:
            popup = dialog.InfoDialog(unicode(title), unicode(message), callback=answer_cb)
            log.error(_('unmanaged dialog type: %s'), type_)
        popup.show()

    def dialogFailure(self, failure):
        dialog.InfoDialog("Error",
                          unicode(failure), Width="400px").center()

    def showFailure(self, err_data, msg=''):
        """Show a failure that has been returned by an asynchronous bridge method.

        @param failure (defer.Failure): Failure instance
        @param msg (unicode): message to display
        """
        # FIXME: message is lost by JSON, we hardcode it for now... remove msg argument when possible
        err_code, err_obj = err_data
        title = err_obj['message']['faultString'] if isinstance(err_obj['message'], dict) else err_obj['message']
        self.showDialog(msg, title, 'error')

    def onJoinMUCFailure(self, err_data):
        """Show a failure that has been returned when trying to join a room.

        @param failure (defer.Failure): Failure instance
        """
        # FIXME: remove asap, see self.showFailure
        err_code, err_obj = err_data
        if err_obj["data"] == "AlreadyJoinedRoom":
            msg = _(u"The room has already been joined.")
            err_obj["message"] = _(u"Information")
        else:
            msg = _(u"Invalid room identifier. Please give a room short or full identifier like 'room' or '%s'.") % self.default_muc
            err_obj["message"] = _(u"Error")
        self.showFailure(err_data, msg)


if __name__ == '__main__':
    app = SatWebFrontend()
    app.onModuleLoad()
    host_listener.callListeners(app)
