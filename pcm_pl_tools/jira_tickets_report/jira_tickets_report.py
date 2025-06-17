# -*- coding: utf-8 -*-

import urllib3
import requests
import base64
import os



def get_jira_data(key=''):
    print('Get JIRA data')
    #cert = './cert/Kupniewska_Marzena-chain.pem'
    #print(user, pwd)
    tok = user + ':' + pwd
    encoded_tok = base64.b64encode(tok.encode()).decode()
    headers = {'Content-Type': 'application/json', 'Authorization': 'Basic %s' % encoded_tok}
    proxy = {'http': '', 'https': ''}
    url = 'https://jira.devtools.intel.com/rest/api/2/search?jql=project={0}&maxResults=200'.format(key)
    url = 'https://jira.devtools.intel.com/rest/api/2/search?jql=project={0} AND cf[41500]="QAT Drivers" AND (status=New OR status=Blocked OR status=3)&maxResults=200'.format(key)
    #url = 'http://jira.devtools.intel.com/rest/api/2/search?jql=project={0} AND cf[41500]="QAT Drivers" AND status!=Closed&maxResults=200'.format(key)
    #url = 'http://jira.devtools.intel.com/rest/api/2/search?jql=project={0}'.format(key)
    r = requests.get(url, headers=headers, proxies=proxy, verify=False)
    print(r.status_code)
    res = list()
    li = ['Ticket', 'Reporter', 'Assignee', 'Created Date', 'Last Comment Date', 'Status', 'Url', 'Summary']
    res.append(li)
    z = (r.json())
    #print(z)
    print(
        '******************************************************************************************************************************************************************************************************************************')

    print("| %8s | %80s | %20s | %20s | %30s | %30s | %12s |" % ('Ticket', 'Summary', 'Reporter', 'Assignee', 'Created Date', 'Last Comment Date', 'Status'))
    print(
        '******************************************************************************************************************************************************************************************************************************')


    for i in z["issues"]:
        ticket_key = i['key']
        #<a href="https://jira.devtools.intel.com/browse/LSG-1783"> LSG-1783</a>
        #t_url = 'https://jira.devtools.intel.com/browse/'
        #params = {'var1': ticket_key}
        ticket_url = ('https://jira.devtools.intel.com/browse/{0}').format(ticket_key)
        reporter = i['fields']['reporter']['displayName']
        try:
            assignee = i['fields']['assignee']['displayName']
        except:
            assignee = ''
        summary = i['fields']['summary']
        created_date_raw = i['fields']['created']
        created_date = change_date_time(created_date_raw)
        #print(ticket_key, i['self'])
        try:
            last_comment_date_raw = get_last_comment(i['self'])
        except:
            last_comment_date_raw = ''
        #print(last_comment_date)

        last_comment_date = change_date_time(last_comment_date_raw)

        try:
            status = (i['fields']['status']['name'])
        except:
            status = 'unknown'

        li_i = [ticket_key, reporter, assignee, created_date, last_comment_date, status, ticket_url, summary]
        res.append(li_i)
        print("| %8s | %80s | %20s | %20s | %30s | %30s | %12s | " % (ticket_key, summary, reporter, assignee, created_date, last_comment_date, status))

        #print('----------------------------------------------------------------------------------------------------')
    print('******************************************************************************************************************************************************************************************************************************')
    print('Issues:', len(z["issues"]))
    return res

def get_last_comment(ticket=''):
    #print('get jira')
    tok = user + ':' + pwd
    encoded_tok = base64.b64encode(tok.encode()).decode()
    headers = {'Content-Type': 'application/json', 'Authorization': 'Basic %s' % encoded_tok}
    proxy = {'http': '', 'https': ''}
    url = ticket
    #url = 'https://jira.devtools.intel.com/rest/api/2/issue/12239505'
    r = requests.get(url, headers=headers, proxies=proxy, verify=False)
    z = (r.json())
    x = ''
    x = z['fields']['comment']['comments'][-1]['updated']
    return x

def change_date_time(date_time=''):
    if date_time != '':
        l = date_time.split('.')
        z = l[0].split('T')
        dt = z[0] + ' ' + z[1]
    else:
        dt = ''
    return dt


def set_table(li_max=list()):  # generate table from data from list
    lin = li_max[0]
    table_head = ('<table border="1"><tr><th style="width:7%">{0}</th><th style="width:38%">{6}</th><th style="width:12%">{1}</th><th style="width:12%">{2}</th><th style="width:12%">{3}</th><th style="width:12%">{4}</th><th style="width:7%">{5}</th></tr>\n').format(lin[0], lin[1], lin[2], lin[3], lin[4], lin[5], lin[7])
    table_content = ''
    table_end = '</table>'
    for li in li_max[1:]:
        href = ('<a href="{0}">{1}</a>').format(li[6], li[0])
        #print(li, href)
        table_content = table_content + ("<tr><td>{0}</td><td>{6}</td><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td><td>{5}</td>").format(href, li[1], li[2], li[3], li[4], li[5], li[7])
        table_content = table_content + "</tr>\n"

    res = table_head + table_content + table_end
    # print(res)
    return res


def set_html(tb=''):  # generate html page
    html_head = '<!DOCTYPE html><html>\n'
    html_style = '<style>\ntable{width:1800px;}\nth {width: 80px;}\ntable {background-color:#FFFFE0;}\n</style>\n'
    html_body = '<body>\n'
    html_package = "<h2> Tickets list: <h2>"
    html_end = '\n</body></html>'
    html_ret = html_head + html_style + html_body + html_package + tb + html_end
    return html_ret


def save_html(page=''):  # save html page fot local anf Jenkins enviroment
    with open('./tickets_table.html', 'w', encoding="utf-8") as html_file:
        html_file.write(page)


if __name__ == '__main__':
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    user = os.getenv('CREDS_USR')
    pwd = os.getenv('CREDS_PSW')
    #key = 'LSG'
    key = os.getenv('PROJECT_KEY')
    li = list()
    li = get_jira_data(key)
    tb = set_table(li)
    page = set_html(tb)
    save_html(page)
