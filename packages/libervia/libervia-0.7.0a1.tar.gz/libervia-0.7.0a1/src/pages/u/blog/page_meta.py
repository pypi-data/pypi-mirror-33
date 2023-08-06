#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

name = u"user_blog"


def parse_url(self, request):
    # in this subpage, we want path args and query args
    # (i.e. what's remaining in URL: filters, id, etc.)
    # to be used by blog's url parser, so we don't skip parse_url
    data = self.getRData(request)
    service = data[u"service"]
    self.pageRedirect(
        u"blog_view", request, skip_parse_url=False, path_args=[service.full(), u"@"]
    )
