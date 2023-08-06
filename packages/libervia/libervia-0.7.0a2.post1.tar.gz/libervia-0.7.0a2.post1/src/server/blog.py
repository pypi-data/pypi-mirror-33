#!/usr/bin/python
# -*- coding: utf-8 -*-

# Libervia: a Salut à Toi frontend
# Copyright (C) 2011-2018 Jérôme Poisson <goffi@goffi.org>
# Copyright (C) 2013-2016 Adrien Cossa <souliane@mailoo.org>

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

from sat.core.i18n import _, D_
from sat_frontends.tools.strings import addURLToText, fixXHTMLLinks
from sat.core.log import getLogger

log = getLogger(__name__)
from sat.tools.common import data_format
from sat.tools import xml_tools
from dbus.exceptions import DBusException
from twisted.internet import defer
from twisted.web import server
from twisted.web.resource import Resource
from twisted.words.protocols.jabber.jid import JID
from twisted.words.xish import domish
from jinja2 import Environment, PackageLoader
from datetime import datetime
import re
import os
import sys
import urllib

from libervia.server.html_tools import sanitizeHtml, convertNewLinesToXHTML
from libervia.server.constants import Const as C

NS_ATOM = "http://www.w3.org/2005/Atom"
PARAMS_TO_GET = (
    C.STATIC_BLOG_PARAM_TITLE,
    C.STATIC_BLOG_PARAM_BANNER,
    C.STATIC_BLOG_PARAM_KEYWORDS,
    C.STATIC_BLOG_PARAM_DESCRIPTION,
)
re_strip_empty_div = re.compile(r"<div ?/>|<div> *?</div>")

# TODO: check disco features and use max_items when RSM is not available
# FIXME: change navigation links handling, this is is fragile
# XXX: this page will disappear, LiberviaPage will be used instead
# TODO: delete this page and create a compatibility page for links


def getDefaultQueryData(request):
    """Return query data which must be present in all links

    @param request(twisted.web.http.Request): request instance comming from render
    @return (dict): a dict with values as expected by urllib.urlencode
    """
    default_query_data = {}
    try:
        default_query_data["tag"] = request.extra_dict[
            "mam_filter_{}".format(C.MAM_FILTER_CATEGORY)
        ].encode("utf-8")
    except KeyError:
        pass
    return default_query_data


def _quote(value):
    """Quote a value for use in url

    @param value(unicode): value to quote
    @return (str): quoted value
    """
    return urllib.quote(value.encode("utf-8"), "")


def _unquote(quoted_value):
    """Unquote a value coming from url

    @param unquote_value(str): value to unquote
    @return (unicode): unquoted value
    """
    assert not isinstance(quoted_value, unicode)
    return urllib.unquote(quoted_value).decode("utf-8")


def _urlencode(query):
    """Same as urllib.urlencode, but use '&amp;' instead of '&'"""
    return "&amp;".join(
        [
            "{}={}".format(urllib.quote_plus(str(k)), urllib.quote_plus(str(v)))
            for k, v in query.iteritems()
        ]
    )


class TemplateProcessor(object):

    THEME = "default"

    def __init__(self, host):
        self.host = host

        # add Libervia's themes directory to the python path
        sys.path.append(os.path.dirname(os.path.normpath(self.host.themes_dir)))
        themes = os.path.basename(os.path.normpath(self.host.themes_dir))
        self.env = Environment(loader=PackageLoader(themes, self.THEME))

    def useTemplate(self, request, tpl, data=None):
        theme_url = os.path.join("/", C.THEMES_URL, self.THEME)

        data_ = {
            "images": os.path.join(theme_url, "images"),
            "styles": os.path.join(theme_url, "styles"),
        }
        if data:
            data_.update(data)

        template = self.env.get_template("{}.html".format(tpl))
        return template.render(**data_).encode("utf-8")


