
import urllib3
import requests
import base64
from requests_kerberos import HTTPKerberosAuth
import json
import pandas as pd
import decode
from requests.auth import HTTPBasicAuth

def sample0():
    user = "username"
    pwd = "password"
    tok = user + ':' + pwd
    encoded_tok = base64.b64encode(tok.encode()).decode()

    headers = {'Content-Type': 'application/json', 'Authorization': 'Basic %s' % encoded_tok}
    proxy = {'http': '', 'https': ''}
    URL = 'https://hsdes.intel.com/appstore/article/#/18016813433'
    r = requests.get(URL, headers=headers, proxies=proxy, verify=False)

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    headers = {'Content-type': 'application/json'}
    # Replace the ID here with some article ID
    url = 'https://hsdes.intel.com/rest/article/1806651053'
    response = requests.get(url, verify=False, auth=HTTPKerberosAuth(), headers=headers)
    z = (response.json())
    y = (z['data'])
    print(json.dumps(z, indent=4, sort_keys=True))
    pd.DataFrame(y).to_excel("out.xlsx")

    print("############################################"*4)


def sample2():
    user = "username"
    pwd = "password"
    tok = user + ':' + pwd
    encoded_tok = base64.b64encode(tok.encode()).decode()

    headers = {'Content-Type': 'application/json', 'Authorization': 'Basic %s' % encoded_tok}
    proxy = {'http': '', 'https': ''}
    URL = 'https://hsdes.intel.com/appstore/article/#/18016813433'
    r = requests.get(URL, headers=headers, proxies=proxy, verify=False)

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    headers = {'Content-type': 'application/json'}

    url = 'https://hsdes.intel.com/rest/query/execution/eql?start_at=1&max_results=4000'

    payload = """
    {
      "eql":"select id,title , status, release, release_affected, feature.feature_type,family where feature.feature_type = 'requirement' and (family = 'CPM (Content Processing Module)' or family = 'nCPM') and status != 'strawman' "
    }

    """

    response = requests.post(url, verify=False, auth=HTTPKerberosAuth(), headers=headers, data=payload)
    i = 0
    li = list()

    if (response.status_code == 200):
        data_rows = response.json()['data']
        for row in data_rows:
            print("{:<4} {:<12} {:<10} {:<90} {:<10}".format(i, row['id'], row['status'], row['release_affected'], row['title']))
            i += 1
            li.append((i, row['id'], row['status'], row['release_affected'], row['title']))

    pd.DataFrame(li).to_excel("hsdes_data.xlsx")
    #print(json.dumps(data_rows, indent=4, sort_keys=True))
    print("#######################################################"*4)
    print(response.json()['max_results'], response.json()['start_at'], response.json()['total'])

############################################################################################




def sample1():
    user = ""
    pwd = ""
    tok = user + ':' + pwd
    encoded_tok = base64.b64encode(tok.encode()).decode()

    headers = {'Content-Type': 'application/json', 'Authorization': 'Basic %s' % encoded_tok}
    proxy = {'http': '', 'https': ''}
    URL = 'https://hsdes.intel.com/appstore/article/#/18016813433'
    r = requests.get(URL, headers=headers, proxies=proxy, verify=False)

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    headers = {'Content-type': 'application/json'}
    # Replace the ID here with some article ID
    url = 'https://hsdes.intel.com/rest/article/1806651053'
    response = requests.get(url, verify=False, auth=HTTPKerberosAuth(), headers=headers)
    z = (response.json())
    # print(z)
    y = (z['data'])
    # print(y)
    print(json.dumps(z, indent=4, sort_keys=True))
    x = y[0]
    # pd.DataFrame(y).to_excel("out.xlsx")

    print("############################################" * 4)
    return(z)


