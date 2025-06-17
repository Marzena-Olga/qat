import os
import urllib3
import requests
import hsdes
import base64
from requests_kerberos import HTTPKerberosAuth
from requests.auth import HTTPBasicAuth
import json
import sqlite3
import decode


# pip3  --proxy http://proxy-chain.intel.com:911 install jira




def get_hsd_rec():
    lp = decode.get_cred()
    user = lp['login']
    pwd = lp['pass']
    tok = 'ger/' + user + ':' + pwd
    #print(tok)
    encoded_tok = base64.b64encode(tok.encode()).decode()

    headers = {'Content-Type': 'application/json', 'Authorization': 'Basic %s' % encoded_tok}
    proxy = {'http': '', 'https': ''}
    URL = 'https://hsdes.intel.com/'
    r = requests.get(URL, headers=headers, proxies=proxy, verify=False)

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    headers = {'Content-type': 'application/json'}

    url = 'https://hsdes.intel.com/rest/query/execution/eql?start_at=1&max_results=4000'

    payload = """
    {
      "eql":"select id,title , status, release, release_affected, feature.feature_type,family where feature.feature_type = 'requirement' and (family = 'CPM (Content Processing Module)' or family = 'nCPM') and status != 'strawman' "
    }
    """

    p = requests.sessions.session()
    p.verify = './cert/Kupniewska_Marzena-chain.pem'

    response = p.post(url, verify=True, auth=HTTPKerberosAuth(), headers=headers, data=payload)
    #response = requests.post(url, verify=True, auth=HTTPKerberosAuth(), headers=headers, data=payload)
    #response = requests.post(url, verify=False, proxies=proxy, headers=headers, data=payload)
    i = 0
    li = list()

    if (response.status_code == 200):
        data_rows = response.json()['data']
        for row in data_rows:
            print("{:<4} {:<12} {:<10} {:<90} {:<10}".format(i, row['id'], row['status'], row['release_affected'],
                                                             row['title']))
            i += 1
            li.append((int(row['id']), row['status'], row['release_affected'], row['title']))

        print("############################################" * 4)
        print(response.json()['max_results'], response.json()['start_at'], response.json()['total'])
        print("############################################" * 4)
    print(response)
    return li


def store_hsd(hsd_rec=list()):
    try:
        sqliteConnection = sqlite3.connect('hsdes.db')
        cursor = sqliteConnection.cursor()
        print("Database created and Successfully Connected to SQLite")
        query = """ CREATE TABLE IF NOT EXISTS hsdes (
                                                id integer PRIMARY KEY,
                                                status text,
                                                affected text,
                                                title text
                                            ); """
        cursor.execute(query)
        record = cursor.fetchall()
        print(record)

        for li in hsd_rec:
            print(li)
            query = """select * from hsdes where id = {} """.format(li[0])
            print(query)
            cursor.execute(query)
            record = cursor.fetchall()
            print(record)
            if record == []:
                query = """insert into hsdes (id,status,affected,title) values (?,?,?,?)"""
                tuple = (li[0], li[1], li[2], li[3])
                print('INSERT', query, tuple)
                cursor.execute(query, tuple)
                sqliteConnection.commit()
            else:
                if record[0] != li:
                    query = """Update hsdes set status = ? , affected = ? , title = ? where id = ?"""
                    tuple = (li[1], li[2], li[3], li[0])
                    print("UPDATE", query, tuple)
                    cursor.execute(query, tuple)
                    sqliteConnection.commit()

        cursor.close()

    except sqlite3.Error as error:
        print("Error while connecting to sqlite", error)
    finally:
        if (sqliteConnection):
            sqliteConnection.close()
            print("The SQLite connection is closed")


