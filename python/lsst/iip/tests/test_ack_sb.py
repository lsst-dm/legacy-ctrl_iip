""" Testing file used for Ack Scoreboard 
	Used with pytest as the Unit testing module """

import redis
import yaml
import pytest
import random
import sys

sys.path.insert(0, '../iip')
from AckScoreboard import *

# Global variable used when running _multiple tests
test_len = 20

# Creates AckScoreboard object used to test the methods below
# Can either last for the entire testing session or on a per test basis,
# one can be created


@pytest.fixture(scope='session')
def acb(request):
    return AckScoreboard()


def test_check_connection(acb):
    assert acb.check_connection(), ("Check Connection should have connected"
                                    "but did not...")


def test_add_timed_ack_basic(acb):
    # Create Ack message
    ack_msg = {}
    ack_msg['MSG_TYPE'] = "HEALTH_CHECK"
    ack_msg['ACK_ID'] = "Forwarder_Check_01"
    ack_msg['COMPONENT_NAME'] = "Forwarder"
    assert acb.add_timed_ack(ack_msg), ("Add ACK failed on basic test..."
                                        "Message was %r" % ack_msg)


def test_add_timed_ack_multiple(acb):
    # Create Ack message
    ack_msg = {}
    ack_msg['MSG_TYPE'] = "HEALTH_CHECK"
    ack_msg['COMPONENT_NAME'] = "Forwarder"
    for i in range(test_len):
        ack_msg['ACK_ID'] = "Forwarder_Check_" + str(i)
        assert acb.add_timed_ack(ack_msg), ("Add ACK failed on multiple test..."
                                            "Message was %r" % ack_msg)


def test_add_timed_ack_fail(acb):
    # If Ack message was empty
    ack_msg = {}
    assert acb.add_timed_ack(
        ack_msg) == False, ("Add ACK should not have added an empty ACK message...")
    ack_msg['MSG_TYPE'] = "HEALTH_CHECK"
    ack_msg['COMPONENT_NAME'] = "Forwarder"
    # If Ack ID was empty
    ack_msg['ACK_ID'] = ""
    # Should either return False or raise exception...
    assert acb.add_timed_ack(
        ack_msg) == False, ("Add ACK should not have added an empty ACK_ID message...")


def test_get_components_for_timed_ack_basic(acb):
    # DB is already populated
    expected_msg = {}
    expected_msg['MSG_TYPE'] = "HEALTH_CHECK"
    expected_msg['ACK_ID'] = "Forwarder_Check_01"
    expected_msg['COMPONENT_NAME'] = "Forwarder"
    expected_msg_dict = {}
    expected_msg_dict["Forwarder"] = expected_msg
    timed_ack = "Forwarder_Check_01"
    assert acb.get_components_for_timed_ack(timed_ack) == expected_msg_dict, ("Get component for timed ack did"
                                                                              "not return correct component..."
                                                                              "Components should have been %r" % ack_msg)


def test_get_components_for_timed_ack_multiple(acb):
    # DB is already populated
    expected_msg = {}
    expected_msg['MSG_TYPE'] = "HEALTH_CHECK"
    expected_msg['COMPONENT_NAME'] = "Forwarder"
    expected_msg_dict = {}
    expected_msg_dict["Forwarder"] = expected_msg
    for i in range(test_len):
        expected_msg['ACK_ID'] = "Forwarder_Check_" + str(i)
        timed_ack = "Forwarder_Check_" + str(i)
        assert acb.get_components_for_timed_ack(timed_ack) == expected_msg_dict, ("Get component for timed ack multiple"
                                                                                  "did not return correct component..."
                                                                                  "Components should have been %r" % ack_msg)


def test_get_components_for_timed_ack_failed(acb):
    # Get component for Ack not in DB
    timed_ack = "Does_Not_Exist"
    assert acb.get_components_for_timed_ack(timed_ack) is None, ("Get Components did not return None for"
                                                                 "an Ack that was not in Database...")
