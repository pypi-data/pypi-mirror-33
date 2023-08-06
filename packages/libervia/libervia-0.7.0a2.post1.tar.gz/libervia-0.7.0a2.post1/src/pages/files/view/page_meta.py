#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from libervia.server.constants import Const as C
from sat.core.i18n import _
from twisted.internet import defer
from twisted.web import static
from libervia.server.utils import ProgressHandler
import tempfile
import os
import os.path
from sat.core.log import getLogger

log = getLogger("pages/files/view")
"""files handling pages"""

name = u"files_view"
access = C.PAGES_ACCESS_PROFILE


def parse_url(self, request):
    self.getPathArgs(request, ["service", "*path"], min_args=2, service="jid", path="")


def cleanup(dummy, tmp_dir, dest_path):
    try:
        os.unlink(dest_path)
    except OSError:
        log.warning(_(u"Can't remove temporary file {path}").format(path=dest_path))
    try:
        os.rmdir(tmp_dir)
    except OSError:
        log.warning(_(u"Can't remove temporary directory {path}").format(path=tmp_dir))


@defer.inlineCallbacks
def render(self, request):
    data = self.getRData(request)
    profile = self.getProfile(request)
    service, path_elts = data[u"service"], data[u"path"]
    basename = path_elts[-1]
    dir_elts = path_elts[:-1]
    dir_path = u"/".join(dir_elts)
    tmp_dir = tempfile.mkdtemp()
    dest_path = os.path.join(tmp_dir, basename)
    request.notifyFinish().addCallback(cleanup, tmp_dir, dest_path)
    progress_id = yield self.host.bridgeCall(
        "fileJingleRequest",
        service.full(),
        dest_path,
        basename,
        u"",
        u"",
        {u"path": dir_path},
        profile,
    )
    log.debug(u"file requested")
    yield ProgressHandler(self.host, progress_id, profile).register()
    log.debug(u"file downloaded")
    self.delegateToResource(request, static.File(dest_path))
