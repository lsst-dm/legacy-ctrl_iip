rabbitmqctl add_vhost /bunny
rabbitmqctl add_vhost /test

### Consumer and Publisher for each Primary Forwarder to Foreman plus permissions
rabbitmqctl add_user F1 F1
rabbitmqctl add_user F2 F2
rabbitmqctl add_user F3 F3
rabbitmqctl add_user F4 F4
rabbitmqctl add_user F5 F5
rabbitmqctl add_user F6 F6
rabbitmqctl add_user F7 F7
rabbitmqctl add_user F8 F8
rabbitmqctl add_user F9 F9
rabbitmqctl add_user F10 F10
rabbitmqctl add_user F11 F11

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

rabbitmqctl set_permissions -p /bunny F1  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F2  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F3  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F4  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F5  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F6  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F7  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F8  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F9  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F10 '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F11 '.*' '.*' '.*'

rabbitmqctl set_permissions -p /test F1  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F2  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F3  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F4  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F5  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F6  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F7  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F8  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F9  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F10 '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F11 '.*' '.*' '.*'

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
############################################################

### Consumer and Publisher for each Primary Forwarder in relation to its subcomponents + perms
rabbitmqctl add_user F1_FETCH F1_FETCH
rabbitmqctl add_user F2_FETCH F2_FETCH
rabbitmqctl add_user F3_FETCH F3_FETCH
rabbitmqctl add_user F4_FETCH F4_FETCH
rabbitmqctl add_user F5_FETCH F5_FETCH
rabbitmqctl add_user F6_FETCH F6_FETCH
rabbitmqctl add_user F7_FETCH F7_FETCH
rabbitmqctl add_user F8_FETCH F8_FETCH
rabbitmqctl add_user F9_FETCH F9_FETCH
rabbitmqctl add_user F10_FETCH F10_FETCH
rabbitmqctl add_user F11_FETCH F11_FETCH

rabbitmqctl add_user F1_FETCH_PUB F1_FETCH_PUB
rabbitmqctl add_user F2_FETCH_PUB F2_FETCH_PUB
rabbitmqctl add_user F3_FETCH_PUB F3_FETCH_PUB
rabbitmqctl add_user F4_FETCH_PUB F4_FETCH_PUB
rabbitmqctl add_user F5_FETCH_PUB F5_FETCH_PUB
rabbitmqctl add_user F6_FETCH_PUB F6_FETCH_PUB
rabbitmqctl add_user F7_FETCH_PUB F7_FETCH_PUB
rabbitmqctl add_user F8_FETCH_PUB F8_FETCH_PUB
rabbitmqctl add_user F9_FETCH_PUB F9_FETCH_PUB
rabbitmqctl add_user F10_FETCH_PUB F10_FETCH_PUB
rabbitmqctl add_user F11_FETCH_PUB F11_FETCH_PUB

rabbitmqctl add_user F1_FORMAT F1_FORMAT
rabbitmqctl add_user F2_FORMAT F2_FORMAT
rabbitmqctl add_user F3_FORMAT F3_FORMAT
rabbitmqctl add_user F4_FORMAT F4_FORMAT
rabbitmqctl add_user F5_FORMAT F5_FORMAT
rabbitmqctl add_user F6_FORMAT F6_FORMAT
rabbitmqctl add_user F7_FORMAT F7_FORMAT
rabbitmqctl add_user F8_FORMAT F8_FORMAT
rabbitmqctl add_user F9_FORMAT F9_FORMAT
rabbitmqctl add_user F10_FORMAT F10_FORMAT
rabbitmqctl add_user F11_FORMAT F11_FORMAT

rabbitmqctl add_user F1_FORMAT_PUB F1_FORMAT_PUB
rabbitmqctl add_user F2_FORMAT_PUB F2_FORMAT_PUB
rabbitmqctl add_user F3_FORMAT_PUB F3_FORMAT_PUB
rabbitmqctl add_user F4_FORMAT_PUB F4_FORMAT_PUB
rabbitmqctl add_user F5_FORMAT_PUB F5_FORMAT_PUB
rabbitmqctl add_user F6_FORMAT_PUB F6_FORMAT_PUB
rabbitmqctl add_user F7_FORMAT_PUB F7_FORMAT_PUB
rabbitmqctl add_user F8_FORMAT_PUB F8_FORMAT_PUB
rabbitmqctl add_user F9_FORMAT_PUB F9_FORMAT_PUB
rabbitmqctl add_user F10_FORMAT_PUB F10_FORMAT_PUB
rabbitmqctl add_user F11_FORMAT_PUB F11_FORMAT_PUB

