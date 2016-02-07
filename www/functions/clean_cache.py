#! /usr/bin/env python

import os
import datetime
from random import randint

def clean_hitlists():
    if randint(0,1000) == 0:
        path = os.path.abspath(os.path.dirname(__file__)).replace('functions', '') + '/data/hitlists/'
        for filename in [path + i for i in os.listdir(path)]:
            file_modified = datetime.datetime.fromtimestamp(os.path.getmtime(filename))
            if datetime.datetime.now() - file_modified > datetime.timedelta(hours=1):
                os.remove(filename)
        return True
    else:
        return False
