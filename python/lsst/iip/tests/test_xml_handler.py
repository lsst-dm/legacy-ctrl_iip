""" Testing file used for XMLHandler
        Used with pytest as the Unit testing module """

import pytest
import sys
from lxml import etree

sys.path.insert(0, "../iip") 
from const import * 

class TestXMLHandler: 

    @pytest.fixture(scope="session")
    def xmlH(self): 
        """Return a XMLHandler instance for the test session.
        """
        from XMLHandler import XMLHandler 
        return XMLHandler() 

    @pytest.fixture
    def pyDict(self): 
        """python dictionary test case to match against the output 
           of either encodeXML or decodeXML method
        """
        pydict = {}
        pydict[MSG_TYPE] = "NCSA_READOUT_ACK"
        pydict[JOB_NUM] = 6
        pydict["COMPONENT_NAME"] = "NCSA"
        pydict["ACK_ID"] = "ack_sequence"
        pydict["ACK_BOOL"] = False
        pydict["EXPECTED_DISTRIBUTOR_ACKS"] = 10 
        pydict["RECEIVED_DISTRIBUTOR_ACKS"] = 10
        pydict["MISSING_DISTRIBUTORS"] = 0 
        return pydict
    
    @pytest.fixture
    def xmlString(self): 
        """XML String test case to match against the output 
           of either encodeXML or decodeXML method
        """
        xmlString =('<messageDict>'
                        '<message MSG_TYPE="NCSA_READOUT_ACK">'
                            '<JOB_NUM>6</JOB_NUM>'
                            '<COMPONENT_NAME>NCSA</COMPONENT_NAME>'
                            '<ACK_ID>ack_sequence</ACK_ID>'
                            '<ACK_BOOL ack_bool_false="false"/>'
                            '<EXPECTED_DISTRIBUTOR_ACKS>10</EXPECTED_DISTRIBUTOR_ACKS>'
                            '<RECEIVED_DISTRIBUTOR_ACKS>10</RECEIVED_DISTRIBUTOR_ACKS>'
                            '<MISSING_DISTRIBUTORS>0</MISSING_DISTRIBUTORS>'
                        '</message>'
                    '</messageDict>') 
        return xmlString  

    def test_encodeXML(self, xmlH, pyDict): 
        result = xmlH.encodeXML(pyDict)
        resultDict = xmlH.decodeXML(result)
        assert pyDict == resultDict, "Resulting XML format is not valid." 

    def test_decodeXML(self, xmlH, xmlString, pyDict): 
        xml = etree.fromstring(xmlString) 
        result = xmlH.decodeXML(xml) 
        assert pyDict == result, "Resulting python dictionary is not valid."
