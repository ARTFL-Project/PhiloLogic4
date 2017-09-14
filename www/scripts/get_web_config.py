#!/usr/bin/env python

import os
import sqlite3
from wsgiref.handlers import CGIHandler

from philologic.runtime import WebConfig
from philologic.Config import MakeDBConfig
from philologic.DB import DB


def get_web_config(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'), ("Access-Control-Allow-Origin", "*")]
    start_response(status, headers)
    db_path = os.path.abspath(os.path.dirname(__file__)).replace('scripts', '')
    config = WebConfig(db_path)
    config.time_series_status = time_series_tester(config)
    db_locals = MakeDBConfig(os.path.join(db_path, "data/db.locals.py"))
    config.data["available_metadata"] = db_locals.metadata_fields
    yield config.to_json()


def time_series_tester(config):
    db = DB(config.db_path + '/data/')
    c = db.dbh.cursor()
    try:
        c.execute("SELECT COUNT(*) FROM toms WHERE %s IS NOT NULL" % config.time_series_year_field)
        count = c.fetchone()[0]
        if count > 0:
            return True
        else:
            return False
    except sqlite3.OperationalError:
        return False


if __name__ == "__main__":
    CGIHandler().run(get_web_config)
