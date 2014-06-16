#!/usr/bin/env python

import os
from philologic.DB import DB
import sys
import socket
import re

def access_control(environ,start_response):
    path = os.path.abspath(os.path.dirname(__file__)).replace('functions', '') + '/data/'
    db = DB(path,encoding='utf-8')
    if "open_access" in db.locals:  ## failsafe in case the variable is not db.locals.py
        if db.locals['open_access']:
            return True
        else:
            access_value = check_access(db, environ)
            return access_value
    else:
        return True

    
def check_access(db, environ):
    access = {}
    access_file = db.locals['access_file']
    execfile(access_file, globals(), access)
    domain_list = set(access["domain_list"])
    blocked_ips = set(access["blocked_ips"])
    
    incoming_address = environ['REMOTE_ADDR']
    fq_domain_name = socket.getfqdn(incoming_address).split(',')[-1]
    edit_domain = re.split('\.',fq_domain_name)

    ## this if is probably an unnecessary step, oh well... ##
    if re.match('edu',edit_domain[-1]):
        match_domain = '.'.join([edit_domain[-2],edit_domain[-1]])
        print >> sys.stderr, "MATCH DOMAIN:", match_domain
    else:
        if len(edit_domain) == 2:
                match_domain = '.'.join([edit_domain[-2],edit_domain[-1]])
                print >> sys.stderr, "MATCH DOMAIN:", match_domain
        else:
                match_domain = fq_domain_name
                print >> sys.stderr, "MATCH DOMAIN:", match_domain
    
    access_response = False
    if incoming_address not in blocked_ips:
        if incoming_address in domain_list or match_domain in domain_list:
            access_response = True

    print >> sys.stderr, "ACCESS RESPONSE: ", access_response

    return access_response