#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This script create RPM packages for Fedora Linux.
# This script should be run as a Jenkins job
# Author: Marzena Kupniewska
# Maintainer: Marzena Kupniewska

__author__ = "Marzena Kupniewska"

"""
    Script for rpm kernel creation
"""

import os
import subprocess
import fileinput
from datetime import datetime
import shutil
import sys


now_start = datetime.now()

#variables and environment

FEDPKG_DEPS="fedpkg fedora-packager rpmdevtools ncurses-devel pesign grubby"
command = ('sudo dnf install -y ${0}').format(FEDPKG_DEPS)
os.system(command)
command = 'sudo grep `whoami` /etc/pesign/users || whoami | sudo tee -a /etc/pesign/users'
os.system(command)
command = 'sudo /usr/libexec/pesign/pesign-authorize'
os.system(command)

QAT_SRC="cryptodev-2.6"
FEDORA_KERNEL_SRC="kernel"
QAT_REPO="https://github.com/intel-innersource/drivers.qat.linux.qatkernel.git"
FEDPKG_DEPS="fedpkg fedora-packager rpmdevtools ncurses-devel pesign grubby"
FEDORA_PATCHES_FILE="linux-kernel-test.patch"

FEDORA_KERNEL_BRANCH = os.getenv('FEDORA_KERNEL_BRANCH')
Q_P = str(os.getenv('QAT_PATCHES'))
WORKDIR = os.getenv('BUILD_DIRECTORY')
QAT_BUILD_S_N = os.getenv('BUILD_SN')
QAT_BUILD_STR = os.getenv('BUILD_STRING')
QAT_BRANCH = os.getenv('BRANCH')
WORKSPACE = os.getenv('WORKSPACE')
RPMROOT = os.getenv('RPMROOT')



if (Q_P) != '' :
    QAT_PATCHES=(Q_P).split(",")
else:
    QAT_PATCHES=list()  #declare empty list if script don't get params

if len(FEDORA_KERNEL_BRANCH) == '':
    FEDORA_KERNEL_BRANCH = 'main'

if WORKDIR == '':
    WORKDIR = 'fed_rpms_4_dev_conf'

if QAT_BUILD_S_N == '':
    QAT_BUILD_S_N = '0000'

if QAT_BUILD_STR == '':
    QAT_BUILD_STR = 'qat_custom'

if QAT_BRANCH == '':
    QAT_BRANCH = 'master'

BD = WORKDIR  #relative build directory
WORKDIR=WORKSPACE+'/'+WORKDIR  #absolute build directory
QAT_BUILD_TAG=QAT_BUILD_S_N+'\.'+QAT_BUILD_STR

print(FEDORA_KERNEL_BRANCH, QAT_PATCHES, WORKDIR, QAT_BRANCH, QAT_BUILD_TAG)



print("########################################################################################################")

#clone qatkernel repo and prepare linux-kernel-test.patch file with patches

command = ("rm -rf {0}/{1}").format(WORKDIR, QAT_SRC)
os.system(command)

command = ("git clone {0} {1}/{2} -b {3}").format(QAT_REPO, WORKDIR, QAT_SRC, QAT_BRANCH) 
#git clone https://github.com/intel-innersource/drivers.qat.linux.qatkernel.git /var/lib/jenkins/workspace/workspace/RPMS_QAT/fed_rpms_4_dev_conf/cryptodev-2.6 -b master
print(command)
os.system(command)

list_patches = list()
print ("Patches :", len(QAT_PATCHES))
if len(QAT_PATCHES) >0:
    for patch in QAT_PATCHES:
        command = ('cd {0}/{1} && git format-patch -1 {2}').format(BD,QAT_SRC,patch)  #cd fed_rpms_4_dev_conf/cryptodev-2.6 && git format-patch -1 5ee52118ac14
        print(command)
        s = os.popen(command)
        o = s.read()
        print(o)  #0001-crypto-qat-expose-device-state-through-sysfs-for-4xx.patch
        (list_patches).append(o)
    print(list_patches)

    all_content = str()
    for i in list_patches:
        print("########################################################################################################")
        i = i.replace('\n','')
        print(i)
        command = ('./{0}/{1}/{2}').format(BD,QAT_SRC,i)
        print(command)
        print("########################################################################################################")
        with open(command) as f:  #./fed_rpms_4_dev_conf/cryptodev-2.6/0001-crypto-qat-change-behaviour-of-adf_cfg_add_key_value.patch
            content = f.read()
            all_content = all_content + content
    print("Patches: ", all_content)
    command =  ('./{0}/{1}').format(BD,FEDORA_PATCHES_FILE)   #./fed_rpms_4_dev_conf/linux-kernel-test.patch
    print (command)
    if os.path.exists(command):
        os.remove(command)  
    with open (command,'w') as f2:
        f2.write(all_content)

##############################################################################################################################

command = ('./{0}/{1}').format(BD,QAT_SRC)
if os.path.exists(command):
        pass
        #os.rmdir(command)

##############################################################################################################################

#clone fedora repo 

print("########################################################################################################")
print("Clone fedora repo ")
print("########################################################################################################")

