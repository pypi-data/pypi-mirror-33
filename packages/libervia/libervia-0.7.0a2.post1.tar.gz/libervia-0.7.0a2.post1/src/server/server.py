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

from twisted.application import service
from twisted.internet import reactor, defer
from twisted.web import server
from twisted.web import static
from twisted.web import resource as web_resource
from twisted.web import util as web_util
from twisted.web import http
from twisted.python.components import registerAdapter
from twisted.python import failure
from twisted.words.protocols.jabber import jid

from txjsonrpc.web import jsonrpc
from txjsonrpc import jsonrpclib

from sat.core.log import getLogger

log = getLogger(__name__)
from sat_frontends.bridge.dbus_bridge import (
    Bridge,
    BridgeExceptionNoService,
    const_TIMEOUT as BRIDGE_TIMEOUT,
)
from sat.core.i18n import _, D_
from sat.core import exceptions
from sat.tools import utils
from sat.tools.common import regex
from sat.tools.common import template

import re
import glob
import os.path
import sys
import tempfile
import shutil
import uuid
import urlparse
import urllib
import time
from httplib import HTTPS_PORT
import libervia
from libervia.server import websockets
from libervia.server.pages import LiberviaPage
from libervia.server.utils import quote, ProgressHandler
from functools import partial

try:
    import OpenSSL
    from twisted.internet import ssl
except ImportError:
    ssl = None

from libervia.server.constants import Const as C
from libervia.server.blog import MicroBlog
from libervia.server import session_iface


# following value are set from twisted.plugins.libervia_server initialise (see the comment there)
DATA_DIR_DEFAULT = OPT_PARAMETERS_BOTH = OPT_PARAMETERS_CFG = coerceDataDir = None


class LiberviaSession(server.Session):
    sessionTimeout = C.SESSION_TIMEOUT

    def __init__(self, *args, **kwargs):
        self.__lock = False
        server.Session.__init__(self, *args, **kwargs)

    def lock(self):
        """Prevent session from expiring"""
        self.__lock = True
        self._expireCall.reset(sys.maxint)

    def unlock(self):
        """Allow session to expire again, and touch it"""
        self.__lock = False
        self.touch()

    def touch(self):
        if not self.__lock:
            server.Session.touch(self)


class ProtectedFile(static.File):
    """A static.File class which doens't show directory listing"""

    def directoryListing(self):
        return web_resource.NoResource()


class LiberviaRootResource(ProtectedFile):
    """Specialized resource for Libervia root

    handle redirections declared in sat.conf
    """

    def _initRedirections(self, options):
        ## redirections
        self.redirections = {}
        self.inv_redirections = {}  # new URL to old URL map

        if options["url_redirections_dict"] and not options["url_redirections_profile"]:
            # FIXME: url_redirections_profile should not be needed. It is currently used to
            #        redirect to an URL which associate the profile with the service, but this
            #        is not clean, and service should be explicitly specified
            raise ValueError(
                u"url_redirections_profile need to be filled if you want to use url_redirections_dict"
            )

        for old, new_data in options["url_redirections_dict"].iteritems():
            # new_data can be a dictionary or a unicode url
            if isinstance(new_data, dict):
                # new_data dict must contain either "url", "page" or "path" key (exclusive)
                # if "path" is used, a file url is constructed with it
                if len({"path", "url", "page"}.intersection(new_data.keys())) != 1:
                    raise ValueError(
                        u'You must have one and only one of "url", "page" or "path" key in your url_redirections_dict data'
                    )
                if "url" in new_data:
                    new = new_data["url"]
                elif "page" in new_data:
                    new = new_data
                    new["type"] = "page"
                    new.setdefault("path_args", [])
                    if not isinstance(new["path_args"], list):
                        log.error(
                            _(
                                u'"path_args" in redirection of {old} must be a list. Ignoring the redirection'.format(
                                    old=old
                                )
                            )
                        )
                        continue
                    new.setdefault("query_args", {})
                    if not isinstance(new["query_args"], dict):
                        log.error(
                            _(
                                u'"query_args" in redirection of {old} must be a dictionary. Ignoring the redirection'.format(
                                    old=old
                                )
                            )
                        )
                        continue
                    new["path_args"] = [quote(a) for a in new["path_args"]]
                    # we keep an inversed dict of page redirection (page/path_args => redirecting URL)
                    # so getURL can return the redirecting URL if the same arguments are used
                    # making the URL consistent
                    args_hash = tuple(new["path_args"])
                    LiberviaPage.pages_redirects.setdefault(new_data["page"], {})[
                        args_hash
                    ] = old

                    # we need lists in query_args because it will be used
                    # as it in request.path_args
                    for k, v in new["query_args"].iteritems():
                        if isinstance(v, basestring):
                            new["query_args"][k] = [v]
                elif "path" in new_data:
                    new = "file:{}".format(urllib.quote(new_data["path"]))
            elif isinstance(new_data, basestring):
                new = new_data
                new_data = {}
            else:
                log.error(
                    _(u"ignoring invalid redirection value: {new_data}").format(
                        new_data=new_data
                    )
                )
                continue

            # some normalization
            if not old.strip():
                # root URL special case
                old = ""
            elif not old.startswith("/"):
                log.error(
                    _(
                        u"redirected url must start with '/', got {value}. Ignoring"
                    ).format(value=old)
                )
                continue
            else:
                old = self._normalizeURL(old)

            if isinstance(new, dict):
                # dict are handled differently, they contain data
                # which ared use dynamically when the request is done
                self.redirections[old] = new
                if not old:
                    if new[u"type"] == u"page":
                        log.info(
                            _(u"Root URL redirected to page {name}").format(
                                name=new[u"page"]
                            )
                        )
                else:
                    if new[u"type"] == u"page":
                        page = LiberviaPage.getPageByName(new[u"page"])
                        url = page.getURL(*new.get(u"path_args", []))
                        self.inv_redirections[url] = old
                continue

            # at this point we have a redirection URL in new, we can parse it
            new_url = urlparse.urlsplit(new.encode("utf-8"))

            # we handle the known URL schemes
            if new_url.scheme == "xmpp":
                location = LiberviaPage.getPagePathFromURI(new)
                if location is None:
                    log.warning(
                        _(
                            u"ignoring redirection, no page found to handle this URI: {uri}"
                        ).format(uri=new)
                    )
                    continue
                request_data = self._getRequestData(location)
                if old:
                    self.inv_redirections[location] = old

            elif new_url.scheme in ("", "http", "https"):
                # direct redirection
                if new_url.netloc:
                    raise NotImplementedError(
                        u"netloc ({netloc}) is not implemented yet for url_redirections_dict, it is not possible to redirect to an external website".format(
                            netloc=new_url.netloc
                        )
                    )
                location = urlparse.urlunsplit(
                    ("", "", new_url.path, new_url.query, new_url.fragment)
                ).decode("utf-8")
                request_data = self._getRequestData(location)
                if old:
                    self.inv_redirections[location] = old

            elif new_url.scheme in ("file"):
                # file or directory
                if new_url.netloc:
                    raise NotImplementedError(
                        u"netloc ({netloc}) is not implemented for url redirection to file system, it is not possible to redirect to an external host".format(
                            netloc=new_url.netloc
                        )
                    )
                path = urllib.unquote(new_url.path)
                if not os.path.isabs(path):
                    raise ValueError(
                        u"file redirection must have an absolute path: e.g. file:/path/to/my/file"
                    )
                # for file redirection, we directly put child here
                segments, dummy, last_segment = old.rpartition("/")
                url_segments = segments.split("/") if segments else []
                current = self
                for segment in url_segments:
                    resource = web_resource.NoResource()
                    current.putChild(segment, resource)
                    current = resource
                resource_class = (
                    ProtectedFile if new_data.get("protected", True) else static.File
                )
                current.putChild(last_segment, resource_class(path))
                log.info(
                    u"Added redirection from /{old} to file system path {path}".format(
                        old=old.decode("utf-8"), path=path.decode("utf-8")
                    )
                )
                continue  # we don't want to use redirection system, so we continue here

            else:
                raise NotImplementedError(
                    u"{scheme}: scheme is not managed for url_redirections_dict".format(
                        scheme=new_url.scheme
                    )
                )

            self.redirections[old] = request_data
            if not old:
                log.info(
                    _(u"Root URL redirected to {uri}").format(
                        uri=request_data[1].decode("utf-8")
                    )
                )

        # no need to keep url_redirections*, they will not be used anymore
        del options["url_redirections_dict"]
        del options["url_redirections_profile"]

        # the default root URL, if not redirected
        if not "" in self.redirections:
            self.redirections[""] = self._getRequestData(C.LIBERVIA_MAIN_PAGE)

    def _normalizeURL(self, url, lower=True):
        """Return URL normalized for self.redirections dict

        @param url(unicode): URL to normalize
        @param lower(bool): lower case of url if True
        @return (str): normalized URL
        """
        if lower:
            url = url.lower()
        return "/".join((p for p in url.encode("utf-8").split("/") if p))

    def _getRequestData(self, uri):
        """Return data needed to redirect request

        @param url(unicode): destination url
        @return (tuple(list[str], str, str, dict): tuple with
            splitted path as in Request.postpath
            uri as in Request.uri
            path as in Request.path
            args as in Request.args
        """
        uri = uri.encode("utf-8")
        # XXX: we reuse code from twisted.web.http.py here
        #      as we need to have the same behaviour
        x = uri.split(b"?", 1)

        if len(x) == 1:
            path = uri
            args = {}
        else:
            path, argstring = x
            args = http.parse_qs(argstring, 1)

        # XXX: splitted path case must not be changed, as it may be significant
        #      (e.g. for blog items)
        return (
            self._normalizeURL(path.decode("utf-8"), lower=False).split("/"),
            uri,
            path,
            args,
        )

    def _redirect(self, request, request_data):
        """Redirect an URL by rewritting request

        this is *NOT* a HTTP redirection, but equivalent to URL rewritting
        @param request(web.http.request): original request
        @param request_data(tuple): data returned by self._getRequestData
        @return (web_resource.Resource): resource to use
        """
        # recursion check
        try:
            request._redirected
        except AttributeError:
            pass
        else:
            try:
                dummy, uri, dummy, dummy = request_data
            except ValueError:
                uri = u""
            log.error(
                D_(
                    u"recursive redirection, please fix this URL:\n{old} ==> {new}"
                ).format(old=request.uri.decode("utf-8"), new=uri.decode("utf-8"))
            )
            return web_resource.NoResource()

        request._redirected = True  # here to avoid recursive redirections

        if isinstance(request_data, dict):
            if request_data["type"] == "page":
                try:
                    page = LiberviaPage.getPageByName(request_data["page"])
                except KeyError:
                    log.error(
                        _(
                            u'Can\'t find page named "{name}" requested in redirection'
                        ).format(name=request_data["page"])
                    )
                    return web_resource.NoResource()
                request.postpath = request_data["path_args"][:] + request.postpath

                try:
                    request.args.update(request_data["query_args"])
                except (TypeError, ValueError):
                    log.error(
                        _(u"Invalid args in redirection: {query_args}").format(
                            query_args=request_data["query_args"]
                        )
                    )
                    return web_resource.NoResource()
                return page
            else:
                raise exceptions.InternalError(u"unknown request_data type")
        else:
            path_list, uri, path, args = request_data
            log.debug(
                u"Redirecting URL {old} to {new}".format(
                    old=request.uri.decode("utf-8"), new=uri.decode("utf-8")
                )
            )
            # we change the request to reflect the new url
            request.postpath = path_list[1:] + request.postpath
            request.args = args

        # we start again to look for a child with the new url
        return self.getChildWithDefault(path_list[0], request)

    def getChildWithDefault(self, name, request):
        # XXX: this method is overriden only for root url
        #      which is the only ones who need to be handled before other children
        if name == "" and not request.postpath:
            return self._redirect(request, self.redirections[""])
        return super(LiberviaRootResource, self).getChildWithDefault(name, request)

    def getChild(self, name, request):
        resource = super(LiberviaRootResource, self).getChild(name, request)

        if isinstance(resource, web_resource.NoResource):
            # if nothing was found, we try our luck with redirections
            # XXX: we want redirections to happen only if everything else failed
            path_elt = request.prepath + request.postpath
            for idx in xrange(len(path_elt), 0, -1):
                test_url = "/".join(path_elt[:idx]).lower()
                if test_url in self.redirections:
                    request_data = self.redirections[test_url]
                    request.postpath = path_elt[idx:]
                    return self._redirect(request, request_data)

        return resource

    def createSimilarFile(self, path):
        # XXX: this method need to be overriden to avoid recreating a LiberviaRootResource

        f = LiberviaRootResource.__base__(
            path, self.defaultType, self.ignoredExts, self.registry
        )
        # refactoring by steps, here - constructor should almost certainly take these
        f.processors = self.processors
        f.indexNames = self.indexNames[:]
        f.childNotFound = self.childNotFound
        return f


