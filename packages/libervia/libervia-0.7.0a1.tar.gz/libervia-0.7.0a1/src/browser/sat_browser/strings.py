#!/usr/bin/python
# -*- coding: utf-8 -*-

# SAT helpers methods for plugins
# Copyright (C) 2013-2016 Adrien Cossa (souliane@mailoo.org)

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

from __pyjamas__ import JS


def getURLParams(url):
    """This comes from pyjamas.Location.makeUrlDict with a small change
    to also parse full URLs, and parameters with no value specified
    (in that case the default value "" is used).
    @param url: any URL with or without parameters
    @return: a dictionary of the parameters, if any was given, or {}
    """
    dict_ = {}
    if "/" in url:
        # keep the part after the last "/"
        url = url[url.rindex("/") + 1:]
    if url.startswith("?"):
        # remove the first "?"
        url = url[1:]
    pairs = url.split("&")
    for pair in pairs:
        if len(pair) < 3:
            continue
        kv = pair.split("=", 1)
        dict_[kv[0]] = kv[1] if len(kv) > 1 else ""
    return dict_


def addURLToText(text, new_target=True):
    """Check a text for what looks like an URL and make it clickable.

    @param string (unicode): text to process
    @param new_target (bool): if True, make the link open in a new window
    """
    # FIXME: Workaround for a pyjamas bug with regex, base method in sat.frontends.tools.strings
    # In some case, Pyjamas' re module get crazy and freeze browsers (tested with Iceweasel and Chromium).
    # we use javascript as a workaround
    # This method is inspired from https://stackoverflow.com/questions/1500260/detect-urls-in-text-with-javascript
    JS("""var urlRegex = /(https?:\/\/[^\s]+)/g;
    var target = new_target ? ' target="_blank"' : '';
    return text.replace(urlRegex, function(url) {
        return '<a href="' + url + '"' + target + ' class="url">' + url + '</a>';
    })""")


def addURLToImage(text):
    """Check a XHTML text for what looks like an imageURL and make it clickable.

    @param text (unicode): text to process
    """
    # FIXME: Pyjamas re module is not stable so we use pure JS instead, base method in sat.frontends.tools.strings
    JS("""var imgRegex = /<img[^>]* src="([^"]+)"[^>]*>/g;
    return text.replace(imgRegex, function(img, src) {
        return '<a href="' + src + '" target="_blank">' + img + '</a>';
    })""")

def fixXHTMLLinks(xhtml):
    """Add http:// if the scheme is missing and force opening in a new window.

    @param string (unicode): XHTML Content
    """
    # FIXME: Pyjamas re module is not stable so we use pure JS instead, base method in sat.frontends.tools.strings
    JS("""var subs = [];
    var tag_re = /<a(?: \w+="[^"]*")* ?\/?>/g;
    var result;
    while ((result = tag_re.exec(xhtml)) !== null) {
        tag = result[0];
        var link_result = /href="([^"]*)"/.exec(tag);
        if (link_result && !(link_result[1].startsWith("#"))) {  // found a link which is not an internal anchor
            var link = link_result[0];
            var url = link_result[1];
            if (! /target="([^"]*)"/.test(tag)) {  // no target
                subs.push([tag, '<a target="_blank"' + tag.slice(2, tag.length)]);
            }
            if (! /^\w+:\/\//.test(url)) {  // no scheme
                subs.push([link, 'href="http://' + url + '"']);
            }
        }
    }
    for (i in subs) {
        xhtml = xhtml.replace(subs[i][0], subs[i][1]);
    }
    """)
    return xhtml
