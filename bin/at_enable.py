from SALPY_ATArchiver import *

class Commander:
    def __init__(self):
        self.mgr = SAL_ATArchiver()
        self.timeout = 10
        

    def enable(self):
        data = ATArchiver_command_enableC()
        self.mgr.salCommand("ATArchiver_command_enable")
        data.device = ""
        data.property = ""
        data.action = ""
        data.value = 0

        cmdId = self.mgr.issueCommand_enable(data)
        status = self.mgr.waitForCompletion_enable(cmdId, self.timeout)

        print(f"status = {status}")

if __name__ == "__main__":
    cmdr = Commander()
    cmdr.enable()
    cmdr.mgr.salShutdown()

    