rabbitmqctl add_user F1_FORWARD F1_FORWARD
rabbitmqctl add_user F2_FORWARD F2_FORWARD
rabbitmqctl add_user F3_FORWARD F3_FORWARD
rabbitmqctl add_user F4_FORWARD F4_FORWARD
rabbitmqctl add_user F5_FORWARD F5_FORWARD
rabbitmqctl add_user F6_FORWARD F6_FORWARD
rabbitmqctl add_user F7_FORWARD F7_FORWARD
rabbitmqctl add_user F8_FORWARD F8_FORWARD
rabbitmqctl add_user F9_FORWARD F9_FORWARD
rabbitmqctl add_user F10_FORWARD F10_FORWARD
rabbitmqctl add_user F11_FORWARD F11_FORWARD

rabbitmqctl add_user F1_FORWARD_PUB F1_FORWARD_PUB
rabbitmqctl add_user F2_FORWARD_PUB F2_FORWARD_PUB
rabbitmqctl add_user F3_FORWARD_PUB F3_FORWARD_PUB
rabbitmqctl add_user F4_FORWARD_PUB F4_FORWARD_PUB
rabbitmqctl add_user F5_FORWARD_PUB F5_FORWARD_PUB
rabbitmqctl add_user F6_FORWARD_PUB F6_FORWARD_PUB
rabbitmqctl add_user F7_FORWARD_PUB F7_FORWARD_PUB
rabbitmqctl add_user F8_FORWARD_PUB F8_FORWARD_PUB
rabbitmqctl add_user F9_FORWARD_PUB F9_FORWARD_PUB
rabbitmqctl add_user F10_FORWARD_PUB F10_FORWARD_PUB
rabbitmqctl add_user F11_FORWARD_PUB F11_FORWARD_PUB
######################################################

### Each forwarder subcomponent pub and sub to Primary Forwarder
rabbitmqctl add_user FETCH_F1 FETCH_F1
rabbitmqctl add_user FETCH_F2 FETCH_F2
rabbitmqctl add_user FETCH_F3 FETCH_F3
rabbitmqctl add_user FETCH_F4 FETCH_F4
rabbitmqctl add_user FETCH_F5 FETCH_F5
rabbitmqctl add_user FETCH_F6 FETCH_F6
rabbitmqctl add_user FETCH_F7 FETCH_F7
rabbitmqctl add_user FETCH_F8 FETCH_F8
rabbitmqctl add_user FETCH_F9 FETCH_F9
rabbitmqctl add_user FETCH_F10 FETCH_F10
rabbitmqctl add_user FETCH_F11 FETCH_F11

rabbitmqctl add_user FETCH_F1_PUB FETCH_F1_PUB
rabbitmqctl add_user FETCH_F2_PUB FETCH_F2_PUB
rabbitmqctl add_user FETCH_F3_PUB FETCH_F3_PUB
rabbitmqctl add_user FETCH_F4_PUB FETCH_F4_PUB
rabbitmqctl add_user FETCH_F5_PUB FETCH_F5_PUB
rabbitmqctl add_user FETCH_F6_PUB FETCH_F6_PUB
rabbitmqctl add_user FETCH_F7_PUB FETCH_F7_PUB
rabbitmqctl add_user FETCH_F8_PUB FETCH_F8_PUB
rabbitmqctl add_user FETCH_F9_PUB FETCH_F9_PUB
rabbitmqctl add_user FETCH_F10_PUB FETCH_F10_PUB
rabbitmqctl add_user FETCH_F11_PUB FETCH_F11_PUB

rabbitmqctl add_user FORMAT_F1 FORMAT_F1
rabbitmqctl add_user FORMAT_F2 FORMAT_F2
rabbitmqctl add_user FORMAT_F3 FORMAT_F3
rabbitmqctl add_user FORMAT_F4 FORMAT_F4
rabbitmqctl add_user FORMAT_F5 FORMAT_F5
rabbitmqctl add_user FORMAT_F6 FORMAT_F6
rabbitmqctl add_user FORMAT_F7 FORMAT_F7
rabbitmqctl add_user FORMAT_F8 FORMAT_F8
rabbitmqctl add_user FORMAT_F9 FORMAT_F9
rabbitmqctl add_user FORMAT_F10 FORMAT_F10
rabbitmqctl add_user FORMAT_F11 FORMAT_F11

