FLOG=~/xfer_dir/rcv_logg.test
while true; do
  if [ -f ./sentinel.test ]
    then
      date +"%Y-%m-%d %H:%M:%S.%5N" >> $FLOG
      echo "----" >> $FLOG
      break
  fi
done
echo "Found sentinel file at this time " >> $FLOG
echo "==" >> $FLOG

