from lxml import etree 
from StringIO import *
from const import *

class XMLHandler(): 
    def __init__(self): 
        self._schemafile = open("relaxSchema.xml")
        self._schemadoc = etree.parse(self._schemafile)
        self._schemaNG = etree.RelaxNG(self._schemadoc)

    def validate(self, rootNode): 
        return self._schemaNG.validate(rootNode)
    
    def encodeXML(self, pydict): 
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
        pydict = {}
        pydict[MSG_TYPE] = rootNode[0].get("MSG_TYPE")
        for node in rootNode.iter(): 
            if node.text != None:
                pydict[node.tag] = node.text
            if node.tag == "ACK_BOOL": 
                pydict["ACK_BOOL"] = True if pydict["ACK_BOOL"] == "true" else False
        return pydict

    def printXML(self, rootNode): 
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
