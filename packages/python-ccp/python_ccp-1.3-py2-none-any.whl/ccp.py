#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""copy paste program with clip-server use stdin and stdout version 1.3

Usage:      ccp copy <name> [-p <password>]
            ccp paste <name> [-p <password>]

Option:     -p Encrypt with password

Example:    echo "this_is_data" | ccp copy this_is_name
            ccp paste this_is_name
"""

import requests
import os
import sys
from hashlib import md5
from getpass import getpass
from docopt_dispatch import dispatch
from Crypto.Cipher import AES

__version__ = 1.3
__name__ = "ccp"

HOST = os.environ.get('CLIP_SERVER') or 'http://clip.rop.sh'

if sys.platform == "win32":
    import os, msvcrt
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

def die(status):
    sys.stdout.write("Error [%s]"%(str(status)))
    exit()

def path(name):
    return "%s/%s" % (HOST, name)

def encrypt(data, password):
    iv = os.urandom(16)
    key = md5(password).digest()
    h = md5(data).digest()
    cipher = AES.new(key, AES.MODE_CBC, iv)
    length = 16 - (len(data) % 16)
    data += chr(length)*length
    c = cipher.encrypt(data)

    return iv + h + c

def decrypt(data, password):
    iv = data[:16]
    h = data[16:32]
    data = data[32:]
    key = md5(password).digest()
    cipher = AES.new(key, AES.MODE_CBC, iv)
    p = cipher.decrypt(data)

    p = p[:-ord(p[-1])]

    if md5(p).digest() != h:
        die("wrong password")

    return p

def paste(name):
    r = requests.get(path(name))
    if r.status_code == 200:
        return r.content

    die(r.status_code)

def copy(name, data):
    r = requests.post(path(name), data=data)
    if r.status_code == 201:
        return True

    die(r.status_code)

@dispatch.on('copy')
def do_copy(name, **kwargs):
    data = sys.stdin.read()
    if kwargs["p"]:
        password = kwargs["password"] or ""
        data = encrypt(data, password.strip())

    data = data.encode("base64")

    copy(name, data)

@dispatch.on('paste')
def do_paste(name, **kwargs):
    data = paste(name).decode("base64")

    if not data:
        sys.stdout.write("error [%d]")

    if kwargs["p"]:
        password = kwargs["password"] or ""
        data = decrypt(data, password.strip())

    sys.stdout.write(data)

def main():
    dispatch(__doc__)

if __name__ == '__main__':
    main()
