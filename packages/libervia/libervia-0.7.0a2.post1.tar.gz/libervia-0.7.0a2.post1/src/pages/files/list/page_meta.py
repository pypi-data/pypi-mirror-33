#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from libervia.server.constants import Const as C
from sat.core.i18n import _
from twisted.internet import defer
from libervia.server import session_iface
from libervia.server import pages_tools
from sat.core.log import getLogger
from sat.tools.common import uri
import json
import os

log = getLogger("pages/files/list")
"""files handling pages"""

name = u"files_list"
access = C.PAGES_ACCESS_PROFILE
template = u"file/overview.html"


def parse_url(self, request):
    self.getPathArgs(request, ["service", "*path"], min_args=1, service="jid", path="")


@defer.inlineCallbacks
def prepare_render(self, request):
    data = self.getRData(request)
    thumb_limit = data.get("thumb_limit", 300)
    template_data = request.template_data
    service, path_elts = data[u"service"], data[u"path"]
    path = u"/".join(path_elts)
    profile = self.getProfile(request) or C.SERVICE_PROFILE

    files_data = yield self.host.bridgeCall("FISList", service.full(), path, {}, profile)
    for file_data in files_data:
        try:
            extra_raw = file_data[u"extra"]
        except KeyError:
            pass
        else:
            file_data[u"extra"] = json.loads(extra_raw) if extra_raw else {}
        dir_path = path_elts + [file_data["name"]]
        if file_data[u"type"] == C.FILE_TYPE_DIRECTORY:
            page = self
        elif file_data[u"type"] == C.FILE_TYPE_FILE:
            page = self.getPageByName("files_view")

            ## thumbnails ##
            try:
                thumbnails = file_data[u"extra"]["thumbnails"]
                if not thumbnails:
                    raise KeyError
            except KeyError:
                pass
            else:
                thumbnails.sort(key=lambda t: t["size"])
                thumb = thumbnails[0]
                for thumb_data in thumbnails:
                    if thumb_data["size"][0] > thumb_limit:
                        break
                    thumb = thumb_data
                if u"url" in thumb:
                    file_data["thumb_url"] = thumb["url"]
                elif u"id" in thumb:
                    try:
                        thumb_path = yield self.host.bridgeCall(
                            "bobGetFile", service.full(), thumb[u"id"], profile
                        )
                    except Exception as e:
                        log.warning(
                            _(u"Can't retrieve thumbnail: {reason}").format(reason=e)
                        )
                    else:
                        filename = os.path.basename(thumb_path)
                        session_data = self.host.getSessionData(
                            request, session_iface.ISATSession
                        )
                        file_data["thumb_url"] = os.path.join(
                            session_data.cache_dir, filename
                        )
        else:
            raise ValueError(
                u"unexpected file type: {file_type}".format(file_type=file_data[u"type"])
            )
        file_data[u"url"] = page.getURL(service.full(), *dir_path)

        ## comments ##
        comments_url = file_data.get(u"comments_url")
        if comments_url:
            parsed_url = uri.parseXMPPUri(comments_url)
            comments_service = file_data[u"comments_service"] = parsed_url["path"]
            comments_node = file_data[u"comments_node"] = parsed_url["node"]
            try:
                comments_count = file_data[u"comments_count"] = int(
                    file_data["comments_count"]
                )
            except KeyError:
                comments_count = None
            if comments_count and data.get("retrieve_comments", False):
                file_data[u"comments"] = yield pages_tools.retrieveComments(
                    self, comments_service, comments_node, profile=profile
                )

    template_data[u"files_data"] = files_data
    template_data[u"path"] = path
    if path_elts:
        template_data[u"parent_url"] = self.getURL(service.full(), *path_elts[:-1])
