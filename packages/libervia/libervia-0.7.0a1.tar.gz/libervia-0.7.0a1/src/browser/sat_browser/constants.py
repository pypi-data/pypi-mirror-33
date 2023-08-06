#!/usr/bin/python
# -*- coding: utf-8 -*-

# Libervia: a SAT frontend
# Copyright (C) 2009-2018 Jérôme Poisson (goffi@goffi.org)

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

from libervia.common.constants import Const as C


# Auxiliary functions
param_to_bool = lambda value: value == 'true'


class Const(C):
    """Add here the constants that are only used by the browser side."""

    # Cached parameters, e.g those that have an incidence on UI display/refresh:
    #     - they can be any parameter (not necessarily specific to Libervia)
    #     - list them as a couple (category, name)
    CACHED_PARAMS = [('General', C.SHOW_OFFLINE_CONTACTS),
                     ('General', C.SHOW_EMPTY_GROUPS),
                     ]

    WEB_PANEL_DEFAULT_URL = "http://salut-a-toi.org"
    WEB_PANEL_SCHEMES = {'http', 'https', 'ftp', 'file'}

    CONTACT_DEFAULT_DISPLAY=('bare', 'nick')