rabbitmqctl add_user FORMAT_F1_PUB FORMAT_F1_PUB
rabbitmqctl add_user FORMAT_F2_PUB FORMAT_F2_PUB
rabbitmqctl add_user FORMAT_F3_PUB FORMAT_F3_PUB
rabbitmqctl add_user FORMAT_F4_PUB FORMAT_F4_PUB
rabbitmqctl add_user FORMAT_F5_PUB FORMAT_F5_PUB
rabbitmqctl add_user FORMAT_F6_PUB FORMAT_F6_PUB
rabbitmqctl add_user FORMAT_F7_PUB FORMAT_F7_PUB
rabbitmqctl add_user FORMAT_F8_PUB FORMAT_F8_PUB
rabbitmqctl add_user FORMAT_F9_PUB FORMAT_F9_PUB
rabbitmqctl add_user FORMAT_F10_PUB FORMAT_F10_PUB
rabbitmqctl add_user FORMAT_F11_PUB FORMAT_F11_PUB

rabbitmqctl add_user FORWARD_F1 FORWARD_F1
rabbitmqctl add_user FORWARD_F2 FORWARD_F2
rabbitmqctl add_user FORWARD_F3 FORWARD_F3
rabbitmqctl add_user FORWARD_F4 FORWARD_F4
rabbitmqctl add_user FORWARD_F5 FORWARD_F5
rabbitmqctl add_user FORWARD_F6 FORWARD_F6
rabbitmqctl add_user FORWARD_F7 FORWARD_F7
rabbitmqctl add_user FORWARD_F8 FORWARD_F8
rabbitmqctl add_user FORWARD_F9 FORWARD_F9
rabbitmqctl add_user FORWARD_F10 FORWARD_F10
rabbitmqctl add_user FORWARD_F11 FORWARD_F11

rabbitmqctl add_user FORWARD_F1_PUB FORWARD_F1_PUB
rabbitmqctl add_user FORWARD_F2_PUB FORWARD_F2_PUB
rabbitmqctl add_user FORWARD_F3_PUB FORWARD_F3_PUB
rabbitmqctl add_user FORWARD_F4_PUB FORWARD_F4_PUB
rabbitmqctl add_user FORWARD_F5_PUB FORWARD_F5_PUB
rabbitmqctl add_user FORWARD_F6_PUB FORWARD_F6_PUB
rabbitmqctl add_user FORWARD_F7_PUB FORWARD_F7_PUB
rabbitmqctl add_user FORWARD_F8_PUB FORWARD_F8_PUB
rabbitmqctl add_user FORWARD_F9_PUB FORWARD_F9_PUB
rabbitmqctl add_user FORWARD_F10_PUB FORWARD_F10_PUB
rabbitmqctl add_user FORWARD_F11_PUB FORWARD_F11_PUB





rabbitmqctl set_permissions -p /bunny F1  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F2  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F3  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F4  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F5  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F6  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F7  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F8  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F9  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F10 '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F11 '.*' '.*' '.*'

rabbitmqctl set_permissions -p /test F1  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F2  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F3  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F4  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F5  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F6  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F7  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F8  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F9  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F10 '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F11 '.*' '.*' '.*'

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


rabbitmqctl set_permissions -p /bunny F1_FETCH  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F2_FETCH  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F3_FETCH  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F4_FETCH  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F5_FETCH  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F6_FETCH  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F7_FETCH  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F8_FETCH  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F9_FETCH  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F10_FETCH '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F11_FETCH '.*' '.*' '.*'

rabbitmqctl set_permissions -p /test F1_FETCH  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F2_FETCH  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F3_FETCH  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F4_FETCH  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F5_FETCH  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F6_FETCH  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F7_FETCH  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F8_FETCH  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F9_FETCH  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F10_FETCH '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F11_FETCH '.*' '.*' '.*'

rabbitmqctl set_permissions -p /bunny F1_FETCH_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F2_FETCH_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F3_FETCH_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F4_FETCH_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F5_FETCH_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F6_FETCH_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F7_FETCH_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F8_FETCH_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F9_FETCH_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F10_FETCH_PUB '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F11_FETCH_PUB '.*' '.*' '.*'

