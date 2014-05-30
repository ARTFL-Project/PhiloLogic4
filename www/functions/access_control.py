#!/usr/bin/env python

from os.path import dirname
from philologic.DB import DB
import sqlite3
import sys
import socket
import re

def access_control(environ,start_response):
    dbfile = dirname(environ["SCRIPT_FILENAME"]) + '/data'
    db = DB(dbfile,encoding='utf-8')
    if "open_access" in db.locals:  ## failsafe in case the variable is not db.locals.py
        if db.locals['open_access']:
            return True
        else:
            access_value = check_access(db, environ)
            return access_value
    else:
        return True

    
def check_access(db, environ):
    access_db = db.locals['access_db']
    conn = sqlite3.connect(access_db)
    c = conn.cursor()
    
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


    c.execute('SELECT access_value FROM domain_list WHERE client_address  = \'' + incoming_address + '\' OR client_address = \'' + match_domain + '\'')

    access_response = c.fetchall()

    print >> sys.stderr, "SQL ACCESS RESPONSE: ", access_response

    if not access_response:
        return False
    else:
        return True