def sample3():
    print('get jira')
    user = ""
    pwd = ""
    lp = decode.get_cred()
    user = lp['login']
    pwd = lp['pass']
    tok = user + ':' + pwd
    auth = HTTPBasicAuth(user, pwd)
    encoded_tok = base64.b64encode(tok.encode()).decode()
    headers = {'Content-Type': 'application/json', 'Authorization': 'Basic %s' % encoded_tok}
    proxy = {'http': '', 'https': ''}
    URL = 'https://jira.devtools.intel.com/browse/DPASP-52302'
    r = requests.get(URL, headers=headers, proxies=proxy, verify=False)
    print(r.status_code)
    # print(r)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    # headers = {'Content-Type': 'application/json'}
    # headers = {'Content-type': 'application/json'}
    # Replace the ID here with some article ID
    # url = 'https://jira.devtools.intel.com/rest/api/2/issue/DPASP-52271'
    # url = 'https://jira.devtools.intel.com/rest/api/2/version/154856'
    url = 'https://jira.devtools.intel.com/rest/api/2/search?jql=project=DPASP'
    # url = 'https://jira.devtools.intel.com/rest/api/2/search?jql=External?Issue?ID=14014161456'
    response = requests.get(url, verify=False, headers=headers)
    # response = requests.request("GET", url, verify=False, headers=headers, auth=auth)
    print(response.status_code)
    z = (response.json())
    # print((z['fields'])['customfield_10808'])
    # for a in z:
    #    print('#####################################################################################################################')
    #    print(json.dumps(a))
    # y = (z['data'])
    y = (z['issues'])
    for a in y:
        print(
            '#####################################################################################################################')
        print(json.dumps((a['fields'])['customfield_10808']), json.dumps((a['fields'])['summary']))
    # print(json.dumps(z, indent=4, sort_keys=True))
    # print(json.dumps(z))
    # dane = json.dumps({
    #    "archived": False,
    #    "name": "CPM 2p0",
    #    "projectId": 29309,
    #    "released": False
    # })
    # url = 'https://jira.devtools.intel.com/rest/api/2/version'
    # response = requests.post(url, verify=False, json=dane, headers=headers, proxies=proxy)
    # print(response.status_code)

    # x = y[0]


def sample4(encoded_tok=''):
    print('set jira')


    headers = {'Content-Type': 'application/json', 'Authorization': 'Basic %s' % encoded_tok}
    proxy = {'http': '', 'https': ''}

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # dane = {"fields": {"project": {"key": "DPASP"}, "assignee": {"key": "JIRAUSER232909", "name": "mkupniew"}, "versions": [{"name": "CPM 1p8"}, {"name": "CPM 3p2"}], "customfield_28700": "https://hsdes.intel.com/appstore/article/#/14014161456", "customfield_10808": "14014161456", "summary": "Test REST API 3", "description": "Create test REST API 3", "issuetype": {"name": "Requirement"}}}

    dane = {"fields": {"project": {"key": "DPASP"}, "assignee": {"key": "", "name": ""},
                       "versions": [{"name": "CPM 1p8"}, {"name": "CPM 3p2"}, {"name": "CPM 1p7"},
                                    {"name": "CPM 2p0a"}],
                       "customfield_28700": "https://hsdes.intel.com/appstore/article/#/14014161456",
                       "customfield_10808": "14014161456", "summary": "Test REST API 4",
                       "description": "Create test REST API 4", "issuetype": {"name": "Requirement"}}}

    dane = {"fields": {"project": {"key": "QAT32"}, "assignee": {"key": "", "name": ""}, "versions": [{"name": "CPM 3p2"}],
                #"customfield_28700": "https://hsdes.intel.com/appstore/article/#/18016854852",
                "customfield_10808": "18016854852", "summary": "DPA Resistance: ECDHE-P384",
                "description": "DPA Resistance: ECDHE-P384", "issuetype": {"name": "Requirement"}}}

    # dane = {"fields": {"project": {"key": "DPASP"},
    #  "versions": [{"name": "CPM 1p8"}, {"name": "CPM 3p2"}, {"name": "CPM 1p7"},
    #              {"name": "CPM 2p0a"}],
    # "issuetype": {"name": "Requirement"}}}

    #url = 'https://jira.devtools.intel.com/rest/api/2/issue/DPASP-52268'
    #url = 'https://jira.devtools.intel.com/rest/api/2/project'
    url = 'https://jira.devtools.intel.com/rest/api/2/issue/'
    response = requests.post(url, verify=False, json=dane, headers=headers, proxies=proxy)
    print(response.status_code)
    z = (response.json())
    print(json.dumps(z, indent=4, sort_keys=True))


###################################################################################
def sample5():
    url = "https://jira.devtools.intel.com/rest/api/latest/version"
    user = ""
    pwd = ""
    tok = user + ':' + pwd
    encoded_tok = base64.b64encode(tok.encode()).decode()

    headers = {'Content-Type': 'application/json', 'Authorization': 'Basic %s' % encoded_tok}
    proxy = {'http': '', 'https': ''}
    URL = 'https://jira.devtools.intel.com/'
    r = requests.get(URL, headers=headers, proxies=proxy, verify=False)
    print(r)

    auth = HTTPBasicAuth(user, pwd)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    payload = json.dumps({
        "archived": False,
        "name": "CPM 2p0a",
        "projectId": 29309,
        "released": False
    })
    dane = payload

    response = requests.request("POST", url, verify=False, data=payload, headers=headers, auth=auth)
    # response = requests.post(url, verify=False, json=dane, headers=headers, proxies=proxy)

    # print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))
    print(response)