class JSONRPCMethodManager(jsonrpc.JSONRPC):
    def __init__(self, sat_host):
        jsonrpc.JSONRPC.__init__(self)
        self.sat_host = sat_host

    def asyncBridgeCall(self, method_name, *args, **kwargs):
        return self.sat_host.bridgeCall(method_name, *args, **kwargs)


class MethodHandler(JSONRPCMethodManager):
    def __init__(self, sat_host):
        JSONRPCMethodManager.__init__(self, sat_host)

    def render(self, request):
        self.session = request.getSession()
        profile = session_iface.ISATSession(self.session).profile
        if not profile:
            # user is not identified, we return a jsonrpc fault
            parsed = jsonrpclib.loads(request.content.read())
            fault = jsonrpclib.Fault(
                C.ERRNUM_LIBERVIA, C.NOT_ALLOWED
            )  # FIXME: define some standard error codes for libervia
            return jsonrpc.JSONRPC._cbRender(
                self, fault, request, parsed.get("id"), parsed.get("jsonrpc")
            )  # pylint: disable=E1103
        return jsonrpc.JSONRPC.render(self, request)

    @defer.inlineCallbacks
    def jsonrpc_getVersion(self):
        """Return SàT version"""
        try:
            defer.returnValue(self._version_cache)
        except AttributeError:
            self._version_cache = yield self.sat_host.bridgeCall("getVersion")
            defer.returnValue(self._version_cache)

    def jsonrpc_getLiberviaVersion(self):
        """Return Libervia version"""
        return self.sat_host.full_version

    def jsonrpc_disconnect(self):
        """Disconnect the profile"""
        sat_session = session_iface.ISATSession(self.session)
        profile = sat_session.profile
        self.sat_host.bridgeCall("disconnect", profile)

    def jsonrpc_getContacts(self):
        """Return all passed args."""
        profile = session_iface.ISATSession(self.session).profile
        return self.sat_host.bridgeCall("getContacts", profile)

    @defer.inlineCallbacks
    def jsonrpc_addContact(self, entity, name, groups):
        """Subscribe to contact presence, and add it to the given groups"""
        profile = session_iface.ISATSession(self.session).profile
        yield self.sat_host.bridgeCall("addContact", entity, profile)
        yield self.sat_host.bridgeCall("updateContact", entity, name, groups, profile)

    def jsonrpc_delContact(self, entity):
        """Remove contact from contacts list"""
        profile = session_iface.ISATSession(self.session).profile
        return self.sat_host.bridgeCall("delContact", entity, profile)

    def jsonrpc_updateContact(self, entity, name, groups):
        """Update contact's roster item"""
        profile = session_iface.ISATSession(self.session).profile
        return self.sat_host.bridgeCall("updateContact", entity, name, groups, profile)

    def jsonrpc_subscription(self, sub_type, entity):
        """Confirm (or infirm) subscription,
        and setup user roster in case of subscription"""
        profile = session_iface.ISATSession(self.session).profile
        return self.sat_host.bridgeCall("subscription", sub_type, entity, profile)

    def jsonrpc_getWaitingSub(self):
        """Return list of room already joined by user"""
        profile = session_iface.ISATSession(self.session).profile
        return self.sat_host.bridgeCall("getWaitingSub", profile)

    def jsonrpc_setStatus(self, presence, status):
        """Change the presence and/or status
        @param presence: value from ("", "chat", "away", "dnd", "xa")
        @param status: any string to describe your status
        """
        profile = session_iface.ISATSession(self.session).profile
        return self.sat_host.bridgeCall(
            "setPresence", "", presence, {"": status}, profile
        )

    def jsonrpc_messageSend(self, to_jid, msg, subject, type_, extra={}):
        """send message"""
        profile = session_iface.ISATSession(self.session).profile
        return self.asyncBridgeCall(
            "messageSend", to_jid, msg, subject, type_, extra, profile
        )

    ## PubSub ##

    def jsonrpc_psNodeDelete(self, service, node):
        """Delete a whole node

        @param service (unicode): service jid
        @param node (unicode): node to delete
        """
        profile = session_iface.ISATSession(self.session).profile
        return self.asyncBridgeCall("psNodeDelete", service, node, profile)

    # def jsonrpc_psRetractItem(self, service, node, item, notify):
    #     """Delete a whole node

    #     @param service (unicode): service jid
    #     @param node (unicode): node to delete
    #     @param items (iterable): id of item to retract
    #     @param notify (bool): True if notification is required
    #     """
    #     profile = session_iface.ISATSession(self.session).profile
    #     return self.asyncBridgeCall("psRetractItem", service, node, item, notify, profile)

    # def jsonrpc_psRetractItems(self, service, node, items, notify):
    #     """Delete a whole node

    #     @param service (unicode): service jid
    #     @param node (unicode): node to delete
    #     @param items (iterable): ids of items to retract
    #     @param notify (bool): True if notification is required
    #     """
    #     profile = session_iface.ISATSession(self.session).profile
    #     return self.asyncBridgeCall("psRetractItems", service, node, items, notify, profile)

    ## microblogging ##

    def jsonrpc_mbSend(self, service, node, mb_data):
        """Send microblog data

        @param service (unicode): service jid or empty string to use profile's microblog
        @param node (unicode): publishing node, or empty string to use microblog node
        @param mb_data(dict): microblog data
        @return: a deferred
        """
        profile = session_iface.ISATSession(self.session).profile
        return self.asyncBridgeCall("mbSend", service, node, mb_data, profile)

    def jsonrpc_mbRetract(self, service, node, items):
        """Delete a whole node

        @param service (unicode): service jid, empty string for PEP
        @param node (unicode): node to delete, empty string for default node
        @param items (iterable): ids of items to retract
        """
        profile = session_iface.ISATSession(self.session).profile
        return self.asyncBridgeCall("mbRetract", service, node, items, profile)

    def jsonrpc_mbGet(self, service_jid, node, max_items, item_ids, extra):
        """Get last microblogs from publisher_jid

        @param service_jid (unicode): pubsub service, usually publisher jid
        @param node(unicode): mblogs node, or empty string to get the defaut one
        @param max_items (int): maximum number of item to get or C.NO_LIMIT to get everything
        @param item_ids (list[unicode]): list of item IDs
        @param rsm (dict): TODO
        @return: a deferred couple with the list of items and metadatas.
        """
        profile = session_iface.ISATSession(self.session).profile
        return self.asyncBridgeCall(
            "mbGet", service_jid, node, max_items, item_ids, extra, profile
        )

    def jsonrpc_mbGetFromMany(self, publishers_type, publishers, max_items, extra):
        """Get many blog nodes at once

        @param publishers_type (unicode): one of "ALL", "GROUP", "JID"
        @param publishers (tuple(unicode)): tuple of publishers (empty list for all, list of groups or list of jids)
        @param max_items (int): maximum number of item to get or C.NO_LIMIT to get everything
        @param extra (dict): TODO
        @return (str): RT Deferred session id
        """
        profile = session_iface.ISATSession(self.session).profile
        return self.sat_host.bridgeCall(
            "mbGetFromMany", publishers_type, publishers, max_items, extra, profile
        )

    def jsonrpc_mbGetFromManyRTResult(self, rt_session):
        """Get results from RealTime mbGetFromMany session

        @param rt_session (str): RT Deferred session id
        """
        profile = session_iface.ISATSession(self.session).profile
        return self.asyncBridgeCall("mbGetFromManyRTResult", rt_session, profile)

    def jsonrpc_mbGetFromManyWithComments(
        self,
        publishers_type,
        publishers,
        max_items,
        max_comments,
        rsm_dict,
        rsm_comments_dict,
    ):
        """Helper method to get the microblogs and their comments in one shot

        @param publishers_type (str): type of the list of publishers (one of "GROUP" or "JID" or "ALL")
        @param publishers (list): list of publishers, according to publishers_type (list of groups or list of jids)
        @param max_items (int): optional limit on the number of retrieved items.
        @param max_comments (int): maximum number of comments to retrieve
        @param rsm_dict (dict): RSM data for initial items only
        @param rsm_comments_dict (dict): RSM data for comments only
        @param profile_key: profile key
        @return (str): RT Deferred session id
        """
        profile = session_iface.ISATSession(self.session).profile
        return self.sat_host.bridgeCall(
            "mbGetFromManyWithComments",
            publishers_type,
            publishers,
            max_items,
            max_comments,
            rsm_dict,
            rsm_comments_dict,
            profile,
        )

    def jsonrpc_mbGetFromManyWithCommentsRTResult(self, rt_session):
        """Get results from RealTime mbGetFromManyWithComments session

        @param rt_session (str): RT Deferred session id
        """
        profile = session_iface.ISATSession(self.session).profile
        return self.asyncBridgeCall(
            "mbGetFromManyWithCommentsRTResult", rt_session, profile
        )

    # def jsonrpc_sendMblog(self, type_, dest, text, extra={}):
    #     """ Send microblog message
    #     @param type_ (unicode): one of "PUBLIC", "GROUP"
    #     @param dest (tuple(unicode)): recipient groups (ignored for "PUBLIC")
    #     @param text (unicode): microblog's text
    #     """
    #     profile = session_iface.ISATSession(self.session).profile
    #     extra['allow_comments'] = 'True'

    #     if not type_:  # auto-detect
    #         type_ = "PUBLIC" if dest == [] else "GROUP"

    #     if type_ in ("PUBLIC", "GROUP") and text:
    #         if type_ == "PUBLIC":
    #             #This text if for the public microblog
    #             log.debug("sending public blog")
    #             return self.sat_host.bridge.sendGroupBlog("PUBLIC", (), text, extra, profile)
    #         else:
    #             log.debug("sending group blog")
    #             dest = dest if isinstance(dest, list) else [dest]
    #             return self.sat_host.bridge.sendGroupBlog("GROUP", dest, text, extra, profile)
    #     else:
    #         raise Exception("Invalid data")

    # def jsonrpc_deleteMblog(self, pub_data, comments):
    #     """Delete a microblog node
    #     @param pub_data: a tuple (service, comment node identifier, item identifier)
    #     @param comments: comments node identifier (for main item) or False
    #     """
    #     profile = session_iface.ISATSession(self.session).profile
    #     return self.sat_host.bridge.deleteGroupBlog(pub_data, comments if comments else '', profile)

    # def jsonrpc_updateMblog(self, pub_data, comments, message, extra={}):
    #     """Modify a microblog node
    #     @param pub_data: a tuple (service, comment node identifier, item identifier)
    #     @param comments: comments node identifier (for main item) or False
    #     @param message: new message
    #     @param extra: dict which option name as key, which can be:
    #         - allow_comments: True to accept an other level of comments, False else (default: False)
    #         - rich: if present, contain rich text in currently selected syntax
    #     """
    #     profile = session_iface.ISATSession(self.session).profile
    #     if comments:
    #         extra['allow_comments'] = 'True'
    #     return self.sat_host.bridge.updateGroupBlog(pub_data, comments if comments else '', message, extra, profile)

    # def jsonrpc_sendMblogComment(self, node, text, extra={}):
    #     """ Send microblog message
    #     @param node: url of the comments node
    #     @param text: comment
    #     """
    #     profile = session_iface.ISATSession(self.session).profile
    #     if node and text:
    #         return self.sat_host.bridge.sendGroupBlogComment(node, text, extra, profile)
    #     else:
    #         raise Exception("Invalid data")

    # def jsonrpc_getMblogs(self, publisher_jid, item_ids, max_items=C.RSM_MAX_ITEMS):
    #     """Get specified microblogs posted by a contact
    #     @param publisher_jid: jid of the publisher
    #     @param item_ids: list of microblogs items IDs
    #     @return list of microblog data (dict)"""
    #     profile = session_iface.ISATSession(self.session).profile
    #     d = self.asyncBridgeCall("getGroupBlogs", publisher_jid, item_ids, {'max_': unicode(max_items)}, False, profile)
    #     return d

    # def jsonrpc_getMblogsWithComments(self, publisher_jid, item_ids, max_comments=C.RSM_MAX_COMMENTS):
    #     """Get specified microblogs posted by a contact and their comments
    #     @param publisher_jid: jid of the publisher
    #     @param item_ids: list of microblogs items IDs
    #     @return list of couple (microblog data, list of microblog data)"""
    #     profile = session_iface.ISATSession(self.session).profile
    #     d = self.asyncBridgeCall("getGroupBlogsWithComments", publisher_jid, item_ids, {}, max_comments, profile)
    #     return d

    # def jsonrpc_getMassiveMblogs(self, publishers_type, publishers, rsm=None):
    #     """Get lasts microblogs posted by several contacts at once

    #     @param publishers_type (unicode): one of "ALL", "GROUP", "JID"
    #     @param publishers (tuple(unicode)): tuple of publishers (empty list for all, list of groups or list of jids)
    #     @param rsm (dict): TODO
    #     @return: dict{unicode: list[dict])
    #         key: publisher's jid
    #         value: list of microblog data (dict)
    #     """
    #     profile = session_iface.ISATSession(self.session).profile
    #     if rsm is None:
    #         rsm = {'max_': unicode(C.RSM_MAX_ITEMS)}
    #     d = self.asyncBridgeCall("getMassiveGroupBlogs", publishers_type, publishers, rsm, profile)
    #     self.sat_host.bridge.massiveSubscribeGroupBlogs(publishers_type, publishers, profile)
    #     return d

    # def jsonrpc_getMblogComments(self, service, node, rsm=None):
    #     """Get all comments of given node
    #     @param service: jid of the service hosting the node
    #     @param node: comments node
    #     """
    #     profile = session_iface.ISATSession(self.session).profile
    #     if rsm is None:
    #         rsm = {'max_': unicode(C.RSM_MAX_COMMENTS)}
    #     d = self.asyncBridgeCall("getGroupBlogComments", service, node, rsm, profile)
    #     return d

    def jsonrpc_getPresenceStatuses(self):
        """Get Presence information for connected contacts"""
        profile = session_iface.ISATSession(self.session).profile
        return self.sat_host.bridgeCall("getPresenceStatuses", profile)

    def jsonrpc_historyGet(self, from_jid, to_jid, size, between, search=""):
        """Return history for the from_jid/to_jid couple"""
        sat_session = session_iface.ISATSession(self.session)
        profile = sat_session.profile
        sat_jid = sat_session.jid
        if not sat_jid:
            raise exceptions.InternalError("session jid should be set")
        if (
            jid.JID(from_jid).userhost() != sat_jid.userhost()
            and jid.JID(to_jid).userhost() != sat_jid.userhost()
        ):
            log.error(
                u"Trying to get history from a different jid (given (browser): {}, real (backend): {}), maybe a hack attempt ?".format(
                    from_jid, sat_jid
                )
            )
            return {}
        d = self.asyncBridgeCall(
            "historyGet", from_jid, to_jid, size, between, search, profile
        )

        def show(result_dbus):
            result = []
            for line in result_dbus:
                # XXX: we have to do this stupid thing because Python D-Bus use its own types instead of standard types
                #     and txJsonRPC doesn't accept D-Bus types, resulting in a empty query
                uuid, timestamp, from_jid, to_jid, message, subject, mess_type, extra = (
                    line
                )
                result.append(
                    (
                        unicode(uuid),
                        float(timestamp),
                        unicode(from_jid),
                        unicode(to_jid),
                        dict(message),
                        dict(subject),
                        unicode(mess_type),
                        dict(extra),
                    )
                )
            return result

        d.addCallback(show)
        return d

    def jsonrpc_mucJoin(self, room_jid, nick):
        """Join a Multi-User Chat room

        @param room_jid (unicode): room JID or empty string to generate a unique name
        @param nick (unicode): user nick
        """
        profile = session_iface.ISATSession(self.session).profile
        d = self.asyncBridgeCall("joinMUC", room_jid, nick, {}, profile)
        return d

    def jsonrpc_inviteMUC(self, contact_jid, room_jid):
        """Invite a user to a Multi-User Chat room

        @param contact_jid (unicode): contact to invite
        @param room_jid (unicode): room JID or empty string to generate a unique name
        """
        profile = session_iface.ISATSession(self.session).profile
        room_id = room_jid.split("@")[0]
        service = room_jid.split("@")[1]
        return self.sat_host.bridgeCall(
            "inviteMUC", contact_jid, service, room_id, {}, profile
        )

    def jsonrpc_mucLeave(self, room_jid):
        """Quit a Multi-User Chat room"""
        profile = session_iface.ISATSession(self.session).profile
        try:
            room_jid = jid.JID(room_jid)
        except:
            log.warning("Invalid room jid")
            return
        return self.sat_host.bridgeCall("mucLeave", room_jid.userhost(), profile)

    def jsonrpc_mucGetRoomsJoined(self):
        """Return list of room already joined by user"""
        profile = session_iface.ISATSession(self.session).profile
        return self.sat_host.bridgeCall("mucGetRoomsJoined", profile)

    def jsonrpc_mucGetDefaultService(self):
        """@return: the default MUC"""
        d = self.asyncBridgeCall("mucGetDefaultService")
        return d

    def jsonrpc_launchTarotGame(self, other_players, room_jid=""):
        """Create a room, invite the other players and start a Tarot game.

        @param other_players (list[unicode]): JIDs of the players to play with
        @param room_jid (unicode): room JID or empty string to generate a unique name
        """
        profile = session_iface.ISATSession(self.session).profile
        return self.sat_host.bridgeCall(
            "tarotGameLaunch", other_players, room_jid, profile
        )

    def jsonrpc_getTarotCardsPaths(self):
        """Give the path of all the tarot cards"""
        _join = os.path.join
        _media_dir = _join(self.sat_host.media_dir, "")
        return map(
            lambda x: _join(C.MEDIA_DIR, x[len(_media_dir) :]),
            glob.glob(_join(_media_dir, C.CARDS_DIR, "*_*.png")),
        )

    def jsonrpc_tarotGameReady(self, player, referee):
        """Tell to the server that we are ready to start the game"""
        profile = session_iface.ISATSession(self.session).profile
        return self.sat_host.bridgeCall("tarotGameReady", player, referee, profile)

    def jsonrpc_tarotGamePlayCards(self, player_nick, referee, cards):
        """Tell to the server the cards we want to put on the table"""
        profile = session_iface.ISATSession(self.session).profile
        return self.sat_host.bridgeCall(
            "tarotGamePlayCards", player_nick, referee, cards, profile
        )

    def jsonrpc_launchRadioCollective(self, invited, room_jid=""):
        """Create a room, invite people, and start a radio collective.

        @param invited (list[unicode]): JIDs of the contacts to play with
        @param room_jid (unicode): room JID or empty string to generate a unique name
        """
        profile = session_iface.ISATSession(self.session).profile
        return self.sat_host.bridgeCall("radiocolLaunch", invited, room_jid, profile)

    def jsonrpc_getEntitiesData(self, jids, keys):
        """Get cached data for several entities at once

        @param jids: list jids from who we wants data, or empty list for all jids in cache
        @param keys: name of data we want (list)
        @return: requested data"""
        if not C.ALLOWED_ENTITY_DATA.issuperset(keys):
            raise exceptions.PermissionError(
                "Trying to access unallowed data (hack attempt ?)"
            )
        profile = session_iface.ISATSession(self.session).profile
        try:
            return self.sat_host.bridgeCall("getEntitiesData", jids, keys, profile)
        except Exception as e:
            raise failure.Failure(jsonrpclib.Fault(C.ERRNUM_BRIDGE_ERRBACK, unicode(e)))

    def jsonrpc_getEntityData(self, jid, keys):
        """Get cached data for an entity

        @param jid: jid of contact from who we want data
        @param keys: name of data we want (list)
        @return: requested data"""
        if not C.ALLOWED_ENTITY_DATA.issuperset(keys):
            raise exceptions.PermissionError(
                "Trying to access unallowed data (hack attempt ?)"
            )
        profile = session_iface.ISATSession(self.session).profile
        try:
            return self.sat_host.bridgeCall("getEntityData", jid, keys, profile)
        except Exception as e:
            raise failure.Failure(jsonrpclib.Fault(C.ERRNUM_BRIDGE_ERRBACK, unicode(e)))

    def jsonrpc_getCard(self, jid_):
        """Get VCard for entiry
        @param jid_: jid of contact from who we want data
        @return: id to retrieve the profile"""
        profile = session_iface.ISATSession(self.session).profile
        return self.sat_host.bridgeCall("getCard", jid_, profile)

    @defer.inlineCallbacks
    def jsonrpc_avatarGet(self, entity, cache_only, hash_only):
        session_data = session_iface.ISATSession(self.session)
        profile = session_data.profile
        # profile_uuid = session_data.uuid
        avatar = yield self.asyncBridgeCall(
            "avatarGet", entity, cache_only, hash_only, profile
        )
        if hash_only:
            defer.returnValue(avatar)
        else:
            filename = os.path.basename(avatar)
            avatar_url = os.path.join(session_data.cache_dir, filename)
            defer.returnValue(avatar_url)

    def jsonrpc_getAccountDialogUI(self):
        """Get the dialog for managing user account
        @return: XML string of the XMLUI"""
        profile = session_iface.ISATSession(self.session).profile
        return self.sat_host.bridgeCall("getAccountDialogUI", profile)

    def jsonrpc_getParamsUI(self):
        """Return the parameters XML for profile"""
        profile = session_iface.ISATSession(self.session).profile
        return self.asyncBridgeCall("getParamsUI", C.SECURITY_LIMIT, C.APP_NAME, profile)

    def jsonrpc_asyncGetParamA(self, param, category, attribute="value"):
        """Return the parameter value for profile"""
        profile = session_iface.ISATSession(self.session).profile
        if category == "Connection":
            # we need to manage the followings params here, else SECURITY_LIMIT would block them
            if param == "JabberID":
                return self.asyncBridgeCall(
                    "asyncGetParamA", param, category, attribute, profile_key=profile
                )
            elif param == "autoconnect":
                return defer.succeed(C.BOOL_TRUE)
        d = self.asyncBridgeCall(
            "asyncGetParamA",
            param,
            category,
            attribute,
            C.SECURITY_LIMIT,
            profile_key=profile,
        )
        return d

    def jsonrpc_setParam(self, name, value, category):
        profile = session_iface.ISATSession(self.session).profile
        return self.sat_host.bridgeCall(
            "setParam", name, value, category, C.SECURITY_LIMIT, profile
        )

    def jsonrpc_launchAction(self, callback_id, data):
        # FIXME: any action can be launched, this can be a huge security issue if callback_id can be guessed
        #       a security system with authorised callback_id must be implemented, similar to the one for authorised params
        profile = session_iface.ISATSession(self.session).profile
        d = self.asyncBridgeCall("launchAction", callback_id, data, profile)
        return d

    def jsonrpc_chatStateComposing(self, to_jid_s):
        """Call the method to process a "composing" state.
        @param to_jid_s: contact the user is composing to
        """
        profile = session_iface.ISATSession(self.session).profile
        return self.sat_host.bridgeCall("chatStateComposing", to_jid_s, profile)

    def jsonrpc_getNewAccountDomain(self):
        """@return: the domain for new account creation"""
        d = self.asyncBridgeCall("getNewAccountDomain")
        return d

    def jsonrpc_syntaxConvert(
        self, text, syntax_from=C.SYNTAX_XHTML, syntax_to=C.SYNTAX_CURRENT
    ):
        """ Convert a text between two syntaxes
        @param text: text to convert
        @param syntax_from: source syntax (e.g. "markdown")
        @param syntax_to: dest syntax (e.g.: "XHTML")
        @param safe: clean resulting XHTML to avoid malicious code if True (forced here)
        @return: converted text """
        profile = session_iface.ISATSession(self.session).profile
        return self.sat_host.bridgeCall(
            "syntaxConvert", text, syntax_from, syntax_to, True, profile
        )

    def jsonrpc_getLastResource(self, jid_s):
        """Get the last active resource of that contact."""
        profile = session_iface.ISATSession(self.session).profile
        return self.sat_host.bridgeCall("getLastResource", jid_s, profile)

    def jsonrpc_getFeatures(self):
        """Return the available features in the backend for profile"""
        profile = session_iface.ISATSession(self.session).profile
        return self.sat_host.bridgeCall("getFeatures", profile)

    def jsonrpc_skipOTR(self):
        """Tell the backend to leave OTR handling to Libervia."""
        profile = session_iface.ISATSession(self.session).profile
        return self.sat_host.bridgeCall("skipOTR", profile)

    def jsonrpc_namespacesGet(self):
        return self.sat_host.bridgeCall("namespacesGet")


