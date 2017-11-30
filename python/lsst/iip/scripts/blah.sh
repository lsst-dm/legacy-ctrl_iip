#rabbitmqctl add_vhost /bunny


rabbitmqctl add_user F1_PUB F1_PUB
rabbitmqctl add_user F2_PUB F2_PUB
rabbitmqctl add_user F3_PUB F3_PUB
rabbitmqctl add_user F4_PUB F4_PUB
rabbitmqctl add_user F5_PUB F5_PUB
rabbitmqctl add_user F6_PUB F6_PUB
rabbitmqctl add_user F7_PUB F7_PUB
rabbitmqctl add_user F8_PUB F8_PUB
rabbitmqctl add_user F9_PUB F9_PUB
rabbitmqctl add_user F10_PUB F10_PUB
rabbitmqctl add_user F11_PUB F11_PUB


rabbitmqctl set_permissions -p /bunny F1_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F2_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F3_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F4_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F5_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F6_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F7_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F8_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F9_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F10_PUB '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F11_PUB '.*' '.*' '.*'

rabbitmqctl set_permissions -p /test F1_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F2_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F3_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F4_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F5_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F6_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F7_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F8_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F9_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F10_PUB '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F11_PUB '.*' '.*' '.*'


rabbitmqctl add_user D1_PUB D1_PUB
rabbitmqctl add_user D2_PUB D2_PUB
rabbitmqctl add_user D3_PUB D3_PUB
rabbitmqctl add_user D4_PUB D4_PUB
rabbitmqctl add_user D5_PUB D5_PUB
rabbitmqctl add_user D6_PUB D6_PUB
rabbitmqctl add_user D7_PUB D7_PUB
rabbitmqctl add_user D8_PUB D8_PUB
rabbitmqctl add_user D9_PUB D9_PUB
rabbitmqctl add_user D10_PUB D10_PUB
rabbitmqctl add_user D11_PUB D11_PUB

rabbitmqctl set_permissions -p /bunny D1_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny D2_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny D3_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny D4_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny D5_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny D6_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny D7_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny D8_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny D9_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny D10_PUB '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny D11_PUB '.*' '.*' '.*'

rabbitmqctl set_permissions -p /test D1_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test D2_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test D3_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test D4_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test D5_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test D6_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test D7_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test D8_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test D9_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test D10_PUB '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test D11_PUB '.*' '.*' '.*'


