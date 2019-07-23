#!/bin/sh
set -x
python3 command.py -D ATArchiver -d 1 enterControl
sleep 2
python3 command.py -D ATArchiver -d 1 start -s Normal
sleep 2
python3 command.py -D ATArchiver -d 1 enable
sleep 2
python3 logevent.py -d 1 startIntegration -q 0 -s 1 -n AT_O_20190312_000007 -i 0 -t 4.0 -e 1.0 -p 1
sleep 2
python3 logevent.py -d 1 endReadout -q 0 -s 1 -n AT_O_20190312_000007 -i 0 -t 4.0 -e 1.0 -p 1
sleep 2
python3 logevent.py -d 1 largeFileObjectAvailable -b 1 -c 1 -g "AtHeaderService" -m 1 -u "http://141.142.238.74:8000/AT_O_20190312_000007.header" -v 1.0 -i AT_O_20190312_000007 -p 1
set +x
