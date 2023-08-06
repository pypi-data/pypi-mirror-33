#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from libervia.server.constants import Const as C
from sat.core.log import getLogger

log = getLogger("pages/photo/album")

name = u"photos_album"
access = C.PAGES_ACCESS_PROFILE
template = u"photo/album.html"


def parse_url(self, request):
    self.getPathArgs(request, ["service", "*path"], min_args=1, service="jid", path="")


def prepare_render(self, request):
    data = self.getRData(request)
    data["thumb_limit"] = 1200
    data["retrieve_comments"] = True
    files_page = self.getPageByName(u"files_list")
    return files_page.prepare_render(self, request)


def on_data_post(self, request):
    blog_page = self.getPageByName(u"blog_view")
    return blog_page.on_data_post(self, request)