rabbitmqctl set_permissions -p /test F1_FETCH_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F2_FETCH_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F3_FETCH_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F4_FETCH_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F5_FETCH_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F6_FETCH_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F7_FETCH_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F8_FETCH_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F9_FETCH_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F10_FETCH_PUB '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F11_FETCH_PUB '.*' '.*' '.*'
##
rabbitmqctl set_permissions -p /bunny FETCH_F1  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FETCH_F2  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FETCH_F3  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FETCH_F4  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FETCH_F5  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FETCH_F6  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FETCH_F7  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FETCH_F8  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FETCH_F9  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FETCH_F10 '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FETCH_F11 '.*' '.*' '.*'

rabbitmqctl set_permissions -p /test FETCH_F1  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FETCH_F2  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FETCH_F3  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FETCH_F4  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FETCH_F5  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FETCH_F6  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FETCH_F7  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FETCH_F8  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FETCH_F9  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FETCH_F10 '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FETCH_F11 '.*' '.*' '.*'

rabbitmqctl set_permissions -p /bunny FETCH_F1_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FETCH_F2_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FETCH_F3_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FETCH_F4_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FETCH_F5_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FETCH_F6_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FETCH_F7_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FETCH_F8_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FETCH_F9_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FETCH_F10_PUB '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FETCH_F11_PUB '.*' '.*' '.*'

rabbitmqctl set_permissions -p /test FETCH_F1_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FETCH_F2_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FETCH_F3_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FETCH_F4_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FETCH_F5_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FETCH_F6_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FETCH_F7_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FETCH_F8_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FETCH_F9_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FETCH_F10_PUB '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FETCH_F11_PUB '.*' '.*' '.*'
##

rabbitmqctl set_permissions -p /bunny FORMAT_F1  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FORMAT_F2  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FORMAT_F3  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FORMAT_F4  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FORMAT_F5  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FORMAT_F6  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FORMAT_F7  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FORMAT_F8  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FORMAT_F9  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FORMAT_F10 '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FORMAT_F11 '.*' '.*' '.*'

rabbitmqctl set_permissions -p /test FORMAT_F1  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FORMAT_F2  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FORMAT_F3  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FORMAT_F4  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FORMAT_F5  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FORMAT_F6  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FORMAT_F7  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FORMAT_F8  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FORMAT_F9  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FORMAT_F10 '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FORMAT_F11 '.*' '.*' '.*'

rabbitmqctl set_permissions -p /bunny FORMAT_F1_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FORMAT_F2_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FORMAT_F3_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FORMAT_F4_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FORMAT_F5_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FORMAT_F6_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FORMAT_F7_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FORMAT_F8_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FORMAT_F9_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FORMAT_F10_PUB '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FORMAT_F11_PUB '.*' '.*' '.*'

rabbitmqctl set_permissions -p /test FORMAT_F1_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FORMAT_F2_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FORMAT_F3_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FORMAT_F4_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FORMAT_F5_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FORMAT_F6_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FORMAT_F7_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FORMAT_F8_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FORMAT_F9_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FORMAT_F10_PUB '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FORMAT_F11_PUB '.*' '.*' '.*'
##
rabbitmqctl set_permissions -p /bunny FORWARD_F1  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FORWARD_F2  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FORWARD_F3  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FORWARD_F4  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FORWARD_F5  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FORWARD_F6  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FORWARD_F7  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FORWARD_F8  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FORWARD_F9  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FORWARD_F10 '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FORWARD_F11 '.*' '.*' '.*'

rabbitmqctl set_permissions -p /test FORWARD_F1  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FORWARD_F2  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FORWARD_F3  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FORWARD_F4  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FORWARD_F5  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FORWARD_F6  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FORWARD_F7  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FORWARD_F8  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FORWARD_F9  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FORWARD_F10 '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FORWARD_F11 '.*' '.*' '.*'

rabbitmqctl set_permissions -p /bunny FORWARD_F1_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FORWARD_F2_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FORWARD_F3_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FORWARD_F4_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FORWARD_F5_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FORWARD_F6_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FORWARD_F7_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FORWARD_F8_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FORWARD_F9_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FORWARD_F10_PUB '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny FORWARD_F11_PUB '.*' '.*' '.*'

