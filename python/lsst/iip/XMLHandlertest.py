from lxml import etree
from StringIO import * 
from XMLHandler import * 

pydict = {}
pydict["MSG_TYPE"] = "NEW_JOB_ACK"
pydict["JOB_NUM"] = 6
pydict["ACK_BOOL"] = False 
pydict["BASE_RESOURCES"] = False 
pydict["NEEDED_FORWARDERS"] = 10
pydict["AVAILABLE_FORWARDERS"] = 9
pydict["NCSA_RESOURCES"] = False
pydict["NEEDED_WORKERS"] = 10
pydict["NEEDED_DISTRIBUTORS"] = 10
pydict["AVAILABLE_DISTRIBUTORS"] = 10
pydict["AVAILABLE_WORKERS"] = 10


handler = XMLHandler()
root = handler.encodeXML(pydict)
handler.printXML(root)
print(handler.validate(root))

d = handler.decodeXML(root)
print d
"""
p2 = {}
p2["MSG_TYPE"] = "NCSA_READOUT_ACK"
p2["JOB_NUM"] = 6
p2["COMPONENT_NAME"] = "NCSA"
p2["ACK_ID"] = "id22"
p2["ACK_BOOL"] = False
p2["EXPECTED_DISTRIBUTOR_ACKS"] = 10
p2["RECEIVED_DISTRIBUTOR_ACKS"] = 9
p2["MISSING_DISTRIBUTORS"] = 1
"""

#schemafile = open("../ctrl_iip/python/lsst/iip/schema/relaxSchema.xml")
#schemafile = open("test.xml")
#schemadoc = etree.parse(schemafile)
#schemaNG = etree.RelaxNG(schemadoc)
#schemaNG.assertValid(root)


f = StringIO("""
            <messageDict>
            <message MSG_TYPE="NEW_JOB_ACK"> 
                <JOB_NUM>6</JOB_NUM>
                <ACK_BOOL ncsa_resources_true="true" ack_bool_false="false" base_resources_true="true"/>
                </message> 
            </messageDict> 
        """)
doc = etree.parse(f)
# print(etree.tostring(doc, pretty_print=True)) 
# schemaNG.assertValid(doc) 
