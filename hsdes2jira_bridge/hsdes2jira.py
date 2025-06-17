import urllib3
import requests
import base64
from requests_kerberos import HTTPKerberosAuth
import json
import decode
from requests.auth import HTTPBasicAuth

#######################################################################################################################################################
#function get data from HSDES server
#######################################################################################################################################################

def get_hsdes_data(affected='', cert=''):
    print('Get HSDES data')
    #lp = decode.get_cred()
    #user = lp['login']
    #pwd = lp['pass']
    #tok = 'ger/' + user + ':' + pwd
    #encoded_tok = base64.b64encode(tok.encode()).decode()
    #headers = {'Content-Type': 'application/json', 'Authorization': 'Basic %s' % encoded_tok}
    #proxy = {'http': '', 'https': ''}
    #url = 'https://hsdes.intel.com/'
    #r = requests.get(url, headers=headers, proxies=proxy, verify=False)
    #print(r.status_code)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    headers = {'Content-type': 'application/json'}
    url = 'https://hsdes.intel.com/rest/query/execution/eql?start_at=1&max_results=4000'

    payload = """
        {
            "eql":"select id,title , status, release, release_affected, feature.feature_type,family where feature.feature_type = 'requirement' and (family = 'CPM (Content Processing Module)' or family = 'nCPM') and status != 'strawman'  "
        }
        """

    p = requests.sessions.session()
    p.verify = './cert/Kupniewska_Marzena-chain.pem'
    p.verify = cert
    response = p.post(url, verify=True, auth=HTTPKerberosAuth(), headers=headers, data=payload)
    i = 1
    li = list()

    if (response.status_code == 200):
        data_rows = response.json()['data']
        for row in data_rows:
            ra = list()
            ra = (row['release_affected']).split(',')
            if (affected in ra) == True:
                #print("{:<4} {:<12} {:<10} {:<90} {:<10}".format(i, row['id'], row['status'], row['release_affected'],row['title']))
                print("{:<4} {:<12} {:<10} {:<70}".format(i, row['id'], row['status'], row['title']), ra)
                i += 1
                li.append([str(row['id']), row['title'], ra, row['status']])

        print("############################################" * 4)
        print('Max results:', response.json()['max_results'], 'Start at:', response.json()['start_at'], 'Records:', response.json()['total'], 'Records with', affected, ':', i-1)
        print("############################################" * 4)
    print(response)
    return li

#######################################################################################################################################################
#function get data from JIRA server
#######################################################################################################################################################

def get_jira_data(key=''):
    print('Get JIRA data')
    lp = decode.get_cred()
    user = lp['login']
    pwd = lp['pass']
    tok = user + ':' + pwd
    encoded_tok = base64.b64encode(tok.encode()).decode()
    headers = {'Content-Type': 'application/json', 'Authorization': 'Basic %s' % encoded_tok}
    proxy = {'http': '', 'https': ''}
    #url = 'https://jira.devtools.intel.com/rest/api/2/search?jql=project={}&maxResults=4000'.format(key)
    url = 'http://jira.devtools.intel.com/rest/api/2/search?jql=project={0} AND issuetype=21&maxResults=1000'.format(key)
    r = requests.get(url, headers=headers, proxies=proxy, verify=False)
    print(r.status_code)
    res = list()
    z = (r.json())
    for i in z["issues"]:
        tm = (i['fields']['customfield_10808'])
        if tm != None:
            res.append(i['fields']['customfield_10808']) #list of ID tickets
    #print('Tickets:', len(res))
    print("*********************************************" * 5)
    print("List HSDES ID:", res)
    print("*********************************************" * 5)
    res_list = list()
    for i in res:
        for j in z["issues"]:
            vl = list()
            if i == j['fields']['customfield_10808']:
                af = j['fields']['versions']
                for afi in af:
                    vl.append(afi['name'])
                #print(j['key'], j['fields']['customfield_10808'], j['fields']['project']['key'], j['fields']['summary'], vl)
                tl = [j['fields']['customfield_10808'], j['fields']['summary'], vl]
        res_list.append(tl)
    print("*************************"*4)
    for i in res_list:
        print(i)
    print("############################################" * 4)
    print('Tickets:', len(res_list))
    print("############################################" * 4)
    return res_list

