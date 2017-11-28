rabbitmqctl add_vhost /bunny
rabbitmqctl add_vhost /test

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


for i in {1..25}; do 
   x="CL_"$i; 
   rabbitmqctl add_user $x $x;
   rabbitmqctl set_permissions -p /test $x \'.\*\' \'.\*\' \'.\*\'
   rabbitmqctl set_permissions -p /bunny $x \'.\*\' \'.\*\' \'.\*\'
   done


for i in {1..25}; do 
   x="EVN_"$i; 
   rabbitmqctl add_user $x $x;
   rabbitmqctl set_permissions -p /test $x \'.\*\' \'.\*\' \'.\*\'
   rabbitmqctl set_permissions -p /bunny $x \'.\*\' \'.\*\' \'.\*\'
   done






