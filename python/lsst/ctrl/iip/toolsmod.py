# This file is part of ctrl_iip
# 
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import subprocess
import yaml
import pprint

def get_timestamp():
    return (subprocess.check_output('date +"%Y-%m-%d %H:%M:%S.%5N"', shell=True)).decode('ascii')

def get_epoch_timestamp():
    return (subprocess.check_output('date +"%s%N"', shell=True)).decode('ascii')

def singleton(object, instantiated=[]):
    assert object.__class__ not in instantiated, \
        "%s is a Singleton class but is already instantiated" % object.__class__
    instantiated.append(object.__class__)


prp = pprint.PrettyPrinter(indent=4)
#DP = False  #Set to true for Debug Printing
DP = True  #Set to true for Debug Printing
METRIX = True 

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

########
# Dictionary showing the state a transition ends in
next_state = {}
next_state["ENTER_CONTROL"] = "STANDBY"
next_state["EXIT_CONTROL"] = "OFFLINE"
next_state["START"] = "DISABLE"
next_state["ENABLE"] = "ENABLE"
next_state["DISABLE"] = "DISABLE"
next_state["STANDBY"] = "STANDBY"
next_state["SET_VALUE"] = "ENABLE"
next_state["ABORT"] = "DISABLE"
next_state["STOP"] = "DISABLE"

summary_state_enum = {'DISABLE':0,
                      'ENABLE':1, 
                      'FAULT':2, 
                      'OFFLINE':3, 
                      'STANDBY':4}

# Values used in state_matrix and in the ascii representation below...
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
#Offline |        | TRUE   |        |        |        |        |  TRUE  |
#------------------------------------------------------------------------
#Standby |  TRUE  |        |  TRUE  |        |  TRUE  |        |  TRUE  |
#------------------------------------------------------------------------
#Disable |        |  TRUE  |        |  TRUE  |  TRUE  |        |        |
#------------------------------------------------------------------------
#Enable  |        |        |  TRUE  |        |  TRUE  |        |        |
#------------------------------------------------------------------------
#Fault   |        |        |        |        |        |        |        |
#------------------------------------------------------------------------
#Initial |        |  TRUE  |        |        |        |        |        |
#------------------------------------------------------------------------
#Final   |        |        |        |        |        |        |        |
#------------------------------------------------------------------------

w, h = 7, 7;
state_matrix = [[False for x in range(w)] for y in range(h)] 
state_matrix[0][6] = True
state_matrix[0][1] = True
state_matrix[1][6] = True
state_matrix[1][0] = True
state_matrix[1][2] = True
state_matrix[1][4] = True
state_matrix[2][1] = True
state_matrix[2][3] = True
state_matrix[2][4] = True
state_matrix[3][2] = True
state_matrix[3][4] = True
state_matrix[5][1] = True

# Disallow same state transitions 
#state_matrix[0][0] = True
#state_matrix[1][1] = True
#state_matrix[2][2] = True
#state_matrix[3][3] = True
#state_matrix[4][4] = True
#state_matrix[5][5] = True
#state_matrix[6][6] = True


# Error codes are 4 digit numbers
# Most Significant digit is 5 for DM Errors
# Next digit (the 'hundreds' position) is:
# 1 OCS BRidge
# 2 DMCS
# 3 ArchiveDevice
# 4 Archive Controller
# 5 PromptProcess Device
# 6 AuxDevice
# 7 Forwarder
# 8 NCSA Foreman
# 9 Distributor
#
# The two least significant digits are specific errors
# So, Error Code 5371 is a DM Error originating in the Archive Device. Error is #71
#
# Error Codes
# Suffixes (Two least significant digits)
# 01 - Threading error
# 05 - No Response error
# 10 - General Scoreboard init error
# 11 - Rabbit Connection error
# 12 - Redis Connection Error
#
# 20 - Component Configuration Setup
# 21 - ForwarderCfg.yaml not found error
# 22 - YAML Key not found error 
# 23 - Cannot create directory error
# 24 - Cannot copy file error 
# 
#
# 30 - General Message error
# 31 - Publisher error
# 32 - Consumer error
# 35 - Message Handler error
#
# 50 - General ACK Error
# 51 - No Response to HEALTH_CHECK message
# 52 - No Response to XFER_PARAMS message
# 53 - No Start Integration Response from Device
# 54 - No Response to END_READOUT message
# 55 - No New Session Response
# 56 - No Next Visit Response

#Status Codes
# 4451 - No response from Archive Controller


""" Exception classes 
""" 
class L1Exception(Exception): 
    pass 

class L1Error(L1Exception): 
    """ Raise as general exception from main execution layer """
    def __init__(self, arg): 
        self.errormsg = arg

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

class L1NcsaForemanError(L1Error):
    """ Raise for general Archive Foreman error """
    def __init__(self, arg): 
        self.errormsg = arg

class L1ArchiveDeviceError(L1Error):
    """ Raise for general Archive Foreman error """
    def __init__(self, arg): 
        self.errormsg = arg

class L1PromptProcessError(L1Error):
    """ Raise for general Prompt Process Foreman error """
    def __init__(self, arg): 
        self.errormsg = arg

class L1DMCSError(L1Error):
    """ Raise for general DMCS error """
    def __init__(self, arg): 
        self.errormsg = arg

class L1ConsumerError(L1Error):
    """ Raise for general Archive Foreman error """
    def __init__(self, arg): 
        self.errormsg = arg

class L1PublisherError(L1Error):
    """ Raise for general Archive Foreman error """
    def __init__(self, arg): 
        self.errormsg = arg

class L1ForwarderError(L1Error):
    """ Raise for general Forwarder error """
    def __init__(self, arg): 
        self.errormsg = arg

class L1ConfigIOError(L1Error):
    """ Raise for general Forwarder error """
    def __init__(self, arg): 
        self.errormsg = arg

class L1ConfigKeyError(L1Error):
    """ Raise for general Forwarder error """
    def __init__(self, arg): 
        self.errormsg = arg


