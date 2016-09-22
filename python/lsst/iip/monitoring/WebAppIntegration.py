import time
import subprocess
from rdbtools import RdbCallback, RdbParser

"""
    Python 3.x is not fully supported.
    See FAQ. https://github.com/sripathikrishnan/redis-rdb-tools/wiki/FAQs
    MIT License
    Assumptions: 
    * Curl program is installed
    * InfluxDB is installed and running on localhost:8086
    * InfluxDB called mydb is created beforehand
    * Rdb dump file is in current directory and called "dump.rdb" 
    * Import file to influxDB is called "influximport.txt"
    * Conversion table is true and valid with business policies
    * If value is not in conversion table, it is set to -1 
    * Parser object collects only two states, STATUS and STATE

    Excution time is between 0.015 and 0.024 seconds. 
    Average is about 0.017 seconds. 
"""
class WebAppIntegration: 
    def __init__(self): 
        self._parser = Parser()
        self._rdbparser = RdbParser(self._parser)
        self._rdbparser.parse("dump.rdb")
        self._bDict = self._parser.bigDict 
        self._mydb = False

        # conversion table for values 
        self._conversionTable = {}
        self._conversionTable["HEALTHY"] = 0
        self._conversionTable["REGISTERING"] = 1
        self._conversionTable["IDLE"] = 0

    def importInflux(self): 
        """ Import file to InfluxDB """ 
        cmd = "curl -i -XPOST 'http://localhost:8086/write?db=mydb' --data-binary @influximport.txt"
        subprocess.call(cmd, shell=True)

    def create_db(self): 
        """ Create a database called mydb if it doesn't exist """ 
        cmd = "curl -i XPOST http://localhost:8086/query --data-urlencode 'q=CREATE DATABASE mydb'"
        if not self._mydb:
            subprocess.call(cmd, shell=True)
            self._mydb = True
        else: 
            print("MyDB exists.")

    def writeToFile(self): 
        """ Create a file called influximport.txt in compatibility with InfluxDB """
        filename = open("influximport.txt", "w")
        currentTime = time.time() 
        for item, value in self._bDict.iteritems(): 
            writeLine = "machine,machine_name=" + item + " "
            for kee, val in value.iteritems(): 
                if val in self._conversionTable: 
                    writeLine += kee + "=" + str(self._conversionTable[val])
                else: 
                    writeLine += kee + "=" + str(-1)
                if kee != value.keys()[-1]: 
                    writeLine += ","
            writeLine += " " + str(currentTime).split(".")[0]
            filename.write(writeLine + "\n")
        filename.close()


class Parser(RdbCallback): 
    def __init__(self): 
        super(Parser, self).__init__()
        self.bigDict = {}  
        self.states = ["STATE", "STATUS"] 
    
    def hset(self, key, field, value): 
        if str(field) in self.states: 
            if str(key) in self.bigDict: 
                self.bigDict[str(key)][str(field)] = str(value)  
            else: 
                self.bigDict[str(key)] = {} 
                self.bigDict[str(key)][str(field)] = str(value) 

def main(): 
    start_time = time.time() 
    web = WebAppIntegration()
    web.writeToFile() 
    try: 
        web.importInflux()
        print("Import successful.") 
    except:
        print("Importing to InfluxDB failed.")

    print "Execution time is %s." % (time.time() - start_time)


if __name__ ==  "__main__": 
    main() 
