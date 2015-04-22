#! /usr/bin/env python

import os
from philologic.Config import MakeWebConfig


def WebConfig():
    db_path = os.path.abspath(os.path.dirname(__file__)).replace('functions', '')
    return MakeWebConfig(db_path + '/data/web_config.cfg')
