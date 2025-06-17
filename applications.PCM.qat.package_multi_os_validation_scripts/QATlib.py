# library file

from posixpath import split
import paramiko
import json
import os
import subprocess
import time
import glob
from typing import OrderedDict
import urllib
from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth
import datetime
from datetime import datetime
import sys
from shutil import which
import requests
from joblib import Parallel, delayed


#########################################################################################
#start vms functions

def get_vms():  #get all data from json file and return dictionary
    with open(r'./config/VM_OS_list.json') as json_file:
        data = json.load(json_file)
    return data 

def host_list(z=''):  #get dictionary and return list of host
    li = list()
    for p in z:
        li.append(p['NAME'])
    return li

def run_vm(li = []): #get list of host and start vm-s
    print(li)
    subprocess.call(["virsh", "list", "--all"])
    for i in li:
        subprocess.call(["virsh", "start", i])
    subprocess.call(["virsh", "list", "--all"])

def run_vm_esxi(li = []): #get list of host and start vm-s
    print(li)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    esxi = '10.102.16.150'
    try:
        ssh.connect(esxi, 22)
        for i in li:
            print(i)
            command = ("vim-cmd vmsvc/getallvms | grep {}").format(i)
            #print(command)
            stdin, stdout, stderr = ssh.exec_command(command)
            lines = stdout.readlines()
            #print(lines)
            z = (lines[0]).split()
            print(z[0])
            command2 = 'vim-cmd vmsvc/power.on {}'.format(z[0])
            stdin, stdout, stderr = ssh.exec_command(command2)
            lines = stdout.readlines()
            print(lines)
    
    except:
        print(esxi, ' No SSH connection  ')
    
    finally:
        if ssh:
            ssh.close()

#########################################################################################
#shutdows vms functions

def list_running_vms(): #get list running vms
    li = os.popen("virsh list --all").read()
    li2 = list()
    z = list()
    li = li.split('\n')
    for i in li:
        #print(i)
        li2.append(i.split())
    li2.pop(0)
    li2.pop(0) 
    li2.pop(-1) 
    li2.pop(-1)
    for i in li2:
        #print(i[1])
        if (i[2]) == 'running':
            z.append(i[1])
    #print(z)
    return z

def stop_vm(z = list()): #shutdown running vms and second step: poweroff running vms
    for i in z:
        subprocess.call(["virsh", "shutdown",i])
    time.sleep(60)
    z = list_running_vms()
    if z != []:
        for i in z:
            subprocess.call(["virsh", "destroy",i])  
        time.sleep(60)
    subprocess.call(["virsh", "list", "--all"])

#########################################################################################
#select and get packages from arifactory functions

def get_cred(): #get credentials form json file for generic account
    # with open('./config/pstore.json') as json_file:
    #     data = json.load(json_file)
    #     for p in data['ar_creds']:
    #         login = p['login']
    #         passwd = p['pass']
    #print('**********************************************************')
    WORKDIR = os.getenv('WORKSPACE')
    #print(WORKDIR)
    login = os.getenv('CREDS_USR')
    #print(ulogin)
    passwd = os.getenv('CREDS_PSW')
    #print(upassword)
    #print('**********************************************************')
    ret = dict()
    ret[login] = passwd
    return(ret)

def set_html_cred(cred = dict(), url_path = ''): #login to http session
    login = (list(cred.keys())[0])
    passwd = (list(cred.values())[0])
    password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    top_level_url = "https://af01p-ir.devtools.intel.com/artifactory/"
    password_mgr.add_password(None, top_level_url, login, passwd)
    h = urllib.request.HTTPBasicAuthHandler(password_mgr)
    opener = urllib.request.build_opener(h)
    opener.open(url_path)
    urllib.request.install_opener(opener)
    
    co = 0
    cz = 0
    #print(co)
    while co != 1:
        try:
            err = urllib.request.urlopen(top_level_url).read()
            co = 1
            time.sleep(5)
        except:
            print('Error Artifactory connection')
            cz = cz + 1
            if cz >0:
                co = 0
        #print(err)
        if cz == 9: sys.exit('Problem with Artifactory connection')



