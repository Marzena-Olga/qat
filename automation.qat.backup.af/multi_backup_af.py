
import json
import os
from requests.auth import HTTPBasicAuth
from datetime import datetime
import sys
import requests

print('*********************************** Start backup QAT packages ****************************')


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

    print('**********************************************************')
    WORKDIR = os.getenv('WORKSPACE')
    print(WORKDIR)
    ulogin = os.getenv('CREDS_USR')
    # print(ulogin)
    upassword = os.getenv('CREDS_PSW')
    # print(upassword)
    print('**********************************************************')



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
    # print(json.dumps(response.json(), indent=4, sort_keys=True))
    li2 = list()

    for i in li:  # get files with correct path
        if i["path"].find(reg3) != -1:
            # print(i)
            li2.append(i)
    print("Items:", len(li2))
    z = dict()
    result_list = list()
    for i in li2:  # get latest file
        print(url_root)
        print(i)
        z['path'] = url_root + i['path'] + '/' + i['name']
        z['name'] = i['name']
        #print(z)
        result_list.append(z.copy())

    #for i in result_list:
        #print(i)
    return result_list


def make_dir(result_li, root_path):
    check = os.path.exists(root_path)
    if check == False:
        os.mkdir(root_path)
    for i in result_li:
        folder_list = (i['path']).split('/')
        #print(folder_list)
        folder_list.remove('https:')
        folder_list.remove('')
        folder_list.remove('af01p-ir.devtools.intel.com')
        folder_list.remove('artifactory')
        folder_list.remove('scb-local')
        #print(folder_list)
        folder_list.pop()
        #print(folder_list)
        arti_path = root_path
        for j in folder_list:
            arti_path = arti_path + '/' + j
            #print(arti_path)
            check = os.path.exists(arti_path)
            #print(check)
            if check is False:
                os.mkdir(arti_path)
        file_path = (arti_path + '/' + i['name'])
        #print(file_path)
        check = os.path.isfile(file_path)
        #print(check)
        if check is False:
            print('Create folder:', arti_path)
            command = ('curl {0} --output {1}/{2}').format(i['path'], arti_path, i['name'])
            print("Execute command:", command)
            os.system(command)


#params

url_path_list = [
    'https://af01p-ir.devtools.intel.com/artifactory/scb-local/QAT_packages/QAT17/',
    'https://af01p-ir.devtools.intel.com/artifactory/scb-local/QAT_packages/QAT18/',
    'https://af01p-ir.devtools.intel.com/artifactory/scb-local/QAT_packages/QAT21/',
    'https://af01p-ir.devtools.intel.com/artifactory/scb-local/QAT_packages/QAT20/',
    'https://af01p-ir.devtools.intel.com/artifactory/scb-local/QAT_packages/QAT22/',
    'https://af01p-ir.devtools.intel.com/artifactory/scb-local/QAT_packages/QAT19/'
]

arti_path = os.getenv('ARTI_PATH')
url_path = os.getenv('URL_PATH')
url_root = os.getenv('URL_ROOT')

if arti_path is None:
    arti_path = '/qat'

if url_root is None:
   url_root = 'https://af01p-ir.devtools.intel.com/artifactory/scb-local/'  

print(url_root)

#temporary params

#url_path = 'https://af01p-ir.devtools.intel.com/artifactory/scb-local/QAT_packages/QAT18/'
#url_path = 'https://af01p-ir.devtools.intel.com/artifactory/scb-local/QAT_packages/QAT20/'



if url_path is None:
    print ("Run backup from list")
    print(url_path_list)
    for i in url_path_list:
        url_path = i
        print(url_path)
        result_li = get_package(url_path, url_root)
        make_dir(result_li, arti_path)
else:
    result_li = get_package(url_path, url_root)
    make_dir(result_li, arti_path)





