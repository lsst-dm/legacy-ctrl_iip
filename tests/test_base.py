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
import unittest
from lsst.ctrl.iip.base import base


class BaseTestCase(unittest.TestCase):

    def remove_vars(self):
        self.iip_config_dir = None
        if "IIP_CONFIG_DIR" in os.environ:
            self.iip_config_dir = os.environ["IIP_CONFIG_DIR"]
            del os.environ["IIP_CONFIG_DIR"]
        rootdir = os.environ["CTRL_IIP_DIR"]
        path = os.path.join(rootdir, "tests", "test_config")
        os.environ["IIP_CONFIG_DIR"] = path

    def add_vars(self):
        if "IIP_CONFIG_DIR" in os.environ:
            del os.environ["IIP_CONFIG_DIR"]
        if self.iip_config_dir is not None:
            os.environ["IIP_CONFIG_DIR"] = self.iip_config_dir

    def remove_ctrl_iip_dir(self):
        self.ctrl_iip_dir = None
        if "CTRL_IIP_DIR" in os.environ:
            self.ctrl_iip_dir = os.environ["CTRL_IIP_DIR"]
            del os.environ["CTRL_IIP_DIR"]

    def add_ctrl_iip_dir(self):
        if self.ctrl_iip_dir is not None:
            os.environ["CTRL_IIP_DIR"] = self.ctrl_iip_dir

    def test_load_config_file(self):
        self.remove_vars()
        _base = base("L1SystemCfg.yaml", "test_log")
        cred = _base.getCredentials()
        self.assertIsNotNone(cred.getUser("service_user"))
        self.assertIsNotNone(cred.getPasswd("service_passwd"))
        _base.shutdown()
        self.add_vars()

    def test_load_missing_file(self):
        self.remove_vars()
        with self.assertRaises(SystemExit):
            _base = base("fake.yaml", "test_log")
            print(_base)
        self.add_vars()

    def test_bad_configuration(self):
        self.remove_vars()
        self.remove_ctrl_iip_dir()
        del os.environ["IIP_CONFIG_DIR"]
        with self.assertRaises(Exception):
            _base = base("fake.yaml", "test_log")
            print(_base)
        self.add_ctrl_iip_dir()
        self.add_vars()

    def test_standard_configuration(self):
        self.remove_vars()
        del os.environ["IIP_CONFIG_DIR"]
        _base = base("L1SystemCfg.yaml", "test_log")
        _config = _base.getConfiguration()
        print(_config)
        self.add_vars()

    def remove_iip_log_dir(self):
        self.iip_log_dir = None
        if "IIP_LOG_DIR" in os.environ:
            self.iip_log_dir = os.environ["IIP_LOG_DIR"]
            del os.environ["IIP_LOG_DIR"]

    def add_iip_log_dir(self):
        if self.iip_log_dir is not None:
            os.environ["IIP_LOG_DIR"] = self.iip_log_dir

    def test_log(self):
        self.remove_vars()
        _base = base("L1SystemCfg_nolog.yaml", "test_log")
        filename = _base.setupLogging("unit_test.log")
        self.assertEqual(filename, "/tmp/unit_test.log")
        self.add_vars()

    def test_iip_log_dir(self):
        self.remove_vars()
        os.environ["IIP_LOG_DIR"] = "/var/tmp"
        _base = base("L1SystemCfg_nolog.yaml", "test_log")
        filename = _base.setupLogging("unit_test.log")
        self.assertEqual(filename, "/var/tmp/unit_test.log")
        del os.environ["IIP_LOG_DIR"]
        self.add_vars()


if __name__ == "__main__":
    unittest.main()
