import os
import urllib
import urllib3
import requests
#import hsdes
import base64
from requests_kerberos import HTTPKerberosAuth
from requests.auth import HTTPBasicAuth
import json
import sqlite3
import decode
import hsd2jira
import sample
import hsdes2jira




if __name__ == '__main__':
    rp = (os.path.dirname(os.path.realpath(__file__)))
    os.chdir(rp)
    key = 'QAT32'
    affected_version = 'CPM 3p2'
    cert = './cert/Kupniewska_Marzena-chain.pem'
    project_id = hsdes2jira.get_project_id(key)
    print("Project ID: ", project_id)

    hsdes_ticket_list = hsdes2jira.get_hsdes_data(affected_version, cert)
    jira_ticket_list = hsdes2jira.get_jira_data(key=key)
    hsdes2jira.compare_data(hsdes_ticket_list, jira_ticket_list, project_id, key, affected_version)

