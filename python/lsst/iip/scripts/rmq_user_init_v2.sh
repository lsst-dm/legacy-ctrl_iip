echo "User initialization started ..." 
declare -a users=("F" 
		  "D"
		  "FM"
		  "DMCS"
		  "DMCS_PUB"
		  "AFM"
		  "AFM_PUB"
		  "PFM"
		  "PFM_PUB"
		  "PFM_NCSA"
		  "PFM_NCSA_PUB"
		  "NFM_BASE"
		  "NFM_BASE_PUB"
		  "ARCHIE"
		  "ARCHIE_PUB"
		  "AUDIT"
		  "CL_"
		  "EVN_")     

for i in ${users[@]}
do 
    if [ "$i" == "F" ] 
    then
        for j in {1..10}; 
        do
            x="F$j"
            #rabbitmqctl add_user $x $x
            #rabbitmqctl set_permissions -p /bunny $x ".*" ".*" ".*" 
            #rabbitmqctl set_permissions -p /test $x ".*" ".*" ".*" 
            rabbitmqctl set_permissions -p /test_hk $x ".*" ".*" ".*" 
        done
    elif [ "$i" == "D" ]
    then 
        for j in {1..10}; 
            do
            x="D$j"
            #rabbitmqctl add_user $x $x
            #rabbitmqctl set_permissions -p /bunny $x ".*" ".*" ".*" 
            #rabbitmqctl set_permissions -p /test $x ".*" ".*" ".*" 
            rabbitmqctl set_permissions -p /test_hk $x ".*" ".*" ".*" 
        done
    elif [ "$i" == "CL_" ]
    then
        for j in {1..25}; 
        do 
            x="CL_$j" 
            rabbitmqctl add_user $x $x;
            rabbitmqctl set_permissions -p /bunny $x ".*" ".*" ".*" 
            rabbitmqctl set_permissions -p /test $x ".*" ".*" ".*" 
            rabbitmqctl set_permissions -p /test_hk $x ".*" ".*" ".*" 
        done
    elif [ "$i" == "EVN_" ]
    then
        for j in {1..25}; 
        do 
            x="EVN_$j"
            rabbitmqctl add_user $x $x;
            rabbitmqctl set_permissions -p /bunny $x ".*" ".*" ".*" 
            rabbitmqctl set_permissions -p /test $x ".*" ".*" ".*" 
            rabbitmqctl set_permissions -p /test_hk $x ".*" ".*" ".*" 
        done
    else
        #rabbitmqctl add_user $i
        #rabbitmqctl set_permissions -p /bunny $i ".*" ".*" ".*" 
        #rabbitmqctl set_permissions -p /test $i ".*" ".*" ".*" 
        rabbitmqctl set_permissions -p /test_hk $i ".*" ".*" ".*" 
    fi
done
