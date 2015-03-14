#!/usr/bin/env python

import os
from philologic.DB import DB
import sys
import socket
import re


def check_access(environ, config):
    incoming_address = environ['REMOTE_ADDR']
    if previous_access_cleared(incoming_address, config.dbname):
        return False  # We disable access control
    else:
        access = {}
        access_file = config.db_path + '/data/' + config['access_file']
        if not os.path.isfile(access_file):
            return True  # We deny access if no file is provided
        else:
            execfile(access_file, globals(), access)
            domain_list = set(access["domain_list"])
            blocked_ips = set(access["blocked_ips"])

            fq_domain_name = socket.getfqdn(incoming_address).split(',')[-1]
            edit_domain = re.split('\.', fq_domain_name)

            ## this if is probably an unnecessary step, oh well... ##
            if re.match('edu', edit_domain[-1]):
                match_domain = '.'.join([edit_domain[-2], edit_domain[-1]])
                print >> sys.stderr, "MATCH DOMAIN:", match_domain
            else:
                if len(edit_domain) == 2:
                    match_domain = '.'.join([edit_domain[-2], edit_domain[-1]])
                    print >> sys.stderr, "MATCH DOMAIN:", match_domain
                else:
                    match_domain = fq_domain_name
                    print >> sys.stderr, "MATCH DOMAIN:", match_domain

            access_control = True
            print >> sys.stderr, "HERE", incoming_address, access["domain_list"]
            if incoming_address not in blocked_ips:
                if incoming_address in domain_list or match_domain in domain_list:
                    access_control = False  # We disable access control
                    save_access(environ["REMOTE_ADDR"], config.dbname)
            return access_control


def previous_access_cleared(incoming_address, dbname):
    session_file = "/tmp/%s" % '_'.join(dbname.split())
    if os.path.isfile(session_file):
        tmp_file = open(session_file)
        previously_cleared = False
        for line in tmp_file:
            ip = line.strip()
            if ip == incoming_address:
                previous_cleared = True
                break
        return previous_cleared
    else:
        return False


def save_access(incoming_address, dbname):
    session_file = "/tmp/%s" % '_'.join(dbname.split())
    output = open(session_file, 'a')
    print >> output, incoming_address
