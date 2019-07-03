from SALPY_ATArchiver import *


class Commander:
    def __init__(self):
        self.mgr = SAL_ATArchiver()
        self.timeout = 10
        

    def enterControl(self):
        data = ATArchiver_command_enterControlC();
        self.mgr.salCommand("ATArchiver_command_enterControl");
        data.device = ""
        data.property = ""
        data.action = ""
        data.value = 0

        cmdId = self.mgr.issueCommand_enterControl(data)
        status = self.mgr.waitForCompletion_enterControl(cmdId, self.timeout)

        print(f"status = {status}")

if __name__ == "__main__":
    cmdr = Commander()
    cmdr.enterControl()
    cmdr.mgr.salShutdown()
