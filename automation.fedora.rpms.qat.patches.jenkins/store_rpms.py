#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This script create RPM packages for Fedora Linux form tar.gz package.
# This script should be run as a Jenkins job
# Author: Marzena Kupniewska
# Maintainer: Marzena Kupniewska

__author__ = "Marzena Kupniewska"

"""
    Script for rpm package creation
"""


# Script store rpm files to local http server

import os
from datetime import datetime
import sys
import socket

print('*********************************** Start store RPMS script ****************************')

now = datetime.now()
dt = now.strftime("%d_%m_%Y_%H.%M")
print('Create folder',dt)

dest_folder = ('/var/www/html/{0}/').format(dt)
os.mkdir(dest_folder)

command = ('cp -r ./QAT/rpmbuild/RPMS/x86_64/*.rpm {0}').format(dest_folder)
print(command)
x = os.system(command)

hostname=socket.gethostname()
IPAddr=socket.gethostbyname(hostname)



if x == 0:
    message1 = ("http://{0}/{1}").format(IPAddr,dt)
    message2 = ("scp -r root@{0}:/var/lib/www/html/{1}/* .").format(IPAddr,dt)
    print(message1, 'or' ,message2)



print('*********************************** End store RPMS script ****************************')