command = ("rm -rf {0}/kernel").format(BD)
print(command)
os.system(command)
#command = ('cd ./{0} && fedpkg clone -a kernel').format(BD) #cd ./fed_rpms_4_dev_conf && fedpkg clone -a kernel
command = ('cd ./{0} && git config --global core.compression 0 && git clone https://src.fedoraproject.org/rpms/kernel.git kernel').format(BD) #cd ./fed_rpms_4_dev_conf && fedpkg clone -a kernel
print(command)
os.system(command)
pth = ('./{0}/kernel').format(BD)
print ("test repo",os.path.exists(pth))
if (os.path.exists(pth)) == True:
    print("Fedpkg OK")
else:
    print ("Problem with cloning Fedora repo")
    sys.exit(-1)




print("########################################################################################################")

print("Checkout branch repo")

command = ('cd ./{0}/{1} && git checkout {2}').format(BD,FEDORA_KERNEL_SRC,FEDORA_KERNEL_BRANCH) #cd ./fed_rpms_4_dev_conf/kernel && git checkout f36
print(command)
os.system(command)


print("########################################################################################################")

print("Install builddep kernel.spec")

command = ('cd ./{0}/{1} && sudo dnf -y builddep kernel.spec').format(BD,FEDORA_KERNEL_SRC) #cd ./fed_rpms_4_dev_conf/kernel && sudo dnf -y builddep kernel.spec
print(command)
os.system(command)


print("########################################################################################################")

#copy define from .local file to qat_custom (QAT_BUILD_TAG file)
print("Copy define from .local file to qat_custom (QAT_BUILD_TAG file)")


command = ('./{0}/{1}/kernel.spec').format(BD,FEDORA_KERNEL_SRC)  #./fed_rpms_4_dev_conf/kernel/kernel.spec
print(command)
str1 = '# define buildid .local'    
str2 = ("%define buildid {0}").format(QAT_BUILD_TAG)
print(str1,'-->',str2)   #define buildid .local --> %define buildid .0000\.qat_custom

with open (command) as file:
    kernel_spec_content = file.read()
    kernel_spec_content = kernel_spec_content.replace(str1, str2)
with open (command, 'w') as file:
    file.write(kernel_spec_content)

print("########################################################################################################")

print("Copy file with patches to fedora kernel")



command1 = ('./{0}/{1}').format(BD,FEDORA_PATCHES_FILE)     #./fed_rpms_4_dev_conf/linux-kernel-test.patch
command2 = ('./{0}/{1}/ ').format(BD,FEDORA_KERNEL_SRC)      #./fed_rpms_4_dev_conf/kernel/

if os.path.exists(command1):
    command = ('rm -rf ./{0}/{1}/{2}').format(BD,FEDORA_KERNEL_SRC,FEDORA_PATCHES_FILE)
    print(command)
    os.system(command)

    command3 = ('cp {0} {1}').format(command1,command2)    #cp ./fed_rpms_4_dev_conf/linux-kernel-test.patch ./fed_rpms_4_dev_conf/kernel/
    print(command3)
    os.system(command3)

    print("########################################################################################################")
    print("Cat patch file")
    command = ('cat ./{0}/{1}/{2}').format(BD,FEDORA_KERNEL_SRC,FEDORA_PATCHES_FILE)
    print(command)
    s = os.popen(command)
    output = s.read()
    print(output) 

print("########################################################################################################")

print("Build rpm files")

command = ('set -m && cd ./{0}/{1}/ && fedpkg local --define "_topdir {2}/{3}"').format(BD,FEDORA_KERNEL_SRC,WORKSPACE,RPMROOT)  # cd ./fed_rpms_4_dev_conf/kernel/ && fedpkg local
print(command)
s = os.popen(command)
o = s.read()
print(o)

print("########################################################################################################")

#copy rpm files to local http server - finally, copy rpm files to artifactory. 

now = datetime.now()
dt = now.strftime("%d_%m_%Y_%H.%M")
print(dt)


#temporary section
dest_folder = ('/var/www/html/{0}/').format(dt)
os.mkdir(dest_folder)

command = ('cp -r ./{0}/{1}/*.rpm {2}').format(BD,FEDORA_KERNEL_SRC,dest_folder)
print(command)
os.system(command)
command = ('cp -r ./{0}/{1}/x86_64/*.rpm {2}').format(BD,FEDORA_KERNEL_SRC,dest_folder)
print(command)
x = os.system(command)


if x == 0:
    message1 = ("http://10.102.16.187/{0}").format(dt)
    message2 = ("scp -r root@10.102.16.187:/var/lib/www/html/{0}/* .").format(dt)
    print(message1, message2)

command =  ('scp -r {0} root@10.102.16.187:/var/www/html/').format(dest_folder)
print(command)
os.system(command)

#temporary section end

#(jfrog rt upload ./{0}/{1}/*.rpm .any_folder).format(BD,FEDORA_KERNEL_SRC,dest_folder)
#(jfrog rt upload ./{0}/{1}/x86_64/*.rpm .any_folder).format(BD,FEDORA_KERNEL_SRC,dest_folder)

print('Built time: ',now - now_start)

print("########################################################################################################")