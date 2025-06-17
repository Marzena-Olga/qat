#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This script change files retention policy.
# This script should be run as a Jenkins job
# Author: Marzena Kupniewska
# Maintainer: Marzena Kupniewska

import json
import os
from requests.auth import HTTPBasicAuth
from datetime import datetime
import sys
import requests

print('*********************************** Start change retention QAT packages ****************************')


def get_package(url_path, url_root):
    # print(url_path)  #https://af01p-ir.devtools.intel.com/ui/native/scb-local/QAT_packages/QAT19/QAT19_0.3.0/
    pth = url_path.split('/')
    pth = list(filter(None, pth))
    print(pth)  # ['https:', 'af01p-ir.devtools.intel.com', 'ui', 'native', 'scb-local', 'QAT_packages', 'QAT19', 'QAT19_0.3.0']
    reg = (pth[-1])  # QAT19_0.3.0
    # print(reg)
    reg1 = reg[0:3]  # QAT
    # print(reg1) #QAT
    reg1 = reg1 + '*.tar.gz'
    # print(reg1)  #QAT*.tar.gz
    reg4 = url_path.split(
        "scb-local/")  # ['https://af01p-ir.devtools.intel.com/ui/native/', 'QAT_packages/QAT19/QAT19_0.3.0/']
    reg3 = reg4[1]
    print('Search path: ', reg3)  # 'QAT_packages/QAT19/QAT19_0.3.0/'

    qry = json.dumps({
        "type":
            "file",
        "name": {"$match": reg1}  # QAT*.tar.gz  or QAT_UPSTREAM_MAIN.L.0.0.0-00736.tar.gz
        # "path": "QAT_packages/QAT18/QAT18_1.8.0/*"
    })

    DATA = "items.find({})".format(qry)
    print('Query:', DATA)  # items.find({"type": "file", "name": {"$match": "QAT*.tar.gz"}})
    response = requests.post('https://af01p-ir.devtools.intel.com/artifactory/api/search/aql',
                             auth=HTTPBasicAuth(ulogin, upassword), data=DATA)
    print('Response:', response.status_code)
    # print('Response from:', response.url)
    # print(response.json())
    li = (response.json()['results'])
    #print(json.dumps(response.json(), indent=4, sort_keys=True))
    li2 = list()
    for i in li:  # get files with correct path
        if i["path"].find(reg3) != -1:
            #print(i)
            li2.append(i)
    print("Items:", len(li2))
    return_list = list()
    for i in li2:  # get latest file
        print(url_root)
        print(i)
        return_list.append(i['name'])
    print ("******************************************************************************************************")
    return return_list

def change_retention(package_list=list()):
    print(package_list)

    for package in return_list:
        DATA = 'items.find({"type": "file", "name": {"$match": "'+package+'"}}).include("property.*")'
        print(DATA)
        response = requests.post('https://af01p-ir.devtools.intel.com/artifactory/api/search/aql', auth=HTTPBasicAuth(ulogin, upassword), data=DATA)
        print('Response:', response.status_code)
        #print(response.json())
        li = (response.json()['results'])
        #print(json.dumps(response.json(), indent=4, sort_keys=True))
        #print(li)
        print('***********************************************************************************************************')
        for i in li:
            #print(i)
            package_path = (i['path']+'/'+i['name'])
            print(package_path)
            #properties = i['properties']
            properties = list()
            try:
                properties = i['properties']
            except:
                pass
            if properties:
                retention = 730
                #print(retention)
                package_path = i['path'] +'/'+i['name']
                url = ('https://af01p-ir.devtools.intel.com/artifactory/api/storage/scb-local/{0}?properties=retention.days={1}').format(package_path, retention)
                print(url)
                response = requests.put(url, auth=HTTPBasicAuth(ulogin, upassword))
                print(response)
                #[{'key': 'build.name', 'value': 'QAT :: LIN :: GitLab :: QAT_UPSTREAM_PKG'}, {'key': 'vcs.url', 'value': 'ssh:/git@gitlab.devtools.intel.com:29418/QAT/osal'}, {'key': 'build.number', 'value': '4814'}, {'key': 'build.parentName', 'value': 'QAT :: LIN :: GitLab :: SAMPLE_USER :: config=QAT17_4.15.0,os=f22~64bit'}, {'key': 'build.timestamp', 'value': '1631361073579'}, {'key': 'vcs.revision', 'value': '1c5c04b78c5045bd486a2c39daf087e943bc8947'}, {'key': 'retention.days', 'value': '3652'}, {'key': 'build.parentNumber', 'value': '5923'}]
                properties = [{'key': 'retention.days', 'value': retention}]
        print(properties)
        for j in properties:
            if j['key'] == 'retention.days':
                #print(j['value'])
                check_retention = int(j['value'])
        print("Current retention:", check_retention)

        print('***********************************************************************************************************')
        if check_retention < retention:
            url = ('https://af01p-ir.devtools.intel.com/artifactory/api/storage/scb-local/{0}?properties=retention.days={1}').format(package_path, retention)
            print(url)
            response = requests.put(url, auth=HTTPBasicAuth(ulogin, upassword))
            print(response)

            response = requests.post('https://af01p-ir.devtools.intel.com/artifactory/api/search/aql', auth=HTTPBasicAuth(ulogin, upassword), data=DATA)
            print('Response:', response.status_code)
            # print(response.json())
            li = (response.json()['results'])
            # print(json.dumps(response.json(), indent=4, sort_keys=True))
            # print(li)
            print('***********************************************************************************************************')
            for i in li:
                # print(i)
                properties = i['properties']
            for j in properties:
                if j['key'] == 'retention.days':
                    check_retention = int(j['value'])
            print("New retention:", check_retention)
            print('***********************************************************************************************************')


#params

retention = os.getenv('RETENTION')
if retention is None:
    retention = 730 #(two years)

WORKDIR = os.getenv('WORKSPACE')
print(WORKDIR)
ulogin = os.getenv('CREDS_USR')
upassword = os.getenv('CREDS_PSW')

url_path_list = [
    #'https://af01p-ir.devtools.intel.com/artifactory/scb-local/QAT_packages/QAT17/',
    'https://af01p-ir.devtools.intel.com/artifactory/scb-local/QAT_packages/QAT18/',
    'https://af01p-ir.devtools.intel.com/artifactory/scb-local/QAT_packages/QAT21/',
    'https://af01p-ir.devtools.intel.com/artifactory/scb-local/QAT_packages/QAT20/',
    'https://af01p-ir.devtools.intel.com/artifactory/scb-local/QAT_packages/QAT22/',
    'https://af01p-ir.devtools.intel.com/artifactory/scb-local/QAT_packages/QAT19/'
]

url_path = os.getenv('URL_PATH')
url_root = os.getenv('URL_ROOT')

if url_root is None:
   url_root = 'https://af01p-ir.devtools.intel.com/artifactory/scb-local/'

print(url_root)

#temporary params

#url_path = 'https://af01p-ir.devtools.intel.com/artifactory/scb-local/QAT_packages/QAT18/'
#url_path = 'https://af01p-ir.devtools.intel.com/artifactory/scb-local/QAT_packages/QAT20/'

if url_path is None:
    print ("Change retention from url list")
    print(url_path_list)
    for i in url_path_list:
        url_path = i
        #print(url_path)
        return_list= get_package(url_path, url_root)
        change_retention(return_list)
else:
    return_list = get_package(url_path, url_root)
    change_retention(return_list)

