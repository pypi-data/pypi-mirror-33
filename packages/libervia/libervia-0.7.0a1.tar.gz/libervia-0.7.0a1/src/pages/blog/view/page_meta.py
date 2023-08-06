#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
from libervia.server.constants import Const as C
from twisted.words.protocols.jabber import jid
from twisted.internet import defer
from sat.tools.common import data_objects
from libervia.server import session_iface
from sat.core.i18n import _
from sat.tools.common.template import safe
from sat.tools.common import uri
from libervia.server import utils
import unicodedata
import re
import cgi
from sat.core.log import getLogger
log = getLogger('pages/blog/view')

"""generic blog (with service/node provided)"""
name = u'blog_view'
template = u"blog/articles.html"
uri_handlers = {(u'pubsub', u'microblog'): 'microblog_uri'}

RE_TEXT_URL = re.compile(ur'[^a-zA-Z,_]+')
TEXT_MAX_LEN = 60
TEXT_WORD_MIN_LENGHT = 4
URL_LIMIT_MARK = 90  # if canonical URL is longer than that, text will not be appended


def microblog_uri(self, uri_data):
    args = [uri_data[u'path'], uri_data[u'node']]
    if u'item' in uri_data:
        args.extend([u'id', uri_data[u'item']])
    return self.getURL(*args)

def parse_url(self, request):
    """URL is /[service]/[node]/[filter_keyword]/[item]|[other]

    if [node] is '@', default namespace is used
    if a value is unset, default one will be used
    keyword can be one of:
        id: next value is a item id
        tag: next value is a blog tag
    """
    data = self.getRData(request)

    try:
        service = self.nextPath(request)
    except IndexError:
        data['service'] = u''
    else:
        try:
            data[u"service"] = jid.JID(service)
        except Exception:
            log.warning(_(u"bad service entered: {}").format(service))
            self.pageError(request, C.HTTP_BAD_REQUEST)

    try:
        data['node'] = self.nextPath(request)
    except IndexError:
        data['node'] = u''
    else:
        if data['node'] == u'@':
            data['node'] = u''

    try:
        filter_kw = data['filter_keyword'] = self.nextPath(request)
    except IndexError:
        pass
    else:
        if filter_kw == u'id':
            try:
                data[u'item'] = self.nextPath(request)
            except IndexError:
                self.pageError(request, C.HTTP_BAD_REQUEST)
            # we get one more argument in case text has been added to have a nice URL
            try:
                self.nextPath(request)
            except IndexError:
                pass
        elif filter_kw == u'tag':
            try:
                data[u'tag'] = self.nextPath(request)
            except IndexError:
                self.pageError(request, C.HTTP_BAD_REQUEST)
        else:
            # invalid filter keyword
            log.warning(_(u"invalid filter keyword: {filter_kw}").format(filter_kw=filter_kw))
            self.pageError(request, C.HTTP_BAD_REQUEST)


@defer.inlineCallbacks
def appendComments(self, blog_items, identities, profile):
    for blog_item in blog_items:
        if identities is not None:
            author = blog_item.author_jid
            if not author:
                log.warning(_(u"no author found for item {item_id}").format(item_id=blog_item.id))
            else:
                if author not in identities:
                    identities[author] = yield self.host.bridgeCall(u'identityGet', author, profile)
        for comment_data in blog_item.comments:
            service = comment_data[u'service']
            node = comment_data[u'node']
            try:
                comments_data = yield self.host.bridgeCall(u'mbGet',
                                      service,
                                      node,
                                      C.NO_LIMIT,
                                      [],
                                      {},
                                      profile)
            except Exception as e:
                log.warning(_(u"Can't get comments at {node} (service: {service}): {msg}").format(
                    service=service,
                    node=node,
                    msg=e))
                continue

            comments = data_objects.BlogItems(comments_data)
            blog_item.appendCommentsItems(comments)
            yield appendComments(self, comments, identities, profile)

@defer.inlineCallbacks
def getBlogData(self, request, service, node, item_id, extra, profile):
    try:
        if item_id:
            items_id = [item_id]
        else:
            items_id = []
        blog_data = yield self.host.bridgeCall(u'mbGet',
                              service.userhost(),
                              node,
                              C.NO_LIMIT,
                              items_id,
                              extra,
                              profile)
    except Exception as e:
        # FIXME: need a better way to test errors in bridge errback
        if u"forbidden" in unicode(e):
            self.pageError(request, 401)
        else:
            log.warning(_(u"can't retrieve blog for [{service}]: {msg}".format(
                service = service.userhost(), msg=e)))
            blog_data = ([], {})

    items = data_objects.BlogItems(blog_data)
    defer.returnValue((blog_data, items))

