#!/usr/bin/python
# -*- coding: utf-8 -*-

# Libervia: a Salut à Toi frontend
# Copyright (C) 2013-2018 Jérôme Poisson <goffi@goffi.org>
# Copyright (C) 2013-2016 Adrien Cossa <souliane@mailoo.org>
# Copyright (C) 2013  Emmanuel Gil Peyrot <linkmauve@linkmauve.fr>

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

from twisted.internet import defer

if defer.Deferred.debug:
    # if we are in debug mode, we want to use ipdb instead of pdb
    try:
        import ipdb
        import pdb

        pdb.set_trace = ipdb.set_trace
        pdb.post_mortem = ipdb.post_mortem
    except ImportError:
        pass

import os.path
import libervia
import sat

from libervia.server.constants import Const as C

from sat.core.i18n import _
from sat.tools import config

from zope.interface import implements

from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker
import ConfigParser


CONFIG_SECTION = C.APP_NAME.lower()
if libervia.__version__ != sat.__version__:
    import sys

    sys.stderr.write(
        u"""sat module version ({sat_version}) and {current_app} version ({current_version}) mismatch

sat module is located at {sat_path}
libervia module is located at {libervia_path}

Please be sure to have the same version running
""".format(
            sat_version=sat.__version__,
            current_app=C.APP_NAME,
            current_version=libervia.__version__,
            sat_path=os.path.dirname(sat.__file__),
            libervia_path=os.path.dirname(libervia.__file__),
        ).encode(
            "utf-8"
        )
    )
    sys.stderr.flush()
    # we call os._exit to avoid help to be printed by twisted
    import os

    os._exit(1)


def coerceConnectionType(value):  # called from Libervia.OPT_PARAMETERS
    allowed_values = ("http", "https", "both")
    if value not in allowed_values:
        raise ValueError(
            "%(given)s not in %(expected)s"
            % {"given": value, "expected": str(allowed_values)}
        )
    return value


def coerceDataDir(value):  # called from Libervia.OPT_PARAMETERS
    if isinstance(value, unicode):
        # XXX: if value comes from sat.conf, it's unicode,
        # and we need byte str here (for twisted)
        value = value.encode("utf-8")
    value = value.encode("utf-8")
    html = os.path.join(value, C.HTML_DIR)
    if not os.path.isfile(os.path.join(html, C.LIBERVIA_MAIN_PAGE)):
        raise ValueError(
            "%s is not a Libervia's browser HTML directory" % os.path.realpath(html)
        )
    themes_dir = os.path.join(value, C.THEMES_DIR)
    if not os.path.isfile(os.path.join(themes_dir, "default/styles/blog.css")):
        raise ValueError(
            "%s is not a Libervia's server data directory" % os.path.realpath(themes_dir)
        )
    return value


def coerceBool(value):
    return C.bool(value)


def coerceUnicode(value):
    # XXX: we use this method to check which value to convert to Unicode
    #      but we don't do the conversion here as Twisted expect str
    return value


DATA_DIR_DEFAULT = ''
# options which are in sat.conf and on command line,
# see https://twistedmatrix.com/documents/current/api/twisted.python.usage.Options.html
OPT_PARAMETERS_BOTH = [['connection_type', 't', 'https', _(u"'http', 'https' or 'both' "
                        "(to launch both servers).").encode('utf-8'),
                        coerceConnectionType],
                       ['port', 'p', 8080,
                        _(u'The port number to listen HTTP on.').encode('utf-8'), int],
                       ['port_https', 's', 8443,
                        _(u'The port number to listen HTTPS on.').encode('utf-8'), int],
                       ['port_https_ext', 'e', 0, _(u'The external port number used for '
                        u'HTTPS (0 means port_https value).').encode('utf-8'), int],
                       ['tls_private_key', '', '', _(u'TLS certificate private key (PEM '
                        u'format)').encode('utf-8'), coerceUnicode],
                       ['tls_certificate', 'c', 'libervia.pem', _(u'TLS public '
                        u'certificate or private key and public certificate combined '
                        u'(PEM format)').encode('utf-8'), coerceUnicode],
                       ['tls_chain', '', '', _(u'TLS certificate intermediate chain (PEM '
                        u'format)').encode('utf-8'), coerceUnicode],
                       ['redirect_to_https', 'r', True, _(u'Automatically redirect from '
                        u'HTTP to HTTPS.').encode('utf-8'), coerceBool],
                       ['security_warning', 'w', True, _(u'Warn user that he is about to '
                        u'connect on HTTP.').encode('utf-8'), coerceBool],
                       ['passphrase', 'k', '', (_(u"Passphrase for the SàT profile "
                        u"named '%s'") % C.SERVICE_PROFILE).encode('utf-8'),
                        coerceUnicode],
                       ['data_dir', 'd', DATA_DIR_DEFAULT, _(u'Data directory for '
                        u'Libervia').encode('utf-8'), coerceDataDir],
                       ['allow_registration', '', True, _(u'Allow user to register new '
                        u'account').encode('utf-8'), coerceBool],
                       ['base_url_ext', '', '',
                        _(u'The external URL to use as base URL').encode('utf-8'),
                        coerceUnicode],
                      ]