#######################################################################################################################################################
#function compare JIRA&HSDES data
#######################################################################################################################################################
def compare_data(hsdes_data=list(), jira_data=list(), project_id='', key='', affected_version=''):
    print("HSDES tickets: ", hsdes_data)
    print("JIRA tickets: ", jira_data)
    hsdes_idx = list()
    jira_idx = list()
    for i in hsdes_data:
        #print(i[0])
        hsdes_idx.append(i[0])
    for i in jira_data:
        #print(i[0])
        jira_idx.append(i[0])
    #print(hsdes_idx)
    #print(jira_idx)

    print("*****************************" * 4)
    #create ticket list to update
    for i in jira_idx:
        if i in hsdes_idx:
            print("Ticket {0} has requirement".format(i))
        else:
            print("Ticket {0} changed".format(i))
            update_ticket(i, key, affected_version)

    print("*****************************" * 4)
    affected_ver = list()
    ticket_list = list()
    #check and create list of missing tickets
    for i in hsdes_idx:
        if i in jira_idx:
            print(i, "- exist")
        else:
            print(i, "- add ticket to jira:")
            for j in hsdes_data:
                if i in j[0]:
                    print(j)
                    affected_ver.extend(j[2]) #create list of versions
                    t_list = list()
                    d = dict()
                    f = list()
                    lid = list()
                    #t_list.append(j[0], j[1])
                    for lv in j[2]:
                        d['name'] = lv  #create simple dictionare
                        e = json.dumps(d) #convert dictionary to json
                        f.append(e) #add json to list
                    for g in f:
                        h = json.loads(g) #convert from json to dictionary
                        lid.append(h) #create list of dictionaries
                    t_list.append(j[0]), t_list.append(j[1]), t_list.append(lid), t_list.append(j[3]) #create list with json data
                    ticket_list.append(t_list) #create list of list
    #print(affected_ver)
    affected_ver = list(dict.fromkeys(affected_ver)) #remove duplicate items from list
    #print(affected_ver)
    update_versions(affected_ver, project_id, key) #run function to updade versions list in jira
    print("*****************************" * 4)
    print(ticket_list)
    ticket_list = ticket_list[2:4]
    print(ticket_list)
    print("Tickets to be added: ", len(ticket_list))
    post_jira_ticket(ticket_list, key)
    print("*****************************" * 4)

#######################################################################################################################################################
#function update versions in JIRA
#######################################################################################################################################################
def update_versions(affected=list(), project_id='', key=''):
    #affected = ['CPM 3p0']
    print("*********************************" * 5)
    print("List versions: ", affected)
    print("*********************************" * 5)
    lp = decode.get_cred()
    user = lp['login']
    pwd = lp['pass']
    tok = user + ':' + pwd
    encoded_tok = base64.b64encode(tok.encode()).decode()
    auth = HTTPBasicAuth(user, pwd)
    headers = {'Content-Type': 'application/json', 'Authorization': 'Basic %s' % encoded_tok}
    proxy = {'http': '', 'https': ''}
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    url = 'https://jira.devtools.intel.com/rest/api/2/project/{}/version?maxResults=400'.format(key)
    response = requests.get(url, verify=False, headers=headers, )
    print(response.status_code)
    print("Adding versions to Jira")
    z = (response.json())
    l = list()
    for i in z['values']:
        l.append(i['name'])
    url = 'https://jira.devtools.intel.com/rest/api/2/version'
    for i in affected:
        x = (i in l)
        print(i, x, ": exist")
        if x == False:
            print(i)
            dane = json.dumps({
                "archived": False,
                "name": i,
                "projectId": project_id,
                "released": False
            })
            print(dane)
            response = requests.request("POST", url, verify=False, data=dane, headers=headers, auth=auth)
            print(response.status_code)
            print(response.json())

