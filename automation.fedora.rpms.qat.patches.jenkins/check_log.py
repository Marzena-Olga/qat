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


import os
import sys


print('######################################## Start log analize script #############################################################################################################')


with open('./QAT/make.log', 'r') as make_log_file:
    make_log = make_log_file.read()
print('Open ./QAT/make.log file')
make_log_list = (make_log).split('\n')
errors = 0
warnings = 0
errors_list = list()
warnings_list = list()

#print('##################################### Start log #################################################################################################################')
for i in make_log_list:
    #print(make_log_list.index(i),':', i)
    if  i.find(' Error:') != -1 or i.find(' ERROR:') != -1 or i.find(' error:') != -1:
                errors = errors +1
                stre = str(make_log_list.index(i)) + ':' + i
                errors_list.append(stre)
    if i.find(' Warning:') != -1 or i.find(' WARNING:') != -1 or i.find(' warning:') != -1:
                warnings = warnings +1
                strw = str(make_log_list.index(i)) + ':' + i
                warnings_list.append(strw)
#print('######################################## End log ###############################################################################################################')






print('Errors&Warnings:')
print('Errors:', errors)
print('Warnings:', warnings)

if errors >0:
    print('####################### List errors ###########################################################################################################################################')
    for i in errors_list:
        print(i)

if warnings >0:
    print('####################### List warnings #########################################################################################################################################')    
    for i in warnings_list:
        print(i)

print('######################################## End log analize script ###############################################################################################################')



ignore_warnings = os.getenv('IGNORE_WARNINGS')
#print (ignore_warnings)

if ignore_warnings == 'true':
    errors = 0
    warnings = 0


if errors >0 or warnings >0:
    sys.exit(-1)
else:
    sys.exit(0)