def get_hsd_data(affected_version='', project_id='', key='', encoded_tok=''):
    affected = list()
    print(affected_version, project_id, key)
    #affected_version = "'CPM 3p2'"
    try:
        sqliteConnection = sqlite3.connect('hsdes.db')
        cursor = sqliteConnection.cursor()
        print("Database created and Successfully Connected to SQLite")
        query = """select * from hsdes where affected = '{}' """.format(affected_version)
        #query = """select * from hsdes where affected = 'CPM 3p2' limit 6 """
        #query = """select * from hsdes where affected = 'CPM 3p2' """
        print(query)
        cursor.execute(query)
        record = cursor.fetchall()

    except sqlite3.Error as error:
        print("Error while connecting to sqlite", error)

    finally:
        if (sqliteConnection):
            sqliteConnection.close()
            print("The SQLite connection is closed")

        # print(record)
        for tu in record:
            # print(tu[2])
            affected.extend((tu[2]).split(','))
            affected = list(dict.fromkeys(affected))

        post_version(affected, project_id, encoded_tok, key)  #add version to jira

        jl = list()
        for tu in record:
            # print(tu)
            # print(('https://hsdes.intel.com/appstore/article/#/{}').format(tu[0]), tu[1], tu[3])
            aff = (tu[2]).split(',')
            d = dict()
            lid = list()
            lid2 = list()
            for i in aff:
                # [{"name": "CPM 1p8"}, {"name": "CPM 3p2"}]
                d['name'] = i
                e = json.dumps(d)
                lid2.append(e)
            for i in lid2:
                a = json.loads(i)
                lid.append(a)
            json_list = [lid, ('https://hsdes.intel.com/appstore/article/#/{}').format(tu[0]), tu[3], tu[3], tu[0]]
            jl.append(json_list)
        print(jl)
        post_jira_ticket(jl, key, encoded_tok)  #add ticket to jira


def post_version(affected=list(), project_id='', encoded_tok='', key=''):
    #affected = ['CPM 3p0']
    print(affected)
    headers = {'Content-Type': 'application/json', 'Authorization': 'Basic %s' % encoded_tok}
    proxy = {'http': '', 'https': ''}
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    url = 'https://jira.devtools.intel.com/rest/api/2/project/{}/version?maxResults=400'.format(key)
    response = requests.get(url, verify=False, headers=headers, )
    print(response.status_code)
    z = (response.json())
    l = list()
    for i in z['values']:
        l.append(i['name'])
    url = 'https://jira.devtools.intel.com/rest/api/latest/version'
    for i in affected:
        x = (i in l)
        print(i, x)
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


def post_jira_ticket(jl=list(), key='', encoded_tok=''):
    #key = 'QAT32'
    #key = 'DPASP'
    print(jl)
    headers = {'Content-Type': 'application/json', 'Authorization': 'Basic %s' % encoded_tok}
    proxy = {'http': '', 'https': ''}
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    url = 'https://jira.devtools.intel.com/rest/api/2/search?jql=project={}&maxResults=4000'.format(key)
    response = requests.request("GET", url, verify=False, headers=headers)
    print(response.status_code)
    z = (response.json())
    y = (z['issues'])
    l = list()
    for a in y:
        l.append(json.dumps((a['fields'])['customfield_10808']))
    print(l)
    url = 'https://jira.devtools.intel.com/rest/api/2/issue/'
    for zj in jl:
        i = str(zj[4])
        i = '"'+i+'"'
        x = (i in l)
        #print(i, l[0])
        print('Found ', i, ':', x)
        if x == False:
            print(zj)
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
                        "versions": zj[0],
                        #"customfield_28700": zj[1],
                        "customfield_10808": str(zj[4]),
                        "summary": zj[2],
                        "description": zj[3],
                        "issuetype":
                            {
                                "name": "Requirement"
                            }
                    }
            })

            print('Execute request(json):')
            print(dane)
            headers = {"Accept": "application/json", "Content-Type": "application/json"}
            response = requests.request("POST", url, verify=False, data=dane, headers=headers)
            print(response.status_code)
            print('Result:', response.json())


def get_project_id(pname='', encoded_tok=''):
    print('get jira')
    headers = {'Content-Type': 'application/json', 'Authorization': 'Basic %s' % encoded_tok}
    proxy = {'http': '', 'https': ''}
    url = 'https://jira.devtools.intel.com/rest/api/2/project'
    r = requests.get(url, headers=headers, proxies=proxy, verify=False)
    print(r.status_code)
    print(r)
    z = (r.json())
    for i in z:
        if (i['key']) == pname:
            ret = i['id']
    return ret

def gen_token():
    lp = decode.get_cred()
    user = lp['login']
    pwd = lp['pass']
    tok = user + ':' + pwd
    encoded_tok = base64.b64encode(tok.encode()).decode()
    return encoded_tok