def sample6():
    print('get jira')
    lp = decode.get_cred()
    user = lp['login']
    pwd = lp['pass']
    tok = user + ':' + pwd
    encoded_tok = base64.b64encode(tok.encode()).decode()
    headers = {'Content-Type': 'application/json', 'Authorization': 'Basic %s' % encoded_tok}
    proxy = {'http': '', 'https': ''}
    #url = 'https://jira.devtools.intel.com/browse/DPASP-52302'
    #url = 'https://jira.devtools.intel.com/rest/api/2/issue/7780105'
    url = 'https://jira.devtools.intel.com/rest/api/2/issue/7903797' #issue query
    #url = "https://jira.devtools.intel.com/rest/api/2/version/164326"
    #url = 'https://jira.devtools.intel.com/rest/api/2/user?username=mkupniew'  #user qery
    #url = 'https://jira.devtools.intel.com/rest/api/2/project?projectname=Qat32'  #project query
    #url = 'https://jira.devtools.intel.com/rest/api/2/project?key=QAT32'  # project query
    #url = 'https://jira.devtools.intel.com/rest/api/2/project'
    #url = "https://jira.devtools.intel.com/rest/api/2/project/85812"
    r = requests.get(url, headers=headers, proxies=proxy, verify=False)
    print(r.status_code)
    print(r)
    z = (r.json())
    #print(json.dumps(z, indent=4, sort_keys=True))
    #print(z)
    #for i in z:
    #    if (i['key']) == 'QAT32':
    #        print(i)#['expand'])
    #        print(i['key'], i['id'])
    print(json.dumps(z, indent=4, sort_keys=True))

    #urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def sample7():
    print('get jira')
    lp = decode.get_cred()
    user = lp['login']
    pwd = lp['pass']
    tok = user + ':' + pwd
    encoded_tok = base64.b64encode(tok.encode()).decode()
    headers = {'Content-Type': 'application/json', 'Authorization': 'Basic %s' % encoded_tok}
    proxy = {'http': '', 'https': ''}

    url = 'https://jira.devtools.intel.com/rest/api/2/issue/7903797' #issue query

    r = requests.get(url, headers=headers, proxies=proxy, verify=False)
    print(r.status_code)
    print(r)
    z = (r.json())
    print(z["expand"])
    x = (z["fields"])
    print(x)
    print(x['customfield_10808'])
    print(z['fields']['customfield_10808'])
    print(z['fields']['summary'])
    #print(json.dumps(z, indent=4, sort_keys=True))
    #print(z)
    #for i in z:
    #    if (i['key']) == 'QAT32':
    #        print(i)#['expand'])
    #        print(i['key'], i['id'])
    print(json.dumps(z, indent=4, sort_keys=True))

def sample8():
    print('get jira')
    lp = decode.get_cred()
    user = lp['login']
    pwd = lp['pass']
    tok = user + ':' + pwd
    encoded_tok = base64.b64encode(tok.encode()).decode()
    headers = {'Content-Type': 'application/json', 'Authorization': 'Basic %s' % encoded_tok}
    proxy = {'http': '', 'https': ''}

    #url = 'https://jira.devtools.intel.com/rest/api/2/issue/7903797' #issue query
    #url = 'http://jira.devtools.intel.com/rest/api/2/issue/createmeta/QAT32/issuetypes'
    url = 'http://jira.devtools.intel.com/rest/api/2/issue/createmeta/QAT32/issuetypes/21'
    url = 'http://jira.devtools.intel.com/rest/api/2/search?jql=project=QAT32 AND issuetype=21&maxResults=1000'
    r = requests.get(url, headers=headers, proxies=proxy, verify=False)
    print(r.status_code)
    print(r)
    res = list()
    z = (r.json())
    print('Tickets:', len(z["issues"]))
    for i in z["issues"]:
        #print(i['fields']['customfield_10808'])
        tm = (i['fields']['customfield_10808'])
        if tm != None:
            res.append(i['fields']['customfield_10808']) #list of ID tickets
    print("*********************************************" *4)
    print(res)
    res_list = list()
    for i in res:
        for j in z["issues"]:

            vl = list()
            #tl = list()
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
    return(res_list)
    #print(json.dumps(z["issues"], indent=4, sort_keys=True))