class MicroBlog(Resource, TemplateProcessor):
    isLeaf = True

    def __init__(self, host):
        self.host = host
        Resource.__init__(self)
        TemplateProcessor.__init__(self, host)
        self.avatars_cache = {}

    def _avatarPathToUrl(self, avatar, request, bare_jid_s):
        filename = os.path.basename(avatar)
        avatar_url = os.path.join(self.host.service_cache_url, filename)
        self.avatars_cache[bare_jid_s] = avatar_url
        return avatar_url

    def getAvatarURL(self, pub_jid, request):
        """Return avatar of a jid if in cache, else ask for it.

        @param pub_jid (JID): publisher JID
        @return: deferred avatar URL (unicode)
        """
        bare_jid_s = pub_jid.userhost()
        try:
            url = self.avatars_cache[bare_jid_s]
        except KeyError:
            self.avatars_cache[
                bare_jid_s
            ] = ""  # avoid to request the vcard several times
            d = self.host.bridgeCall(
                "avatarGet", bare_jid_s, False, False, C.SERVICE_PROFILE
            )
            d.addCallback(self._avatarPathToUrl, request, bare_jid_s)
            return d
        return defer.succeed(url if url else C.DEFAULT_AVATAR_URL)

    def render_GET(self, request):
        if not request.postpath or len(request.postpath) > 2:
            return self.useTemplate(
                request, "static_blog_error", {"message": "You must indicate a nickname"}
            )

        prof_requested = _unquote(request.postpath[0])

        try:
            prof_found = self.host.bridge.profileNameGet(prof_requested)
        except DBusException:
            prof_found = None
        if not prof_found or prof_found == C.SERVICE_PROFILE:
            return self.useTemplate(
                request, "static_blog_error", {"message": "Invalid nickname"}
            )

        d = defer.Deferred()
        # TODO: jid caching
        self.host.bridge.asyncGetParamA(
            "JabberID",
            "Connection",
            "value",
            profile_key=prof_found,
            callback=d.callback,
            errback=d.errback,
        )
        d.addCallback(self.render_gotJID, request, prof_found)
        return server.NOT_DONE_YET

    def render_gotJID(self, pub_jid_s, request, profile):
        pub_jid = JID(pub_jid_s)

        request.extra_dict = {}  # will be used for RSM and MAM
        self.parseURLParams(request)
        if request.item_id:
            # FIXME: this part seems useless
            # we want a specific item
            # item_ids = [request.item_id]
            # max_items = 1
            max_items = C.NO_LIMIT  # FIXME
        else:
            # max_items = int(request.extra_dict['rsm_max']) # FIXME
            max_items = C.NO_LIMIT
            # TODO: use max_items only when RSM is not available

        if request.atom:
            request.extra_dict.update(request.mam_extra)
            self.getAtom(
                pub_jid,
                max_items,
                request.extra_dict,
                request.extra_comments_dict,
                request,
                profile,
            )

        elif request.item_id:
            # we can't merge mam_extra now because we'll use item_ids
            self.getItemById(
                pub_jid,
                request.item_id,
                request.extra_dict,
                request.extra_comments_dict,
                request,
                profile,
            )
        else:
            request.extra_dict.update(request.mam_extra)
            self.getItems(
                pub_jid,
                max_items,
                request.extra_dict,
                request.extra_comments_dict,
                request,
                profile,
            )

    ## URL parsing

    def parseURLParams(self, request):
        """Parse the request URL parameters.

        @param request: HTTP request
        """
        if len(request.postpath) > 1:
            if request.postpath[1] == "atom.xml":  # return the atom feed
                request.atom = True
                request.item_id = None
            else:
                request.atom = False
                request.item_id = _unquote(request.postpath[1])
        else:
            request.item_id = None
            request.atom = False

        self.parseURLParamsRSM(request)
        # XXX: request.display_single is True when only one blog post is visible
        request.display_single = (request.item_id is not None) or int(
            request.extra_dict["rsm_max"]
        ) == 1
        self.parseURLParamsCommentsRSM(request)
        self.parseURLParamsMAM(request)

    def parseURLParamsRSM(self, request):
        """Parse RSM request data from the URL parameters for main items

        fill request.extra_dict accordingly
        @param request: HTTP request
        """
        if request.item_id:  # XXX: item_id and RSM are not compatible
            return
        try:
            rsm_max = int(request.args["max"][0])
            if rsm_max > C.STATIC_RSM_MAX_LIMIT:
                log.warning(u"Request with rsm_max over limit ({})".format(rsm_max))
                rsm_max = C.STATIC_RSM_MAX_LIMIT
            request.extra_dict["rsm_max"] = unicode(rsm_max)
        except (ValueError, KeyError):
            request.extra_dict["rsm_max"] = unicode(C.STATIC_RSM_MAX_DEFAULT)
        try:
            request.extra_dict["rsm_index"] = request.args["index"][0]
        except (ValueError, KeyError):
            try:
                request.extra_dict["rsm_before"] = request.args["before"][0].decode(
                    "utf-8"
                )
            except KeyError:
                try:
                    request.extra_dict["rsm_after"] = request.args["after"][0].decode(
                        "utf-8"
                    )
                except KeyError:
                    pass

    def parseURLParamsCommentsRSM(self, request):
        """Parse RSM request data from the URL parameters for comments

        fill request.extra_dict accordingly
        @param request: HTTP request
        """
        request.extra_comments_dict = {}
        if request.display_single:
            try:
                rsm_max = int(request.args["comments_max"][0])
                if rsm_max > C.STATIC_RSM_MAX_LIMIT:
                    log.warning(u"Request with rsm_max over limit ({})".format(rsm_max))
                    rsm_max = C.STATIC_RSM_MAX_LIMIT
                request.extra_comments_dict["rsm_max"] = unicode(rsm_max)
            except (ValueError, KeyError):
                request.extra_comments_dict["rsm_max"] = unicode(
                    C.STATIC_RSM_MAX_COMMENTS_DEFAULT
                )
        else:
            request.extra_comments_dict["rsm_max"] = "0"

    def parseURLParamsMAM(self, request):
        """Parse MAM request data from the URL parameters for main items

        fill request.extra_dict accordingly
        @param request: HTTP request
        """
        # XXX: we use a separate dict for MAM as the filters are not used
        #      when display_single is set (because it then use item_ids which
        #      can't be used with MAM), but it is still used in this case
        #      for navigation links.
        request.mam_extra = {}
        try:
            request.mam_extra[
                "mam_filter_{}".format(C.MAM_FILTER_CATEGORY)
            ] = request.args["tag"][0].decode("utf-8")
        except KeyError:
            pass

    ## Items retrieval

    def getItemById(
        self, pub_jid, item_id, extra_dict, extra_comments_dict, request, profile
    ):
        """

        @param pub_jid (jid.JID): publisher JID
        @param item_id(unicode): ID of the item to retrieve
        @param extra_dict (dict): extra configuration for initial items only
        @param extra_comments_dict (dict): extra configuration for comments only
        @param request: HTTP request
        @param profile
        """

        def gotItems(items):
            items, metadata = items
            item = items[0]  # assume there's only one item

            def gotMetadata(result):
                dummy, rsm_metadata = result
                try:
                    metadata["rsm_count"] = rsm_metadata["rsm_count"]
                except KeyError:
                    pass
                try:
                    metadata["rsm_index"] = unicode(int(rsm_metadata["rsm_index"]) - 1)
                except KeyError:
                    pass

                metadata["rsm_first"] = metadata["rsm_last"] = item["id"]

                def gotComments(comments):
                    # at this point we can merge mam dict
                    request.extra_dict.update(request.mam_extra)
                    # build the items as self.getItems would do it (and as self.renderHTML expects them to be)
                    comments = [
                        (
                            item["comments_service"],
                            item["comments_node"],
                            "",
                            comments[0],
                            comments[1],
                        )
                    ]
                    self.renderHTML(
                        [(item, comments)], metadata, request, pub_jid, profile
                    )

                # get the comments
                # max_comments = int(extra_comments_dict['rsm_max']) # FIXME
                max_comments = C.NO_LIMIT
                # TODO: use max_comments only when RSM is not available
                self.host.bridge.mbGet(
                    item["comments_service"],
                    item["comments_node"],
                    max_comments,
                    [],
                    extra_comments_dict,
                    C.SERVICE_PROFILE,
                    callback=gotComments,
                    errback=lambda failure: self.renderError(failure, request, pub_jid),
                )

            # XXX: retrieve RSM information related to the main item. We can't do it while
            # retrieving the item, because item_ids and rsm should not be used together.
            self.host.bridge.mbGet(
                pub_jid.userhost(),
                "",
                0,
                [],
                {"rsm_max": "1", "rsm_after": item["id"]},
                C.SERVICE_PROFILE,
                callback=gotMetadata,
                errback=lambda failure: self.renderError(failure, request, pub_jid),
            )

        # get the main item
        self.host.bridge.mbGet(
            pub_jid.userhost(),
            "",
            0,
            [item_id],
            extra_dict,
            C.SERVICE_PROFILE,
            callback=gotItems,
            errback=lambda failure: self.renderError(failure, request, pub_jid),
        )

    def getItems(
        self, pub_jid, max_items, extra_dict, extra_comments_dict, request, profile
    ):
        """

        @param pub_jid (jid.JID): publisher JID
        @param max_items(int): maximum number of item to get, C.NO_LIMIT for no limit
        @param extra_dict (dict): extra configuration for initial items only
        @param extra_comments_dict (dict): extra configuration for comments only
        @param request: HTTP request
        @param profile
        """

        def getResultCb(data, rt_session):
            remaining, results = data
            # we have requested one node only
            assert remaining == 0
            assert len(results) == 1
            service, node, failure, items, metadata = results[0]
            if failure:
                self.renderError(failure, request, pub_jid)
            else:
                self.renderHTML(items, metadata, request, pub_jid, profile)

        def getResult(rt_session):
            self.host.bridge.mbGetFromManyWithCommentsRTResult(
                rt_session,
                C.SERVICE_PROFILE,
                callback=lambda data: getResultCb(data, rt_session),
                errback=lambda failure: self.renderError(failure, request, pub_jid),
            )

        # max_comments = int(extra_comments_dict['rsm_max']) # FIXME
        max_comments = 0
        # TODO: use max_comments only when RSM is not available
        self.host.bridge.mbGetFromManyWithComments(
            C.JID,
            [pub_jid.userhost()],
            max_items,
            max_comments,
            extra_dict,
            extra_comments_dict,
            C.SERVICE_PROFILE,
            callback=getResult,
        )

    def getAtom(
        self, pub_jid, max_items, extra_dict, extra_comments_dict, request, profile
    ):
        """

        @param pub_jid (jid.JID): publisher JID
        @param max_items(int): maximum number of item to get, C.NO_LIMIT for no limit
        @param extra_dict (dict): extra configuration for initial items only
        @param extra_comments_dict (dict): extra configuration for comments only
        @param request: HTTP request
        @param profile
        """

        def gotItems(data):
            # Generate a clean atom feed with uri linking to this blog
            # from microblog data
            items, metadata = data
            feed_elt = domish.Element((NS_ATOM, u"feed"))
            title = _(u"{user}'s blog").format(user=profile)
            feed_elt.addElement(u"title", content=title)

            base_blog_url = self.host.getExtBaseURL(
                request, u"blog/{user}".format(user=profile)
            )

            # atom link
            link_feed_elt = feed_elt.addElement("link")
            link_feed_elt["href"] = u"{base}/atom.xml".format(base=base_blog_url)
            link_feed_elt["type"] = u"application/atom+xml"
            link_feed_elt["rel"] = u"self"

            # blog link
            link_blog_elt = feed_elt.addElement("link")
            link_blog_elt["rel"] = u"alternate"
            link_blog_elt["type"] = u"text/html"
            link_blog_elt["href"] = base_blog_url

            # blog link XMPP uri
            blog_xmpp_uri = metadata["uri"]
            link_blog_elt = feed_elt.addElement("link")
            link_blog_elt["rel"] = u"alternate"
            link_blog_elt["type"] = u"application/atom+xml"
            link_blog_elt["href"] = blog_xmpp_uri

            feed_elt.addElement("id", content=_quote(blog_xmpp_uri))
            updated_unix = max([float(item["updated"]) for item in items])
            updated_dt = datetime.fromtimestamp(updated_unix)
            feed_elt.addElement(
                u"updated", content=u"{}Z".format(updated_dt.isoformat("T"))
            )

            for item in items:
                entry_elt = feed_elt.addElement(u"entry")

                # Title
                try:
                    title = item["title"]
                except KeyError:
                    # for microblog (without title), we use an abstract of content as title
                    title = u"{}…".format(u" ".join(item["content"][:70].split()))
                entry_elt.addElement(u"title", content=title)

                # HTTP link
                http_link_elt = entry_elt.addElement(u"link")
                http_link_elt["rel"] = u"alternate"
                http_link_elt["type"] = u"text/html"
                http_link_elt["href"] = u"{base}/{quoted_id}".format(
                    base=base_blog_url, quoted_id=_quote(item["id"])
                )
                # XMPP link
                xmpp_link_elt = entry_elt.addElement(u"link")
                xmpp_link_elt["rel"] = u"alternate"
                xmpp_link_elt["type"] = u"application/atom+xml"
                xmpp_link_elt["href"] = u"{blog_uri};item={item_id}".format(
                    blog_uri=blog_xmpp_uri, item_id=item["id"]
                )

                # date metadata
                entry_elt.addElement(u"id", content=item["atom_id"])
                updated = datetime.fromtimestamp(float(item["updated"]))
                entry_elt.addElement(
                    u"updated", content=u"{}Z".format(updated.isoformat("T"))
                )
                published = datetime.fromtimestamp(float(item["published"]))
                entry_elt.addElement(
                    u"published", content=u"{}Z".format(published.isoformat("T"))
                )

                # author metadata
                author_elt = entry_elt.addElement(u"author")
                author_elt.addElement("name", content=item.get("author", profile))
                try:
                    author_elt.addElement(
                        "uri", content=u"xmpp:{}".format(item["author_jid"])
                    )
                except KeyError:
                    pass
                try:
                    author_elt.addElement("email", content=item["author_email"])
                except KeyError:
                    pass

                # categories
                for tag in data_format.dict2iter("tag", item):
                    category_elt = entry_elt.addElement(u"category")
                    category_elt["term"] = tag

                # content
                try:
                    content_xhtml = item["content_xhtml"]
                except KeyError:
                    content_elt = entry_elt.addElement("content", content="content")
                    content_elt["type"] = "text"
                else:
                    content_elt = entry_elt.addElement("content")
                    content_elt["type"] = "xhtml"
                    content_elt.addChild(
                        xml_tools.ElementParser()(content_xhtml, namespace=C.NS_XHTML)
                    )

            atom_feed = u'<?xml version="1.0" encoding="utf-8"?>\n{}'.format(
                feed_elt.toXml()
            )
            self.renderAtomFeed(atom_feed, request),

        self.host.bridge.mbGet(
            pub_jid.userhost(),
            "",
            max_items,
            [],
            extra_dict,
            C.SERVICE_PROFILE,
            callback=gotItems,
        )

    ## rendering

    def _updateDict(self, value, dict_, key):
        dict_[key] = value

    def _getImageParams(self, options, key, default, alt):
        """regexp from http://answers.oreilly.com/topic/280-how-to-validate-urls-with-regular-expressions/"""
        url = options[key] if key in options else ""
        regexp = (
            r"^(https?|ftp)://[a-z0-9-]+(\.[a-z0-9-]+)+(/[\w-]+)*/[\w-]+\.(gif|png|jpg)$"
        )
        if re.match(regexp, url):
            url = url
        else:
            url = default
        return BlogImage(url, alt)

    def renderError(self, failure, request, pub_jid):
        request.setResponseCode(500)
        request.write(
            self.useTemplate(
                request, "static_blog_error", {"message": "Can't access requested data"}
            )
        )
        request.finish()

    def renderHTML(self, items, metadata, request, pub_jid, profile):
        """Retrieve the user parameters before actually rendering the static blog

        @param items(list[tuple(dict, list)]): same as in self._renderHTML
        @param metadata(dict): original node metadata
        @param request: HTTP request
        @param pub_jid (JID): publisher JID
        @param profile (unicode): %(doc_profile)s
        """
        d_list = []
        options = {}

        d = self.getAvatarURL(pub_jid, request)
        d.addCallback(self._updateDict, options, "avatar")
        d.addErrback(self.renderError, request, pub_jid)
        d_list.append(d)

        for param_name in PARAMS_TO_GET:
            d = defer.Deferred()
            self.host.bridge.asyncGetParamA(
                param_name,
                C.STATIC_BLOG_KEY,
                "value",
                C.SERVER_SECURITY_LIMIT,
                profile,
                callback=d.callback,
                errback=d.errback,
            )
            d.addCallback(self._updateDict, options, param_name)
            d.addErrback(self.renderError, request, pub_jid)
            d_list.append(d)

        dlist_d = defer.DeferredList(d_list)
        dlist_d.addCallback(
            lambda dummy: self._renderHTML(items, metadata, options, request, pub_jid)
        )

    def _renderHTML(self, items, metadata, options, request, pub_jid):
        """Actually render the static blog.

        If mblog_data is a list of dict, we are missing the comments items so we just
        display the main items. If mblog_data is a list of couple, each couple is
        associating a main item data with the list of its comments, so we render all.
        @param items(list[tuple(dict, list)]): list of 2-tuple with
            - item(dict): item microblog data
            - comments_list(list[tuple]): list of 5-tuple with
                - service (unicode): pubsub service where the comments node is
                - node (unicode): comments node
                - failure (unicode): empty in case of success, else error message
                - comments(list[dict]): list of microblog data
                - comments_metadata(dict): metadata of the comment node
        @param metadata(dict): original node metadata
        @param options: dict defining the blog's parameters
        @param request: the HTTP request
        @param pub_jid (JID): publisher JID
        """
        if not isinstance(options, dict):
            options = {}
        user = sanitizeHtml(pub_jid.user)
        base_url = os.path.join("/blog/", user)

        def getOption(key):
            return sanitizeHtml(options[key]) if key in options else ""

        avatar = os.path.normpath("/{}".format(getOption("avatar")))
        title = getOption(C.STATIC_BLOG_PARAM_TITLE) or user
        query_data = _urlencode(getDefaultQueryData(request)).decode("utf-8")

        xmpp_uri = metadata["uri"]
        if len(items) == 1:
            # FIXME: that's really not a good way to get item id
            #        this must be changed after static blog refactorisation
            item_id = items[0][0]["id"]
            xmpp_uri += u";item={}".format(_quote(item_id))

        data = {
            "url_base": base_url,
            "xmpp_uri": xmpp_uri,
            "url_query": u"?{}".format(query_data) if query_data else "",
            "keywords": getOption(C.STATIC_BLOG_PARAM_KEYWORDS),
            "description": getOption(C.STATIC_BLOG_PARAM_DESCRIPTION),
            "title": title,
            "favicon": avatar,
            "banner_img": self._getImageParams(
                options, C.STATIC_BLOG_PARAM_BANNER, avatar, title
            ),
        }

        data["navlinks"] = NavigationLinks(request, items, metadata, base_url)
        data["messages"] = []
        for item in items:
            item, comments_list = item
            comments, comments_count = [], 0
            for node_comments in comments_list:
                comments.extend(node_comments[3])
                try:
                    comments_count += int(node_comments[4]["rsm_count"])
                except KeyError:
                    pass
            data["messages"].append(
                BlogMessage(request, base_url, item, comments, comments_count)
            )

        request.write(self.useTemplate(request, "static_blog", data))
        request.finish()

    def renderAtomFeed(self, feed, request):
        request.write(feed.encode("utf-8"))
        request.finish()


