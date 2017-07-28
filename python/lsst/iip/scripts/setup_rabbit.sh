sudo rabbitmqctl add_vhost /bunny

sudo rabbitmqctl add_user BASE BASE 
sudo rabbitmqctl add_user BASE_PUB BASE_PUB
sudo rabbitmqctl add_user AFM AFM 
sudo rabbitmqctl add_user AFM_PUB AFM_PUB
sudo rabbitmqctl add_user PFM PFM 
sudo rabbitmqctl add_user PFM_PUB PFM_PUB
sudo rabbitmqctl add_user PFM_NCSA PFM_NCSA
sudo rabbitmqctl add_user PFM_NCSA_PUB PFM_NCSA_PUB
sudo rabbitmqctl add_user ARCHIE ARCHIE
sudo rabbitmqctl add_user AUDIT AUDIT
sudo rabbitmqctl add_user DMCS DMCS
sudo rabbitmqctl add_user DMCS_PUB DMCS_PUB
sudo rabbitmqctl add_user NCSA NCSA
sudo rabbitmqctl add_user F1 F1
sudo rabbitmqctl add_user D1 D1

sudo rabbitmqctl set_permissions -p /bunny BASE ".*" ".*" ".*"
sudo rabbitmqctl set_permissions -p /bunny BASE_PUB ".*" ".*" ".*"
sudo rabbitmqctl set_permissions -p /bunny AFM ".*" ".*" ".*"
sudo rabbitmqctl set_permissions -p /bunny AFM_PUB ".*" ".*" ".*"
sudo rabbitmqctl set_permissions -p /bunny PFM ".*" ".*" ".*"
sudo rabbitmqctl set_permissions -p /bunny PFM_PUB ".*" ".*" ".*"
sudo rabbitmqctl set_permissions -p /bunny PFM_NCSA ".*" ".*" ".*"
sudo rabbitmqctl set_permissions -p /bunny PFM_NCSA_PUB ".*" ".*" ".*"
sudo rabbitmqctl set_permissions -p /bunny ARCHIE ".*" ".*" ".*"
sudo rabbitmqctl set_permissions -p /bunny AUDIT ".*" ".*" ".*"
sudo rabbitmqctl set_permissions -p /bunny DMCS ".*" ".*" ".*"
sudo rabbitmqctl set_permissions -p /bunny DMCS_PUB ".*" ".*" ".*"
sudo rabbitmqctl set_permissions -p /bunny NCSA ".*" ".*" ".*"
sudo rabbitmqctl set_permissions -p /bunny F1 ".*" ".*" ".*"
sudo rabbitmqctl set_permissions -p /bunny D1 ".*" ".*" ".*"