class WaitingRequests(dict):
    def setRequest(self, request, profile, register_with_ext_jid=False):
        """Add the given profile to the waiting list.

        @param request (server.Request): the connection request
        @param profile (str): %(doc_profile)s
        @param register_with_ext_jid (bool): True if we will try to register the profile with an external XMPP account credentials
        """
        dc = reactor.callLater(BRIDGE_TIMEOUT, self.purgeRequest, profile)
        self[profile] = (request, dc, register_with_ext_jid)

    def purgeRequest(self, profile):
        """Remove the given profile from the waiting list.

        @param profile (str): %(doc_profile)s
        """
        try:
            dc = self[profile][1]
        except KeyError:
            return
        if dc.active():
            dc.cancel()
        del self[profile]

    def getRequest(self, profile):
        """Get the waiting request for the given profile.

        @param profile (str): %(doc_profile)s
        @return: the waiting request or None
        """
        return self[profile][0] if profile in self else None

    def getRegisterWithExtJid(self, profile):
        """Get the value of the register_with_ext_jid parameter.

        @param profile (str): %(doc_profile)s
        @return: bool or None
        """
        return self[profile][2] if profile in self else None


class Register(JSONRPCMethodManager):
    """This class manage the registration procedure with SàT
    It provide an api for the browser, check password and setup the web server"""

    def __init__(self, sat_host):
        JSONRPCMethodManager.__init__(self, sat_host)
        self.profiles_waiting = {}
        self.request = None

    def render(self, request):
        """
        Render method with some hacks:
           - if login is requested, try to login with form data
           - except login, every method is jsonrpc
           - user doesn't need to be authentified for explicitely listed methods, but must be for all others
        """
        if request.postpath == ["login"]:
            return self.loginOrRegister(request)
        _session = request.getSession()
        parsed = jsonrpclib.loads(request.content.read())
        method = parsed.get("method")  # pylint: disable=E1103
        if method not in ["getSessionMetadata", "registerParams", "menusGet"]:
            # if we don't call these methods, we need to be identified
            profile = session_iface.ISATSession(_session).profile
            if not profile:
                # user is not identified, we return a jsonrpc fault
                fault = jsonrpclib.Fault(
                    C.ERRNUM_LIBERVIA, C.NOT_ALLOWED
                )  # FIXME: define some standard error codes for libervia
                return jsonrpc.JSONRPC._cbRender(
                    self, fault, request, parsed.get("id"), parsed.get("jsonrpc")
                )  # pylint: disable=E1103
        self.request = request
        return jsonrpc.JSONRPC.render(self, request)

    def loginOrRegister(self, request):
        """This method is called with the POST information from the registering form.

        @param request: request of the register form
        @return: a constant indicating the state:
            - C.BAD_REQUEST: something is wrong in the request (bad arguments)
            - a return value from self._loginAccount or self._registerNewAccount
        """
        try:
            submit_type = request.args["submit_type"][0]
        except KeyError:
            return C.BAD_REQUEST

        if submit_type == "register":
            self._registerNewAccount(request)
            return server.NOT_DONE_YET
        elif submit_type == "login":
            self._loginAccount(request)
            return server.NOT_DONE_YET
        return Exception("Unknown submit type")

    @defer.inlineCallbacks
    def _registerNewAccount(self, request):
        try:
            login = request.args["register_login"][0]
            password = request.args["register_password"][0]
            email = request.args["email"][0]
        except KeyError:
            request.write(C.BAD_REQUEST)
            request.finish()
            return
        status = yield self.sat_host.registerNewAccount(request, login, password, email)
        request.write(status)
        request.finish()

    @defer.inlineCallbacks
    def _loginAccount(self, request):
        """Try to authenticate the user with the request information.

        will write to request a constant indicating the state:
            - C.PROFILE_LOGGED: profile is connected
            - C.PROFILE_LOGGED_EXT_JID: profile is connected and an external jid has been used
            - C.SESSION_ACTIVE: session was already active
            - C.BAD_REQUEST: something is wrong in the request (bad arguments)
            - C.PROFILE_AUTH_ERROR: either the profile (login) or the profile password is wrong
            - C.XMPP_AUTH_ERROR: the profile is authenticated but the XMPP password is wrong
            - C.ALREADY_WAITING: a request has already been submitted for this profil, C.PROFILE_LOGGED_EXT_JID)e
            - C.NOT_CONNECTED: connection has not been established
        the request will then be finished
        @param request: request of the register form
        """
        try:
            login = request.args["login"][0]
            password = request.args["login_password"][0]
        except KeyError:
            request.write(C.BAD_REQUEST)
            request.finish()
            return

        assert login

        try:
            status = yield self.sat_host.connect(request, login, password)
        except (
            exceptions.DataError,
            exceptions.ProfileUnknownError,
            exceptions.PermissionError,
        ):
            request.write(C.PROFILE_AUTH_ERROR)
            request.finish()
            return
        except exceptions.NotReady:
            request.write(C.ALREADY_WAITING)
            request.finish()
            return
        except exceptions.TimeOutError:
            request.write(C.NO_REPLY)
            request.finish()
            return
        except exceptions.InternalError as e:
            request.write(e.message)
            request.finish()
            return
        except exceptions.ConflictError:
            request.write(C.SESSION_ACTIVE)
            request.finish()
            return
        except ValueError as e:
            if e.message in (C.PROFILE_AUTH_ERROR, C.XMPP_AUTH_ERROR):
                request.write(e.message)
                request.finish()
                return
            else:
                raise e

        assert status
        request.write(status)
        request.finish()

    def jsonrpc_isConnected(self):
        _session = self.request.getSession()
        profile = session_iface.ISATSession(_session).profile
        return self.sat_host.bridgeCall("isConnected", profile)

    def jsonrpc_connect(self):
        _session = self.request.getSession()
        profile = session_iface.ISATSession(_session).profile
        if self.waiting_profiles.getRequest(profile):
            raise jsonrpclib.Fault(
                1, C.ALREADY_WAITING
            )  # FIXME: define some standard error codes for libervia
        self.waiting_profiles.setRequest(self.request, profile)
        self.sat_host.bridgeCall("connect", profile)
        return server.NOT_DONE_YET

    def jsonrpc_getSessionMetadata(self):
        """Return metadata useful on session start

        @return (dict): metadata which can have the following keys:
            "plugged" (bool): True if a profile is already plugged
            "warning" (unicode): a security warning message if plugged is False and if it make sense
                this key may not be present
            "allow_registration" (bool): True if registration is allowed
                this key is only present if profile is unplugged
        @return: a couple (registered, message) with:
        - registered:
        - message:
        """
        metadata = {}
        _session = self.request.getSession()
        profile = session_iface.ISATSession(_session).profile
        if profile:
            metadata["plugged"] = True
        else:
            metadata["plugged"] = False
            metadata["warning"] = self._getSecurityWarning()
            metadata["allow_registration"] = self.sat_host.options["allow_registration"]
        return metadata

    def jsonrpc_registerParams(self):
        """Register the frontend specific parameters"""
        # params = """<params><individual>...</category></individual>"""
        # self.sat_host.bridge.paramsRegisterApp(params, C.SECURITY_LIMIT, C.APP_NAME)

    def jsonrpc_menusGet(self):
        """Return the parameters XML for profile"""
        # XXX: we put this method in Register because we get menus before being logged
        return self.sat_host.bridgeCall("menusGet", "", C.SECURITY_LIMIT)

    def _getSecurityWarning(self):
        """@return: a security warning message, or None if the connection is secure"""
        if (
            self.request.URLPath().scheme == "https"
            or not self.sat_host.options["security_warning"]
        ):
            return None
        text = (
            "<p>"
            + D_("You are about to connect to an unsecure service.")
            + "</p><p>&nbsp;</p><p>"
        )

        if self.sat_host.options["connection_type"] == "both":
            new_port = (
                (":%s" % self.sat_host.options["port_https_ext"])
                if self.sat_host.options["port_https_ext"] != HTTPS_PORT
                else ""
            )
            url = "https://%s" % self.request.URLPath().netloc.replace(
                ":%s" % self.sat_host.options["port"], new_port
            )
            text += D_(
                "Please read our %(faq_prefix)ssecurity notice%(faq_suffix)s regarding HTTPS"
            ) % {
                "faq_prefix": '<a href="http://salut-a-toi.org/faq.html#https" target="#">',
                "faq_suffix": "</a>",
            }
            text += "</p><p>" + D_("and use the secure version of this website:")
            text += '</p><p>&nbsp;</p><p align="center"><a href="%(url)s">%(url)s</a>' % {
                "url": url
            }
        else:
            text += D_("You should ask your administrator to turn on HTTPS.")

        return text + "</p><p>&nbsp;</p>"