def get_html_packages(url_path = ''): #get directory content, select and return dictionary with directories and datetime, 
    #html_page = urllib.request.urlopen(url_path)
    patch_data=dict()
    up = url_path+'?lastModified'
    with open('./config/pstore.json') as json_file:
        data = json.load(json_file)
        for p in data['ar_creds']:
            api_key = p['apikey']
    art_api = 'X-JFrog-Art-Api:'+api_key
    print(up)
    cmd_curl = "curl -H {} -X GET {}?lastModified".format(art_api, str(url_path))
    print(cmd_curl)
    p = os.popen(cmd_curl)
    #print(p.read())
    z = p.read()
    #print(type(z))
    soup = BeautifulSoup(z, "html.parser")
    #print(soup)
    z_dict = json.loads(z)
    err = z_dict['errors']
    #print(err[0]['status'])
    if (err[0]['status']) > 300:
        print(err)
        sys.exit("Artifactory access problem, http status {}".format(err[0]['status']))
    #print(json.dumps(z_json, indent=4, sort_keys=True))
    #print("#####################################################################################")
    max = ([url_path + node.get('href') for node in soup.find_all('a') if node.get('href').endswith('')])
    max2 = ([node.get('href') for node in soup.find_all('a') if node.get('href').endswith('')])
    soup_string = str(soup)
    soup_li = soup_string.split()
    #print("########################################################################################################")
    for i in max2:
        for j in soup_li:
            if j.find(i) != -1:
                klucz = str(soup_li[(soup_li.index(j)+1)] + ' ' + soup_li[(soup_li.index(j)+2)]) 
                print(klucz)
                patch_data[klucz] = max[max2.index(i)]  
    
    print((list(patch_data.keys())[0]))
    patch_data.pop(list(patch_data.keys())[0])
    #print(patch_data)
    return patch_data

def select_html_package (patch_data = dict()):  #select newest directory by datetime and return dictionary with path to file and name file
    daty = OrderedDict()
    for k in patch_data:
        #03-Jun-2021 12:17
        pom = datetime.datetime.strptime(k, '%d-%b-%Y %H:%M')
        daty[pom] = k
    w = (list(daty.values()))
    v = (list(daty.keys()))
    pom2 = v[0]
    for g in v:
        if (pom2 < g) == True:
            pom2 = g
    dt = (daty[pom2])        
    file_url=(patch_data[dt])
    #data = urllib.request.urlopen(file_url).read()
    ##############################################
    api_key = ''
    art_api = 'X-JFrog-Art-Api:'+api_key
    cmd_curl = "curl -H {} -X GET {}?lastModified".format(art_api, str(file_url))
    print(cmd_curl)
    p = os.popen(cmd_curl)
    #print(p.read())
    z = p.read()
    soup = BeautifulSoup(z, "html.parser")

    ##############################################
    #soup = BeautifulSoup(data, 'html.parser')
    max = [node.get('href') for node in soup.find_all('a') if node.get('href').endswith('.tar.gz')]
    res = dict()
    res['http_url']=file_url
    res['http_file']=max[0]       
    return res