rabbitmqctl set_permissions -p /test FORWARD_F1_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FORWARD_F2_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FORWARD_F3_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FORWARD_F4_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FORWARD_F5_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FORWARD_F6_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FORWARD_F7_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FORWARD_F8_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FORWARD_F9_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FORWARD_F10_PUB '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test FORWARD_F11_PUB '.*' '.*' '.*'
##
############################################################

rabbitmqctl set_permissions -p /bunny F1_FORMAT  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F2_FORMAT  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F3_FORMAT  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F4_FORMAT  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F5_FORMAT  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F6_FORMAT  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F7_FORMAT  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F8_FORMAT  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F9_FORMAT  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F10_FORMAT '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F11_FORMAT '.*' '.*' '.*'

rabbitmqctl set_permissions -p /test F1_FORMAT  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F2_FORMAT  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F3_FORMAT  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F4_FORMAT  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F5_FORMAT  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F6_FORMAT  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F7_FORMAT  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F8_FORMAT  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F9_FORMAT  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F10_FORMAT '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F11_FORMAT '.*' '.*' '.*'

rabbitmqctl set_permissions -p /bunny F1_FORMAT_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F2_FORMAT_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F3_FORMAT_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F4_FORMAT_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F5_FORMAT_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F6_FORMAT_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F7_FORMAT_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F8_FORMAT_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F9_FORMAT_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F10_FORMAT_PUB '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F11_FORMAT_PUB '.*' '.*' '.*'

rabbitmqctl set_permissions -p /test F1_FORMAT_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F2_FORMAT_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F3_FORMAT_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F4_FORMAT_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F5_FORMAT_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F6_FORMAT_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F7_FORMAT_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F8_FORMAT_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F9_FORMAT_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F10_FORMAT_PUB '.*' '.*' '.*'

############################################################
rabbitmqctl set_permissions -p /bunny F1_FORWARD  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F2_FORWARD  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F3_FORWARD  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F4_FORWARD  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F5_FORWARD  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F6_FORWARD  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F7_FORWARD  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F8_FORWARD  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F9_FORWARD  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F10_FORWARD '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F11_FORWARD '.*' '.*' '.*'

rabbitmqctl set_permissions -p /test F1_FORWARD  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F2_FORWARD  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F3_FORWARD  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F4_FORWARD  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F5_FORWARD  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F6_FORWARD  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F7_FORWARD  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F8_FORWARD  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F9_FORWARD  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F10_FORWARD '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F11_FORWARD '.*' '.*' '.*'

rabbitmqctl set_permissions -p /bunny F1_FORWARD_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F2_FORWARD_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F3_FORWARD_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F4_FORWARD_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F5_FORWARD_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F6_FORWARD_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F7_FORWARD_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F8_FORWARD_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F9_FORWARD_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F10_FORWARD_PUB '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny F11_FORWARD_PUB '.*' '.*' '.*'

rabbitmqctl set_permissions -p /test F1_FORWARD_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F2_FORWARD_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F3_FORWARD_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F4_FORWARD_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F5_FORWARD_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F6_FORWARD_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F7_FORWARD_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F8_FORWARD_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F9_FORWARD_PUB  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test F10_FORWARD_PUB '.*' '.*' '.*'

############################################################

rabbitmqctl add_user D1 D1
rabbitmqctl add_user D2 D2
rabbitmqctl add_user D3 D3
rabbitmqctl add_user D4 D4
rabbitmqctl add_user D5 D5
rabbitmqctl add_user D6 D6
rabbitmqctl add_user D7 D7
rabbitmqctl add_user D8 D8
rabbitmqctl add_user D9 D9
rabbitmqctl add_user D10 D10
rabbitmqctl add_user D11 D11

rabbitmqctl set_permissions -p /bunny D1  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny D2  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny D3  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny D4  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny D5  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny D6  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny D7  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny D8  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny D9  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny D10 '.*' '.*' '.*'
rabbitmqctl set_permissions -p /bunny D11 '.*' '.*' '.*'

rabbitmqctl set_permissions -p /test D1  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test D2  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test D3  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test D4  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test D5  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test D6  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test D7  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test D8  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test D9  '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test D10 '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test D11 '.*' '.*' '.*'

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


rabbitmqctl add_user FM FM
rabbitmqctl set_permissions -p /bunny FM '.*' '.*' '.*'
rabbitmqctl set_user_tags FM administrator

