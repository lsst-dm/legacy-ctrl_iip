import subprocess

def get_timestamp():
    return subprocess.check_output('date +"%Y-%m-%d %H:%M:%S.%5N"', shell=True)

def get_epoch_timestamp():
    return subprocess.check_output('date +"%s%N"', shell=True)

def singleton(object, instantiated=[]):
    assert object.__class__ not in instantiated, \
        "%s is a Singleton class but is already instantiated" % object.__class__
    instantiated.append(object.__class__)




""" Exception class for LSST/IIP Project  
""" 
class L1Exception(Exception): 
    pass 

class L1MessageError(L1Exception): 
    """ Raise when asserting check_message in XML returns exception """
    def __init__(self, arg): 
        self.errormsg = arg