def get_package(url_path):
    print(url_path)  #https://af01p-ir.devtools.intel.com/ui/native/scb-local/QAT_packages/QAT19/QAT19_0.3.0/
    pth = url_path.split('/') 
    pth = list(filter(None, pth))
    print(pth)  #['https:', 'af01p-ir.devtools.intel.com', 'ui', 'native', 'scb-local', 'QAT_packages', 'QAT19', 'QAT19_0.3.0']
    reg = (pth[-1]) #QAT19_0.3.0
    print(reg)
    reg1 = reg[0:3]  #QAT
    print(reg1) #QAT
    reg1 = reg1 + '*.tar.gz'
    print(reg1)  #QAT*.tar.gz
    reg4 = url_path.split("scb-local/")  #['https://af01p-ir.devtools.intel.com/ui/native/', 'QAT_packages/QAT19/QAT19_0.3.0/']
    reg3 = reg4[1] 
    print(reg3) #'QAT_packages/QAT19/QAT19_0.3.0/'
    
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
            "name": {"$match": reg1}
            #"path": "QAT_packages/QAT18/QAT18_1.8.0/*"
        })

    DATA = "items.find({})".format(qry)
    print(DATA) #items.find({"type": "file", "name": {"$match": "QAT*.tar.gz"}})
    response = requests.post('https://af01p-ir.devtools.intel.com/artifactory/api/search/aql', auth=HTTPBasicAuth (ulogin, upassword), data=DATA)
    print(response.status_code)
    print(response.url)
    #print(response.json())
    li = (response.json()['results'])
    #print(json.dumps(response.json(), indent=4, sort_keys=True))
    d1 = d2 = ''
    li2 = list()
    for i in li:
        if i["path"].find(reg3) != -1:
            #print(i)
            li2.append(i)

    for i in li2:
        #print(i['created'])
        d1 = i['created']
        #print(d1, d2)
        if d1 >= d2:
            #print(i)
            result = i
        d2 = d1
    print(result)
    res = 'https://af01p-ir.devtools.intel.com/artifactory/scb-local/' + result['path'] +'/'+ result['name']
    res2 = dict()
    res2['http_url']='https://af01p-ir.devtools.intel.com/artifactory/scb-local/' + result['path'] + '/'
    res2['http_file']=result['name']
    #https://af01p-ir.devtools.intel.com/artifactory/scb-local/QAT_packages/QAT18/QAT18_1.8.0/QAT18.L.1.8.0-00006/QAT18.L.1.8.0-00006.tar.gz
    print(res)
    print(res2) #{'http_url': 'https://af01p-ir.devtools.intel.com/artifactory/scb-local/QAT_packages/QAT17/QAT17_MAIN/QAT1.7_DEV.L.0.0.0-04790', 'http_file': 'QAT1.7_DEV.L.0.0.0-04790.tar.gz'}
    return res2


def download_package(res = dict()): #delete other files in pkg directory and download newest package 
    print('tgt:',res)
    art_path = res['http_url']
    art_file = res['http_file']
    art_path = art_path.replace('https://af01p-ir.devtools.intel.com/artifactory/', '')
    print(art_path)
    print(art_file)
    #test = "jfrog rt dl scb-local/QAT_packages/QAT18/QAT18_MAIN/QAT18_MAIN.L.0.0.0-00213/QAT18_MAIN.L.0.0.0-00213.tar.gz ."
    command = "jfrog rt dl {}{}".format(art_path,art_file)
    print(command)
    os.system(command)
    local_pth = art_path.replace('scb-local/', '')
    if (os.path.isdir('./pkg'))  != True:
        os.mkdir('./pkg')
    if (os.path.isdir('./data'))  != True:
        os.mkdir('./data')
    file_list = os.listdir('./pkg/')
    #print(file_list)
    for f in file_list:
        os.remove('./pkg/'+f) 
    command2 = "mv ./{}{} ./pkg/".format(local_pth,art_file)  
    print(command2)
    os.system(command2)

#########################################################################################
#select and send packages from local directory to VMs

def get_file():  #get newest file
    list_of_files = glob.glob('./pkg/*.tar.gz')
    latest_file = max(list_of_files, key=os.path.getctime)
    latest_file = latest_file.replace('./pkg/', '')
    return latest_file

def ip_list(z = ''): #create list with VMs IP
    li = list()
    for p in z:
        #print(p['IP'])
        li.append(p['IP'])
    return li

def send_package(lt_file = '', ip_host_list = ''):  #copy selected file to VMs
    lt_file2 = "./pkg/{}".format(str(lt_file))
    for hname in ip_host_list:
        print('copy', lt_file2, 'to ', hname)
        subprocess.call(["scp","-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null", lt_file2, hname+':/root/'])

