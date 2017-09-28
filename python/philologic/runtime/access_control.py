#!/usr/bin/env python

from __future__ import absolute_import, print_function
import os
import socket
import imp
import re
import hashlib
import time
import struct
import sys
from philologic.DB import DB

# These should always be allowed for local access
local_blocks = ["10.0.0.", "172.16.0.", "192.168.0.", "127.0.0."]

ip_ranges = [re.compile(r'^%s.*' % i) for i in local_blocks]


def check_access(environ, config):
    db = DB(config.db_path + '/data/')
    incoming_address, match_domain = get_client_info(environ)

    if config.access_file:
        if os.path.isabs(config.access_file):
            access_file = config.access_file
        else:
            access_file = os.path.join(config.db_path, "data", config.access_file)
        if not os.path.isfile(access_file):
            print("UNAUTHORIZED ACCESS TO: %s from domain %s" % (incoming_address, match_domain), file=sys.stderr)
            return ()
    else:
        return make_token(incoming_address, db)

    # Load access config file. If loading fails, grant access.
    try:
        access_config = imp.load_source("access_config", access_file)
    except Exception as e:
        print("ACCESS ERROR", repr(e), file=sys.stderr)
        print("UNAUTHORIZED ACCESS TO: %s from domain %s" % (incoming_address, match_domain), file=sys.stderr)
        return ()

    # Let's first check if the IP is local and grant access if it is.
    for ip_range in ip_ranges:
        if ip_range.search(incoming_address):
            return make_token(incoming_address, db)

    try:
        domain_list = set(access_config.domain_list)
    except:
        domain_list = []

    try:
        allowed_ips = set([])
        for ip in access_config.allowed_ips:
            split_numbers = ip.split('.')
            if len(split_numbers) == 4:
                if re.search(r'\d+-\d+', split_numbers[3]):
                    for last_num in range(int(split_numbers[3].split('-')[0]), int(split_numbers[3].split('-')[1])+1):
                        allowed_ips.add(".".join(split_numbers[:3]) + "." + str(last_num))
                elif re.search(r'\d+-\A', split_numbers[3]):
                    for last_num in range(int(split_numbers[3].split('-')[0]), 255):
                        allowed_ips.add(".".join(split_numbers[:3]) + "." + str(last_num))
                else:
                    allowed_ips.add(ip)
            else:
                allowed_ips.add(ip)
    except Exception as e:
        print(repr(e), file=sys.stderr)
        allowed_ips = []
    try:
        blocked_ips = set(access_config.blocked_ips)
    except:
        blocked_ips = []

    if incoming_address not in blocked_ips:
        if match_domain in domain_list:
            return make_token(incoming_address, db)
        else:
            for domain in domain_list:
                if domain in match_domain:
                    return make_token(incoming_address, db)
        for ip_range in allowed_ips:
            if re.search(r'^%s.*' % ip_range, incoming_address):
                return make_token(incoming_address, db)

    # If no token returned, we block access.
    print("UNAUTHORIZED ACCESS TO: %s from domain %s" % (incoming_address, match_domain), file=sys.stderr)
    return ()

def get_client_info(environ):
    incoming_address = environ['REMOTE_ADDR']
    fq_domain_name = socket.getfqdn(incoming_address).split(',')[-1]
    edit_domain = re.split('\.', fq_domain_name)

    if re.match('edu', edit_domain[-1]):
        match_domain = '.'.join([edit_domain[-2], edit_domain[-1]])
    else:
        if len(edit_domain) == 2:
            match_domain = '.'.join([edit_domain[-2], edit_domain[-1]])
        else:
            match_domain = fq_domain_name
    return incoming_address, match_domain

def login_access(environ, request, config, headers):
    db = DB(config.db_path + '/data/')
    if request.authenticated:
        access = True
    else:
        if request.username and request.password:
            access = check_login_info(config, request)
            if access:
                incoming_address = environ['REMOTE_ADDR']
                token = make_token(incoming_address, db)
                if token:
                    h, ts = token
                    headers.append(("Set-Cookie", "hash=%s" % h))
                    headers.append(("Set-Cookie", "timestamp=%s" % ts))
        else:
            access = False
    return access, headers


def check_login_info(config, request):
    login_file_path = os.path.join(config.db_path, "data/logins.txt")
    if os.path.exists(login_file_path):
        with open(login_file_path) as password_file:
            for line in password_file:
                line = line.strip()
                if not line: # empty line
                    continue
                fields = line.split('\t')
                user = fields[0]
                passwd = fields[1]
                if user == request.username and passwd == request.password:
                    return True
            return False
    else:
        return False


def make_token(incoming_address, db):
    h = hashlib.md5()
    h.update(incoming_address)
    now = str(time.time())
    h.update(now)
    secret = db.locals.secret
    h.update(secret)
    return (h.hexdigest(), now)
