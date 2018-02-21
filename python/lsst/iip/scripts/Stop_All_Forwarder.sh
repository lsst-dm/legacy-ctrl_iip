ssh -i ~/.ssh/id_rsa F1@141.142.238.181 <<- "END1"
    VAR=$(pidof Forwarder)
    kill -9 $VAR
END1

ssh -i ~/.ssh/id_rsa F2@141.142.238.182 <<- "END2"
    VAR=$(pidof Forwarder)
    kill -9 $VAR
END2

ssh -i ~/.ssh/id_rsa F3@141.142.238.183 <<- "END3"
    VAR=$(pidof Forwarder)
    kill -9 $VAR
END3

ssh -i ~/.ssh/id_rsa F4@141.142.238.184 <<- "END4"
    VAR=$(pidof Forwarder)
    kill -9 $VAR
END4

ssh -i ~/.ssh/id_rsa F5@141.142.238.185 <<- "END5"
    VAR=$(pidof Forwarder)
    kill -9 $VAR
END5

ssh -i ~/.ssh/id_rsa F6@141.142.238.186 <<- "END6"
    VAR=$(pidof Forwarder)
    kill -9 $VAR
END6

ssh -i ~/.ssh/id_rsa F7@141.142.238.187 <<- "END7"
    VAR=$(pidof Forwarder)
    kill -9 $VAR
END7

ssh -i ~/.ssh/id_rsa F8@141.142.238.188 <<- "END8"
    VAR=$(pidof Forwarder)
    kill -9 $VAR
END8

ssh -i ~/.ssh/id_rsa F9@141.142.238.189 <<- "END9"
    VAR=$(pidof Forwarder)
    kill -9 $VAR
END9

ssh -i ~/.ssh/id_rsa F10@141.142.238.190 <<- "END10"
    VAR=$(pidof Forwarder)
    kill -9 $VAR
END10
