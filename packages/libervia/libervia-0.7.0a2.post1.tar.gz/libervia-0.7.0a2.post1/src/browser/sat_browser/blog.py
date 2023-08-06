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
from sat.tools.common import data_format
from sat.core.i18n import _ #, D_

from pyjamas.ui.SimplePanel import SimplePanel
from pyjamas.ui.VerticalPanel import VerticalPanel
from pyjamas.ui.ScrollPanel import ScrollPanel
from pyjamas.ui.HorizontalPanel import HorizontalPanel
from pyjamas.ui.Label import Label
from pyjamas.ui.HTML import HTML
from pyjamas.ui.Image import Image
from pyjamas.ui.ClickListener import ClickHandler
from pyjamas.ui.FlowPanel import FlowPanel
from pyjamas.ui import KeyboardListener as keyb
from pyjamas.ui.KeyboardListener import KeyboardHandler
from pyjamas.ui.FocusListener import FocusHandler
from pyjamas.ui.MouseListener import MouseHandler
from pyjamas.Timer import Timer

from datetime import datetime

import html_tools
import dialog
import richtext
import editor_widget
import libervia_widget
from constants import Const as C
from sat_frontends.quick_frontend import quick_widgets
from sat_frontends.quick_frontend import quick_blog

unicode = str # XXX: pyjamas doesn't manage unicode
ENTRY_RICH = (C.ENTRY_MODE_RICH, C.ENTRY_MODE_XHTML)


