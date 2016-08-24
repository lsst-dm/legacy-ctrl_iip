from lxml import etree
from StringIO import *
from const import *

class XMLHandler:
    def __init__(self):
        self._schemafile = open("schema/relaxSchema.xml")
        self._schemadoc = etree.parse(self._schemafile)
        self._schemaNG = etree.RelaxNG(self._schemadoc)

    def validate(self, rootNode):
        """ Validate the XML with the schema
            :param rootNode: root Node of the XML element
            :type rootNode: lxml etree
        """
        return self._schemaNG.validate(rootNode)

    def encodeXML(self, pydict):
        """Encode python dictionary into XML
           Has to convert ACK_BOOL to "true" so that it works with xml boolean
           :param pydict: python dictionary
           :type pydict: dict
        """
        root = etree.Element("messageDict")
        msg = etree.Element("message", MSG_TYPE=pydict[MSG_TYPE])
        root.append(msg)
        pydict["ACK_BOOL"] = "true" if pydict["ACK_BOOL"] == True else "false"
        for kee, value in pydict.items():
            if kee != MSG_TYPE:
                keenode = etree.Element(kee)
                msg.append(keenode)
                keenode.text = str(value)
        return root

    def decodeXML(self, rootNode):
        """Decode XML tree to python dictionary
           Has to convert the "true" back to python boolean True
           :param rootNode: XML root node
           :type rootNode: lxml etree
        """
        pydict = {}
        pydict[MSG_TYPE] = rootNode[0].get("MSG_TYPE")
        for node in rootNode.iter():
            if node.text != None:
                pydict[node.tag] = node.text
            if node.tag == "ACK_BOOL":
                pydict["ACK_BOOL"] = True if pydict["ACK_BOOL"] == "true" else False
        return pydict

    def tostring(self, rootNode):
        """Changes the XML tree to string
           :param rootNode: XML root node
        """
        return etree.tostring(rootNode)

    def toTree(self, xmlstring):
        """Changes String back to XML tree
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
        <message MSG_TYPE="IN_READY_STATE">
            <JOB_NUM>6</JOB_NUM>
        </message>
        <message MSG_TYPE="INSUFFICIENT_DISTRIBUTORS">
            <JOB_NUM>5 </JOB_NUM>
            <NEEDED_WORKERS>2 </NEEDED_WORKERS>
            <AVAILABLE_FORWARDERS> 5 </AVAILABLE_FORWARDERS>
        </message>
    </messageDict>
    """)
    readout_dict = {}
    readout_dict[MSG_TYPE] = "DISTRIBUTOR_READOUT_ACK"
    readout_dict[JOB_NUM] = 4
    readout_dict[NAME] = "CONSUME"
    readout_dict["ACK_BOOL"] = True
    readout_dict["ACK_ID"] = "TIMED_ACK_ID"
    root =  handler.encodeXML(readout_dict)
    # handler.printXML(root)
    dictionary = handler.decodeXML(root)
    for key, value in dictionary.items():
        print key, value

    en = handler.encodeXML(dictionary)
    print handler.validate(en)

if __name__ == "__main__":
    main()
