###############################################################################
###############################################################################
## Copyright 2000-2018 The Board of Trustees of the University of Illinois.
## All rights reserved.
##
## Developed by:
##
##   LSST Image Ingest and Distribution Team
##   National Center for Supercomputing Applications
##   University of Illinois
##   http://www.ncsa.illinois.edu/enabling/data/lsst
##
## Permission is hereby granted, free of charge, to any person obtaining
## a copy of this software and associated documentation files (the
## "Software"), to deal with the Software without restriction, including
## without limitation the rights to use, copy, modify, merge, publish,
## distribute, sublicense, and/or sell copies of the Software, and to
## permit persons to whom the Software is furnished to do so, subject to
## the following conditions:
##
##   Redistributions of source code must retain the above copyright
##   notice, this list of conditions and the following disclaimers.
##
##   Redistributions in binary form must reproduce the above copyright
##   notice, this list of conditions and the following disclaimers in the
##   documentation and/or other materials provided with the distribution.
##
##   Neither the names of the National Center for Supercomputing
##   Applications, the University of Illinois, nor the names of its
##   contributors may be used to endorse or promote products derived from
##   this Software without specific prior written permission.
##
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
## EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
## MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
## IN NO EVENT SHALL THE CONTRIBUTORS OR COPYRIGHT HOLDERS BE LIABLE FOR
## ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
## CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
## WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS WITH THE SOFTWARE.



from lxml import etree
from const import *
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
        subTree = self.recursive_encodeXML(msg, pydict)
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
                    subsubNode = self.recursive_encodeXML(subNode, val)
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
