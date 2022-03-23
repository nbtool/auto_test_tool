#!/usr/bin/env python3
# coding=utf-8

import json
import binascii
import sys
import os


AUTO_EN = {'AUTO_DIS':0,'AUTO_EN':1}
TRIGGER = {'TRIGGER_EDGE':0,'TRIGGER_KEEP':1}
RULE = {'RULE_OR':0,'RULE_AND':1}
DP_KIND = {'DP_KIND_VALUE':0,'DP_KIND_BOOL':1,'DP_KIND_ENUM':2,'DP_KIND_RAW':3,'DP_KIND_STRING':4}
EV_OP = {'EV_OP_E':0,'EV_OP_NE':1,'EV_OP_B':2,'EV_OP_S':3,'EV_OP_BE':4,'EV_OP_SE':5,'EV_OP_SBE':6,'EV_OP_SB':7,'EV_OP_NSBE':8,'EV_OP_NSB':9}
AC_OP = {'AC_OP_TOGGLE':0,'AC_OP_SET':1,'AC_OP_ADD':2,'AC_OP_CUT':3}
AT_OP = {'AT_OP_EN':0,'AT_OP_DIS':1,'AT_OP_EXE':2}


    
def ty_mesh_local_auto_create_frame_auto_head(json_string):
    # read from json
    auto_id = int(json_string['auto']['id'])
    attr_enable = AUTO_EN[json_string['auto']['attr']['en']]
    
    # create head frame
    buf = []
    buf.append((auto_id >> 8) & 0xFF)
    buf.append(auto_id & 0xFF)
    buf.append(attr_enable << 7)

    # log
    print('auto_id=%d, attr_enable=%d' %(auto_id, attr_enable),' --> ',binascii.b2a_hex(bytearray(buf))) 
    return buf

def ty_mesh_local_auto_create_frame_sub_event(event_json):
    # read params form json
    pub_address = int(event_json['pub_address'], 16)
    dpid = int(event_json['dpid'])
    trigger = TRIGGER[event_json['trigger']]
    dpkind = DP_KIND[event_json['dp_kind']]
    op = EV_OP[event_json['op']]

    # create frame
    buf = []
    buf.append((pub_address >> 8) & 0xFF) #pub_address
    buf.append((pub_address) & 0xFF)

    buf.append(dpid)
    buf.append((trigger<<7) | (dpkind<<4) | op)

    datas = []
    if dpkind == DP_KIND['DP_KIND_BOOL'] or dpkind == DP_KIND['DP_KIND_ENUM'] :
        a = int(event_json['a'])
        datas.append((a) & 0xFF)
    else:
        if op == EV_OP['EV_OP_E'] or op == EV_OP['EV_OP_NE'] or op == EV_OP['EV_OP_B'] or op == EV_OP['EV_OP_S'] or op == EV_OP['EV_OP_BE'] or op == EV_OP['EV_OP_SE']:
            a = int(event_json['a'])
            datas.append((a >> 8) & 0xFF)
            datas.append((a) & 0xFF)
        else:
            a = int(event_json['a'])
            b = int(event_json['b'])
            datas.append((a >> 8) & 0xFF)
            datas.append((a) & 0xFF)
            datas.append((b >> 8) & 0xFF)
            datas.append((b) & 0xFF)

    buf = buf + datas

    print('pub_address=%x, dpid=%d, dpkind=%d, trigger=%d, op=%d, datas=' %(pub_address, dpid, dpkind, trigger, op) ,binascii.b2a_hex(bytearray(datas)),' --> ',binascii.b2a_hex(bytearray(buf)))
    return buf

