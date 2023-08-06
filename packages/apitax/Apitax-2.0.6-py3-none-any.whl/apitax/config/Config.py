import configparser
from apitax.utilities.Numbers import isNumber
from apitax.utilities.Booleans import isBoolean, str2bool
from apitax.utilities.Files import getPathToTopLevel

# Reads the config and allows us to retrieve values from it
class Config:
    def __init__(self, path=getPathToTopLevel('config.txt')):
        self.cp = configparser.RawConfigParser()
        cFilePath = path
        self.cp.read(cFilePath)
        self.path = ''

    def get(self, param):
        prop: str = self.cp.get('Config', param)
        if(isBoolean(prop)):
            return str2bool(prop)
        elif(isNumber(prop)):
            return float(prop)
        return prop

    def has(self, param):
        return self.cp.has_option('Config', param)
        
    def serialize(self, serializable:list):
        returner = dict()
        for property in serializable:
            if(self.has(property)):
                returner.update({property: self.get(property)})
        return returner
