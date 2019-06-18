import importlib
import time
#from SALPY_ATArchiver import *
#from SALPY_CatchupArchiver import *
#from SALPY_EFD import *
#from SALPY_MTArchiver import *
#from SALPY_PromptProcessing import *

def test_ocs_commands(device_name):
    commands = [ "enable", "disable", "enterControl", "exitControl", "standby", "start", "abort" ]
    timeout = 5

    module = importlib.import_module("SALPY_%s" % (device_name))
    class_ = getattr(module, "SAL_%s" % (device_name))
    mgr = class_()

    for command in commands:
        mgr.salCommand("%s_command_%s" % (device_name, command))
        data_ = getattr(module, "%s_command_%sC" % (device_name, command))
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


cscs = ["ATArchiver", "CatchupArchiver", "MTArchiver", "PromptProcessing"]

for csc in cscs:
    test_ocs_commands(csc)

exit()

