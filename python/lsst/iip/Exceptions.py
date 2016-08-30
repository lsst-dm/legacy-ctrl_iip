class IIPException(Exception): 
    pass 

class InvalidXML(IIPException): 
    """ Raise when asserting check_message in XML returns exception """
    def __init__(self, arg): 
        self.errormsg = arg
