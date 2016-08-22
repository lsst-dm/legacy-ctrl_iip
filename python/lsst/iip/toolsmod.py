import subprocess

def get_timestamp():
    return subprocess.check_output('date +"%Y-%m-%d %H:%M:%S.%5N"', shell=True)

def singleton(object, instantiated=[]):
    assert object.__class__ not in instantiated, \
        "%s is a Singleton class but is already instantiated" % object.__class__
    instantiated.append(object.__class__)