rabbitmqctl add_user DMCS DMCS
rabbitmqctl set_permissions -p /bunny DMCS '.*' '.*' '.*'
rabbitmqctl set_user_tags DMCS administrator


rabbitmqctl add_user AFM AFM
rabbitmqctl set_permissions -p /bunny AFM '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test AFM '.*' '.*' '.*'

rabbitmqctl add_user AFM_PUB AFM_PUB
rabbitmqctl set_permissions -p /bunny AFM_PUB '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test AFM_PUB '.*' '.*' '.*'


rabbitmqctl add_user AUX AUX
rabbitmqctl set_permissions -p /bunny AUX '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test AUX '.*' '.*' '.*'

rabbitmqctl add_user AUX_PUB AUX_PUB
rabbitmqctl set_permissions -p /bunny AUX_PUB '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test AUX_PUB '.*' '.*' '.*'


rabbitmqctl add_user PFM PFM
rabbitmqctl set_permissions -p /bunny PFM '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test PFM '.*' '.*' '.*'

rabbitmqctl add_user PFM_PUB PFM_PUB
rabbitmqctl set_permissions -p /bunny PFM_PUB '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test PFM_PUB '.*' '.*' '.*'


rabbitmqctl add_user PFM_NCSA PFM_NCSA
rabbitmqctl set_permissions -p /bunny PFM_NCSA '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test PFM_NCSA '.*' '.*' '.*'

rabbitmqctl add_user PFM_NCSA_PUB PFM_NCSA_PUB
rabbitmqctl set_permissions -p /bunny PFM_NCSA_PUB '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test PFM_NCSA_PUB '.*' '.*' '.*'


rabbitmqctl add_user NFM_BASE NFM_BASE
rabbitmqctl set_permissions -p /bunny NFM_BASE '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test NFM_BASE '.*' '.*' '.*'

rabbitmqctl add_user NFM_BASE_PUB NFM_BASE_PUB
rabbitmqctl set_permissions -p /bunny NFM_BASE_PUB '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test NFM_BASE_PUB '.*' '.*' '.*'

rabbitmqctl add_user NFM_NCSA NFM_NCSA
rabbitmqctl set_permissions -p /bunny NFM_NCSA '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test NFM_NCSA '.*' '.*' '.*'

rabbitmqctl add_user NFM_NCSA_PUB NFM_NCSA_PUB
rabbitmqctl set_permissions -p /bunny NFM_NCSA_PUB '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test NFM_NCSA_PUB '.*' '.*' '.*'

rabbitmqctl add_user ARCHIE ARCHIE
rabbitmqctl set_permissions -p /bunny ARCHIE '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test ARCHIE '.*' '.*' '.*'

rabbitmqctl add_user ARCHIE_PUB ARCHIE_PUB
rabbitmqctl set_permissions -p /bunny ARCHIE_PUB '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test ARCHIE_PUB '.*' '.*' '.*'

rabbitmqctl add_user DMCS DMCS
rabbitmqctl set_permissions -p /bunny DMCS '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test DMCS '.*' '.*' '.*'

rabbitmqctl add_user DMCS_PUB DMCS_PUB
rabbitmqctl set_permissions -p /bunny DMCS_PUB '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test DMCS_PUB '.*' '.*' '.*'

rabbitmqctl add_user AUDIT AUDIT
rabbitmqctl set_permissions -p /bunny AUDIT '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test AUDIT '.*' '.*' '.*'

rabbitmqctl add_user OCS OCS 
rabbitmqctl set_permissions -p /bunny OCS '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test OCS '.*' '.*' '.*'

rabbitmqctl add_user OCS_PUB OCS_PUB 
rabbitmqctl set_permissions -p /bunny OCS_PUB '.*' '.*' '.*'
rabbitmqctl set_permissions -p /test OCS_PUB '.*' '.*' '.*'

for i in {1..25}; do 
   x="CL_"$i; 
   rabbitmqctl add_user $x $x;
   rabbitmqctl set_permissions -p /test $x '.*' '.*' '.*'
   rabbitmqctl set_permissions -p /bunny $x '.*' '.*' '.*'
   done

for i in {1..25}; do 
   x="EVN_"$i; 
   rabbitmqctl add_user $x $x;
   rabbitmqctl set_permissions -p /test $x '.*' '.*' '.*'
   rabbitmqctl set_permissions -p /bunny $x '.*' '.*' '.*'
   done

