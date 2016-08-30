""" Testing file used for Job ScoreBoard 
	Used with pytest as the Unit testing module """

import redis
import yaml
import pytest
import random
import sys

sys.path.insert(0, '../iip')
from JobScoreboard import *

# Global variable used when running _multiple tests
test_len = 20
test_len_max = 40

# Creates JobScoreboard object used to test the methods below
# Can either last for the entire testing session or per test one can be created


@pytest.fixture(scope='session')
def jb(request):
    return JobScoreboard()


def test_check_connection(jb):
    assert jb.check_connection(), "Check Connection should have connected, but did not..."


def test_add_job_basic(jb):
    job_number = 1
    rafts = 11
    # Assuming add_job returns True or False
    assert jb.add_job(job_number, rafts), ("Add job fails during basic test..."
                                           "Job number was %d and rafts was %d"
                                           % (job_number, rafts))


def test_add_job_multiple(jb):
    for i in range(20):
        job_number = i
        rafts = random.randint(1, 22)
        # Assuming add_job returns True or False
        assert jb.add_job(job_number, rafts), ("Add job fails during basic test..."
                                               "Job number was %d and rafts was %d"
                                               % (job_number, rafts))


def test_add_job_fail(jb):
    job_number = 1
    rafts = -11
    # Assuming either True or False is returned or exception is thrown... TBD
    # pytest.raises(ExpectedException, func, args) if execption is thrown
    assert jb.add_job(job_number, rafts) == False, ("Add job passed when it should have failed..."
                                                    "Job number was %d and rafts was %d"
                                                    % (job_number, rafts))
    rafts = ""
    # if raft number was empty
    assert jb.add_job(job_number, rafts) == False, ("Add job passed when it should have failed..."
                                                    "Job number was %d and rafts was %d"
                                                    % (job_number, rafts))
    # if job number was empty
    job_number = ""
    rafts = 11
    assert jb.add_job(job_number, rafts) == False, ("Add job passed when it should have failed..."
                                                    "Job number was %d and rafts was %d"
                                                    % (job_number, rafts))

### Skipped set_job_params since it was not in BaseForeman ###


def test_set_value_for_job_basic(jb):
    # Job should be already created. Should return 0 since it is updating it
    job_number = 19
    assert jb.set_value_for_job(job_number, "STATE", "READY") == 0, ("Set Value for Job failed..."
                                                                     "Job number was %d, STATE was READY"
                                                                     % job_number)
    # Job number that does not exist
    job_number = 55
    assert jb.set_value_for_job(job_number, "STATE", "READY"), ("Set Value for Job failed..."
                                                                "Job number was %d, STATE was READY"
                                                                % job_number)


def test_set_value_for_job_fail(jb):
    # Assuming either True or False is returned or exception is thrown... TBD
    # If key was nothing
    assert jb.set_value_for_job("", "STATE", "READY") == False, ("Set Value for Job passed when should have failed..."
                                                                 "Key was empty")
    # If field was nothing
    job_number = 10
    assert jb.set_value_for_job(job_number, "", "READY") == False, ("Set Value for Job failed..."
                                                                    "Job number was %d, Field was empty"
                                                                    % job_number)
    # If value was nothing
    assert jb.set_value_for_job(job_number, "STATE", "") == False, ("Set Value for Job failed..."
                                                                    "Job number was %d, Value was empty"
                                                                    % job_number)
    # Should test for if non-strings are entered in the fields
    # Possibly


def test_set_pairs_basic(jb):
    pairs = {}
    pairs['F1'] = 'D2'
    pairs['F2'] = 'D6'
    pairs['F3'] = 'D11'
    pairs['F4'] = 'D1'
    pairs['F5'] = 'D7'
    job_number = 2
    assert jb.set_pairs_for_job(job_number, pairs), "Set Pairs Failed..."


def test_set_pairs_multiple(jb):
    pairs_small = {}
    pairs_small['F1'] = 'D2'
    pairs_small['F2'] = 'D6'
    pairs_small['F3'] = 'D11'
    pairs_small['F4'] = 'D1'
    pairs_small['F5'] = 'D7'

    pairs_big = {}
    for j in range(22):
        name = 'F' + str(j)
        mate = 'D' + str(j)
        pairs_big[name] = mate

    for i in range(test_len):
        job_number = i
    assert jb.set_pairs_for_job(
        job_number, pairs_small), "Set Pairs Small Failed..."

    for i in range(test_len, test_len_max, 1):
        job_number = i
        assert jb.set_pairs_for_job(
            job_number, pairs_big), "Set Pairs Big Failed..."


def test_set_pairs_fail(jb):
    # If the pair list is empty
    job_number = 1
    pairs = {}
    assert jb.set_pairs_for_job(
        job_number, pairs) == False, "Set Pairs Passed when pair list was empty..."
    # If the job number was nothing
    job_number = ""
    pairs['F1'] = 'D2'
    pairs['F2'] = 'D6'
    pairs['F3'] = 'D11'
    pairs['F4'] = 'D1'
    pairs['F5'] = 'D7'
    assert jb.set_pairs_for_job(
        job_number, pairs) == False, "Set Pairs Passed when job number was empty..."


