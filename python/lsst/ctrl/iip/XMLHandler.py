# This file is part of ctrl_iip
#
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


from lxml import etree
from copy import deepcopy
import sys


class XMLHandler:
    def __init__(self, callback=None):
        try:
            self._schemafile = open("schema/relaxSchema.xml")
        except IOError:
            print("Cannot open schema file")
            sys.exit(96)
        self._schemadoc = etree.parse(self._schemafile)
        self._schemaNG = etree.RelaxNG(self._schemadoc)
        self._consumer_callback = callback

    def xmlcallback(self, ch, method, properties, body):
        """ Decode the message body before consuming
            Setting the consumer callback function
        """
        msgTree = self.toTree(body)
        pydict = self.decodeXML(msgTree)
        self._consumer_callback(ch, method, properties, pydict)

    def validate(self, rootNode):
        """ Validate the XML with the schema
            :param rootNode: root Node of the XML element
            :type rootNode: lxml etree
        """
        return self._schemaNG.validate(rootNode)

    def encodeXML(self, dictValue):
        """ Encode python dictionary into XML
            Has to convert ACK_BOOL to "ack_bool_true" so that it works with conditional
            :param dictValue: python dictionary to encode XML
            :type dictValue: dict
        """
        pydict = deepcopy(dictValue)
        root = etree.Element("messageDict")
        msg = etree.Element("message", MSG_TYPE=pydict["MSG_TYPE"])
        root.append(msg)
        subTree = self.recursive_encodeXML(msg, pydict)  # XXX - never used??
        return root

    def recursive_encodeXML(self, node, msgDict):
        """ Recursively encode the XML dictionary
            :param node: empty XML node to add elements
            :param msgDict: python dictionary to convert values from
            :type node: lxml Element
            :type msgDict: dict
        """
        for kee, val in list(msgDict.items()):
            if kee != "MSG_TYPE":
                subNode = etree.SubElement(node, kee)
                if type(val) != dict:
                    if kee == "ACK_BOOL":
                        boolean = str(val).lower()
                        subNode.set("ack_bool_" + boolean, boolean)
                    else:
                        subNode.text = str(val)
                else:
                    subsubNode = self.recursive_encodeXML(subNode, val)  # XXX - never used??
        return self.get_parent(node)

    def get_parent(self, node):
        """ Recursively calls the parent node of current element
            :param node: XML root node to call its parent
            :type node: lxml Element
        """
        if node.getparent() is None:
            return node
        else:
            return self.get_parent(node.getparent())

    def decodeXML(self, rootNode):
        """ Decode XML tree to python dictionary
            Has to convert the "true" back to python boolean True
            :param rootNode: XML root node to conver to python dictionary
            :type rootNode: lxml etree
        """
        pydict = {}
        message = rootNode.find("message")
        xmlDict = self.recursive_decodeXML(rootNode, pydict)
        xmlDict["message"]["MSG_TYPE"] = next(val for kee, val in message.attrib.items() if kee.startswith("MSG_TYPE"))
        return xmlDict["message"]

    def recursive_decodeXML(self, rootnode, msgDict):
        """ Recursively decode XML back to python dictionary
            :param rootnode: XML root node to convert to python dictionary
            :param msgDict: empty python dictionary to add elements
            :type rootnode: lxml Element
            :type msgDict: dict
        """
        for node in rootnode:
            if len(node) != 0:
                smallDict = {}
                self.recursive_decodeXML(node, smallDict)
                msgDict[node.tag] = smallDict
            else:
                if len(node.attrib) != 0:
                    ack_bool = next(val for kee, val in node.attrib.items() if kee.startswith("ack_bool"))
                    msgDict[node.tag] = True if ack_bool == "True" else False
                else:
                    msgDict[node.tag] = node.text
        return msgDict

    def tostring(self, rootNode):
        """ Changes the XML tree to string
            :param rootNode: XML root node
        """
        return etree.tostring(rootNode)

    def toTree(self, xmlstring):
        """ Changes String back to XML tree
            :param xmlstring: XML string
        """
        return etree.XML(xmlstring)

    def printXML(self, rootNode):
        """ print out XML tree in formatted manner
            :param rootNode: root Node of XML tree
            :type rootNode: lxml etree root node
        """
        print((etree.tostring(rootNode, pretty_print=True)))