@defer.inlineCallbacks
def prepare_render(self, request):
    data = self.getRData(request)
    # if the comments are not explicitly hidden, we show them
    service, node, item_id, show_comments = data.get(u'service', u''), data.get(u'node', u''), data.get(u'item'), data.get(u'show_comments', True)
    profile = self.getProfile(request)
    if profile is None:
        profile = C.SERVICE_PROFILE

    ## pagination/filtering parameters
    params = self.getAllPostedData(request, multiple=False)
    if item_id:
        extra = {}
    else:
        extra = {u'rsm_max': u'10'}
        if u'after' in params:
            extra[u'rsm_after'] = params[u'after']
        elif u'before' in params:
            extra[u'rsm_before'] = params[u'before']
        tag = data.get('tag')
        if tag:
            extra[u'mam_filter_{}'.format(C.MAM_FILTER_CATEGORY)] = tag

    ## main data ##
    # we get data from backend/XMPP here
    blog_data, items = yield getBlogData(self, request, service, node, item_id, extra, profile)

    ## navigation ##
    # no let's fill service, node and pagination URLs
    template_data = request.template_data
    if u'service' not in template_data:
        template_data[u'service'] = service
    if u'node' not in template_data:
        template_data[u'node'] = node
    target_profile = template_data.get(u'target_profile')

    if items:
        if not item_id:
            last_id = items[-1].id
            template_data['older_url'] = self.getParamURL(request, after=last_id)
            if u'before' in params or u'after' in params:
                first_id = items[0].id
                template_data['newer_url']  = self.getParamURL(request, before=first_id)
    else:
        if item_id:
            # if item id has been specified in URL and it's not found,
            # we must return an error
            self.pageError(request, C.HTTP_NOT_FOUND)

        # no items, we have requested items before last post, or blog is empty
        extra = {u'rsm_max': u'10'}
        blog_data, items = yield getBlogData(self, request, service, node, None, extra, profile)
        if items:
            last_id = items[-1].id
            template_data['older_url'] = self.getParamURL(request, after=last_id)

    ## identities ##
    # identities are use to show nice nickname or avatars
    identities = template_data[u'identities'] = self.host.getSessionData(request, session_iface.ISATSession).identities

    ## Comments ##
    # if comments are requested, we need to take them
    if show_comments:
        yield appendComments(self, items, identities, profile)

    ## URLs ##
    # We will fill items_http_uri and tags_http_uri in template_data with suitable urls
    # if we know the profile, we use it instead of service + blog (nicer url)
    if target_profile is None:
        blog_base_url_item = self.getPageByName(u'blog_view').getURL(service.full(), node or u'@', u'id')
        blog_base_url_tag = self.getPageByName(u'blog_view').getURL(service.full(), node or u'@', u'tag')
    else:
        blog_base_url_item = self.getURLByNames([(u'user', [target_profile]), (u'user_blog', [u'id'])])
        blog_base_url_tag = self.getURLByNames([(u'user', [target_profile]), (u'user_blog', [u'tag'])])
        # we also set the background image if specified by user
        bg_img = yield self.host.bridgeCall(u'asyncGetParamA', u'Background', u'Blog page', u'value', -1, template_data[u'target_profile'])
        if bg_img:
            template_data['dynamic_style'] = safe(u"""
                :root {
                    --bg-img: url("%s");
                }
                """ % cgi.escape(bg_img, True))

    template_data[u'items'] = data[u'items'] = items
    if request.args.get('reverse') == ['1']:
        template_data[u'items'].items.reverse()
    template_data[u'items_http_uri'] = items_http_uri = {}
    template_data[u'tags_http_uri'] = tags_http_uri = {}


    for item in items:
        blog_canonical_url = u'/'.join([blog_base_url_item, utils.quote(item.id)])
        if len(blog_canonical_url) > URL_LIMIT_MARK:
            blog_url = blog_canonical_url
        else:
            # we add text from title or body at the end of URL
            # to make it more human readable
            text = item.title or item.content
            # we change special chars to ascii one, trick found at https://stackoverflow.com/a/3194567
            text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore')
            text = RE_TEXT_URL.sub(u' ', text).lower()
            text = u'-'.join([t for t in text.split() if t and len(t)>=TEXT_WORD_MIN_LENGHT])
            while len(text) > TEXT_MAX_LEN:
                if u'-' in text:
                    text = text.rsplit(u'-', 1)[0]
                else:
                    text = text[:TEXT_MAX_LEN]
            if text:
                blog_url = blog_canonical_url + u'/' + text
            else:
                blog_url = blog_canonical_url

        items_http_uri[item.id] = self.host.getExtBaseURL(request, blog_url)
        for tag in item.tags:
            if tag not in tags_http_uri:
                tag_url = u'/'.join([blog_base_url_tag, utils.quote(tag)])
                tags_http_uri[tag] = self.host.getExtBaseURL(request, tag_url)

    # if True, page should display a comment box
    template_data[u'allow_commenting'] = data.get(u'allow_commenting', False)

    # last but not least, we add a xmpp: link to the node
    uri_args = {u'path': service.full()}
    if node:
        uri_args[u'node'] = node
    if item_id:
        uri_args[u'item'] = item_id
    template_data[u'xmpp_uri'] = uri.buildXMPPUri(u'pubsub', subtype='microblog', **uri_args)


@defer.inlineCallbacks
def on_data_post(self, request):
    profile = self.getProfile(request)
    if profile is None:
        self.pageError(request, C.HTTP_UNAUTHORIZED)
    type_ = self.getPostedData(request, u'type')
    if type_ == u'comment':
        service, node, body = self.getPostedData(request, (u'service', u'node', u'body'))

        if not body:
            self.pageError(request, C.HTTP_BAD_REQUEST)
        comment_data = {u"content": body}
        try:
            yield self.host.bridgeCall(u'mbSend', service, node, comment_data, profile)
        except Exception as e:
            if u"forbidden" in unicode(e):
                self.pageError(request, 401)
            else:
                raise e
    else:
        log.warning(_(u"Unhandled data type: {}").format(type_))