#########################################################################################
#decompress packages on VMs

def decompress_package(lt_file = '', ip_host_list = ''): #decompress package on VMs
    ssh =paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    command = "rm -rf /QAT && mkdir /QAT" 
    command2 = "tar -zxf /root/"+lt_file +" -C /QAT/"   
     
    for h in ip_host_list:
        try:
            print(h)
            ssh.connect(h, 22)
            stdin, stdout, stderr = ssh.exec_command(command)
            lines = stdout.readlines()
            #print(lines)
            print(command2) 
            stdin, stdout, stderr = ssh.exec_command(command2)
            lines = stdout.readlines()
            #print(lines)
        except:
            print(h, ' No SSH connection  ')

#########################################################################################
#configure, make package on VMs

def build_package(vms = ''):
    file_list = os.listdir('./data/')
    print(file_list)
    for f in file_list:
        os.remove('./data/'+f)    

    host_list=list()
    for js in vms:
        h = js['IP']
        n = js['NAME']
        print(h, n)
        host_list.append([h,n])
        #build_package_single_machine([h, n])
    #print("Host list:", host_list)
    now = datetime.now()
    print(now)
    #for i in host_list:
    #    build_package_single_machine(i)

    Parallel(n_jobs=20)(delayed(build_package_single_machine)(i) for i in host_list)
    
    now_end = datetime.now()
    print("************************************")
    print('Configure&make time:', now_end - now)
    print("************************************")

def build_package_single_machine(h_n=list()):
    kernel_log = list()
    configure_log = list()
    make_log = list()
    ssh =paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    h=h_n[0]
    n=h_n[1]


    try:
        ssh.connect(h, 22)
        print("Connection to :", h)
            
        c = ("Configure {}").format(h)
        print(h, c)
        command = ("cd /QAT && ./configure  2>&1 | tee /tmp/{}_configure.log && echo $?").format(n)
        print(h, "Configure commnad: ", command)
        stdin, stdout, stderr = ssh.exec_command(command)
        configure_log = stdout.readlines()
        print(h, "Exit code: ", configure_log[-1])
            
        c = ("Make {}").format(h)
        print(h, c)
        command2 = ("cd /QAT && make -j4 2>&1 && echo $?| tee /tmp/{}_make.log").format(n)
        print(h, "Make command: ", command2)
        stdin, stdout, stderr = ssh.exec_command(command2)
        make_log = stdout.readlines()
        print(h, "Exit code: ", make_log[-1])
            
        #command6 = "echo $?"
        #stdin, stdout, stderr = ssh.exec_command(command6)
        #lines = stdout.read()
        #print(lines)
        #kernel_log.append(lines)

        command3 = "uname -r"
        stdin, stdout, stderr = ssh.exec_command(command3)
        lines = stdout.readlines()
        print(h, "Kernel version: ", lines[0])
        kernel_log.append(lines[0])

    except:
        print(h, ' No SSH connection  ')
        make_log = ['Error SSH connection','255']
        kernel_log = ['Error SSH connection','255']

        

    with open(('./data/{}.log').format(n), 'w') as log_file:
        for i in make_log:
            log_file.write("%s\n" % i)
                
    with open(('./data/{}.sys.log').format(n), 'w') as log_file:
        for i in kernel_log:
            log_file.write("%s\n" % i)

    print("Disconnect", h)
    print("*********************************************************************************************************************")

#########################################################################################
#parse log files and create html output

