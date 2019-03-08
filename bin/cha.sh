#!/bin/sh

# startup sequence

  /opt/sal/ts_sal/test/atArchiver/cpp/src/sacpp_atArchiver_enterControl_commander 0
  sleep 3

  /opt/sal/ts_sal/test/atArchiver/cpp/src/sacpp_atArchiver_start_commander Normal
  sleep 3

  /opt/sal/ts_sal/test/atArchiver/cpp/src/sacpp_atArchiver_standby_commander 0
  sleep 1

  /opt/sal/ts_sal/test/atArchiver/cpp/src/sacpp_atArchiver_disable_commander 0
  sleep 1

  /opt/sal/ts_sal/test/atArchiver/cpp/src/sacpp_atArchiver_enable_commander 0
  sleep 1
  echo "[OK] ENABLE COMPLETE."
  echo "System UP and running."
  echo " "