# Create a new object for every function then populate it
@pytest.fixture(scope='function')
def jb_2(request):
    return JobScoreboard()


def test_get_pairs_basic(jb_2):
    pairs = {}
    pairs['F1'] = 'D2'
    pairs['F2'] = 'D6'
    pairs['F3'] = 'D11'
    pairs['F4'] = 'D1'
    pairs['F5'] = 'D7'
    job_number = 2
    jb_2.set_pairs_for_job(job_number, pairs)
    assert jb_2.get_pairs_for_job(job_number) == pairs, ("Get Pairs failed to return the pairs for %d"
                                                         % job_number)


def test_get_pairs_multiple(jb_2):
    pairs = {}
    for j in range(22):
        name = 'F' + str(j)
        mate = 'D' + str(j)
        pairs[name] = mate
    for i in range(test_len):
        job_number = i
        jb_2.set_pairs_for_job(job_number, pairs)

    for i in range(test_len):
        assert jb_2.get_pairs_for_job(
            i) == pairs, ("Get Pairs multiple failed to return the pairs for %d" % i)


def test_get_pairs_fail(jb_2):
    ### Not sure what to test on this one... ###
    """pairs = {}
    pairs['F1'] = 'D2'
    pairs['F2'] = 'D6'
    pairs['F3'] = 'D11'
    pairs['F4'] = 'D1'
    pairs['F5'] = 'D7'
    job_number = 5
    jb_2.set_pairs_for_job(job_number, pairs)
    # Add another pair 
    pairs['F6'] = 'D9'
    assert jb_2.get_pairs_for_job(job_number) == pairs, ("Get Pairs returned incorrect pairs for %d" % job_number)"""
    pass


def test_get_value_job_basic(jb_2):
    # Create Job and add it
    job_number = 1
    rafts = 11
    jb_2.add_job(job_number, rafts)
    # Set the Value for the Job
    jb_2.set_value_for_job(job_number, "STATE", "READY")
    assert jb_2.get_value_for_job(
        job_number, "STATE") == "READY", ("Get value for job failed to return correct value...")


def test_get_value_job_multiple(jb_2):
    # Populate DB with Jobs
    for i in range(test_len):
        job_number = i
        rafts = i
        jb_2.add_job(job_number, rafts)
        jb_2.set_value_for_job(job_number, "STATE", "READY")
        assert jb_2.get_value_for_job(job_number, "STATE") == "READY", ("Get value for multiple jobs failed to return correct value..."
                                                                        "Job number was %d" % job_number)


def test_get_value_job_fail(jb_2):
    # Add job to DB
    job_number = ""
    rafts = 2
    jb_2.add_job(job_number, rafts)
    jb_2.set_value_for_job(job_number, "STATE", "READY")
    assert jb_2.get_value_for_job(job_number, "STATE") == "READY", ("Get value for jobs should have failed but passed..."
                                                                    "Job number was empty")


def test_delete_job_basic(jb_2):
    # returns the number of of removed elements
    pairs = {}
    pairs['F1'] = 'D2'
    pairs['F2'] = 'D6'
    pairs['F3'] = 'D11'
    pairs['F4'] = 'D1'
    pairs['F5'] = 'D7'
    job_number = 55
    rafts = 11
    # Add the Job
    jb_2.add_job(job_number, rafts)
    # Set the Value for the Job
    jb_2.set_value_for_job(job_number, "STATE", "READY")
    # Populate the DB
    jb_2.set_pairs_for_job(job_number, pairs)
    assert jb_2.get_pairs_for_job(
        job_number) == pairs, ("Get Pairs did not return the correct worker pairs for the job")
    # Delete the job from the DB
    assert jb_2.delete_job(job_number) != 0, (
        "Delete Job should have returned the number of elements deleted, but returned 0...")
    # Job is deleted but pairs still exist...
    assert jb_2.get_pairs_for_job(
        job_number) is None, ("Get Pairs should have returned None")
    # Try get Value for Job
    assert jb_2.get_value_for_job(job_number, "STATE") == "READY", ("Get value for job returned something"
                                                                    "but Job does not exist...")


def test_delete_job_multiple(jb_2):
    pairs = {}
    pairs['F1'] = 'D2'
    pairs['F2'] = 'D6'
    pairs['F3'] = 'D11'
    pairs['F4'] = 'D1'
    pairs['F5'] = 'D7'
    # Job number is either i or j
    for i in range(test_len):
        rafts = 11
        # Add the Job
        jb_2.add_job(i, rafts)
        # Set the Value for the Job
        jb_2.set_value_for_job(i, "STATE", "READY")
    # Delete all the jobs
    for j in range(test_len):
        # Should this be != or not?
        assert jb_2.delete_job(
            j) != 0, ("Delete Job should have returned the number of elements deleted, but returned 0...")
        # Job is deleted so check if pairs is gone
        assert jb_2.get_pairs_for_job(
            j) is None, ("Get Pairs should have returned None")
        # Try get Value for Job
        assert jb_2.get_value_for_job(j, "STATE") == "READY", ("Get value for job returned something"
                                                               "but Job does not exist...")

### print_all may not be needed to be tested... ###