class SignalHandler(jsonrpc.JSONRPC):
    def __init__(self, sat_host):
        web_resource.Resource.__init__(self)
        self.register = None
        self.sat_host = sat_host
        self._last_service_prof_disconnect = time.time()
        self.signalDeferred = {}  # dict of deferred (key: profile, value: Deferred)
        # which manages the long polling HTTP request with signals
        self.queue = {}

    def plugRegister(self, register):
        self.register = register

    def jsonrpc_getSignals(self):
        """Keep the connection alive until a signal is received, then send it
        @return: (signal, *signal_args)"""
        _session = self.request.getSession()
        profile = session_iface.ISATSession(_session).profile
        if profile in self.queue:  # if we have signals to send in queue
            if self.queue[profile]:
                return self.queue[profile].pop(0)
            else:
                # the queue is empty, we delete the profile from queue
                del self.queue[profile]
        _session.lock()  # we don't want the session to expire as long as this connection is active

        def unlock(signal, profile):
            _session.unlock()
            try:
                source_defer = self.signalDeferred[profile]
                if source_defer.called and source_defer.result[0] == "disconnected":
                    log.info(u"[%s] disconnected" % (profile,))
                    try:
                        _session.expire()
                    except KeyError:
                        #  FIXME: happen if session is ended using login page
                        #        when pyjamas page is also launched
                        log.warning(u"session is already expired")
            except IndexError:
                log.error("Deferred result should be a tuple with fonction name first")

        self.signalDeferred[profile] = defer.Deferred()
        self.request.notifyFinish().addBoth(unlock, profile)
        return self.signalDeferred[profile]

    def getGenericCb(self, function_name):
        """Return a generic function which send all params to signalDeferred.callback
        function must have profile as last argument"""

        def genericCb(*args):
            profile = args[-1]
            if not profile in self.sat_host.prof_connected:
                return
            signal_data = (function_name, args[:-1])
            try:
                signal_callback = self.signalDeferred[profile].callback
            except KeyError:
                self.queue.setdefault(profile, []).append(signal_data)
            else:
                signal_callback(signal_data)
                del self.signalDeferred[profile]

        return genericCb

    def actionNewHandler(self, action_data, action_id, security_limit, profile):
        """actionNew handler

        XXX: We need need a dedicated handler has actionNew use a security_limit which must be managed
        @param action_data(dict): see bridge documentation
        @param action_id(unicode): identitifer of the action
        @param security_limit(int): %(doc_security_limit)s
        @param profile(unicode): %(doc_profile)s
        """
        if not profile in self.sat_host.prof_connected:
            return
        # FIXME: manage security limit in a dedicated method
        #        raise an exception if it's not OK
        #        and read value in sat.conf
        if security_limit >= C.SECURITY_LIMIT:
            log.debug(
                u"Ignoring action  {action_id}, blocked by security limit".format(
                    action_id=action_id
                )
            )
            return
        signal_data = ("actionNew", (action_data, action_id, security_limit))
        try:
            signal_callback = self.signalDeferred[profile].callback
        except KeyError:
            self.queue.setdefault(profile, []).append(signal_data)
        else:
            signal_callback(signal_data)
            del self.signalDeferred[profile]

    def connected(self, profile, jid_s):
        """Connection is done.

        @param profile (unicode): %(doc_profile)s
        @param jid_s (unicode): the JID that we were assigned by the server, as the resource might differ from the JID we asked for.
        """
        #  FIXME: _logged should not be called from here, check this code
        #  FIXME: check if needed to connect with external jid
        # jid_s is handled in QuickApp.connectionHandler already
        # assert self.register  # register must be plugged
        # request = self.sat_host.waiting_profiles.getRequest(profile)
        # if request:
        #     self.sat_host._logged(profile, request)

    def disconnected(self, profile):
        if profile == C.SERVICE_PROFILE:
            # if service profile has been disconnected, we try to reconnect it
            # if we can't we show error message
            # and if we have 2 disconnection in a short time, we don't try to reconnect
            # and display an error message
            disconnect_delta = time.time() - self._last_service_prof_disconnect
            if disconnect_delta < 15:
                log.error(
                    _(
                        u"Service profile disconnected twice in a short time, please check connection"
                    )
                )
            else:
                log.info(
                    _(
                        u"Service profile has been disconnected, but we need it! Reconnecting it..."
                    )
                )
                d = self.sat_host.bridgeCall(
                    "connect", profile, self.sat_host.options["passphrase"], {}
                )
                d.addErrback(
                    lambda failure_: log.error(
                        _(
                            u"Can't reconnect service profile, please check connection: {reason}"
                        ).format(reason=failure_)
                    )
                )
            self._last_service_prof_disconnect = time.time()
            return

        if not profile in self.sat_host.prof_connected:
            log.info(
                _(
                    u"'disconnected' signal received for a not connected profile ({profile})"
                ).format(profile=profile)
            )
            return
        self.sat_host.prof_connected.remove(profile)
        if profile in self.signalDeferred:
            self.signalDeferred[profile].callback(("disconnected",))
            del self.signalDeferred[profile]
        else:
            if profile not in self.queue:
                self.queue[profile] = []
            self.queue[profile].append(("disconnected",))

    def render(self, request):
        """
        Render method wich reject access if user is not identified
        """
        _session = request.getSession()
        parsed = jsonrpclib.loads(request.content.read())
        profile = session_iface.ISATSession(_session).profile
        if not profile:
            # user is not identified, we return a jsonrpc fault
            fault = jsonrpclib.Fault(
                C.ERRNUM_LIBERVIA, C.NOT_ALLOWED
            )  # FIXME: define some standard error codes for libervia
            return jsonrpc.JSONRPC._cbRender(
                self, fault, request, parsed.get("id"), parsed.get("jsonrpc")
            )  # pylint: disable=E1103
        self.request = request
        return jsonrpc.JSONRPC.render(self, request)


