def singleton(object, instantiated=[]):
  assert object.__class__ not in instantiated, \
    "%s is a Singleton class but is already instantiated" % object.__class__
  instantiated.append(object.__class__)