#######################################################################################################################################################
#function create ticket in JIRA
#######################################################################################################################################################
def post_jira_ticket(jl=list(), key=''):
    #key = 'QAT32'
    #key = 'DPASP'
    print(jl)
    lp = decode.get_cred()
    user = lp['login']
    pwd = lp['pass']
    tok = user + ':' + pwd
    encoded_tok = base64.b64encode(tok.encode()).decode()
    auth = HTTPBasicAuth(user, pwd)
    headers = {'Content-Type': 'application/json', 'Authorization': 'Basic %s' % encoded_tok}
    proxy = {'http': '', 'https': ''}
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    url = 'https://jira.devtools.intel.com/rest/api/2/issue/'
    for zj in jl:
        print(zj)
        lnk = 'https://hsdes.intel.com/appstore/article/#/{0}'.format(zj[0])
        print(lnk)
        dane = json.dumps({
            "fields":
                {
                    "project":
                        {
                            "key": key
                        },
                    "assignee":
                        {
                            "key": "",
                            "name": ""
                        },
                    "versions": zj[2],
                    "customfield_28700": lnk,
                    "customfield_10808": str(zj[0]),
                    "summary": zj[1],
                    "description": zj[1],
                    "issuetype":
                        {
                            "name": "Requirement"
                        }
                }
        })

        print('Execute request(json):')
        print(dane)
        #headers = {"Accept": "application/json", "Content-Type": "application/json"}
        response = requests.request("POST", url, verify=False, data=dane, headers=headers, auth=auth)
        print(response.status_code)
        print('Result:', response.json())

#######################################################################################################################################################
#function update ticket in JIRA
#######################################################################################################################################################
def update_ticket(ticket_id='',key='',affected_version=''):
    print('Get JIRA data')
    #ticket_id = '18020444801'
    #affected_version = 'CPM 3p2'
    #key = 'QAT32'
    lp = decode.get_cred()
    user = lp['login']
    pwd = lp['pass']
    tok = user + ':' + pwd
    auth = HTTPBasicAuth(user, pwd)
    encoded_tok = base64.b64encode(tok.encode()).decode()
    headers = {'Content-Type': 'application/json', 'Authorization': 'Basic %s' % encoded_tok}
    proxy = {'http': '', 'https': ''}

    url = 'http://jira.devtools.intel.com/rest/api/2/search?jql=project={0} AND issuetype=21&maxResults=1000'.format(key)
    r = requests.get(url, headers=headers, proxies=proxy, verify=False)
    print(r.status_code)
    z = (r.json())
    for i in z["issues"]:
        if ticket_id == (i['fields']['customfield_10808']):
            url = i['self']
            print(i['fields']['labels'])
    print(url)
    r = requests.get(url, headers=headers, proxies=proxy, verify=False)
    print(r.status_code)
    z = (r.json())
    v = z['fields']['versions']
    l = z['fields']['labels']
    print(l)
    for i in v:
        if i['name'] == affected_version:
            v.remove(i)
    print("Versions: {0}".format(v))
    dane = json.dumps({"fields":
                            {
                                "versions": v
                            }
                    })
    print(dane)
    response = requests.put(url, headers=headers, proxies=proxy, verify=False, data=dane, auth=auth)
    print(response.status_code)
    l.append("No_longer_required_by_HSDes")
    l = list(dict.fromkeys(l))
    print(l)
    dane = json.dumps({"fields":
        {
            "labels": l
        }
    })
    print(dane)
    response = requests.put(url, headers=headers, proxies=proxy, verify=False, data=dane, auth=auth)
    print(response.status_code)

#######################################################################################################################################################
#function get project ID from JIRA
#######################################################################################################################################################
def get_project_id(pname=''):
    print('Get JIRA data')
    lp = decode.get_cred()
    user = lp['login']
    pwd = lp['pass']
    tok = user + ':' + pwd
    auth = HTTPBasicAuth(user, pwd)
    encoded_tok = base64.b64encode(tok.encode()).decode()
    headers = {'Content-Type': 'application/json', 'Authorization': 'Basic %s' % encoded_tok}
    proxy = {'http': '', 'https': ''}
    url = 'https://jira.devtools.intel.com/rest/api/2/project'
    r = requests.get(url, headers=headers, proxies=proxy, verify=False, auth=auth)
    print(r.status_code)
    print(r)
    z = (r.json())
    for i in z:
        if (i['key']) == pname:
            ret = i['id']
    return ret