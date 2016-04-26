
while true; do
  if [ -a ./sentinel.test ]
    then
      date +"%Y-%m-%d %H:%M:%S.%5N" >> rcv_logg.test
      echo "-----------------------" >> rcv_logg.test
      break
  fi
done
echo "Found sentinel file at this time above" >> rcv_logg.test
echo "================================" >> rcv_logg.test

