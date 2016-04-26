
# $1 = job number
# $2 = command

echo "Job Number:  "$1 >> logg$1
echo "Job Number:  "$1 
echo "Start Time: " >> logg$1
date +"%Y-%m-%d %H:%M:%S.%5N" >> logg$1

#$2
echo $2 >> logg$1
echo $2



echo "End Time: " >> logg$1
date +"%Y-%m-%d %H:%M:%S.%5N" >> logg$1
echo "--------------------" >> logg$1
