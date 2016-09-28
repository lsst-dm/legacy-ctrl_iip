import yaml

def read_yaml(filename): 
    openFile = open(filename)
    config = yaml.load(openFile)
    return config
