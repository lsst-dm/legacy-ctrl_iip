#!/bin/sh

# startup sequence

python3 command.py -D ATArchiver enterControl
sleep 3
python3 command.py -D ATArchiver start --settings Normal
sleep 3
python3 command.py -D ATArchiver standby
sleep 1
python3 command.py -D ATArchiver disable
sleep 1
python3 command.py -D ATArchiver enable
sleep 1
echo "[OK] ENABLE COMPLETE."
echo "System UP and running."
echo
