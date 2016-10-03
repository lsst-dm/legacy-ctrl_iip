from RegisterForeman import *
from ForwarderScoreboard import * 

forwarder_dict = {"FORWARDER_0": {"NAME": "FORWARDER_0", "CONSUME_QUEUE": "F0_consume"}}
FWD_SCBD = ForwarderScoreboard(forwarder_dict)


def register_machines(): 
    # run this on its thread
    r = RegisterForeman("FORWARDER", FWD_SCBD)
    r.run()

register_machines()
