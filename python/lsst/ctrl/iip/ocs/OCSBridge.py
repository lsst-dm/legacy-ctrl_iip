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

from lsst.ctrl.iip.ocs.Bridge import Bridge
from lsst.ctrl.iip.ocs.proxies.ATArchiverProxy import ATArchiverProxy
from lsst.ctrl.iip.ocs.proxies.ATCameraProxy import ATCameraProxy
from lsst.ctrl.iip.ocs.proxies.CatchupArchiverProxy import CatchupArchiverProxy
from lsst.ctrl.iip.ocs.proxies.EFDProxy import EFDProxy
from lsst.ctrl.iip.ocs.proxies.MTArchiverProxy import MTArchiverProxy
from lsst.ctrl.iip.ocs.proxies.PromptProcessingProxy import PromptProcessingProxy


class OCSBridge(Bridge):
    """Represents the bridge between OCS and the CSCs.  Messages from SAL
    are received and then retransmitted to the CSCs using RabbitMQ, and via versa
    Parameters
    ----------
    config_filename: `str`
        The configuration file to use to initialize the OCSBridge
    """
    def __init__(self, config_filename, local_ack=False, debugLevel=0):
        super().__init__(config_filename, 'OCSBridge.log')

        # create a list of all CSCs for the OCSBridge to manage
        proxies = []
        proxies.append(ATArchiverProxy(local_ack, debugLevel))
        proxies.append(ATCameraProxy(local_ack, debugLevel))
        proxies.append(CatchupArchiverProxy(local_ack, debugLevel))
        proxies.append(EFDProxy(local_ack, debugLevel))
        proxies.append(MTArchiverProxy(local_ack, debugLevel))
        proxies.append(PromptProcessingProxy(local_ack, debugLevel))

        # register the list of proxies with the OCSBridge
        # Note that setting "sendLocalAcks" to True means that
        # the acknowledgements are sent back from the OCS Bridge,
        # not from the outside devices.  This is done for standalone
        # testing.
        self.register_devices(proxies)
