#!/usr/bin/env python

from __future__ import absolute_import
from philologic.Config import MakeWebConfig


class brokenConfig(object):
    def __init__(self, db_path, traceback):
        self.production = True
        self.db_path = db_path
        self.theme = 'default_theme.css'
        self.valid_config = False
        self.traceback = traceback
        self.global_config_location = "/etc/philologic/philologic4.cfg"


def WebConfig(db_path):
    try:
        return MakeWebConfig(db_path + '/data/web_config.cfg')
    except Exception as e:
        traceback = str(e)
        return brokenConfig(db_path, traceback)
