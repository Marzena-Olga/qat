#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This script prepare package to OneBKC.
# This script should be run as a Jenkins job
# Author: Marzena Kupniewska
# Maintainer: Marzena Kupniewska

import json
import os
from requests.auth import HTTPBasicAuth
import requests
import urllib3
import sys
import codecs
import base64


def split_jira_tickets(tickets=''):
    tickets_list = tickets.split(',')
    summary_return_attachment_list = list()
    for i in tickets_list:
        print(i)
        attachment_list = prepare_data(get_jira_ticket(i))
        for j in attachment_list:
            summary_return_attachment_list.append(j) 
    return summary_return_attachment_list

def get_jira_ticket(ticket=''):
    tok = user + ':' + password
    encoded_tok = base64.b64encode(tok.encode()).decode()
    headers = {'Content-Type': 'application/json', 'Authorization': 'Basic %s' % encoded_tok}
    proxy = {'http': '', 'https': ''}

    auth = HTTPBasicAuth(user, password)
    headers = {'Content-Type': 'application/json'}
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    url = ('https://jira.devtools.intel.com/rest/api/2/issue/{0}').format(ticket)
    #response = requests.get(url, verify=False, headers=headers, auth=auth)
    response = requests.get(url, headers=headers, proxies=proxy, verify=False, auth=auth)
    print('Return status code:', response.status_code)
    #print('Result:', response.json())
    #print(json.dumps(response.json(), indent=4, sort_keys=True))
    return response.json()

def prepare_data(response=''):
    #print('Result:', response)
    print('********************************************************************************************')
    print('Description:')
    print(response['fields']['description'])
    print('********************************************************************************************')
    print('Attachments:')
    print(response['fields']['attachment'])
    print('********************************************************************************************')
    attachment_list = (response['fields']['attachment'])
    return_attachment_list = list()
    for i in attachment_list:
        return_attachment_list.append(i['content'])
    return return_attachment_list

def make_package(ral=list(), package_name=str(), package_url=str()):
    package_name = package_name.lower()
    package_name = package_name.replace('.tar.gz', '')
    out_str = ("\\\\10.102.16.205\workspace\OneBKC_Package_Creator\{0}").format(package_name)
    #make directory structure
    try:
        os.system('rm -rf {0}').format(package_name)
    except:
        pass
    try:
        os.mkdir(package_name)
    except:
        pass
    path = os.path.join(package_name, package_name)
    try:
        os.mkdir(path)
    except:
        pass
    path = os.path.join(package_name, package_name, 'Reports')
    try:
        os.mkdir(path)
    except:
        pass
    print(os.getcwd())
    os.chdir(path)
    print(os.getcwd())

    #download klocwork/protex reports to Reports directory

    tok = user + ':' + password
    encoded_tok = base64.b64encode(tok.encode()).decode()
    headers = {'Content-Type': 'application/json', 'Authorization': 'Basic %s' % encoded_tok}
    proxy = {'http': '', 'https': ''}
    #r = requests.get(url, headers=headers, proxies=proxy, verify=False)
    
    auth = HTTPBasicAuth(user, password)
    for i in ral:
        print(i)
        pkg = i.split('/')
        print(pkg[-1])
        #r = requests.get(i, auth=auth, verify=False)
        r = requests.get(i, headers=headers, proxies=proxy, verify=False, auth=auth)
        open(pkg[-1], 'wb').write(r.content)

    #copy guides to folder ./package_name/package_name

    os.chdir('..')
    print(os.getcwd())
    os.system('copy ..\..\doc\*.* .')

    #download package from artifactory to ./package_name/package_name folder

    r = requests.get(package_url, auth=auth, verify=False)
    pkg = package_url.split('/')
    print(pkg[-1])
    #open(pkg[-1], 'wb').write(r.content)
    open(one_bkc_name, 'wb').write(r.content)

    #create zip package
    print(os.getcwd())
    zip_name = one_bkc_name.replace('.tar.gz', '.zip')
    #shutil.make_archive(zip_name, 'zip', '.')
    command = ('powershell Compress-Archive * {0} -Force').format(zip_name)
    os.system(command)
    command = ('move *.zip ..')
    os.system(command)

    #create json file with version = package_name

    os.chdir('..')
    print(os.getcwd())
    json_name = (one_bkc_name.replace('.tar.gz', '.json'))
    #os.system(('copy ..\json\*.* .\{0}').format(json_name))
    json_version = (one_bkc_name.replace('.tar.gz',''))

    data = {'metaDataComponents': [
        {"mainFile": "632506-0.9-intel-qat-getting-started-guide-v2.0.pdf", "fileType": "pdf", "type": "gettingStartedGuide"},
        {"mainFile": "632507-1.0.1-qat-software-for-linux-release-notes-hardware-v2.0.pdf", "fileType": "pdf", "type": "releaseNotes"},
        {"mainFile": "777577_ReleaseNotes_Addendum.pdf", "fileType": "pdf", "type": "releaseNotesAddendum"},
        {"mainFile": "Reports/*.xlsx", "type": "ipScanReport"},
        {"mainFile": "Reports/*.pdf", "type": "staticAnalysisReport"}],
    "name": "QAT",
    "version": json_version,
    "metaDataSchemaVersion": "1.0",
    "packageRevision": 0
    }

    #with open(r'.\{0}'.format(json_name)) as json_file:
     #   data = json.load(json_file)
      #  data['version'] = (json_name.replace('.json', ''))

    with open(json_name, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii = False, indent = 4)

    #\\10.102.16.205\workspace\OneBKC_Package_Creator\qat20.l.1.1.21-00030
    print("###########################################################################")
    print(out_str)
    print("###########################################################################")

if __name__ == '__main__':
    
    
    user = os.getenv('CREDS_USR')
    password = os.getenv('CREDS_PSW')
    #ticket = 'QPJN-57'
    #package_url = 'https://af01p-ir.devtools.intel.com/artifactory/scb-local/QAT_packages/QAT20/QAT20_1.1.21/QAT20.L.1.1.21-00030/QAT20.L.1.1.21-00030.tar.gz'
    #one_bkc_name = ('emr_po_QAT20.L.1.1.21-00030_internal_only.tar.gz').lower()

    tickets = os.getenv('JIRA_TICKETS')
    package_url = os.getenv('PACKAGE_LINK')
    one_bkc_name = os.getenv('PACKAGE_NAME')
    one_bkc_name=one_bkc_name.strip()

    print("*********************************************************************")
    print("env variables")
    print(tickets)
    print(package_url)
    print(one_bkc_name)
    print("*********************************************************************")
    
    print(tickets)
    print(package_url)

    if tickets is None:
        print("Tickets field is empty")
        sys.exit(-1)

    if package_url is None:
        print("Package URL is empty")
        sys.exit(-1)

    package_name = (package_url.split('/'))[-1]

    if one_bkc_name is None:
        one_bkc_name = package_name
    one_bkc_name = one_bkc_name.lower()

    
    print(package_name)
    print(one_bkc_name)



    #res = get_jira_ticket(tickets)
    #ral = prepare_data(res)
    ral = split_jira_tickets(tickets)
    print (ral)
    make_package(ral, package_name, package_url)




