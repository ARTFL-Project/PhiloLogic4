#!/usr/bin/env python

import os
import sys
import urlparse
sys.path.append('..')
from functions.wsgi_handler import parse_cgi
from wsgiref.handlers import CGIHandler
import reports as r
import functions as f
import cgi
import json
import csv
import uuid


def export_results(environ,start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/plain; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response(status,headers)
    environ["SCRIPT_FILENAME"] = environ["SCRIPT_FILENAME"].replace('scripts/export_results.py', '')
    cgi = urlparse.parse_qs(environ["QUERY_STRING"],keep_blank_values=True)
    output_format = cgi.get('output_format',[''])[0]
    db, path_components, q = parse_cgi(environ)
    config = f.WebConfig()
    path = os.path.abspath(os.path.dirname(__file__)).replace('scripts', "")
    
    if q['report'] == "concordance" or q['report'] == None:
        results_string, flat_list = export_concordance(db, config, q, path)

    unique_filename = str(uuid.uuid4())
    if output_format == "json":
        write_json(path, unique_filename, results_string)
        link = config.db_url + "/data/exports/" + unique_filename + ".json"
    elif output_format == "csv":
        write_csv(path, unique_filename, flat_list)
        link = config.db_url + "/data/exports/" + unique_filename + '.csv'
    elif output_format == "tab":
        write_tab(path, unique_filename, flat_list)
        link = config.db_url + "/data/exports/" + unique_filename + '.tab'
    yield link

def export_concordance(db, config, q, path):
    hits = db.query(q["q"],q["method"],q["arg"],**q["metadata"])
    results_list = []
    flat_list = [["citation", "text"]]
    for i in hits:
        citation = f.concordance_citation(db, config, i)
        text = r.fetch_concordance(i, path, config.concordance_length)
        results_list.append({"citation": citation, "text": text})
        flat_list.append([citation.encode('utf-8'), text.encode('utf-8')])
    return results_list, flat_list
    
def write_json(path, unique_filename, results):
    output = open(path + "/data/exports/" + unique_filename + '.json', 'w')
    output.write(json.dumps(results))
    output.close()

def write_csv(path, unique_filename, results):
    output = open(path + "/data/exports/" + unique_filename + '.csv', 'wb')
    writer = csv.writer(output)
    for i in results:
        writer.writerow(i)
    output.close()

def write_tab(path, unique_filename, results):
    output = open(path + "/data/exports/" + unique_filename + '.tab', 'w')
    for i in results:
        i = [j.replace('\n', '').replace('\t', '') for j in i]
        row = '\t'.join(i) + '\n'
        output.write(row)
    output.close()

if __name__ == "__main__":
    CGIHandler().run(export_results)