class UploadManager(web_resource.Resource):
    """This class manage the upload of a file
    It redirect the stream to SàT core backend"""

    isLeaf = True
    NAME = "path"  # name use by the FileUpload

    def __init__(self, sat_host):
        self.sat_host = sat_host
        self.upload_dir = tempfile.mkdtemp()
        self.sat_host.addCleanup(shutil.rmtree, self.upload_dir)

    def getTmpDir(self):
        return self.upload_dir

    def _getFileName(self, request):
        """Generate unique filename for a file"""
        raise NotImplementedError

    def _fileWritten(self, request, filepath):
        """Called once the file is actually written on disk
        @param request: HTTP request object
        @param filepath: full filepath on the server
        @return: a tuple with the name of the async bridge method
        to be called followed by its arguments.
        """
        raise NotImplementedError

    def render(self, request):
        """
        Render method with some hacks:
           - if login is requested, try to login with form data
           - except login, every method is jsonrpc
           - user doesn't need to be authentified for getSessionMetadata, but must be for all other methods
        """
        filename = self._getFileName(request)
        filepath = os.path.join(self.upload_dir, filename)
        # FIXME: the uploaded file is fully loaded in memory at form parsing time so far
        #       (see twisted.web.http.Request.requestReceived). A custom requestReceived should
        #       be written in the futur. In addition, it is not yet possible to get progression informations
        #       (see http://twistedmatrix.com/trac/ticket/288)

        with open(filepath, "w") as f:
            f.write(request.args[self.NAME][0])

        def finish(d):
            error = isinstance(d, Exception) or isinstance(d, failure.Failure)
            request.write(C.UPLOAD_KO if error else C.UPLOAD_OK)
            # TODO: would be great to re-use the original Exception class and message
            # but it is lost in the middle of the backtrace and encapsulated within
            # a DBusException instance --> extract the data from the backtrace?
            request.finish()

        d = JSONRPCMethodManager(self.sat_host).asyncBridgeCall(
            *self._fileWritten(request, filepath)
        )
        d.addCallbacks(lambda d: finish(d), lambda failure: finish(failure))
        return server.NOT_DONE_YET