# Options which are in sat.conf only
OPT_PARAMETERS_CFG = [
    ["empty_password_allowed_warning_dangerous_list", None, "", None],
    ["url_redirections_profile", None, "", None],
    ["url_redirections_dict", None, {}, None],
    ["menu_json", None, C.DEFAULT_MENU, None],
    ["tickets_trackers_json", None, None, None],
    ["mr_handlers_json", None, None, None],
]


def initialise(options):
    """Method to initialise global modules"""
    from twisted.internet import glib2reactor

    glib2reactor.install()
    # XXX: We need to configure logs before any log method is used,
    #      so here is the best place.
    from sat.core import log_config

    log_config.satConfigure(C.LOG_BACKEND_TWISTED, C, backend_data=options)
    from libervia.server import server

    # we can't import this file from libervia.server.server because it's not a true module
    # (there is no __init__.py file, as required by twistd plugin system), so we set the
    # global values from here
    server.DATA_DIR_DEFAULT = DATA_DIR_DEFAULT
    server.OPT_PARAMETERS_BOTH = OPT_PARAMETERS_BOTH
    server.OPT_PARAMETERS_CFG = OPT_PARAMETERS_CFG
    server.coerceDataDir = coerceDataDir


class Options(usage.Options):
    # optArgs is not really useful in our case, we need more than a flag
    optParameters = OPT_PARAMETERS_BOTH

    def __init__(self):
        """Read SàT configuration file in order to overwrite the hard-coded default values

        Priority for the usage of the values is (from lowest to highest):
            - hard-coded default values
            - values from SàT configuration files
            - values passed on the command line
        """
        # If we do it the reading later: after the command line options have been parsed,
        # there's no good way to know
        # if the  options values are the hard-coded ones or if they have been passed
        # on the command line.

        # FIXME: must be refactored + code can be factorised with backend
        config_parser = ConfigParser.SafeConfigParser()
        config_parser.read(C.CONFIG_FILES)
        self.handleDeprecated(config_parser)
        for param in self.optParameters + OPT_PARAMETERS_CFG:
            name = param[0]
            try:
                value = config.getConfig(config_parser, CONFIG_SECTION, name, Exception)
                if isinstance(value, unicode):
                    value = value.encode("utf-8")
                try:
                    param[2] = param[4](value)
                except IndexError:  # the coerce method is optional
                    param[2] = value
            except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
                pass
        usage.Options.__init__(self)
        for opt_data in OPT_PARAMETERS_CFG:
            self[opt_data[0]] = opt_data[2]

    def handleDeprecated(self, config_parser):
        """display warning and/or change option when a deprecated option if found

        param config_parser(ConfigParser): read ConfigParser instance for sat.conf
        """
        replacements = (("ssl_certificate", "tls_certificate"),)
        for old, new in replacements:
            try:
                value = config.getConfig(config_parser, CONFIG_SECTION, old, Exception)
            except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
                pass
            else:
                print(u"\n/!\\ Use of {old} is deprecated, please use {new} instead\n"
                      .format(old=old, new=new))
                config_parser.set(CONFIG_SECTION, new, value)


class LiberviaMaker(object):
    implements(IServiceMaker, IPlugin)

    tapname = C.APP_NAME_FILE
    description = _(u"The web frontend of Salut à Toi")
    options = Options

    def makeService(self, options):
        for opt in OPT_PARAMETERS_BOTH:
            # FIXME: that's a ugly way to get unicode in Libervia
            #        from command line or sat.conf
            #        we should move to argparse and handle options this properly
            try:
                coerce_cb = opt[4]
            except IndexError:
                continue
            if coerce_cb == coerceUnicode:
                options[opt[0]] = options[opt[0]].decode("utf-8")
        initialise(options.parent)
        from libervia.server import server

        return server.Libervia(options)


# affectation to some variable is necessary for twisted introspection to work
serviceMaker = LiberviaMaker()