def ty_mesh_local_auto_create_frame_sub_action(action_json):
    # read params form json
    kind = int(action_json['kind'])

    # create action frame
    action_frame = []
    if kind == 0: # DP
        node_id = int(action_json['node_id'], 16) 
        dpid = int(action_json['dpid'])
        dpkind = DP_KIND[action_json['dp_kind']]
        op = AC_OP[action_json['op']]
    
        datas = []    
        if (dpkind == DP_KIND['DP_KIND_BOOL'] or dpkind == DP_KIND['DP_KIND_ENUM']) and op == AC_OP['AC_OP_SET']:
            a = int(action_json['a'])
            datas.append(a & 0xFF)
        elif dpkind == DP_KIND['DP_KIND_VALUE']:
            a = int(action_json['a'])
            datas.append((a >> 8) & 0xFF)
            datas.append(a & 0xFF)
        elif dpkind == DP_KIND['DP_KIND_RAW']:
            buf = action_json['raw']     
            #datas.append(buf.len())
            #datas = datas + buf
        elif dpkind == DP_KIND['DP_KIND_STRING']:
            buf = action_json['str']     
            datas.append(len(buf))
            datas = datas + list(str.encode(buf))
        elif not (dpkind == DP_KIND['DP_KIND_BOOL'] and op == AC_OP['AC_OP_TOGGLE']):
            print("error")

        action_frame.append(kind)
        action_frame.append(dpid)
        action_frame.append((dpkind << 4) | op)
        action_frame += datas

        # append to total frame
        if action_node_id_list.count(node_id) == 0:
            action_node_id_list.append(node_id)
            frame_actions_list.append([])
            action_num_list.append(0)

        index = action_node_id_list.index(node_id)
  
        frame_actions_list[index] += action_frame
        action_num_list[index] += 1

        # log
        print('kind=%d, dpid=%d, dpkind=%d, op=%d, datas=' %(kind, dpid, dpkind, op) ,binascii.b2a_hex(bytearray(datas)),' --> ',binascii.b2a_hex(bytearray(action_frame)))
    elif kind == 1: # DELAY
        # read from json
        delay = int(action_json['delay'])
            
        # create action frame
        action_frame.append(kind)
        action_frame.append((delay >> 8) & 0xFF)
        action_frame.append(delay & 0xFF)

        # append to total frame
        for i in range(len(action_node_id_list)):       
            frame_actions_list[i] += action_frame
            action_num_list[i] += 1
        
        # log
        print('delay=%ds' % delay, ' --> ',binascii.b2a_hex(bytearray(action_frame)))
    elif kind == 2: # AUTO
        # read from json
        auto_id = int(action_json['auto_id'])
        op = int(AT_OP[action_json['op']])

        # create action frame
        action_frame.append(kind)
        action_frame.append((auto_id >> 8) & 0xFF)
        action_frame.append(auto_id & 0xFF)
        action_frame.append(op)

        # append to first frame
        frame_actions_list[0] += action_frame
        action_num_list[0] += 1
        
        # log
        print('auto id=%d, op=%d' %(auto_id, op), ' --> ',binascii.b2a_hex(bytearray(action_frame)))
    else:
        print('error')



def search(path,s):
	#result = [filename for t in os.walk(path) for filename in t[2] if s in os.path.splitext(filename)[0]]
    result = []
    for t in os.walk(path): #返回的是root,dirs,files
        for filename in t[2]: #t[2]指的就是files
            if s in os.path.splitext(filename)[1]: #test.txt [0]为test [1]为.txt 文件名和扩展名
                result.append(filename)

    result.sort()
    return result



dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
json_files = search(dirname+'/test_json/','.json')
json_file_num = len(json_files)
json_file = ""
if json_file_num == 0:
    print('[error] no json file!')
    exit(1)
elif json_file_num == 1:
    json_file = json_files[0]
else:
    while 1<2: 
        print('there are %d json files, chose one' % json_file_num)
        for i in range(json_file_num):
            print("[%d]:%s" % (i+1,json_files[i]))
        index = int(input('chose -> '))-1
        if index < json_file_num and index >= 0:
            json_file = json_files[index]
            break
        else:
            print('chose error')
            
with open(dirname+'/test_json/'+json_file,'r') as jsonfile:
    json_string = json.load(jsonfile)


print("\ncreate frame: 1) create head ...")
frame_head = []
frame_head = ty_mesh_local_auto_create_frame_auto_head(json_string)

print("\ncreate frame: 2) create events ...")
frame_events = []
events_attr_trigger = TRIGGER[json_string['events']['attr']['trigger']]
events_attr_rule = RULE[json_string['events']['attr']['rule']]
event_list = json_string['events']['list']
frame_events.append(events_attr_trigger<<7 | events_attr_rule <<6 | len(event_list))

for event_json in event_list:
    frame_events += ty_mesh_local_auto_create_frame_sub_event(event_json)
    

print("\ncreate frame: 3) create actions ...")
frame_actions_list = [[]]
action_node_id_list = []
action_num_list = []
action_list = json_string['actions']['list']
for action_json in action_list:
    ty_mesh_local_auto_create_frame_sub_action(action_json) 

print("\nprint all frame ...")
fid = open(dirname+'/local_auto.db','wb')
for i in range(len(action_node_id_list)):
    frame_actions_list[i].insert(0,action_num_list[i])
    
    storage_head = []
    storage_head.append((action_node_id_list[i]>>8)&0xFF)
    storage_head.append(action_node_id_list[i]&0xFF)
    storage_head.append(len(frame_head) + len(frame_events)+len(frame_actions_list[i]))
    fid.write(bytearray(storage_head+frame_head+frame_events+frame_actions_list[i]))

    print('frame[%04x]=' % action_node_id_list[i] , binascii.b2a_hex(bytearray(frame_head+frame_events+frame_actions_list[i])))

fid.close()


