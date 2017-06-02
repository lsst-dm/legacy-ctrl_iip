#!/bin/bash
# USAGE: ./thread_gah.sh ./sacpp_archiver_enable_commander X
echo "Checking thread count for $1 command"
$1 $2 &
PD=$!
for i in 1 2 3 4 5 6 7 8 9
do
  LN=`cat /proc/$PD/status |grep Threads`
  echo $LN
  sleep 1
done
echo "End..."
kill -9 $PD

