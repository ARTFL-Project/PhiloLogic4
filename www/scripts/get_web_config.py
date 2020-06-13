#!/usr/bin/env python3

import os
import sqlite3
from wsgiref.handlers import CGIHandler

import sys

sys.path.append("..")
import custom_functions

try:
    from custom_functions import WebConfig
except ImportError:
    from philologic.runtime import WebConfig

from philologic.Config import MakeDBConfig
from philologic.runtime.DB import DB


def get_web_config(_, start_response):
    status = "200 OK"
    headers = [("Content-type", "application/json; charset=UTF-8"), ("Access-Control-Allow-Origin", "*")]
    start_response(status, headers)
    db_path = os.path.abspath(os.path.dirname(__file__)).replace("scripts", "")
    config = WebConfig(db_path)
    config.time_series_status = time_series_tester(config)
    db_locals = MakeDBConfig(os.path.join(db_path, "data/db.locals.py"))
    config.data["available_metadata"] = db_locals.metadata_fields
    yield config.to_json().encode("utf8")


def time_series_tester(config):
    """Test if we have at least two distinct values for time series"""
    frequencies_file = os.path.join(config.db_path, f"frequencies/{config.time_series_year_field}_frequencies")
    if os.path.exists(frequencies_file):
        with open(frequencies_file) as input_file:
            line_count = sum(1 for _ in input_file)
        if line_count > 1:
            return True
    return False


if __name__ == "__main__":
    CGIHandler().run(get_web_config)
