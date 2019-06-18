import importlib
import time
from SALPY_ATArchiver import *

commands = [ "enable", "disable", "enterControl", "exitControl", "standby", "start", "abort" ]

timeout = 5
mgr = SAL_ATArchiver()
for command in commands:
    mgr.salCommand("ATArchiver_command_%s" % command)
    module = importlib.import_module("SALPY_ATArchiver")
    data_ = getattr(module, "ATArchiver_command_%sC" % command)
    data = data_()
    if command == "start": 
        data.settingsToApply = "Normal"
    else: 
        data.value = 1
    issue_cmd = getattr(mgr, "issueCommand_%s" % command)
    cmdId = issue_cmd(data)
    wfc = getattr(mgr, "waitForCompletion_%s" % command)
    retval = wfc(cmdId,timeout)
    print(command)
    time.sleep(1)
mgr.salShutdown()
exit()

