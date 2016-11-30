#!/usr/bin/env python

from __future__ import absolute_import
from philologic.Config import MakeWebConfig


class brokenConfig(object):
    def __init__(self, db_path, traceback):
        self.production = True
        self.db_path = db_path
        self.theme = 'default_theme'
        self.valid_config = False
        self.traceback = traceback


def WebConfig(db_path):
    try:
        return MakeWebConfig(db_path + '/data/web_config.cfg')
    except Exception as e:
        traceback = str(e)
        return brokenConfig(db_path, traceback)
