import paramiko
import json
import os





def get_ink():
    li = list()
    with open(r'./config/VM_OS_list.json') as json_file:
        data = json.load(json_file)
        for p in data:
            z = (p['NAME']).lower()
            if z.find('ink') == -1:
                li.append(p['IP'])
    return li 

def test_os(ink_hosts):
    res=dict()
    z=''
    for ink in ink_hosts:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(ink, 22)

            command = ("cat /etc/os-release")
            stdin, stdout, stderr = ssh.exec_command(command)
            lines = stdout.readlines()
            z=(lines[0])
            z=z.replace('\n','')
            z=z.replace('NAME=','')
            print(ink,z)
            
    
        except:
            print(ink, ' No SSH connection  ')
        res[ink]=z

    #print(res)
    return res

def upgr_hosts(dict_hosts):
    print(dict_hosts)
    for i in dict_hosts:
        print(i,dict_hosts[i])
        run_upgr(i,dict_hosts[i])


def run_upgr(ip_host,os_host):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    os_host=os_host.lower()
    #print (os_host,ip_host)
    if (os_host.find('ubuntu')) != -1:
        command = ("apt-get update -y && apt-get upgrade -y && reboot")
        print('Ubuntu:',command)
    if (os_host.find('sles')) != -1:
        command = ("zypper refresh && zypper update -y && reboot")
        print('SLES:',command)
    if (os_host.find('red hat')) != -1:
        command = ("dnf -y update && reboot")
        print('RHEL:',command)
    if (os_host.find('centos')) != -1:
        command = ("dnf -y update && reboot")
        print('CentOS:',command)
    if (os_host.find('fedora')) != -1:
        command = ("dnf -y update && reboot")
        print('Fedora:',command)

    try:
        ssh.connect(ip_host, 22)
        stdin, stdout, stderr = ssh.exec_command(command)
        lines = stdout.readlines()
        for i in lines:
            i=i.replace('\n','')
            print(i)
    
    except:
            print(ip_host, ' No SSH connection  ')


rp = (os.path.dirname(os.path.realpath(__file__)))
os.chdir(rp)
ink_hosts=get_ink()
print(ink_hosts)
dict_hosts = test_os(ink_hosts)
upgr_hosts(dict_hosts)