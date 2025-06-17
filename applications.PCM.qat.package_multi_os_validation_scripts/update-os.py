from posixpath import split
import paramiko
import json
import os
import subprocess
import time
import glob


rp = (os.path.dirname(os.path.realpath(__file__)))
os.chdir(rp)

def get_vms():
    with open(r'./config/VM_OS_list.json') as json_file:
        data = json.load(json_file)
        for p in data:
            pass
            #print(p)
    return data


vms_list = get_vms()
print(vms_list)