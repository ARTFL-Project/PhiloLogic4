#!/usr/bin/python
from __future__ import absolute_import
import sys,os
from ctypes import *
stdlib=cdll.LoadLibrary("libc.dylib")

stdin = stdlib.fdopen(sys.stdin.fileno(),"r")

libphilo = cdll.LoadLibrary("./libphilo.dylib")

db = libphilo.init_dbh_folder("/var/lib/philologic/databases/PerseusGreekDev/")

s = libphilo.new_search(db,"phrase",None,1,100000,0,None)

libphilo.process_input(s,stdin)


libphilo.search_pass(s,0)
