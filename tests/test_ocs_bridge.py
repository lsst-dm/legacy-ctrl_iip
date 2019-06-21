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

import os
import time
import unittest
import signal
import threading
from lsst.ctrl.iip.ocs.OCSBridge import OCSBridge


def thread_watch():
    time.sleep(15)
    os.kill(os.getpid(), signal.SIGINT)


class OCSBridgeTestCase(unittest.TestCase):
    def setUp(self):
        rootdir = os.environ["CTRL_IIP_DIR"]
        path = os.path.join(rootdir, "tests", "test_config")
        os.environ["IIP_CONFIG_DIR"] = path

    def testOCSBridgeStartup(self):
        bridge = OCSBridge("L1SystemCfg.yaml")

        exists = {"AT": True, "CU": True, "AR": True, "PP": True, "FAKE": False}
        abbrs = {"AT": "ATArchiver", "CU": "CatchupArchiver", "AR": "MTArchiver", "PP": "PromptProcessing"}
        for key in exists.keys():
            device = bridge.get_device(key)
            if device is None:
                self.assertFalse(exists[key])
            else:
                self.assertTrue(exists[key])
                self.assertEqual(device.device_name, abbrs[key])

        bridge.register_SIGINT_handler()

        x = threading.Thread(target=thread_watch)
        x.start()
        bridge.listen_loop()


if __name__ == "__main__":
    unittest.main()
