#!/usr/bin/env python

import os
from philologic.DB import DB
import sys
import socket
import re
import hashlib
import time
import socket, struct
from wsgi_handler import WSGIHandler


# These should always be allowed for local access
local_blocks = ["10.0.0.0/8",
              "172.16.0.0/12",
              "192.168.0.0/16",
              "127.0.0.1/32"]

def check_access(environ, config, db):
    incoming_address = environ['REMOTE_ADDR']
    access = {}
    access_file = config.db_path + '/data/' + config['access_file']
    if not access_file:
        return make_token(incoming_address, db)
    if not os.path.isfile(access_file):
        return make_token(incoming_address, db)
    else:
        try:
            execfile(access_file, globals(), access)
        except:
            return ()
        # We would add whatever other IPs have been defined in the access_file to blocks
        blocks = local_blocks
        for block in blocks:
            if addr_in_cidr(incoming_address, block):
                return make_token(incoming_address, db)
        
        try:
            domain_list = set(access["domain_list"])
        except:
            return () ## No allowed domains, so access request denied
        try:
            blocked_ips = set(access["blocked_ips"])
        except:
            blocked_ips = []
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
        
def login_access(environ, config, db, headers):
    request = WSGIHandler(db, environ)
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
                    headers.append( ("Set-Cookie", "hash=%s" % h) )
                    headers.append( ("Set-Cookie", "timestamp=%s" % ts) )
        else:
            access = False
    return access, headers

def check_login_info(config, request):
    try:
        password_file = open(config.db_path + "/data/logins.txt")
    except IOError:
        return (True, default_reports)
    access = False
    for line in password_file:
        fields = line.strip().split('\t')
        user = fields[0]
        passwd = fields[1]
        if user == request.username:
            if passwd == request.password:
                access = True
                break
            else:
                access = False
                break
    return access

def make_token(incoming_address, db):
    h = hashlib.md5()
    h.update(incoming_address)
    now = str(time.time())
    h.update(now)
    secret = db.locals.secret
    h.update(secret)
    return (h.hexdigest(), now)

## Adapted from http://code.activestate.com/recipes/66517/ 
## Fixed LOTS of bugs.

def dottedQuadToNum(ip):
    "convert decimal dotted quad string to long integer"
    return struct.unpack('!I',socket.inet_aton(ip))[0]

def numToDottedQuad(n):
    "convert long int to dotted quad string"
    return socket.inet_ntoa(struct.pack('!I',n))
      
def makeMask(n):
    "return a mask of n bits as a long integer"
    return ((2L<<n-1)-1) << (32-n)

def ipToNetAndHost(ip, maskbits):
    "returns tuple (network, host) dotted-quad addresses given IP and mask size"
    # (by Greg Jorgensen)

    n = dottedQuadToNum(ip)
    m = makeMask(maskbits)

    host = n & m
    net = n - host

    return numToDottedQuad(net), numToDottedQuad(host)

def addr_in_cidr(addr,block):
    ip,l = block.split("/")
    block_host, block_prefix = ipToNetAndHost(ip,int(l))
    addr_host, addr_prefix = ipToNetAndHost(addr,int(l))
    # print "Block:", block_host, block_prefix
    # print "Address:", addr_host, addr_prefix
    return block_prefix == addr_prefix