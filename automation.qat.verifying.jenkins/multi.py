import os
import sys
#import subprocess
import json
#from joblib import Parallel, delayed
from datetime import datetime

rp = (os.path.dirname(os.path.realpath(__file__)))
os.chdir(rp)

def make_check(oid,workspace,repo):
    #print(oid)
    command = ('mkdir {0}/{1}').format(workspace,oid)
    os.system(command)
    command = ('cp -r {0}/{1}/* {0}/{2}/').format(workspace,repo,oid)
    #print (command)
    os.system(command)
    command = ('cd {0}/{1} && git checkout {1} ').format(workspace,oid)
    os.system(command)
    command = ('cd {0}/{1} && yes "" | make oldconfig > .makeoldconfig_output 2> /dev/null').format(workspace,oid)
    os.system(command)
    command = ('cd {0}/{1} && yes "" | make -j modules_prepare').format(workspace,oid)
    os.system(command)
    command = ('cd {0}/{1} && make -j 48').format(workspace,oid)
    os.system(command)
    command = ('cd {0}/{1} && make M=drivers/crypto/qat clean').format(workspace,oid)
    os.system(command)
    command = ('cd {0}/{1} && make -j 48 M=drivers/crypto/qat W=1 && echo $? ').format(workspace,oid)
    res = os.system(command)
    #print(oid,': ',res)
    command = ('cd {0} && rm -rf {1}').format(workspace,oid)
    #print (command)
    os.system(command)
    return res

def make_check_checkout(oid,workspace,repo):
    #print("##############################################################################################################")
    print(oid)
    command = ('cd {0}/{1} && git checkout {2} ').format(workspace,repo,oid)
    print(command)
    os.system(command)
    print('--------------------------------------------------------------------------------------------------------------------------------------------------------')
    command = ('cd {0}/{1} && yes "" | make oldconfig > .makeoldconfig_output 2>&1 > /dev/null').format(workspace,repo)
    print(command)
    os.system(command)
    print('--------------------------------------------------------------------------------------------------------------------------------------------------------')
    command = ('cd {0}/{1} && yes "" | make -j modules_prepare 2>&1 > /dev/null').format(workspace,repo)
    print(command)
    os.system(command)
    print('--------------------------------------------------------------------------------------------------------------------------------------------------------')
    command = ('cd {0}/{1} && make -j 48 2>&1 > /dev/null').format(workspace,repo)
    print(command)
    os.system(command)
    print('--------------------------------------------------------------------------------------------------------------------------------------------------------')
    command = ('cd {0}/{1} && make M=drivers/crypto/qat clean').format(workspace,repo)
    print(command)
    os.system(command)
    print('--------------------------------------------------------------------------------------------------------------------------------------------------------')
    command = ('cd {0}/{1} && make -j 48 M=drivers/crypto/qat W=1 2>&1 > /dev/null && echo $? ').format(workspace,repo)
    print(command)
    res = os.system(command)
    print("Output:", res)
    print('--------------------------------------------------------------------------------------------------------------------------------------------------------')
    return res
    

print("Start check commits in PR")
src_repo = 'https://github.com/intel-innersource/drivers.qat.linux.qatkernel.git'  
src_branch = 'pfvf'
repo = 'cryptodev-2.6'

pull_request = os.getenv('GITHUB_PR_NUMBER')
pull_request_branch = os.getenv('GITHUB_PR_SOURCE_BRANCH')
workspace = os.getenv('WORKSPACE')
job = os.getenv('JOB_BASE_NAME')

if (workspace == None) or (workspace == ''):
    workspace = 'tp'  #test pull

#print(workspace)
#pull_request = 92
#print(pull_request)

workspace_path=('{0}/{1}').format(workspace,repo)

command = ('git config --global advice.detachedHead false')
os.system(command)

if os.path.isdir(('{0}/{1}').format(workspace,repo)) == True:
    command = ('cd {0}/{1} && git status && echo $?').format(workspace,repo)
    #print(command)
    x = os.system(command)
else:
    if os.path.isdir(workspace)  != True:
        os.mkdir(workspace)
    x = -1
print(x)

if x == 0:
    print('Repo exist')
    command = ('cd {0}/{1} && git remote -v update --prune').format(workspace,repo)
    print(command)
    os.system(command)
    command = ('cd {0}/{1} && git fetch').format(workspace,repo)
    print(command)
    os.system(command)
    command = ('cd {0}/{1} && git checkout {2}').format(workspace,repo,src_branch)
    print(command)
    os.system(command)
    command = ('cd {0}/{1} && git reset --hard origin/{2}').format(workspace,repo,src_branch)
    print(command)
    os.system(command)

else:
    print('Clone repo')
    command = ('mount | grep {0}').format(job)
    ex = os.popen(command)
    mnt = ex.read()
    if mnt.find(job) == -1:
        #print('Mount RAMDisc')
        command = ('mount -t tmpfs -o size=48g tmpfs {0}').format(workspace)
        #print(command)
        #os.system(command)
    
    print ("Clone")
    command = ('cd {0} && rm -rf {1} &&  git clone {2} {3}').format(workspace,repo,src_repo,repo)
    print(command)
    os.system(command)
    command = ('cd {0}/{1} && git checkout {2}').format(workspace,repo,src_branch)
    print(command)
    os.system(command)

if (pull_request == None) or (pull_request == ''):
    command = ('cd {0}/{1} && gh pr list -L 1 ').format(workspace,repo)
    ex = os.popen(command)
    pr = ex.read()
    pr = pr.split()
else:
    pr = [pull_request,'','','','','',pull_request_branch]

print(pr)
print(pull_request)

print('########################################################################################')
print('Pull Request:',pr[0],' -  Branch name:',pr[6])
print('########################################################################################')

command = ('cd {0}/{1} && gh pr checkout {2} ').format(workspace,repo,pr[0])
os.system(command)

command = ('cd {0}/{1} && gh pr view {2} --json commits').format(workspace,repo,pr[0])
ex = os.popen(command)
json_res = ex.read()
json_res = json.loads(json_res)

#print(json.dumps(json_res, indent=4 ))
#print(json_res['commits'])
summary_pr = dict()

for i in (json_res['commits']):
    #print(i['authors'][0]['email'],i['messageHeadline'],i['oid'])
    summary_pr[(json_res['commits']).index(i)] = [i['oid'],i['messageHeadline'],i['authors'][0]['name'],i['committedDate']]

print('Commits:')
for i in summary_pr:
    print(summary_pr[i])
    #print(summary_pr[i][0])

now = datetime.now()

for i in summary_pr:
    print('########################################################################################')
    print("Commit: ", summary_pr[i][0])
    print('########################################################################################')
    res_make = make_check_checkout(summary_pr[i][0],workspace = workspace,repo = repo)
    summary_pr[i].append(res_make)

check = 0
print('--------------------------------------------------------------------------------------------------------------------------------------------------------')
for i in summary_pr:
    #print(summary_pr[i])
    a = (summary_pr[i])
    print('| Commit:',a[0],' | Title:',a[1],'| Author:',a[2],'| Date:',a[3],'| Output:',a[4]) 
    check = check + int(summary_pr[i][-1])
print('--------------------------------------------------------------------------------------------------------------------------------------------------------')
#print('Parallel test')
#Parallel(n_jobs=20)(delayed(make_check)(i,workspace,repo) for i in oids_list)

now_end = datetime.now()
print("************************************")
print('Configure&make time:', now_end - now)
print("************************************")
if check >0:
    sys.exit(-1)
else:
    sys.exit(0)
