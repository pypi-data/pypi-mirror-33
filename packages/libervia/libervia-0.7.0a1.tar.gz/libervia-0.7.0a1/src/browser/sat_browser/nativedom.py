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

"""
This class provide basic DOM parsing based on native javascript parser
__init__ code comes from Tim Down at http://stackoverflow.com/a/8412989
"""

from __pyjamas__ import JS


class Node(object):

    def __init__(self, js_node):
        self._node = js_node

    def _jsNodesList2List(self, js_nodes_list):
        ret = []
        for i in range(len(js_nodes_list)):
            #ret.append(Element(js_nodes_list.item(i)))
            ret.append(self.__class__(js_nodes_list.item(i)))  # XXX: Ugly, but used to work around a Pyjamas's bug
        return ret

    def __getattr__(self, name):
        if name in ('TEXT_NODE', 'ELEMENT_NODE', 'ATTRIBUTE_NODE', 'COMMENT_NODE', 'nodeName', 'nodeType', 'wholeText'):
            return getattr(self._node, name)
        return object.__getattribute__(self, name)

    @property # XXX: doesn't work in --strict mode in pyjs
    def childNodes(self):
        return self._jsNodesList2List(self._node.childNodes)

    def getAttribute(self, attr):
        return self._node.getAttribute(attr)

    def setAttribute(self, attr, value):
        return self._node.setAttribute(attr, value)

    def hasAttribute(self, attr):
        return self._node.hasAttribute(attr)

    def toxml(self):
        return JS("""this._node.outerHTML || new XMLSerializer().serializeToString(this._node);""")


class Element(Node):

    def __init__(self, js_node):
        Node.__init__(self, js_node)

    def getElementsByTagName(self, tagName):
        return self._jsNodesList2List(self._node.getElementsByTagName(tagName))


class Document(Node):

    def __init__(self, js_document):
        Node.__init__(self, js_document)

    @property
    def documentElement(self):
        return Element(self._node.documentElement)


class NativeDOM:

    def __init__(self):
        JS("""

        if (typeof window.DOMParser != "undefined") {
            this.parseXml = function(xmlStr) {
                return ( new window.DOMParser() ).parseFromString(xmlStr, "text/xml");
            };
        } else if (typeof window.ActiveXObject != "undefined" &&
               new window.ActiveXObject("Microsoft.XMLDOM")) {
            this.parseXml = function(xmlStr) {
                var xmlDoc = new window.ActiveXObject("Microsoft.XMLDOM");
                xmlDoc.async = "false";
                xmlDoc.loadXML(xmlStr);
                return xmlDoc;
            };
        } else {
            throw new Error("No XML parser found");
        }
        """)

    def parseString(self, xml):
        return Document(self.parseXml(xml))