class Entry(quick_blog.Entry, VerticalPanel, ClickHandler, FocusHandler, KeyboardHandler):
    """Graphical representation of a quick_blog.Item"""

    def __init__(self, manager, item_data=None, comments_data=None, service=None, node=None):
        quick_blog.Entry.__init__(self, manager, item_data, comments_data, service, node)

        VerticalPanel.__init__(self)

        self.panel = FlowPanel()
        self.panel.setStyleName('mb_entry')

        self.header = HorizontalPanel(StyleName='mb_entry_header')
        self.panel.add(self.header)

        self.entry_actions = VerticalPanel()
        self.entry_actions.setStyleName('mb_entry_actions')
        self.panel.add(self.entry_actions)

        entry_avatar = SimplePanel()
        entry_avatar.setStyleName('mb_entry_avatar')
        author_jid = self.author_jid
        self.avatar = Image(self.blog.host.getAvatarURL(author_jid) if author_jid is not None else C.DEFAULT_AVATAR_URL)
        # TODO: show a warning icon if author is not validated
        entry_avatar.add(self.avatar)
        self.panel.add(entry_avatar)

        self.entry_dialog = VerticalPanel()
        self.entry_dialog.setStyleName('mb_entry_dialog')
        self.panel.add(self.entry_dialog)

        self.comments_panel = None
        self._current_comment = None

        self.add(self.panel)
        ClickHandler.__init__(self)
        self.addClickListener(self)

        self.refresh()
        self.displayed = False # True when entry is added to parent
        if comments_data:
            self.addComments(comments_data)

    def refresh(self):
        self.comment_label = None
        self.update_label = None
        self.delete_label = None
        self.header.clear()
        self.entry_dialog.clear()
        self.entry_actions.clear()
        self._setHeader()
        self._setBubble()
        self._setIcons()

    def _setHeader(self):
        """Set the entry header."""
        if not self.new:
            author = html_tools.html_sanitize(unicode(self.item.author))
            author_jid = html_tools.html_sanitize(unicode(self.item.author_jid))
            if author_jid and not self.item.author_verified:
                author_jid += u' <span style="color:red; font-weight: bold;">⚠</span>'
            if author:
                author += " &lt;%s&gt;" % author_jid
            elif author_jid:
                author = author_jid
            else:
                author = _("<unknown author>")

            update_text = u" — ✍ " + "<span class='mb_entry_timestamp'>%s</span>" % datetime.fromtimestamp(self.item.updated)
            self.header.add(HTML("""<span class='mb_entry_header_info'>
                                      <span class='mb_entry_author'>%(author)s</span> on
                                      <span class='mb_entry_timestamp'>%(published)s</span>%(updated)s
                                    </span>""" % {'author': author,
                                                  'published': datetime.fromtimestamp(self.item.published) if self.item.published is not None else '',
                                                  'updated': update_text if self.item.published != self.item.updated else ''
                                                  }))
            if self.item.comments:
                self.show_comments_link = HTML('')
                self.header.add(self.show_comments_link)

    def _setBubble(self):
        """Set the bubble displaying the initial content."""
        content = {'text': self.item.content_xhtml if self.item.content_xhtml else self.item.content or '',
                   'title': self.item.title_xhtml if self.item.title_xhtml else self.item.title or ''}
        data_format.iter2dict('tag', self.item.tags, content)

        if self.mode == C.ENTRY_MODE_TEXT:
            # assume raw text message have no title
            self.bubble = editor_widget.LightTextEditor(content, modifiedCb=self._modifiedCb, afterEditCb=self._afterEditCb, options={'no_xhtml': True})
        elif self.mode in ENTRY_RICH:
            content['syntax'] = C.SYNTAX_XHTML
            if self.new:
                options = []
            elif self.item.author_jid == self.blog.host.whoami.bare:
                options = ['update_msg']
            else:
                options = ['read_only']
            self.bubble = richtext.RichTextEditor(self.blog.host, content, modifiedCb=self._modifiedCb, afterEditCb=self._afterEditCb, options=options)
        else:
            log.error("Bad entry mode: %s" % self.mode)
        self.bubble.addStyleName("bubble")
        self.entry_dialog.add(self.bubble)
        self.bubble.addEditListener(self._showWarning) # FIXME: remove edit listeners
        self.setEditable(self.editable)

    def _setIcons(self):
        """Set the entry icons (delete, update, comment)"""
        if self.new:
            return

        def addIcon(label, title):
            label = Label(label)
            label.setTitle(title)
            label.addClickListener(self)
            self.entry_actions.add(label)
            return label

        if self.item.comments:
            self.comment_label = addIcon(u"↶", "Comment this message")
            self.comment_label.setStyleName('mb_entry_action_larger')
        else:
            self.comment_label = None
        is_publisher = self.item.author_jid == self.blog.host.whoami.bare
        if is_publisher:
            self.update_label = addIcon(u"✍", "Edit this message")
            # TODO: add delete button if we are the owner of the node
            self.delete_label = addIcon(u"✗", "Delete this message")
        else:
            self.update_label = self.delete_label = None

    def _createCommentsPanel(self):
        """Create the panel if it doesn't exists"""
        if self.comments_panel is None:
            self.comments_panel = VerticalPanel()
            self.comments_panel.setStyleName('microblogPanel')
            self.comments_panel.addStyleName('subPanel')
            self.add(self.comments_panel)

    def setEditable(self, editable=True):
        """Toggle the bubble between display and edit mode.

        @param editable (bool)
        """
        self.editable = editable
        self.bubble.edit(self.editable)
        self.updateIconsAndButtons()

    def updateIconsAndButtons(self):
        """Set the visibility of the icons and the button to switch between blog and microblog."""
        try:
            self.bubble_commands.removeFromParent()
        except (AttributeError, TypeError):
            pass
        if self.editable:
            if self.mode == C.ENTRY_MODE_TEXT:
                html = _(u'<a style="color: blue;">switch to blog</a>')
                title = _(u'compose a rich text message with a title - suitable for writing articles')
            else:
                html = _(u'<a style="color: blue;">switch to microblog</a>')
                title = _(u'compose a short message without title - suitable for sharing news')
            toggle_syntax_button = HTML(html, Title=title)
            toggle_syntax_button.addClickListener(self.toggleContentSyntax)
            toggle_syntax_button.addStyleName('mb_entry_toggle_syntax')
            toggle_syntax_button.setStyleAttribute('top', '-20px')  # XXX: need to force CSS
            toggle_syntax_button.setStyleAttribute('left', '-20px')

            self.bubble_commands = HorizontalPanel(Width="100%")

            if self.mode == C.ENTRY_MODE_TEXT:
                publish_button = HTML(_(u'<a style="color: blue;">shift + enter to publish</a>'), Title=_(u"... or click here"))
                publish_button.addStyleName('mb_entry_publish_button')
                publish_button.addClickListener(lambda dummy: self.bubble.edit(False))
                publish_button.setStyleAttribute('top', '-20px')  # XXX: need to force CSS
                publish_button.setStyleAttribute('left', '20px')
                self.bubble_commands.add(publish_button)

            self.bubble_commands.add(toggle_syntax_button)
            self.entry_dialog.add(self.bubble_commands)

        # hide these icons while editing
        try:
            self.delete_label.setVisible(not self.editable)
        except (TypeError, AttributeError):
            pass
        try:
            self.update_label.setVisible(not self.editable)
        except (TypeError, AttributeError):
            pass
        try:
            self.comment_label.setVisible(not self.editable)
        except (TypeError, AttributeError):
            pass

    def onClick(self, sender):

        if sender == self:
            self.blog.setSelectedEntry(self)
        elif sender == self.delete_label:
            self._onRetractClick()
        elif sender == self.update_label:
            self.setEditable(True)
        elif sender == self.comment_label:
            self._onCommentClick()
        # elif sender == self.show_comments_link:
        #     self._blog_panel.loadAllCommentsForEntry(self)

    def _modifiedCb(self, content):
        """Send the new content to the backend

        @return: False to restore the original content if a deletion has been cancelled
        """
        if not content['text']:  # previous content has been emptied
            if not self.new:
                self._onRetractClick()
            return False

        self.item.content = self.item.content_rich = self.item.content_xhtml = None
        self.item.title = self.item.title_rich = self.item.title_xhtml = None

        if self.mode in ENTRY_RICH:
            # TODO: if the user change his parameters after the message edition started,
            # the message syntax could be different then the current syntax: pass the
            # message syntax in mb_data for the frontend to use it instead of current syntax.
            self.item.content_rich = content['text']  # XXX: this also works if the syntax is XHTML
            self.item.title = content['title']
            self.item.tags = list(data_format.dict2iter('tag', content))
        else:
            self.item.content = content['text']

        self.send()

        return True

    def _afterEditCb(self, content):
        """Post edition treatments

        Remove the entry if it was an empty one (used for creating a new blog post).
        Data for the actual new blog post will be received from the bridge
        @param content(dict): edited content
        """
        if self.new:
            if self.level == 0:
                # we have a main item, we keep the edit entry
                self.reset(None)
                # FIXME: would be better to reset bubble
                # but bubble.setContent() doesn't seem to work
                self.bubble.removeFromParent()
                self._setBubble()
            else:
                # we don't keep edit entries for comments
                self.delete()
        else:
            self.editable = False
            self.updateIconsAndButtons()

    def _showWarning(self, sender, keycode, modifiers):
        if keycode == keyb.KEY_ENTER & keyb.MODIFIER_SHIFT: # FIXME: fix edit_listeners, it's dirty (we have to check keycode/modifiers twice !)
            self.blog.host.showWarning(None, None)
        else:
            # self.blog.host.showWarning(*self.blog.getWarningData(self.type == 'comment'))
            self.blog.host.showWarning(*self.blog.getWarningData(False)) # FIXME: comments are not yet reimplemented

    def _onRetractClick(self):
        """Ask confirmation then retract current entry."""
        assert not self.new

        def confirm_cb(answer):
            if answer:
                self.retract()

        entry_type = _("message") if self.level == 0 else _("comment")
        and_comments = _(" All comments will be also deleted!") if self.item.comments else ""
        text = _("Do you really want to delete this {entry_type}?{and_comments}").format(
                entry_type=entry_type, and_comments=and_comments)
        dialog.ConfirmDialog(confirm_cb, text=text).show()

    def _onCommentClick(self):
        """Add an empty entry for a new comment"""
        if self._current_comment is None:
            if not self.item.comments_service or not self.item.comments_node:
                log.warning("Invalid service and node for comments, can't create a comment")
            self._current_comment = self.addEntry(editable=True, service=self.item.comments_service, node=self.item.comments_node, edit_entry=True)
        self.blog.setSelectedEntry(self._current_comment, True)
        self._current_comment.bubble.setFocus(True)  # FIXME: should be done elsewhere (automatically)?

    def _changeMode(self, original_content, text):
        self.mode = C.ENTRY_MODE_RICH if self.mode == C.ENTRY_MODE_TEXT else C.ENTRY_MODE_TEXT
        if self.mode in ENTRY_RICH and not text:
            text = ' ' # something different than empty string is needed to initialize the rich text editor
        self.item.content = text
        if self.mode in ENTRY_RICH:
            self.item.content_rich = text  # XXX: this also works if the syntax is XHTML
            self.bubble.setDisplayContent()  # needed in case the edition is aborted, to not end with an empty bubble
        else:
            self.item.content_xhtml = ''
        self.bubble.removeFromParent()
        self._setBubble()
        self.bubble.setOriginalContent(original_content)

    def toggleContentSyntax(self):
        """Toggle the editor between raw and rich text"""
        original_content = self.bubble.getOriginalContent()
        rich = self.mode in ENTRY_RICH
        if rich:
            original_content['syntax'] = C.SYNTAX_XHTML

        text = self.bubble.getContent()['text']

        if not text.strip():
            self._changeMode(original_content,'')
        else:
            if rich:
                def confirm_cb(answer):
                    if answer:
                        self.blog.host.bridge.syntaxConvert(text, C.SYNTAX_CURRENT, C.SYNTAX_TEXT, profile=None,
                                                            callback=lambda converted: self._changeMode(original_content, converted))
                dialog.ConfirmDialog(confirm_cb, text=_("Do you really want to lose the title and text formatting?")).show()
            else:
                self.blog.host.bridge.syntaxConvert(text, C.SYNTAX_TEXT, C.SYNTAX_XHTML, profile=None,
                                                    callback=lambda converted: self._changeMode(original_content, converted))

    def update(self, entry=None):
        """Update comments"""
        self._createCommentsPanel()
        self.entries.sort(key=lambda entry: entry.item.published)
        # we put edit_entry at the end
        edit_entry = [] if self.edit_entry is None else [self.edit_entry]
        for idx, entry in enumerate(self.entries + edit_entry):
            if not entry.displayed:
                self.comments_panel.insert(entry, idx)
                entry.displayed = True

    def delete(self):
        quick_blog.Entry.delete(self)

        # _current comment is specific to libervia, we remove it
        if isinstance(self.manager, Entry):
            self.manager._current_comment = None

        # now we remove the pyjamas widgets
        parent = self.parent
        assert isinstance(parent, VerticalPanel)
        self.removeFromParent()
        if not parent.children:
            # the vpanel is empty, we remove it
            parent.removeFromParent()
            try:
                if self.manager.comments_panel == parent:
                    self.manager.comments_panel = None
            except AttributeError:
                assert isinstance(self.manager, quick_blog.QuickBlog)


