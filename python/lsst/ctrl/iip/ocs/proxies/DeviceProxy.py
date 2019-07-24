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

import datetime
import importlib
import logging
from lsst.ctrl.iip.ocs.Action import Action

LOGGER = logging.getLogger(__name__)


class DeviceProxy:
    """Serves as a proxy of a CSC device
    """
    def __init__(self, device_name, device_abbr, messages, local_ack, debugLevel):
        self.device_name = device_name
        self.device_abbr = device_abbr
        self.messages = messages
        self.local_ack = local_ack

        self.next_ack_id = 0

        self.commands = messages.get_commands()
        self.command_acks = messages.get_command_acks()
        self.cmd_actions = None

        self.log_events = messages.get_log_events()

        self.events = messages.get_events()
        self.event_actions = None

        # TODO: These translation tables are here because these events
        # are renamed in other portions of the software, instead of using
        # the names they were originally given.  These tables are here
        # temporarily, and the code that uses them should be removed
        # once this is fixed throughout the rest of the system.
        self.translations = {
            "SUMMARY_STATE_EVENT": "summaryState",
            "RECOMMENDED_SETTINGS_VERSION_EVENT": "settingVersions",
            "SETTINGS_APPLIED_EVENT": "settingsApplied",
            "APPLIED_SETTINGS_MATCH_START_EVENT": "appliedSettingsMatchStart",
            "ERROR_CODE_EVENT": "errorCode"
        }

        self.translated_cmd_acks = {
            "START_ACK": "start_ACK",
            "STOP_ACK": "stop_ACK",
            "ENABLE_ACK": "enable_ACK",
            "DISABLE_ACK": "disable_ACK",
            "ENTER_CONTROL_ACK": "enterControl_ACK",
            "STANDBY_ACK": "standby_ACK",
            "EXIT_CONTROL_ACK": "exitControl_ACK",
            "ABORT_ACK": "abort_ACK",
            "RESET_FROM_FAULT_ACK": "resetFromFault_ACK"
        }


        module = importlib.import_module("SALPY_%s" % device_name)
        class_ = getattr(module, "SAL_%s" % (device_name))
        self.mgr = class_()
        self.mgr.setDebugLevel(debugLevel)

        # while it's likely that the values for each of these
        # states in SAL will be the same for each device, that's
        # not guaranteed, so we get these values on a per device basis.
        self.summary_states = {
            "DISABLE": getattr(module, "SAL__STATE_DISABLED"),
            "ENABLE": getattr(module, "SAL__STATE_ENABLED"),
            "FAULT": getattr(module, "SAL__STATE_FAULT"),
            "OFFLINE": getattr(module, "SAL__STATE_OFFLINE"),
            "STANDBY": getattr(module, "SAL__STATE_STANDBY")
        }
        self.cmd_complete = getattr(module, "SAL__CMD_COMPLETE")

    def get_sal_summary_state(self, state):
        if state in self.summary_states:
            return self.summary_states[state]
        return None

    def get_abbreviation(self):
        return self.device_abbr

    def setup_processors(self):
        """initialize the SAL processors for the registered commands
        """
        for command in self.commands:
            self.mgr.salProcessor(self.device_name+'_command_'+command)

    def setup_log_events(self):
        """initialize SAL processors for registered events
        """
        for log_event in self.log_events:
            self.mgr.salEventPub(self.device_name + "_logevent_" + log_event)

    def setup_events(self):
        for event in self.events:
            self.mgr.salEventSub(self.device_name + "_logevent_" + event)

    def get_ack_command(self, msg_type):
        """ Return the ackCommand associated with device name to acknowledge
        SAL commands
        @param msg_type: message type
        @return function pointer to ack_command
        """
        command = msg_type[:msg_type.rfind("_ACK")]
        ack_command = getattr(self.mgr, "ackCommand_%s" % command)
        return ack_command

    def get_log_event_method(self, log_event_name):
        """ Return the logEvent associated with device name to publish
        SAL events
        @param event_name: SAL event name
        @return function pointer to ack_command
        """
        log_event = getattr(self.mgr, "logEvent_%s" % log_event_name)
        return log_event

    def create_data_object(self, command_name):
        """Returns a data structure for the given command
        @return the SAL data structure associated with this device and command
        """
        return self.create_object("command", command_name)

    def create_logevent_object(self, event_name):
        """Returns a data structure for the given event
        @return the SAL data structure associated with this device and event
        """
        return self.create_object("logevent", event_name)

    def create_object(self, object_type, name):
        """Returns a data structure for the given event
        @return the SAL data structure associated with this device and event
        """
        module = importlib.import_module("SALPY_%s" % self.device_name)
        class_ = getattr(module, "%s_%s_%sC" % (self.device_name, object_type, name))
        data = class_()
        return data

    def create_actions(self):
        """Create the accept and possible the acknowledgement Actions
        for all registered commands
        @param createAcks: whether to handle local acknowledgements
        """
        self.cmd_actions = []
        for command in self.commands:
            accept_command = getattr(self.mgr, "acceptCommand_%s" % command)
            ack_command = getattr(self.mgr, "ackCommand_%s" % command)

            action = Action(self.device_name, command, accept_command, ack_command)

            self.cmd_actions.append(action)

        self.event_actions = []
        for event in self.events:
            event_command = getattr(self.mgr, "getEvent_%s" % event)
            action = Action(self.device_name, event, event_command)
            self.event_actions.append(action)

    def build_msg(self, command, cmdId, ack_id, data):
        """Build a dictionary containing the message to publish to the CSC
        @param device_name: name of the CSC device
        @param command: command that was received
        @param cmdId: the return value of the retrieved commmand
        @param ackId: the acknowledgement id
        @param data: data structure that was filled out by the accept method
        @return a dictionary containing the message parts
        """
        d = {}
        d['MSG_TYPE'] = self.messages.translate(command)
        d['DEVICE'] = self.device_abbr
        d['CMD_ID'] = cmdId
        d['ACK_ID'] = ack_id
        if command == 'start':
            d['CFG_KEY'] = data.settingsToApply
        return d

    def build_bookkeeping_msg(self, command, cmdId, ack_id):
        """Build a dictionary containing the bookkeeping message to publish
        @param device_name: name of the CSC device
        @param command: command that was received
        @param cmdId: the return value of the retrieved commmand
        @param ackId: the acknowledgement id
        @return a dictionary containing the message parts
        """
        d = {}
        d['MSG_TYPE'] = 'BOOK_KEEPING'
        d['SUB_TYPE'] = self.messages.translate(command)
        d['ACK_ID'] = ack_id
        d['CHECKBOX'] = 'false'
        d['TIME'] = self.get_current_time()
        d['CMD_ID'] = str(cmdId)
        d['DEVICE'] = self.device_abbr
        return d

    def get_current_time(self):
        """Return a string of the current time
        @return string form of the current time
        """
        n = datetime.datetime.now()
        retval = n.strftime('%Y-%m-%d %H:%M:%S')
        return retval

    def register_message_sender(self, sender, queue):
        self.message_sender = sender
        self.sender_queue = queue

    def register_message_bookkeeper(self, bookkeeper, queue):
        self.message_bookkeeper = bookkeeper
        self.bookkeeper_queue = queue

    def accept_cmds(self):
        """Accept commands from a device
        """
        for action in self.cmd_actions:
            self.accept_cmd(action)

    def accept_cmd(self, action):
        """Accept commmands for a single type of command action
        @param action: the action to try to recognize
        """
        command = action.message
        data = self.create_data_object(command)
        accept_command = action.message_retriever

        # try to receive the command, if one is available
        cmdId = accept_command(data)

        # if no command was accepted, return
        if cmdId <= 0:
            return

        # A command was accepted;
        # Retrieve the name of the device
        LOGGER.debug('Got command %s for device %s' % (command, self.device_name))

        # If local_ack is True, then send back a SAL ack immeditely, and return.
        # This is done for stand-alone loopback testing.
        if self.local_ack:
            action.ack_method(cmdId, self.cmd_complete, 0, "Done : OK")
            return

        # retrieve the next acknowledgement number to return
        ack_id = self.get_next_timed_ack_id(command)

        # build a message to send
        msg = self.build_msg(command, cmdId, ack_id, data)
        LOGGER.debug('XXX NORMAL: ', msg)

        # build a bookkeeping message to send
        bookkeeping_msg = self.build_bookkeeping_msg(command, cmdId, ack_id)
        LOGGER.debug('XXX BOOKKEEPING: ', bookkeeping_msg)

        # publish a bookkeeping message
        self.message_bookkeeper.publish_message(self.bookkeeper_queue, bookkeeping_msg)

        # publish the message to the CSC device
        self.message_sender.publish_message(self.sender_queue, msg)

    def accept_events(self):
        """Accept events from SAL
        """
        for action in self.event_actions:
            self.accept_event(action)

    def accept_event(self, action):
        """Accept a single event from SAL, reformat it, and send it
        through via RabbitMQ
        @param action: the action to recognize and take
        """
        message = action.message
        data = self.create_logevent_object(message)
        accept_event = action.message_retriever

        status = accept_event(data)
        if status != 0:
            return

        # obtain the correct message composer and build a new dictionary using
        # the data we received based on the message type
        composer = self.messages.get_composer(message)
        msg = composer(data)

        # publish the message to the CSC device
        self.message_sender.publish_message(self.sender_queue, msg)

    def get_next_timed_ack_id(self, command):
        """Return the next acknowledgement id
        @param command: the CSC command that as received
        @return a string with the acknowlegement ID for this command
        """
        self.next_ack_id = self.next_ack_id + 1
        retval = '%s_%06d' % (command, self.next_ack_id)
        return retval

    def outgoing_message_handler(self, msg):
        msg_type = msg["MSG_TYPE"]

        if msg_type in self.translations:
            msg_type = self.translations[msg_type]

        if msg_type in self.command_acks:
            self.ack_cmd(msg_type, msg)
        elif msg_type in self.translated_cmd_acks:
            translated_msg_type = self.translated_cmd_acks[msg_type]
            self.ack_cmd(translated_msg_type, msg)
        elif msg_type in self.log_events:
            self.publish_log_event(msg_type, msg)
        elif msg_type == "BOOK_KEEPING":
            self.process_book_keeping(msg)
        elif msg_type == "RESOLVE_ACK":
            self.process_resolve_ack(msg)
        elif msg_type == "TELEMETRY":
            self.process_telemetry(msg)
        else:
            LOGGER.error("Can't handle %s in device %s" % (msg_type, self.device_name))

    def ack_cmd(self, msg_type, msg):
        """Acknowledge commands received from DMCS to OCS
        @param msg: message received from DMCS
        """
        cmd_id = msg["CMD_ID"]
        ack_command = self.get_ack_command(msg_type)
        ack_command(cmd_id, self.cmd_complete, 0, "Done: OK")
        LOGGER.info("Published %s acknowledgement to OCS for commandId %s" % (self.device_abbr, cmd_id))

    def process_telemetry(self, msg):
        """Process a telemetry message"""
        LOGGER.error(f"Unable to process telemetry message: {msg}")

    def publish_log_event(self, event_name, msg):
        """Publish SAL events back to OCS
        @param msg: message from DMCS
        """

        if event_name in self.translations:
            event_name = self.translations[event_name]
        event_object = self.create_logevent_object(event_name)

        if event_name == "summaryState":
            build_data = self.build_summaryState_object
        else:
            build_data = getattr(self.messages, "build_%s_object" % event_name)
        data = build_data(event_object, msg)
        if data is None:
            msg = "Cannot build message data object for %s" % event_name
            LOGGER.error(msg)
            return
        log_event = self.get_log_event_method(event_name)
        log_event(data, 0)
        LOGGER.info("Published %s Event to OCS" % event_name)

    def build_summaryState_object(self, data, msg):
        """Build summaryState SAL message object
        @param data: summaryState SAL structure
        @param msg: message from DMCS
        @return summaryState SAL structure with data
        """
        data.summaryState = self.summary_states[msg["CURRENT_STATE"]]
        data.priority = 0
        return data

    def process_book_keeping(self, msg):
        pass

    def process_resolve_ack(self, msg):
        pass
