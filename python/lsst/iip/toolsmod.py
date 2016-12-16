import subprocess
import yaml

#def get_timestamp():
#    return subprocess.check_output('date +"%Y-%m-%dT%H:%M:%S.%5N"', shell=True)

def get_timestamp():
    return subprocess.check_output('date +"%Y-%m-%d %H:%M:%S.%5N"', shell=True)

def get_epoch_timestamp():
    return (int(subprocess.check_output('date +"%s%N"', shell=True)) / 86400)

#def get_epoch_timestamp():
#    return subprocess.check_output('date +"%s%N"', shell=True)

def singleton(object, instantiated=[]):
    assert object.__class__ not in instantiated, \
        "%s is a Singleton class but is already instantiated" % object.__class__
    instantiated.append(object.__class__)




""" Exception classes 
""" 
class L1Exception(Exception): 
    pass 

class L1Error(L1Exception): 
    """ Raise as general exception from main execution layer """
    def __init__(self, arg): 
        self.errormsg = arg
        raise

class L1MessageError(L1Exception): 
    """ Raise when asserting check_message in XML returns exception """
    def __init__(self, arg): 
        self.errormsg = arg

class L1RedisError(L1Exception):
    """ Raise when unable to connect to redis """
    def __init__(self, arg): 
        self.errormsg = arg

class L1RabbitConnectionError(L1Exception):
    """ Raise when unable to connect to rabbit """
    def __init__(self, arg): 
        self.errormsg = arg

def intake_yaml_file(filename):
    try:
        f = open(filename)
    except IOError:
        raise L1Error("Cant open %s" % filename)

    #cfg data map...
    cdm = yaml.safe_load(f)
    f.close()
    return cdm

def export_yaml_file(filename, params):
    try:
        f = open(filename, "w")
    except IOError:
        raise L1Error("Cant open %s" % filename)

    #cfg data map...
    f.write(yaml_dump(params))
    f.close()


