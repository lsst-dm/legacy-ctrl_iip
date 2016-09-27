from lxml import etree
from const import *
from copy import deepcopy 
import yaml
import sys


class XMLHandler:
    def __init__(self, callback=None):
        try:
            self._schemafile = open("schema/relaxSchema.xml")
        except IOError:
            print "Cannot open schema file"
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
            Has to convert ACK_BOOL to "true" so that it works with xml boolean
            :param pydict: python dictionary
            :type pydict: dict
        """
        pydict = deepcopy(dictValue)
        root = etree.Element("messageDict")
        msg = etree.Element("message", MSG_TYPE=pydict["MSG_TYPE"]) 
        root.append(msg)

        for kee, value in pydict.items(): 
            if kee != "MSG_TYPE" and type(value) != bool:
                keenode = etree.Element(kee)
                msg.append(keenode)
                keenode.text = str(value)
            elif type(value) == bool: 
                pydict[kee] = str(value).lower()
                if msg.find("ACK_BOOL") is not None: 
                    ack_bool = msg.find("ACK_BOOL")
                    ack_bool.set(kee.lower() + "_" + pydict[kee], pydict[kee]) 
                else: 
                    ack = str(pydict["ACK_BOOL"]).lower()
                    ack_bool = etree.Element("ACK_BOOL")
                    ack_bool.set("ack_bool_" + ack, ack) 
                    ack_bool.set(kee.lower() + "_" + pydict[kee], pydict[kee]) 
                    msg.append(ack_bool) 
        return root

    def decodeXML(self, rootNode):
        """ Decode XML tree to python dictionary
            Has to convert the "true" back to python boolean True
            :param rootNode: XML root node
            :type rootNode: lxml etree
        """
        pydict = {}
        pydict["MSG_TYPE"] = rootNode[0].get("MSG_TYPE") 
        for node in rootNode.iter():
            if node.text != None: 
                pydict[node.tag] = int(node.text) if node.text.isdigit() else node.text
            elif node.tag == "ACK_BOOL": 
                attr = node.attrib
                for kee,value in attr.items():
                    key = kee.replace("_" + value,"")
                    val = True if value == "true" else False
                    pydict[key.upper()] = val
        return pydict

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
        print(etree.tostring(rootNode, pretty_print=True))