class NavigationLinks(object):
    def __init__(self, request, items, metadata, base_url):
        """Build the navigation links.

        @param items (list): list of items
        @param metadata (dict): rsm data
        @param base_url (unicode): the base URL for this user's blog
        @return: dict
        """
        # FIXME: this code must be refactorized, it is fragile
        #        and difficult to maintain

        # query data which must be present in all links
        default_query_data = getDefaultQueryData(request)

        # which links we need to display
        if request.display_single:
            links = ("later_message", "older_message")
            # key must exist when using the template
            self.later_messages = self.older_messages = ""
        else:
            links = ("later_messages", "older_messages")
            self.later_message = self.older_message = ""

        # now we set the links according to RSM
        for key in links:
            query_data = default_query_data.copy()

            if key.startswith("later_message"):
                try:
                    index = int(metadata["rsm_index"])
                except (KeyError, ValueError):
                    pass
                else:
                    if index == 0:
                        # we don't show this link on first page
                        setattr(self, key, "")
                        continue
                try:
                    query_data["before"] = metadata["rsm_first"].encode("utf-8")
                except KeyError:
                    pass
            else:
                try:
                    index = int(metadata["rsm_index"])
                    count = int(metadata.get("rsm_count"))
                except (KeyError, ValueError):
                    # XXX: if we don't have index or count, we can't know if we
                    #      are on the last page or not
                    pass
                else:
                    # if we have index, we don't show the after link
                    # on the last page
                    if index + len(items) >= count:
                        setattr(self, key, "")
                        continue
                try:
                    query_data["after"] = metadata["rsm_last"].encode("utf-8")
                except KeyError:
                    pass

            if request.display_single:
                query_data["max"] = 1

            link = "{}?{}".format(base_url, _urlencode(query_data))
            setattr(self, key, BlogLink(link, key, key.replace("_", " ")))


