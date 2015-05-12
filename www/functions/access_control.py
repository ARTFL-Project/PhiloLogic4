#!/usr/bin/env python

import os
from philologic.DB import DB
import sys
import socket
import re
import hashlib
import time

def check_access(environ, config, db):
    incoming_address = environ['REMOTE_ADDR']
    access = {}
    access_file = config.db_path + '/data/' + config['access_file']
    if not os.path.isfile(access_file):
        return make_token(incoming_address, db)
    else:
        execfile(access_file, globals(), access)
        domain_list = set(access["domain_list"])
        blocked_ips = set(access["blocked_ips"])

        fq_domain_name = socket.getfqdn(incoming_address).split(',')[-1]
        edit_domain = re.split('\.', fq_domain_name)

        if re.match('edu', edit_domain[-1]):
            match_domain = '.'.join([edit_domain[-2], edit_domain[-1]])
        else:
            if len(edit_domain) == 2:
                match_domain = '.'.join([edit_domain[-2], edit_domain[-1]])
            else:
                match_domain = fq_domain_name

        access_granted = True
        if incoming_address not in blocked_ips:
            if incoming_address in domain_list or match_domain in domain_list:
                access_granted = True  # We disable access control
            else:
                access_granted = False
        if access_granted == True:
            return make_token(incoming_address, db)
        else:
            return ()

def make_token(incoming_address, db):
    h = hashlib.md5()
    h.update(incoming_address)
    now = str(time.time())
    h.update(now)
    secret = db.locals.secret
    h.update(secret)
    return (h.hexdigest(), now)

# def previous_access_cleared(incoming_address, dbname):
#     session_file = "/tmp/%s" % '_'.join(dbname.split())
#     if os.path.isfile(session_file):
#         tmp_file = open(session_file)
#         previously_cleared = False
#         for line in tmp_file:
#             ip = line.strip()
#             if ip == incoming_address:
#                 previous_cleared = True
#                 break
#         return previous_cleared
#     else:
#         return False
# 
# 
# def save_access(incoming_address, dbname):
#     session_file = "/tmp/%s" % '_'.join(dbname.split())
#     output = open(session_file, 'a')
#     print >> output, incoming_address