#http://localhost:8080/rest/api/2/issue/createmeta/{projectIdOrKey}/issuetypes


def sample9():
    print('get jira')
    lp = decode.get_cred()
    user = lp['login']
    pwd = lp['pass']
    tok = user + ':' + pwd
    encoded_tok = base64.b64encode(tok.encode()).decode()
    headers = {'Content-Type': 'application/json', 'Authorization': 'Basic %s' % encoded_tok}
    proxy = {'http': '', 'https': ''}
    auth = HTTPBasicAuth(user, pwd)

    url = 'https://jira.devtools.intel.com/rest/api/2/issue/7903797' #issue query

    r = requests.get(url, headers=headers, proxies=proxy, verify=False)
    print(r.status_code)
    print(r)
    z = (r.json())
    print(z['fields']['versions'])
    print(json.dumps(z['fields']['versions'], indent=4, sort_keys=True))
    li = (z['fields']['versions'])
    print(len(li))
    print(li)
    li2 = list()
    #li2.append(li[1])
    #print(li2)
    #print(z['fields']['summary'])
    #########################################################################
    url = 'https://jira.devtools.intel.com/rest/api/2/issue/7903797/editmeta'
    url = 'https://jira.devtools.intel.com/rest/api/2/issue/7903797/'

    dane = json.dumps(
        {"update": {
            'fields': {'versions': [{'self': 'https://jira.devtools.intel.com/rest/api/2/version/164326', 'id': '164326', 'name': 'CPM 3p2', 'archived': False, 'released': False}]},
        }})
    #dane = json.dumps({"update": {"fields": {"versions": {"remove": {"name": "CPM 3p2"}}}}})
    #dane = json.dumps({"update": {"fields": {"summary": [{"set": "User space queue mapping 1"}]}}})
    #dane = json.dumps({"update": {"fields": {"summary": [{"set": "User space queue mapping 1"}]}}})
    #dane = json.dumps({"update": {"fields": {"summary": "User space queue mapping 1"}}})
    dane = json.dumps({"fields": {"summary": "User space queue mapping"}})
    dane = json.dumps({"fields": {"versions": li2}})
    print(dane)
    #response = requests.request("POST", url, verify=False, data=dane, headers=headers, auth=auth)
    response = requests.put(url, headers=headers, proxies=proxy, verify=False, data=dane, auth=auth)
    print(response.status_code)
    #########################################################################
    print("**********************************"*4)
    url = 'https://jira.devtools.intel.com/rest/api/2/issue/7903797'  # issue query

    r = requests.get(url, headers=headers, proxies=proxy, verify=False)
    print(r.status_code)
    print(r)
    z = (r.json())
    print(z['fields']['versions'])
    print(json.dumps(z['fields']['versions'], indent=4, sort_keys=True))
    print(z['fields']['summary'])

    #print(z)
    #for i in z:
    #    if (i['key']) == 'QAT32':
    #        print(i)#['expand'])
    #        print(i['key'], i['id'])
    #print(json.dumps(z, indent=4, sort_keys=True))

def sample10(affected=''):
    lp = decode.get_cred()
    user = lp['login']
    pwd = lp['pass']
    tok = 'ger/' + user + ':' + pwd
    encoded_tok = base64.b64encode(tok.encode()).decode()
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

    response = p.post(url, verify=True, auth=HTTPKerberosAuth(), headers=headers, data=payload)
    # response = requests.post(url, verify=True, auth=HTTPKerberosAuth(), headers=headers, data=payload)
    # response = requests.post(url, verify=False, proxies=proxy, headers=headers, data=payload)
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
                li.append((int(row['id']), row['status'], ra, row['title']))

        print("############################################" * 4)
        print('Max results:', response.json()['max_results'], 'Start at:', response.json()['start_at'], 'Records:', response.json()['total'], 'Records with', affected, ':', i-1)
        print("############################################" * 4)
    print(response)
    return li
'''
"components": [
            {
                "id": "163332",
                "name": "QAT 3.2",
                "self": "https://jira.devtools.intel.com/rest/api/2/component/163332"
            }

'''
'''
"labels": [
            "Performance"
        ],
'''
'''
"fixVersions": [
            {
                "archived": false,
                "id": "154855",
                "name": "CPM 3.2",
                "released": false,
                "self": "https://jira.devtools.intel.com/rest/api/2/version/154855"
            }
        ],
'''
if __name__ == '__main__':
    sample1()
    sample2()
