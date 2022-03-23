#!/bin/bash

old_lightA_node_id="0x0410"
old_pir_pub_address="0xC218"
old_door_pub_address="0xC220"
old_lum_pub_address="0xC228"

new_lightA_node_id="0x0410"
new_pir_pub_address="0xC218"
new_door_pub_address="0xC220"
new_lum_pub_address="0xC228"

grep -rl $old_lightA_node_id ./test_json/ | xargs sed -i "s:"$old_lightA_node_id":"$new_lightA_node_id":g"
grep -rl $old_pir_pub_address ./test_json/ | xargs sed -i "s:"$old_pir_pub_address":"$new_pir_pub_address":g"
grep -rl $old_door_pub_address ./test_json/ | xargs sed -i "s:"$old_door_pub_address":"$new_door_pub_address":g"
grep -rl $old_lum_pub_address ./test_json/ | xargs sed -i "s:"$old_lum_pub_address":"$new_lum_pub_address":g"