def parse_logs(package = ''): #get file list
    file_list = list()
    log_file_list = list()
    print(package)

    f_l = list()
    f_l = os.listdir('./data/')
    for i in f_l:
        if i.find('sys') == -1:
            file_list.append(i)

    print(file_list)
    li_max = list()

    for f in file_list:
        with open('./data/'+f, 'r') as log_file:     #read loges
            data = log_file.readlines()

        li = list()

        f_sys = f.replace(".log","") + ".sys.log"    
        with open('./data/'+f_sys, 'r') as log_sys_file:  #read files with kernel version
            data_sys = log_sys_file.readlines()
        #print(data_sys)

        li.append(f.replace(".log","")) #create list with data
        z = (data_sys[-2]).replace("b'","").replace("\\n","").replace("\n","").replace("'","")
        print(z)
        li.append(z)
        #print('exit c', data[-2])
        z = (data[-2]).replace("b'","").replace("\\n","").replace("\n","").replace("'","")
        li.append(z)
        li.append('')
        li.append('')
        #print(li)
        er = 0
        wa = 0
        for i in data:
            if  i.find('Error') != -1 or i.find('ERROR') != -1:
                er = er +1
        if er > 0:
            li[3]=str(er)      
        for i in data:
            if i.find('Warning') != -1 or i.find('WARNING') != -1:
                wa = wa +1
        if wa > 0:
            li[4]=str(wa)  
        
        li_max.append(li)  
        #print(li_max)
    return(li_max)  #return list of list with data


def set_table(li_max=list()): #generate table from data from list
    table_head = '<table border="1"><tr><th>OS</th><th>Kernel</th><th>Exit code</th><th>Errors</th><th>Warnings</th></tr>\n'
    table_content = ''
    table_end = '</table>'

    for li in li_max:
        table_content = table_content + ("<tr><td>{}</td><td>{}</td>").format(li[0], li[1])
        if li[2] == '0':
            table_content = table_content + '<td>{}</td>'.format(li[2])
        else:
            table_content = table_content + "<td bgcolor='red'>{}</td>".format(li[2])
        if li[3] == '':
            table_content = table_content + '<td></td>'
        else:
            table_content = table_content + "<td bgcolor='red'>{}</td>".format(li[3])
        if li[4] == '':
            table_content = table_content + '<td></td>'
        else:
            table_content = table_content + "<td bgcolor='pink'>{}</td>".format(li[4])
        table_content = table_content + "</tr>\n"

    res = table_head + table_content + table_end
    #print(res)
    return res

def set_html(tb='', package = ''):  #generate html page 
    html_head = '<!DOCTYPE html><html>\n'
    html_style = '<style>\ntable{width:800px;}\nth {width: 80px;}\ntable {background-color:#FFFFE0;}\n</style>\n'
    html_body = '<body>\n'
    html_package = "<h2> Results of compilation: {}<h2>".format(package)
    html_end = '\n</body></html>'
    html_ret = html_head + html_style + html_body + html_package + tb + html_end
    return html_ret

def save_html(page=''): #save html page fot local anf Jenkins enviroment
    with open('./data/results.html', 'w') as html_file:
        html_file.write(page)
    
    file_list = list()
    f_l = list()
    f_l = os.listdir('./data/')
    for i in f_l:
        if i.find('sys') == -1:
            file_list.append(i)

    print(file_list)

    workspace_env = ''
    try:
        workspace_env = os.environ['WORKSPACE']
        print(workspace_env)
    except:
        print("No Jenkins Workspace")

    if len(workspace_env) != 0 :
        for f in file_list:
            d = ("cp ./data/{} {}/{}").format(f,workspace_env,f)
            os.system(d)

        e = ("cp ./data/results.html {}/results.html").format(workspace_env)
        os.system(e)
   

#########################################################################################
#update os

def choose_command(): #check if any of these commands is present
    if (which("dnf") is not None):
        return "dnf -y update"
    elif (which("apt-get") is not None):
        return "apt-get -y update && apt-get -y dist-upgrade"
    elif (which("zypper") is not None):
        return "zypper --non-interactive up"
    else:
        return -1


def system_update(ip_list = ''):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    for ip in ip_list:
        try:
            ssh.connect(ip, 22)
            command = choose_command()
            stdin, stdout, stderr = ssh.exec_command(command)
            lines = stdout.readlines()
            print(lines)
            print(ip)
        except:
            print(ip, ' No SSH connection  ')
