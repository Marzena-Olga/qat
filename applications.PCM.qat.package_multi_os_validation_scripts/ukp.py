
import paramiko
import json
import os

def get_list():
    with open(r'./config/VM_OS_list.json') as json_file:
        data = json.load(json_file)
    return data

def connect_vms(data):
    print(data)
    update = False
    for i in data:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(i['IP'], 22)
            command = ("uname -r")
            stdin, stdout, stderr = ssh.exec_command(command)
            lines = stdout.readline()
            lines = lines.strip()
        except:
            print(i['IP'], ' No SSH connection  ')
        z = (data.index(i))
        if ((data[z])['KERNEL']) != lines:
            print('*****************************************************************************************************************************************************')
            print(data[z])
            ((data[z])['KERNEL']) = lines
            print(data[z])
            update = True
    if update == True:
        with open(r'./config/VM_OS_list.json', 'w') as outfile:
            json.dump(data, outfile, indent=4)
        command = ('git add ./config/VM_OS_list.json && git commit -m "Update config file" && git push --set-upstream origin main')
        print(command)
        os.system(command)
  



rp = (os.path.dirname(os.path.realpath(__file__)))
os.chdir(rp)
connect_vms(get_list())