from lxml import etree
from const import *
import yaml

class XMLHandler:
    def __init__(self, callback=None):
        self._schemafile = open("schema/relaxSchema.xml")
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

    def encodeXML(self, pydict):
        """ Encode python dictionary into XML
            Has to convert ACK_BOOL to "true" so that it works with xml boolean
            :param pydict: python dictionary
            :type pydict: dict
        """
        root = etree.Element("messageDict")
        msg = etree.Element("message", MSG_TYPE=pydict[MSG_TYPE])
        root.append(msg)
        if "ACK_BOOL" in pydict: 
            pydict["ACK_BOOL"] = "true" if pydict["ACK_BOOL"] == True else "false"
        for kee, value in pydict.items():
            if pydict[MSG_TYPE] == "NCSA_READOUT_ACK" and kee == "ACK_BOOL": 
                ack_bool = etree.Element("ACK_BOOL")
                ack_bool.set("ack_"+pydict["ACK_BOOL"], pydict["ACK_BOOL"])
                msg.append(ack_bool)
            elif kee != MSG_TYPE:
                keenode = etree.Element(kee)
                msg.append(keenode)
                keenode.text = str(value)
        return root

    def decodeXML(self, rootNode):
        """ Decode XML tree to python dictionary
            Has to convert the "true" back to python boolean True
            :param rootNode: XML root node
            :type rootNode: lxml etree
        """
        pydict = {}
        pydict[MSG_TYPE] = rootNode[0].get("MSG_TYPE") 
        for node in rootNode.iter():
            if node.text != None: 
                pydict[node.tag] = node.text
            elif node.tag == "ACK_BOOL": 
                if node.text != None: 
                    pydict["ACK_BOOL"] = node.text
                else: 
                    attribute = node.attrib.values()
                    value = "".join(attribute)
                    pydict["ACK_BOOL"] = value
        if "ACK_BOOL" in pydict: 
            pydict["ACK_BOOL"] = True if pydict["ACK_BOOL"] == "true" else False
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

def main():
    handler = XMLHandler()
    f = StringIO("""
    <messageDict>
        <message MSG_TYPE="DISTRIBUTOR_HEALTH_ACK">
            <JOB_NUM>6</JOB_NUM> 
            <COMPONENT_NAME>NCSA</COMPONENT_NAME>
            <ACK_ID>yea</ACK_ID> 
            <ACK_BOOL>true</ACK_BOOL>
        </message>
    </messageDict>
    """)
    readout_dict = {}
    readout_dict[MSG_TYPE] = "DISTRIBUTOR_STANDBY_ACK"
    readout_dict[JOB_NUM] = 4
    readout_dict["COMPONENT_NAME"] = "CONSUME"
    readout_dict["ACK_BOOL"] = True    
    readout_dict["ACK_ID"] = "TIMED_ACK_ID"
    # handler.printXML(root)
    # dictionary = handler.decodeXML(root)
    # for key, value in dictionary.items():
    #     print key, value

    x = yaml.dump(readout_dict)
    print x
    x = yaml.load(x)
    r = handler.encodeXML(x)
    print handler.printXML(r) 
    

if __name__ == "__main__":
    main()