class BlogImage(object):
    def __init__(self, url_, alt):
        self.url = url_
        self.alt = alt


class BlogLink(object):
    def __init__(self, url_, style, text):
        self.url = url_
        self.style = style
        self.text = text


class BlogMessage(object):
    def __init__(self, request, base_url, entry, comments=None, comments_count=0):
        """

        @param request: HTTP request
        @param base_url (unicode): the base URL
        @param entry(dict): item microblog data
        @param comments(list[dict]): list of microblog data
        @param comments_count (int): total number of comments
        """
        if comments is None:
            comments = []
        timestamp = float(entry.get("published", 0))

        # FIXME: for now we assume that the comments' depth is only 1
        is_comment = not entry.get("comments", False)

        self.date = datetime.fromtimestamp(timestamp)
        self.type = "comment" if is_comment else "main_item"
        self.style = "mblog_comment" if is_comment else ""
        self.content = self.getText(entry, "content")

        if is_comment:
            self.author = _(u"from {}").format(entry["author"])
        else:
            self.author = "&nbsp;"
            self.url = "{}/{}".format(base_url, _quote(entry["id"]))
            query_data = getDefaultQueryData(request)
            if query_data:
                self.url += "?{}".format(_urlencode(query_data))
            self.title = self.getText(entry, "title")
            self.tags = [sanitizeHtml(tag) for tag in data_format.dict2iter("tag", entry)]

            count_text = lambda count: D_(u"comments") if count > 1 else D_(u"comment")

            self.comments_text = u"{} {}".format(
                comments_count, count_text(comments_count)
            )

            delta = comments_count - len(comments)
            if request.display_single and delta > 0:
                prev_url = "{}?{}".format(
                    self.url, _urlencode({"comments_max": comments_count})
                )
                prev_text = D_(u"show {count} previous {comments}").format(
                    count=delta, comments=count_text(delta)
                )
                self.all_comments_link = BlogLink(prev_url, "comments_link", prev_text)

        if comments:
            self.comments = [
                BlogMessage(request, base_url, comment) for comment in comments
            ]

    def getText(self, entry, key):
        try:
            xhtml = entry["{}_xhtml".format(key)]
        except KeyError:
            try:
                processor = addURLToText if key.startswith("content") else sanitizeHtml
                return convertNewLinesToXHTML(processor(entry[key]))
            except KeyError:
                return None
        else:
            # FIXME: empty <div /> elements provoke rendering issue
            #        this regex is a temporary workadound, need more investigation
            xhtml = re_strip_empty_div.sub("", xhtml)
            return fixXHTMLLinks(xhtml)
