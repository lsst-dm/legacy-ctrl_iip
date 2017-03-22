import subprocess
import yaml

#def get_timestamp():
#    return subprocess.check_output('date +"%Y-%m-%dT%H:%M:%S.%5N"', shell=True)

def get_timestamp():
    return subprocess.check_output('date +"%Y-%m-%d %H:%M:%S.%5N"', shell=True)

#def get_epoch_timestamp():
#    return (int(subprocess.check_output('date +"%s%N"', shell=True)) / 86400)

def get_epoch_timestamp():
    return subprocess.check_output('date +"%s%N"', shell=True)

def singleton(object, instantiated=[]):
    assert object.__class__ not in instantiated, \
        "%s is a Singleton class but is already instantiated" % object.__class__
    instantiated.append(object.__class__)

state_enumeration = {}
state_enumeration["OFFLINE"] =  0
state_enumeration["STANDBY"] =  1
state_enumeration["DISABLE"] = 2
state_enumeration["ENABLE"] =  3
state_enumeration["FAULT"] =    4
state_enumeration["INITIAL"] =  5
state_enumeration["FINAL"] =    6

# This matrix expresses valid transitions and is reproduced in code afterwards.
#
#    \NEXT STATE
#STATE\
#      \ |Offline |Standby |Disabled|Enabled |Fault   |Initial |Final   |
#------------------------------------------------------------------------ 
#Offline |        |        |        |        |        |        |  TRUE  |
#------------------------------------------------------------------------
#Standby |  TRUE  |        |  TRUE  |        |  TRUE  |        |        |
#------------------------------------------------------------------------
#Disable |        |  TRUE  |        |  TRUE  |  TRUE  |        |        |
#------------------------------------------------------------------------
#Enable  |        |        |  TRUE  |        |  TRUE  |        |        |
#------------------------------------------------------------------------
#Fault   |        |  TRUE  |        |        |        |        |        |
#------------------------------------------------------------------------
#Initial |        |  TRUE  |        |        |        |        |        |
#------------------------------------------------------------------------
#Final   |        |        |        |        |        |        |        |
#------------------------------------------------------------------------

w, h = 7, 7;
state_matrix = [[False for x in range(w)] for y in range(h)] 
state_matrix[0][6] = True
state_matrix[1][0] = True
state_matrix[1][2] = True
state_matrix[1][4] = True
state_matrix[2][1] = True
state_matrix[2][3] = True
state_matrix[2][4] = True
state_matrix[3][2] = True
state_matrix[3][4] = True
state_matrix[4][1] = True
state_matrix[5][1] = True

# Set up same state transitions as OK
state_matrix[0][0] = True
state_matrix[1][1] = True
state_matrix[2][2] = True
state_matrix[3][3] = True
state_matrix[4][4] = True
state_matrix[5][5] = True
state_matrix[6][6] = True

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
    f.write(yaml.dump(params))
    f.close()


