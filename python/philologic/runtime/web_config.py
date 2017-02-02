#!/usr/bin/env python3


from philologic.Config import MakeWebConfig


class brokenConfig(object):
    def __init__(self, db_path, traceback):
        self.production = True
        self.db_path = db_path
        self.theme = 'default_theme.css'
        self.valid_config = False
        self.traceback = traceback


def WebConfig(db_path):
    try:
        return MakeWebConfig(db_path + '/data/web_config.cfg')
    except Exception as exception:
        traceback = str(exception)
        return brokenConfig(db_path, traceback)