class UploadManagerRadioCol(UploadManager):
    NAME = "song"

    def _getFileName(self, request):
        extension = os.path.splitext(request.args["filename"][0])[1]
        return "%s%s" % (
            str(uuid.uuid4()),
            extension,
        )  # XXX: chromium doesn't seem to play song without the .ogg extension, even with audio/ogg mime-type

    def _fileWritten(self, request, filepath):
        """Called once the file is actually written on disk
        @param request: HTTP request object
        @param filepath: full filepath on the server
        @return: a tuple with the name of the async bridge method
        to be called followed by its arguments.
        """
        profile = session_iface.ISATSession(request.getSession()).profile
        return ("radiocolSongAdded", request.args["referee"][0], filepath, profile)


class UploadManagerAvatar(UploadManager):
    NAME = "avatar_path"

    def _getFileName(self, request):
        return str(uuid.uuid4())

    def _fileWritten(self, request, filepath):
        """Called once the file is actually written on disk
        @param request: HTTP request object
        @param filepath: full filepath on the server
        @return: a tuple with the name of the async bridge method
        to be called followed by its arguments.
        """
        profile = session_iface.ISATSession(request.getSession()).profile
        return ("setAvatar", filepath, profile)


class Libervia(service.Service):
    debug = defer.Deferred.debug  # True if twistd/Libervia is launched in debug mode

    def __init__(self, options):
        self.options = options
        self.initialised = defer.Deferred()
        self.waiting_profiles = WaitingRequests()  # FIXME: should be removed

        if self.options["base_url_ext"]:
            self.base_url_ext = self.options.pop("base_url_ext")
            if self.base_url_ext[-1] != "/":
                self.base_url_ext += "/"
            self.base_url_ext_data = urlparse.urlsplit(self.base_url_ext)
        else:
            self.base_url_ext = None
            # we split empty string anyway so we can do things like
            # scheme = self.base_url_ext_data.scheme or 'https'
            self.base_url_ext_data = urlparse.urlsplit("")

        if not self.options["port_https_ext"]:
            self.options["port_https_ext"] = self.options["port_https"]
        if self.options["data_dir"] == DATA_DIR_DEFAULT:
            coerceDataDir(
                self.options["data_dir"]
            )  # this is not done when using the default value

        self.html_dir = os.path.join(self.options["data_dir"], C.HTML_DIR)
        self.themes_dir = os.path.join(self.options["data_dir"], C.THEMES_DIR)

        self._cleanup = []

        self.signal_handler = SignalHandler(self)
        self.sessions = {}  # key = session value = user
        self.prof_connected = set()  # Profiles connected
        self.ns_map = {}  # map of short name to namespaces

        ## bridge ##
        try:
            self.bridge = Bridge()
        except BridgeExceptionNoService:
            print(u"Can't connect to SàT backend, are you sure it's launched ?")
            sys.exit(1)
        self.bridge.bridgeConnect(callback=self._bridgeCb, errback=self._bridgeEb)

    def _namespacesGetCb(self, ns_map):
        self.ns_map = ns_map

    def _namespacesGetEb(self, failure_):
        log.error(_(u"Can't get namespaces map: {msg}").format(msg=failure_))

    def backendReady(self, dummy):
        self.root = root = LiberviaRootResource(self.html_dir)
        _register = Register(self)
        _upload_radiocol = UploadManagerRadioCol(self)
        _upload_avatar = UploadManagerAvatar(self)
        d = self.bridgeCall("namespacesGet")
        d.addCallback(self._namespacesGetCb)
        d.addErrback(self._namespacesGetEb)
        self.signal_handler.plugRegister(_register)
        self.bridge.register_signal("connected", self.signal_handler.connected)
        self.bridge.register_signal("disconnected", self.signal_handler.disconnected)
        # core
        for signal_name in [
            "presenceUpdate",
            "messageNew",
            "subscribe",
            "contactDeleted",
            "newContact",
            "entityDataUpdated",
            "paramUpdate",
        ]:
            self.bridge.register_signal(
                signal_name, self.signal_handler.getGenericCb(signal_name)
            )
        # XXX: actionNew is handled separately because the handler must manage security_limit
        self.bridge.register_signal("actionNew", self.signal_handler.actionNewHandler)
        # plugins
        for signal_name in [
            "psEvent",
            "mucRoomJoined",
            "tarotGameStarted",
            "tarotGameNew",
            "tarotGameChooseContrat",
            "tarotGameShowCards",
            "tarotGameInvalidCards",
            "tarotGameCardsPlayed",
            "tarotGameYourTurn",
            "tarotGameScore",
            "tarotGamePlayers",
            "radiocolStarted",
            "radiocolPreload",
            "radiocolPlay",
            "radiocolNoUpload",
            "radiocolUploadOk",
            "radiocolSongRejected",
            "radiocolPlayers",
            "mucRoomLeft",
            "mucRoomUserChangedNick",
            "chatStateReceived",
        ]:
            self.bridge.register_signal(
                signal_name, self.signal_handler.getGenericCb(signal_name), "plugin"
            )
        self.media_dir = self.bridge.getConfig("", "media_dir")
        self.local_dir = self.bridge.getConfig("", "local_dir")
        self.cache_root_dir = os.path.join(self.local_dir, C.CACHE_DIR)

        # JSON APIs
        self.putChild("json_signal_api", self.signal_handler)
        self.putChild("json_api", MethodHandler(self))
        self.putChild("register_api", _register)

        # files upload
        self.putChild("upload_radiocol", _upload_radiocol)
        self.putChild("upload_avatar", _upload_avatar)

        # static pages
        self.putChild("blog_legacy", MicroBlog(self))
        self.putChild(C.THEMES_URL, ProtectedFile(self.themes_dir))

        # websocket
        if self.options["connection_type"] in ("https", "both"):
            wss = websockets.LiberviaPageWSProtocol.getResource(self, secure=True)
            self.putChild("wss", wss)
        if self.options["connection_type"] in ("http", "both"):
            ws = websockets.LiberviaPageWSProtocol.getResource(self, secure=False)
            self.putChild("ws", ws)

        #  Libervia pages
        LiberviaPage.importPages(self)
        LiberviaPage.setMenu(self.options["menu_json"])
        ## following signal is needed for cache handling in Libervia pages
        self.bridge.register_signal(
            "psEventRaw", partial(LiberviaPage.onNodeEvent, self), "plugin"
        )
        self.bridge.register_signal(
            "messageNew", partial(LiberviaPage.onSignal, self, "messageNew")
        )

        #  Progress handling
        self.bridge.register_signal(
            "progressStarted", partial(ProgressHandler._signal, "started")
        )
        self.bridge.register_signal(
            "progressFinished", partial(ProgressHandler._signal, "finished")
        )
        self.bridge.register_signal(
            "progressError", partial(ProgressHandler._signal, "error")
        )

        # media dirs
        # FIXME: get rid of dirname and "/" in C.XXX_DIR
        self.putChild(os.path.dirname(C.MEDIA_DIR), ProtectedFile(self.media_dir))
        self.cache_resource = web_resource.NoResource()
        self.putChild(C.CACHE_DIR, self.cache_resource)

        # special
        self.putChild(
            "radiocol",
            ProtectedFile(_upload_radiocol.getTmpDir(), defaultType="audio/ogg"),
        )  # FIXME: We cheat for PoC because we know we are on the same host, so we use directly upload dir
        # pyjamas tests, redirected only for dev versions
        if self.version[-1] == "D":
            self.putChild("test", web_util.Redirect("/libervia_test.html"))

        # redirections
        root._initRedirections(self.options)

        server.Request.defaultContentType = "text/html; charset=utf-8"
        wrapped = web_resource.EncodingResourceWrapper(
            root, [server.GzipEncoderFactory()]
        )
        self.site = server.Site(wrapped)
        self.site.sessionFactory = LiberviaSession
        self.renderer = template.Renderer(self)
        self.putChild("templates", ProtectedFile(self.renderer.base_dir))

    def initEb(self, failure):
        log.error(_(u"Init error: {msg}").format(msg=failure))
        reactor.stop()
        return failure

    def _bridgeCb(self):
        self.bridge.getReady(
            lambda: self.initialised.callback(None),
            lambda failure: self.initialised.errback(Exception(failure)),
        )
        self.initialised.addCallback(self.backendReady)
        self.initialised.addErrback(self.initEb)

    def _bridgeEb(self, failure):
        log.error(u"Can't connect to bridge: {}".format(failure))

    @property
    def version(self):
        """Return the short version of Libervia"""
        return C.APP_VERSION

    @property
    def full_version(self):
        """Return the full version of Libervia (with extra data when in development mode)"""
        version = self.version
        if version[-1] == "D":
            # we are in debug version, we add extra data
            try:
                return self._version_cache
            except AttributeError:
                self._version_cache = u"{} ({})".format(
                    version, utils.getRepositoryData(libervia)
                )
                return self._version_cache
        else:
            return version

    def bridgeCall(self, method_name, *args, **kwargs):
        """Call an asynchronous bridge method and return a deferred

        @param method_name: name of the method as a unicode
        @return: a deferred which trigger the result

        """
        d = defer.Deferred()

        def _callback(*args):
            if not args:
                d.callback(None)
            else:
                if len(args) != 1:
                    Exception("Multiple return arguments not supported")
                d.callback(args[0])

        def _errback(result):
            d.errback(
                failure.Failure(
                    jsonrpclib.Fault(C.ERRNUM_BRIDGE_ERRBACK, result.classname)
                )
            )

        kwargs["callback"] = _callback
        kwargs["errback"] = _errback
        getattr(self.bridge, method_name)(*args, **kwargs)
        return d

    @defer.inlineCallbacks
    def _logged(self, profile, request):
        """Set everything when a user just logged in

        @param profile
        @param request
        @return: a constant indicating the state:
            - C.PROFILE_LOGGED
            - C.PROFILE_LOGGED_EXT_JID
        @raise exceptions.ConflictError: session is already active
        """
        register_with_ext_jid = self.waiting_profiles.getRegisterWithExtJid(profile)
        self.waiting_profiles.purgeRequest(profile)
        session = request.getSession()
        sat_session = session_iface.ISATSession(session)
        if sat_session.profile:
            log.error(_(u"/!\\ Session has already a profile, this should NEVER happen!"))
            raise failure.Failure(exceptions.ConflictError("Already active"))

        sat_session.profile = profile
        self.prof_connected.add(profile)
        cache_dir = os.path.join(
            self.cache_root_dir, u"profiles", regex.pathEscape(profile)
        )
        # FIXME: would be better to have a global /cache URL which redirect to profile's cache directory, without uuid
        self.cache_resource.putChild(sat_session.uuid, ProtectedFile(cache_dir))
        log.debug(
            _(u"profile cache resource added from {uuid} to {path}").format(
                uuid=sat_session.uuid, path=cache_dir
            )
        )

        def onExpire():
            log.info(u"Session expired (profile={profile})".format(profile=profile))
            self.cache_resource.delEntity(sat_session.uuid)
            log.debug(
                _(u"profile cache resource {uuid} deleted").format(uuid=sat_session.uuid)
            )
            try:
                # We purge the queue
                del self.signal_handler.queue[profile]
            except KeyError:
                pass
            # and now we disconnect the profile
            self.bridgeCall("disconnect", profile)

        session.notifyOnExpire(onExpire)

        # FIXME: those session infos should be returned by connect or isConnected
        infos = yield self.bridgeCall("sessionInfosGet", profile)
        sat_session.jid = jid.JID(infos["jid"])
        sat_session.backend_started = int(infos["started"])

        state = C.PROFILE_LOGGED_EXT_JID if register_with_ext_jid else C.PROFILE_LOGGED
        defer.returnValue(state)

    @defer.inlineCallbacks
    def connect(self, request, login, password):
        """log user in

        If an other user was already logged, it will be unlogged first
        @param request(server.Request): request linked to the session
        @param login(unicode): user login
            can be profile name
            can be profile@[libervia_domain.ext]
            can be a jid (a new profile will be created with this jid if needed)
        @param password(unicode): user password
        @return (unicode, None): C.SESSION_ACTIVE: if session was aleady active else self._logged value
        @raise exceptions.DataError: invalid login
        @raise exceptions.ProfileUnknownError: this login doesn't exist
        @raise exceptions.PermissionError: a login is not accepted (e.g. empty password not allowed)
        @raise exceptions.NotReady: a profile connection is already waiting
        @raise exceptions.TimeoutError: didn't received and answer from Bridge
        @raise exceptions.InternalError: unknown error
        @raise ValueError(C.PROFILE_AUTH_ERROR): invalid login and/or password
        @raise ValueError(C.XMPP_AUTH_ERROR): invalid XMPP account password
        """

        # XXX: all security checks must be done here, even if present in javascript
        if login.startswith("@"):
            raise failure.Failure(exceptions.DataError("No profile_key allowed"))

        if login.startswith("guest@@") and login.count("@") == 2:
            log.debug("logging a guest account")
        elif "@" in login:
            if login.count("@") != 1:
                raise failure.Failure(
                    exceptions.DataError("Invalid login: {login}".format(login=login))
                )
            try:
                login_jid = jid.JID(login)
            except (RuntimeError, jid.InvalidFormat, AttributeError):
                raise failure.Failure(exceptions.DataError("No profile_key allowed"))

            # FIXME: should it be cached?
            new_account_domain = yield self.bridgeCall("getNewAccountDomain")

            if login_jid.host == new_account_domain:
                # redirect "user@libervia.org" to the "user" profile
                login = login_jid.user
                login_jid = None
        else:
            login_jid = None

        try:
            profile = yield self.bridgeCall("profileNameGet", login)
        except Exception:  # XXX: ProfileUnknownError wouldn't work, it's encapsulated
            # FIXME: find a better way to handle bridge errors
            if (
                login_jid is not None and login_jid.user
            ):  # try to create a new sat profile using the XMPP credentials
                if not self.options["allow_registration"]:
                    log.warning(
                        u"Trying to register JID account while registration is not allowed"
                    )
                    raise failure.Failure(
                        exceptions.DataError(
                            u"JID login while registration is not allowed"
                        )
                    )
                profile = login  # FIXME: what if there is a resource?
                connect_method = "asyncConnectWithXMPPCredentials"
                register_with_ext_jid = True
            else:  # non existing username
                raise failure.Failure(exceptions.ProfileUnknownError())
        else:
            if profile != login or (
                not password
                and profile
                not in self.options["empty_password_allowed_warning_dangerous_list"]
            ):
                # profiles with empty passwords are restricted to local frontends
                raise exceptions.PermissionError
            register_with_ext_jid = False

            connect_method = "connect"

        # we check if there is not already an active session
        sat_session = session_iface.ISATSession(request.getSession())
        if sat_session.profile:
            # yes, there is
            if sat_session.profile != profile:
                # it's a different profile, we need to disconnect it
                log.warning(
                    _(
                        u"{new_profile} requested login, but {old_profile} was already connected, disconnecting {old_profile}"
                    ).format(old_profile=sat_session.profile, new_profile=profile)
                )
                self.purgeSession(request)

        if self.waiting_profiles.getRequest(profile):
            #  FIXME: check if and when this can happen
            raise failure.Failure(exceptions.NotReady("Already waiting"))

        self.waiting_profiles.setRequest(request, profile, register_with_ext_jid)
        try:
            connected = yield self.bridgeCall(connect_method, profile, password)
        except Exception as failure_:
            fault = failure_.faultString
            self.waiting_profiles.purgeRequest(profile)
            if fault in ("PasswordError", "ProfileUnknownError"):
                log.info(
                    u"Profile {profile} doesn't exist or the submitted password is wrong".format(
                        profile=profile
                    )
                )
                raise failure.Failure(ValueError(C.PROFILE_AUTH_ERROR))
            elif fault == "SASLAuthError":
                log.info(
                    u"The XMPP password of profile {profile} is wrong".format(
                        profile=profile
                    )
                )
                raise failure.Failure(ValueError(C.XMPP_AUTH_ERROR))
            elif fault == "NoReply":
                log.info(
                    _(
                        "Did not receive a reply (the timeout expired or the connection is broken)"
                    )
                )
                raise exceptions.TimeOutError
            else:
                log.error(
                    u'Unmanaged fault string "{fault}" in errback for the connection of profile {profile}'.format(
                        fault=fault, profile=profile
                    )
                )
                raise failure.Failure(exceptions.InternalError(fault))

        if connected:
            #  profile is already connected in backend
            # do we have a corresponding session in Libervia?
            sat_session = session_iface.ISATSession(request.getSession())
            if sat_session.profile:
                # yes, session is active
                if sat_session.profile != profile:
                    # existing session should have been ended above
                    # so this line should never be reached
                    log.error(
                        _(
                            u"session profile [{session_profile}] differs from login profile [{profile}], this should not happen!"
                        ).format(session_profile=sat_session.profile, profile=profile)
                    )
                    raise exceptions.InternalError("profile mismatch")
                defer.returnValue(C.SESSION_ACTIVE)
            log.info(
                _(
                    u"profile {profile} was already connected in backend".format(
                        profile=profile
                    )
                )
            )
            #  no, we have to create it

        state = yield self._logged(profile, request)
        defer.returnValue(state)

    def registerNewAccount(self, request, login, password, email):
        """Create a new account, or return error
        @param request(server.Request): request linked to the session
        @param login(unicode): new account requested login
        @param email(unicode): new account email
        @param password(unicode): new account password
        @return(unicode): a constant indicating the state:
            - C.BAD_REQUEST: something is wrong in the request (bad arguments)
            - C.INVALID_INPUT: one of the data is not valid
            - C.REGISTRATION_SUCCEED: new account has been successfully registered
            - C.ALREADY_EXISTS: the given profile already exists
            - C.INTERNAL_ERROR or any unmanaged fault string
        @raise PermissionError: registration is now allowed in server configuration
        """
        if not self.options["allow_registration"]:
            log.warning(
                _(u"Registration received while it is not allowed, hack attempt?")
            )
            raise failure.Failure(
                exceptions.PermissionError(u"Registration is not allowed on this server")
            )

        if (
            not re.match(C.REG_LOGIN_RE, login)
            or not re.match(C.REG_EMAIL_RE, email, re.IGNORECASE)
            or len(password) < C.PASSWORD_MIN_LENGTH
        ):
            return C.INVALID_INPUT

        def registered(result):
            return C.REGISTRATION_SUCCEED

        def registeringError(failure):
            status = failure.value.faultString
            if status == "ConflictError":
                return C.ALREADY_EXISTS
            elif status == "InternalError":
                return C.INTERNAL_ERROR
            else:
                log.error(
                    _(u"Unknown registering error status: {status }").format(
                        status=status
                    )
                )
                return status

        d = self.bridgeCall("registerSatAccount", email, password, login)
        d.addCallback(registered)
        d.addErrback(registeringError)
        return d

    def addCleanup(self, callback, *args, **kwargs):
        """Add cleaning method to call when service is stopped

        cleaning method will be called in reverse order of they insertion
        @param callback: callable to call on service stop
        @param *args: list of arguments of the callback
        @param **kwargs: list of keyword arguments of the callback"""
        self._cleanup.insert(0, (callback, args, kwargs))

    def startService(self):
        """Connect the profile for Libervia and start the HTTP(S) server(s)"""

        def eb(e):
            log.error(_(u"Connection failed: %s") % e)
            self.stop()

        def initOk(dummy):
            try:
                connected = self.bridge.isConnected(C.SERVICE_PROFILE)
            except Exception as e:
                # we don't want the traceback
                msg = [l for l in unicode(e).split("\n") if l][-1]
                log.error(
                    u"Can't check service profile ({profile}), are you sure it exists ?\n{error}".format(
                        profile=C.SERVICE_PROFILE, error=msg
                    )
                )
                self.stop()
                return
            if not connected:
                self.bridge.connect(
                    C.SERVICE_PROFILE,
                    self.options["passphrase"],
                    {},
                    callback=self._startService,
                    errback=eb,
                )
            else:
                self._startService()

        self.initialised.addCallback(initOk)

    ## URLs ##

    def putChild(self, path, resource):
        """Add a child to the root resource"""
        # FIXME: check that no information is leaked (c.f. https://twistedmatrix.com/documents/current/web/howto/using-twistedweb.html#request-encoders)
        self.root.putChild(
            path,
            web_resource.EncodingResourceWrapper(resource, [server.GzipEncoderFactory()]),
        )

    def getExtBaseURLData(self, request):
        """Retrieve external base URL Data

        this method tried to retrieve the base URL found by external user
        It does by checking in this order:
            - base_url_ext option from configuration
            - proxy x-forwarder-host headers
            - URL of the request
        @return (urlparse.SplitResult): SplitResult instance with only scheme and netloc filled
        """
        ext_data = self.base_url_ext_data
        url_path = request.URLPath()
        if not ext_data.scheme or not ext_data.netloc:
            #  ext_data is not specified, we check headers
            if request.requestHeaders.hasHeader("x-forwarded-host"):
                # we are behing a proxy
                # we fill proxy_scheme and proxy_netloc value
                proxy_host = request.requestHeaders.getRawHeaders("x-forwarded-host")[0]
                try:
                    proxy_server = request.requestHeaders.getRawHeaders(
                        "x-forwarded-server"
                    )[0]
                except TypeError:
                    # no x-forwarded-server found, we use proxy_host
                    proxy_netloc = proxy_host
                else:
                    # if the proxy host has a port, we use it with server name
                    proxy_port = urlparse.urlsplit(u"//{}".format(proxy_host)).port
                    proxy_netloc = (
                        u"{}:{}".format(proxy_server, proxy_port)
                        if proxy_port is not None
                        else proxy_server
                    )
                proxy_netloc = proxy_netloc.decode("utf-8")
                try:
                    proxy_scheme = request.requestHeaders.getRawHeaders(
                        "x-forwarded-proto"
                    )[0].decode("utf-8")
                except TypeError:
                    proxy_scheme = None
            else:
                proxy_scheme, proxy_netloc = None, None
        else:
            proxy_scheme, proxy_netloc = None, None

        return urlparse.SplitResult(
            ext_data.scheme or proxy_scheme or url_path.scheme.decode("utf-8"),
            ext_data.netloc or proxy_netloc or url_path.netloc.decode("utf-8"),
            ext_data.path or u"/",
            "",
            "",
        )

    def getExtBaseURL(self, request, path="", query="", fragment="", scheme=None):
        """Get external URL according to given elements

        external URL is the URL seen by external user
        @param path(unicode): same as for urlsplit.urlsplit
            path will be prefixed to follow found external URL if suitable
        @param params(unicode): same as for urlsplit.urlsplit
        @param query(unicode): same as for urlsplit.urlsplit
        @param fragment(unicode): same as for urlsplit.urlsplit
        @param scheme(unicode, None): if not None, will override scheme from base URL
        @return (unicode): external URL
        """
        split_result = self.getExtBaseURLData(request)
        return urlparse.urlunsplit(
            (
                split_result.scheme.decode("utf-8") if scheme is None else scheme,
                split_result.netloc.decode("utf-8"),
                os.path.join(split_result.path, path),
                query,
                fragment,
            )
        )

    def checkRedirection(self, url):
        """check is a part of the URL prefix is redirected then replace it

        @param url(unicode): url to check
        @return (unicode): possibly redirected URL which should link to the same location
        """
        inv_redirections = self.root.inv_redirections
        url_parts = url.strip(u"/").split(u"/")
        for idx in xrange(len(url), 0, -1):
            test_url = u"/" + u"/".join(url_parts[:idx])
            if test_url in inv_redirections:
                rem_url = url_parts[idx:]
                return os.path.join(
                    u"/", u"/".join([inv_redirections[test_url]] + rem_url)
                )
        return url

    ## Sessions ##

    def purgeSession(self, request):
        """helper method to purge a session during request handling"""
        session = request.session
        if session is not None:
            log.debug(_(u"session purge"))
            session.expire()
            # FIXME: not clean but it seems that it's the best way to reset
            #        session during request handling
            request._secureSession = request._insecureSession = None

    def getSessionData(self, request, *args):
        """helper method to retrieve session data

        @param request(server.Request): request linked to the session
        @param *args(zope.interface.Interface): interface of the session to get
        @return (iterator(data)): requested session data
        """
        session = request.getSession()
        if len(args) == 1:
            return args[0](session)
        else:
            return (iface(session) for iface in args)

    @defer.inlineCallbacks
    def getAffiliation(self, request, service, node):
        """retrieve pubsub node affiliation for current user

        use cache first, and request pubsub service if not cache is found
        @param request(server.Request): request linked to the session
        @param service(jid.JID): pubsub service
        @param node(unicode): pubsub node
        @return (unicode): affiliation
        """
        sat_session = self.getSessionData(request, session_iface.ISATSession)
        if sat_session.profile is None:
            raise exceptions.InternalError(u"profile must be set to use this method")
        affiliation = sat_session.getAffiliation(service, node)
        if affiliation is not None:
            defer.returnValue(affiliation)
        else:
            try:
                affiliations = yield self.bridgeCall(
                    "psAffiliationsGet", service.full(), node, sat_session.profile
                )
            except Exception as e:
                log.warning(
                    "Can't retrieve affiliation for {service}/{node}: {reason}".format(
                        service=service, node=node, reason=e
                    )
                )
                affiliation = u""
            else:
                try:
                    affiliation = affiliations[node]
                except KeyError:
                    affiliation = u""
            sat_session.setAffiliation(service, node, affiliation)
            defer.returnValue(affiliation)

    ## Websocket (dynamic pages) ##

    def getWebsocketURL(self, request):
        base_url_split = self.getExtBaseURLData(request)
        if base_url_split.scheme.endswith("s"):
            scheme = u"wss"
        else:
            scheme = u"ws"

        return self.getExtBaseURL(request, path=scheme, scheme=scheme)

    def registerWSToken(self, token, page, request):
        websockets.LiberviaPageWSProtocol.registerToken(token, page, request)

    ## Various utils ##

    def getHTTPDate(self, timestamp=None):
        now = time.gmtime(timestamp)
        fmt_date = u"{day_name}, %d {month_name} %Y %H:%M:%S GMT".format(
            day_name=C.HTTP_DAYS[now.tm_wday], month_name=C.HTTP_MONTH[now.tm_mon - 1]
        )
        return time.strftime(fmt_date, now)

    ## TLS related methods ##

    def _TLSOptionsCheck(self):
        """Check options coherence if TLS is activated, and update missing values

        Must be called only if TLS is activated
        """
        if not self.options["tls_certificate"]:
            log.error(u"a TLS certificate is needed to activate HTTPS connection")
            self.quit(1)
        if not self.options["tls_private_key"]:
            self.options["tls_private_key"] = self.options["tls_certificate"]

        if not self.options["tls_private_key"]:
            self.options["tls_private_key"] = self.options["tls_certificate"]

    def _loadCertificates(self, f):
        """Read a .pem file with a list of certificates

        @param f (file): file obj (opened .pem file)
        @return (list[OpenSSL.crypto.X509]): list of certificates
        @raise OpenSSL.crypto.Error: error while parsing the file
        """
        # XXX: didn't found any method to load a .pem file with several certificates
        #      so the certificates split is done here
        certificates = []
        buf = []
        while True:
            line = f.readline()
            buf.append(line)
            if "-----END CERTIFICATE-----" in line:
                certificates.append(
                    OpenSSL.crypto.load_certificate(
                        OpenSSL.crypto.FILETYPE_PEM, "".join(buf)
                    )
                )
                buf = []
            elif not line:
                log.debug(u"{} certificate(s) found".format(len(certificates)))
                return certificates

    def _loadPKey(self, f):
        """Read a private key from a .pem file

        @param f (file): file obj (opened .pem file)
        @return (list[OpenSSL.crypto.PKey]): private key object
        @raise OpenSSL.crypto.Error: error while parsing the file
        """
        return OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, f.read())

    def _loadCertificate(self, f):
        """Read a public certificate from a .pem file

        @param f (file): file obj (opened .pem file)
        @return (list[OpenSSL.crypto.X509]): public certificate
        @raise OpenSSL.crypto.Error: error while parsing the file
        """
        return OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, f.read())

    def _getTLSContextFactory(self):
        """Load TLS certificate and build the context factory needed for listenSSL"""
        if ssl is None:
            raise ImportError(u"Python module pyOpenSSL is not installed!")

        cert_options = {}

        for name, option, method in [
            ("privateKey", "tls_private_key", self._loadPKey),
            ("certificate", "tls_certificate", self._loadCertificate),
            ("extraCertChain", "tls_chain", self._loadCertificates),
        ]:
            path = self.options[option]
            if not path:
                assert option == "tls_chain"
                continue
            log.debug(u"loading {option} from {path}".format(option=option, path=path))
            try:
                with open(path) as f:
                    cert_options[name] = method(f)
            except IOError as e:
                log.error(
                    u"Error while reading file {path} for option {option}: {error}".format(
                        path=path, option=option, error=e
                    )
                )
                self.quit(2)
            except OpenSSL.crypto.Error:
                log.error(
                    u"Error while parsing file {path} for option {option}, are you sure it is a valid .pem file?".format(
                        path=path, option=option
                    )
                )
                if (
                    option == "tls_private_key"
                    and self.options["tls_certificate"] == path
                ):
                    log.error(
                        u"You are using the same file for private key and public certificate, make sure that both a in {path} or use --tls_private_key option".format(
                            path=path
                        )
                    )
                self.quit(2)

        return ssl.CertificateOptions(**cert_options)

    ## service management ##

    def _startService(self, dummy=None):
        """Actually start the HTTP(S) server(s) after the profile for Libervia is connected.

        @raise ImportError: OpenSSL is not available
        @raise IOError: the certificate file doesn't exist
        @raise OpenSSL.crypto.Error: the certificate file is invalid
        """
        # now that we have service profile connected, we add resource for its cache
        service_path = regex.pathEscape(C.SERVICE_PROFILE)
        cache_dir = os.path.join(self.cache_root_dir, u"profiles", service_path)
        self.cache_resource.putChild(service_path, ProtectedFile(cache_dir))
        self.service_cache_url = u"/" + os.path.join(C.CACHE_DIR, service_path)
        session_iface.SATSession.service_cache_url = self.service_cache_url

        if self.options["connection_type"] in ("https", "both"):
            self._TLSOptionsCheck()
            context_factory = self._getTLSContextFactory()
            reactor.listenSSL(self.options["port_https"], self.site, context_factory)
        if self.options["connection_type"] in ("http", "both"):
            if (
                self.options["connection_type"] == "both"
                and self.options["redirect_to_https"]
            ):
                reactor.listenTCP(
                    self.options["port"],
                    server.Site(
                        RedirectToHTTPS(
                            self.options["port"], self.options["port_https_ext"]
                        )
                    ),
                )
            else:
                reactor.listenTCP(self.options["port"], self.site)

    @defer.inlineCallbacks
    def stopService(self):
        log.info(_("launching cleaning methods"))
        for callback, args, kwargs in self._cleanup:
            callback(*args, **kwargs)
        try:
            yield self.bridgeCall("disconnect", C.SERVICE_PROFILE)
        except Exception:
            log.warning(u"Can't disconnect service profile")

    def run(self):
        reactor.run()

    def stop(self):
        reactor.stop()

    def quit(self, exit_code=None):
        """Exit app when reactor is running

        @param exit_code(None, int): exit code
        """
        self.stop()
        sys.exit(exit_code or 0)


class RedirectToHTTPS(web_resource.Resource):
    def __init__(self, old_port, new_port):
        web_resource.Resource.__init__(self)
        self.isLeaf = True
        self.old_port = old_port
        self.new_port = new_port

    def render(self, request):
        netloc = request.URLPath().netloc.replace(
            ":%s" % self.old_port, ":%s" % self.new_port
        )
        url = "https://" + netloc + request.uri
        return web_util.redirectTo(url, request)


registerAdapter(session_iface.SATSession, server.Session, session_iface.ISATSession)
registerAdapter(
    session_iface.SATGuestSession, server.Session, session_iface.ISATGuestSession
)