class Blog(quick_blog.QuickBlog, libervia_widget.LiberviaWidget, MouseHandler):
    """Panel used to show microblog"""
    warning_msg_public = "This message will be <b>PUBLIC</b> and everybody will be able to see it, even people you don't know"
    warning_msg_group = "This message will be published for all the people of the following groups: <span class='warningTarget'>%s</span>"

    def __init__(self, host, targets, profiles=None):
        quick_blog.QuickBlog.__init__(self, host, targets, C.PROF_KEY_NONE)
        title = ", ".join(targets) if targets else "Blog"
        libervia_widget.LiberviaWidget.__init__(self, host, title, selectable=True)
        MouseHandler.__init__(self)
        self.vpanel = VerticalPanel()
        self.vpanel.setStyleName('microblogPanel')
        self.setWidget(self.vpanel)
        if ((self._targets_type == C.ALL and self.host.mblog_available) or
            (self._targets_type == C.GROUP and self.host.groupblog_available)):
            self.addEntry(editable=True, edit_entry=True)

        self.getAll()

        # self.footer = HTML('', StyleName='microblogPanel_footer')
        # self.footer.waiting = False
        # self.footer.addClickListener(self)
        # self.footer.addMouseListener(self)
        # self.vpanel.add(self.footer)
        # self.next_rsm_index = 0

    def __str__(self):
        return u"Blog Widget [targets: {}, profile: {}]".format(", ".join(self.targets) if self.targets else "meta blog", self.profile)

    def update(self):
        self.entries.sort(key=lambda entry: entry.item.published, reverse=True)

        start_idx = 0
        if self.edit_entry is not None:
            start_idx = 1
            if not self.edit_entry.displayed:
                self.vpanel.insert(self.edit_entry, 0)
                self.edit_entry.displayed = True

        # XXX: enumerate is buggued in pyjamas (start is not used)
        #       we have to use idx
        idx = start_idx
        for entry in self.entries:
            if not entry.displayed:
                self.vpanel.insert(entry, idx)
                entry.displayed = True
            idx += 1

    # def onDelete(self):
    #     quick_widgets.QuickWidget.onDelete(self)
    #     self.host.removeListener('avatar', self.avatarListener)

    # def onAvatarUpdate(self, jid_, hash_, profile):
    #     """Called on avatar update events

    #     @param jid_: jid of the entity with updated avatar
    #     @param hash_: hash of the avatar
    #     @param profile: %(doc_profile)s
    #     """
    #     whoami = self.host.profiles[self.profile].whoami
    #     if self.isJidAccepted(jid_) or jid_.bare == whoami.bare:
    #         self.updateValue('avatar', jid_, hash_)

    @staticmethod
    def onGroupDrop(host, targets):
        """Create a microblog panel for one, several or all contact groups.

        @param host (SatWebFrontend): the SatWebFrontend instance
        @param targets (tuple(unicode)): tuple of groups (empty for "all groups")
        @return: the created MicroblogPanel
        """
        # XXX: pyjamas doesn't support use of cls directly
        widget = host.displayWidget(Blog, targets, dropped=True)
        return widget

    # @property
    # def accepted_groups(self):
    #     """Return a set of the accepted groups"""
    #     return set().union(*self.targets)

    def getWarningData(self, comment):
        """
        @param comment: set to True if the composed message is a comment
        @return: a couple (type, msg) for calling self.host.showWarning"""
        if comment:
            return ("PUBLIC", "This is a <span class='warningTarget'>comment</span> and keep the initial post visibility, so it is potentialy public")
        elif self._targets_type == C.ALL:
            # we have a meta MicroblogPanel, we publish publicly
            return ("PUBLIC", self.warning_msg_public)
        else:
            # FIXME: manage several groups
            return (self._targets_type, self.warning_msg_group % ' '.join(self.targets))

    def ensureVisible(self, entry):
        """Scroll to an entry to ensure its visibility

        @param entry (MicroblogEntry): the entry
        """
        current = entry
        while True:
            parent = current.getParent()
            if parent is None:
                log.warning("Can't find any parent ScrollPanel")
                return
            elif isinstance(parent, ScrollPanel):
                parent.ensureVisible(entry)
                return
            else:
                current = parent

    def setSelectedEntry(self, entry, ensure_visible=False):
        """Select an entry.

        @param entry (MicroblogEntry): the entry to select
        @param ensure_visible (boolean): if True, also scroll to the entry
        """
        if ensure_visible:
            self.ensureVisible(entry)

        entry.addStyleName('selected_entry')  # blink the clicked entry
        clicked_entry = entry  # entry may be None when the timer is done
        Timer(500, lambda timer: clicked_entry.removeStyleName('selected_entry'))

    # def updateValue(self, type_, jid_, value):
    #     """Update a jid value in entries

    #     @param type_: one of 'avatar', 'nick'
    #     @param jid_(jid.JID): jid concerned
    #     @param value: new value"""
    #     assert isinstance(jid_, jid.JID) # FIXME: temporary
    #     def updateVPanel(vpanel):
    #         avatar_url = self.host.getAvatarURL(jid_)
    #         for child in vpanel.children:
    #             if isinstance(child, MicroblogEntry) and child.author == jid_:
    #                 child.updateAvatar(avatar_url)
    #             elif isinstance(child, VerticalPanel):
    #                 updateVPanel(child)
    #     if type_ == 'avatar':
    #         updateVPanel(self.vpanel)

    # def onClick(self, sender):
    #     if sender == self.footer:
    #         self.loadMoreMainEntries()

    # def onMouseEnter(self, sender):
    #     if sender == self.footer:
    #         self.loadMoreMainEntries()


libervia_widget.LiberviaWidget.addDropKey("GROUP", lambda host, item: Blog.onGroupDrop(host, (item,)))
libervia_widget.LiberviaWidget.addDropKey("CONTACT_TITLE", lambda host, item: Blog.onGroupDrop(host, ()))
quick_blog.registerClass("ENTRY", Entry)
quick_widgets.register(quick_blog.QuickBlog, Blog)
