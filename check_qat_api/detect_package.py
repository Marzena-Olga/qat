#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This script search package by tag in artifactory.
# This script should be run as a Jenkins job
# Author: Marzena Kupniewska
# Maintainer: Marzena Kupniewska

import urllib3
import requests
import json
import re
import os
from requests.auth import HTTPBasicAuth
import sys



def find_arftifactory_property():
    ar_path = 'https://af01p-ir.devtools.intel.com/artifactory/scb-local/'  #general artifactory/repository adress - prefix for packages
    DATA = 'items.find({"type": "file", "name": {"$match": "QAT_UPSTREAM*.tar.gz"}}).include("property.*")'   #query to aql to search QAT_UPSTREAM*.tar.gz  files 
    print(DATA)
    response = requests.post('https://af01p-ir.devtools.intel.com/artifactory/api/search/aql',   #RestApi artifactory query
                             auth=HTTPBasicAuth(ulogin, upassword), data=DATA)
    print(response.status_code)
    #print(response.url)
    li = (response.json()['results'])   #list of dictionaries with package information
    #print(json.dumps(response.json(), indent=4, sort_keys=True))
    #print(li)
    print('Search release packages:')
    res_list = list()
    for i in li:
        #print(i['path'] +'/'+i['name'])
        j = i['properties']  #get list properties from dictionary
        for k in j:
            #print(k)
            #print(k['key'])
            if k['key'] == 'tag' and (k['value']).find('Release_') != -1:   #search "tag" propertie with "Released" value
                print("Package:", i['path'] +'/'+i['name'])
                print("Tag:", k['value'])
                res_list.append(i)   #add to list, dictionary with "tag" propertie
    res_list2 = (sorted(res_list, key=lambda x: x['created']))  #sort list by create date - desc
    for i in res_list2:
        print(ar_path + i['path'] + '/' + i['name'])
        print("Created:", i['created'])
        env_str = (ar_path + i['path'] + '/' + i['name'])   # Prepare string with package address 
    
    #print("Set: RELEASE_PACKAGE =", env_str)  
    #os.environ["RELEASE_PACKAGE"] = env_str  #create environment variable with package address
    return env_str

def get_last_artifactory_package():
    ar_path = 'https://af01p-ir.devtools.intel.com/artifactory/scb-local/'
    DATA = 'items.find({"type": "file", "name": {"$match": "QAT_*.tar.gz"}})'
    print(DATA)
    response = requests.post('https://af01p-ir.devtools.intel.com/artifactory/api/search/aql',
                             auth=HTTPBasicAuth(ulogin, upassword), data=DATA)
    print(response.status_code)
    #print(response.url)
    li = (response.json()['results'])
    package_list = list()

    for i in li:
        if i['path'].find('QAT_packages/QAT_U') != -1:
            #print(i['path']+'/'+i['name'])
            package_list.append(i)

    sorted_package_list = (sorted(package_list, key=lambda x: x['created']))
    for i in sorted_package_list:
        #print(i['path']+'/'+i['name'], i['created'])
        last_element = i['path']+'/'+i['name']
        last_path = i['path']
    env_str  = ar_path + '/' + last_element
    print(env_str )
    dest_place = 'scb-local/'+ last_path +'/Collaterals'
    print("#########place######################################")
    print(dest_place)
    print("###############################################")
    os.environ["ABI_REPORTS"] = dest_place
    try:
        os.remove('path.txt')
    except:
        print('No path file')
    with open('path.txt','w') as file:
        file.write(dest_place)

    #print("Set: CHECK_PACKAGE =", env_str)  
    #os.environ["CHECK_PACKAGE"] = env_str   #create environment variable with package address
    #print('###########################################')
    #print(os.getenv('ABI_REPORTS'))
    #print('###########################################')
    return env_str 

def find_package_path(pkg=str()):
    print(pkg)
    ar_path = 'https://af01p-ir.devtools.intel.com/artifactory/scb-local/'
    qry = {"type": "file", "name": {"$match": pkg}}
    qry2 = json.dumps(qry)
    DATA = "items.find({})".format(qry2)
    print(DATA)
    response = requests.post('https://af01p-ir.devtools.intel.com/artifactory/api/search/aql',
                             auth=HTTPBasicAuth(ulogin, upassword), data=DATA)
    print(response.status_code)
    #print(response.url)
    li = (response.json()['results'])
    print(li)
    #print(len(li))
    if (len(li)) == 1:
        return_path = ar_path + li[0]['path'] + '/' + li[0]['name']
        print("Found package", return_path)
        try:
            os.remove('path.txt')
        except:
            print('No path file')
        dest_place = 'scb-local/'+ li[0]['path'] +'/Collaterals'
        with open('path.txt','w') as file:
            file.write(dest_place)

        return return_path
    else:
        print("Package not found")
        sys.exit(-1)



def choice_package():
    release_package = os.getenv('RELEASE_PACKAGE')
    package_to_check = os.getenv('PACKAGE_TO_CHECK')


    if release_package is None:
        release_package = find_arftifactory_property()
    else:
        release_package = release_package.strip()
        release_package = find_package_path(release_package) 

    os.environ["RELEASE_PACKAGE"] = release_package

    if package_to_check is None:
        package_to_check = get_last_artifactory_package()
    else:
        package_to_check = package_to_check.strip()
        package_to_check = find_package_path(package_to_check)

    os.environ["CHECK_PACKAGE"] = package_to_check

    command = ('chmod +x ./check_abi.sh && ./check_abi.sh {0} {1}').format(release_package, package_to_check)
    print(command)
    os.system(command)



if __name__ == '__main__':
    ulogin = os.getenv('CREDS_USR')
    upassword = os.getenv('CREDS_PSW')
    choice_package()
    print('###########################################*###########################################')
    print("Save reports:", os.getenv('ABI_REPORTS'))
    print('###########################################*###########################################')

    #release_env_str = find_arftifactory_property()
    #check_env_str  = get_last_artifactory_package()
    #env_str = 'https://af01p-ir.devtools.intel.com/artifactory/scb-local/QAT_packages/QAT_U/QAT_UPSTREAM_23.08.0/QAT_UPSTREAM_23.08.0.L.0.0.0-00017/QAT_UPSTREAM_23.08.0.L.0.0.0-00017.tar.gz'
    #command = ('chmod +x ./check_abi.sh && ./check_abi.sh {0} {1}').format(release_env_str, check_env_str)
    #os.system(command)
