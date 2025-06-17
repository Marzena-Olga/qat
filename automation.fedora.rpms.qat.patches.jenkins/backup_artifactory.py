#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This script create RPM packages for Fedora Linux form tar.gz package.
# This script should be run as a Jenkins job
# Author: Marzena Kupniewska
# Maintainer: Marzena Kupniewska

__author__ = "Marzena Kupniewska"

"""
    Script for rpm package backup
"""

import json
import os
from requests.auth import HTTPBasicAuth
from datetime import datetime
import sys
import requests


print('*********************************** Start create RPMS script ****************************')

#url_path = ('https://af01p-ir.devtools.intel.com/ui/native/scb-local/QAT_packages/QAT_U/QAT_UPSTREAM_MAIN/')

def get_package(url_path, http_file=''):
    #print(url_path)  #https://af01p-ir.devtools.intel.com/ui/native/scb-local/QAT_packages/QAT19/QAT19_0.3.0/
    pth = url_path.split('/') 
    pth = list(filter(None, pth))
    print(pth)  #['https:', 'af01p-ir.devtools.intel.com', 'ui', 'native', 'scb-local', 'QAT_packages', 'QAT19', 'QAT19_0.3.0']
    reg = (pth[-1]) #QAT19_0.3.0
    #print(reg)
    reg1 = reg[0:3]  #QAT
    #print(reg1) #QAT
    reg1 = reg1 + '*.tar.gz'
    #print(reg1)  #QAT*.tar.gz
    reg4 = url_path.split("scb-local/")  #['https://af01p-ir.devtools.intel.com/ui/native/', 'QAT_packages/QAT19/QAT19_0.3.0/']
    reg3 = reg4[1] 
    print('Search path: ',reg3) #'QAT_packages/QAT19/QAT19_0.3.0/'
    if http_file != '':
        reg1 = http_file
    print('Search: ',reg1) #QAT_UPSTREAM_MAIN.L.0.0.0-00736.tar.gz

    
    #print('**********************************************************')
    WORKDIR = os.getenv('WORKSPACE')
    #print(WORKDIR)
    ulogin = os.getenv('CREDS_USR')
    #print(ulogin)
    upassword = os.getenv('CREDS_PSW')
    #print(upassword)
    #print('**********************************************************')


    qry = json.dumps({
          "type":
            "file",
            "name": {"$match": reg1}  #QAT*.tar.gz  or QAT_UPSTREAM_MAIN.L.0.0.0-00736.tar.gz
            #"path": "QAT_packages/QAT18/QAT18_1.8.0/*"
        })

    DATA = "items.find({})".format(qry)
    print('Query:', DATA) #items.find({"type": "file", "name": {"$match": "QAT*.tar.gz"}})
    response = requests.post('https://af01p-ir.devtools.intel.com/artifactory/api/search/aql', auth=HTTPBasicAuth (ulogin, upassword), data=DATA)
    print('Response:',response.status_code)
    #print('Response from:', response.url)
    #print(response.json())
    li = (response.json()['results'])
    #print(json.dumps(response.json(), indent=4, sort_keys=True))
    d1 = d2 = ''
    result = dict()
    li2 = list()

    for i in li:            #get files with correct path
        if i["path"].find(reg3) != -1:
            #print(i)
            li2.append(i)
    
    for i in li2:        #get latest file
        #print(i['created'])
        d1 = i['created']
        #print(d1, d2)
        if d1 >= d2:
            #print(i)
            result = i
        d2 = d1
    #print(result)

    res = 'https://af01p-ir.devtools.intel.com/artifactory/scb-local/' + result['path'] +'/'+ result['name']
    res2 = dict()
    res2['http_url']='https://af01p-ir.devtools.intel.com/artifactory/scb-local/' + result['path'] + '/'
    res2['http_file']=result['name']
    #https://af01p-ir.devtools.intel.com/artifactory/scb-local/QAT_packages/QAT18/QAT18_1.8.0/QAT18.L.1.8.0-00006/QAT18.L.1.8.0-00006.tar.gz
    print('Found package:',res)
    print('Return value:', res2) #{'http_url': 'https://af01p-ir.devtools.intel.com/artifactory/scb-local/QAT_packages/QAT17/QAT17_MAIN/QAT1.7_DEV.L.0.0.0-04790', 'http_file': 'QAT1.7_DEV.L.0.0.0-04790.tar.gz'}
    return res2
   

http_url = os.getenv('PACKAGE_PATH')
http_file = os.getenv('PACKAGE')

print ('env variables:', http_url, http_url)


if ((http_file is None) and (http_url is None)):
    #print("cond 1")
    http_file_k = ''
    #http_url_k= ('https://af01p-ir.devtools.intel.com/ui/native/scb-local/QAT_packages/QAT_U/QAT_UPSTREAM_MAIN/')
    http_url_k = ('https://af01p-ir.devtools.intel.com/ui/native/scb-local/QAT_packages/QAT_U/')
    url_path = http_url_k 
    print(http_url_k + '/' + http_file_k)
    result = get_package(url_path)
    http_url_k = result['http_url'] 
    http_file_k = result['http_file']

if ((http_file is not None) and (http_url is None)):
    #print("cond 2")
    http_file_k = http_file
    http_url_k = ('https://af01p-ir.devtools.intel.com/ui/native/scb-local/QAT_packages/QAT_U/')
    url_path = http_url_k
    print(http_url_k + '/' + http_file_k)
    result = get_package(url_path,http_file_k)
    http_url_k = result['http_url'] 
    http_file_k = result['http_file']

if ((http_file is None) and (http_url is not None)):
    #print("cond 3")
    http_file_k = ''
    http_url_k = http_url
    url_path = http_url_k
    print(http_url_k + '/' + http_file_k)
    result = get_package(url_path)
    http_url_k = result['http_url'] 
    http_file_k = result['http_file']

if ((http_file is not None) and (http_url is not None)):
    #print("cond 4")
    http_file_k = http_file
    http_url_k = http_url
    url_path = http_url_k
    result = get_package(url_path,http_file_k)
    http_url_k = result['http_url'] 
    http_file_k = result['http_file']
    print(http_url_k + '/' + http_file_k)



download_url = http_url_k + '/' + http_file_k
print('Download URL:',download_url)

