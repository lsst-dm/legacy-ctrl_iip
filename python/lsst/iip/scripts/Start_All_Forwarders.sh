ssh -i ~/.ssh/id_rsa F1@141.142.238.181 <<- "END1"
    cd ~/src/git/ctrl_iip/python/lsst/iip/forwarder/src
    make 
    ./Forwarder > /dev/null&
END1

ssh -i ~/.ssh/id_rsa F2@141.142.238.182 <<- "END2"
    cd ~/src/git/ctrl_iip/python/lsst/iip/forwarder/src
    make 
    ./Forwarder > /dev/null&
END2

ssh -i ~/.ssh/id_rsa F3@141.142.238.183 <<- "END3"
    cd ~/src/git/ctrl_iip/python/lsst/iip/forwarder/src
    make 
    ./Forwarder > /dev/null&
END3

ssh -i ~/.ssh/id_rsa F4@141.142.238.184 <<- "END4"
    cd ~/src/git/ctrl_iip/python/lsst/iip/forwarder/src
    make 
    ./Forwarder > /dev/null&
END4

ssh -i ~/.ssh/id_rsa F5@141.142.238.185 <<- "END5"
    cd ~/src/git/ctrl_iip/python/lsst/iip/forwarder/src
    make 
    ./Forwarder > /dev/null&
END5

ssh -i ~/.ssh/id_rsa F6@141.142.238.186 <<- "END6"
    cd ~/src/git/ctrl_iip/python/lsst/iip/forwarder/src
    make 
    ./Forwarder > /dev/null&
END6

ssh -i ~/.ssh/id_rsa F7@141.142.238.187 <<- "END7"
    cd ~/src/git/ctrl_iip/python/lsst/iip/forwarder/src
    make 
    ./Forwarder > /dev/null&
END7

ssh -i ~/.ssh/id_rsa F8@141.142.238.188 <<- "END8"
    cd ~/src/git/ctrl_iip/python/lsst/iip/forwarder/src
    make 
    ./Forwarder > /dev/null&
END8

ssh -i ~/.ssh/id_rsa F9@141.142.238.189 <<- "END9"
    cd ~/src/git/ctrl_iip/python/lsst/iip/forwarder/src
    make 
    ./Forwarder > /dev/null&
END9

ssh -i ~/.ssh/id_rsa F10@141.142.238.190 <<- "END10"
    cd ~/src/git/ctrl_iip/python/lsst/iip/forwarder/src
    make 
    ./Forwarder > /dev/null&
END10
