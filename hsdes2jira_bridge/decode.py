# -*- coding: utf-8 -*-
import base64
import json
import os

def encode(plainText):
    plainBytes = plainText.encode('ascii')
    encodedBytes = base64.b64encode(plainBytes)
    encodedText = encodedBytes.decode('ascii')
    return encodedText


def decode(obfuscatedText):
    obfuscatedBytes = obfuscatedText.encode('ascii')
    decodedBytes = base64.b64decode(obfuscatedBytes)
    decodedText = decodedBytes.decode('ascii')
    return decodedText

def store_passwd():
    login = input("Login:")
    passwd = input("Password:")
    encpasswd = encode(passwd)
    enclogin = encode(login)
    data = dict()
    data = {
        "qat_creds":
            {
                "login": enclogin,
                "pass": encpasswd
            }
        }
    print(data)
    print(data['qat_creds'])
    with open(r'./pstore.json', 'w') as f:
        json.dump(data, f, indent=4, sort_keys=True)


def get_cred():
    with open(r'./pstore.json') as json_file:
        data = json.load(json_file)
    login = decode((data["qat_creds"])["login"])
    passwd = decode((data["qat_creds"])["pass"])
    d = dict()
    d['login'] = login
    d['pass'] = passwd
    #print(d)
    return d


