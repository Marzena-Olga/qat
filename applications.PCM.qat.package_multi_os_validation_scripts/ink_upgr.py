import paramiko
import json
import os
import time
import sys

def get_ink():
    li = list()
    with open(r'./config/VM_OS_list.json') as json_file:
        data = json.load(json_file)
        for p in data:
            if p['NAME'].find('ink') != -1 or p['NAME'].find('INK') != -1:
                li.append(p['IP'])
    return li 

def chk_upgr(ink_hosts):
    for ink in ink_hosts:
        mk_link(ink) #create link to sources
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            command = ("dnf check-update | grep kernel-next.x86_64") #check for new version of kernel on repo
            ssh.connect(ink, 22)
            stdin, stdout, stderr = ssh.exec_command(command)
            lines = stdout.readlines()
            print(lines)
            
            if lines[0].find('kernel-next.x86_64') != -1:
                print ('Upgrade Intel Next Kernel')
                upgr_krnl(ink) #download, install new kernel and reboot host
                chek_ssh(ink) #wait and test for host after reboot
                #mk_link(ink) #create link to sources
                dwnl_src(ink) #download new sources and compile it
            else:
                print ('No new Intel Next Kernel')
        except:
            print(ink, ' No SSH connection or no new Intel Next Kernel')





def upgr_krnl(ink):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(ink, 22)

        command = ("dnf clean packages")
        stdin, stdout, stderr = ssh.exec_command(command)
        lines = stdout.readlines()
        print(lines)
        command2 = ("rm -rf /usr/lib/firmware/intel/sof && rm -rf /usr/lib/firmware/intel/sof-tplg && dnf upgrade -y && reboot")
        stdin, stdout, stderr = ssh.exec_command(command2)
        lines = stdout.readlines()
        #print(lines) 
        for i in lines:
            i=i.replace('\n','')
            print(i)
    except:
        print(ink, ' No SSH connection  ')

    

def chek_ssh(ink):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    z = 0
    x = 0
    time.sleep(5)
    while (z==0):
        try:
            time.sleep(1)
            ssh.connect(ink, 22)
            z = 1
            print(ink, ' SSH connection  ')   
        except:
            print(x, ink, ' No SSH connection  ')
            z = 0
            x= x + 1
            if x == 100:
                z = 1
                sys.exit('Time out for restart host')

    
    
def mk_link(ink):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(ink, 22)

        command = ("uname -r")
        stdin, stdout, stderr = ssh.exec_command(command)
        lines = stdout.readlines()
        print(lines)
        s=lines[0]
        s=s.replace('\n','')
        print(s)

        command2 = ("ln -s /root/intel-next-kernel/ /usr/lib/modules/{}/build").format(s)
        print(command2)
        stdin, stdout, stderr = ssh.exec_command(command2)
        lines = stdout.readlines()
        print(lines)

        command3 = ("grub2-set-default $(uname -r) && grub2-mkconfig -o /boot/grub2/grub.cfg")
        print(command3)
        stdin, stdout, stderr = ssh.exec_command(command3)
        lines = stdout.readlines()
        print(lines)

    except:
        print(ink, ' No SSH connection  ')


def dwnl_src(ink):
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(ink, 22)

        command = ("cd /root && rm -rf /root/intel-next-kernel/")
        stdin, stdout, stderr = ssh.exec_command(command)
        lines = stdout.readlines()
        print(lines)

        command2 = ("cd /root && git clone ssh://git@gitlab.devtools.intel.com:29418/intel-next/intel-next-kernel.git")
        stdin, stdout, stderr = ssh.exec_command(command2)
        lines = stdout.readlines()
        for i in lines:
            print(i)

        #command3 = ("cd /root/intel-next-kernel/ && git pull ssh://git@gitlab.devtools.intel.com:29418/intel-next/intel-next-kernel.git")
        #stdin, stdout, stderr = ssh.exec_command(command3)
        #lines = stdout.readlines()
        #for i in lines:
        #    print(i)
        

        command4 = ("cd /root/intel-next-kernel && yes "" | make oldconfig && yes "" | make modules_prepare")
        stdin, stdout, stderr = ssh.exec_command(command4)
        lines = stdout.readlines()
        for i in lines:
            i=i.replace('\n','')
            print(i)

    except:
        print(ink, ' No SSH connection  ')


rp = (os.path.dirname(os.path.realpath(__file__)))
os.chdir(rp)
ink_hosts=get_ink()
print(ink_hosts)
chk_upgr(ink_hosts)
