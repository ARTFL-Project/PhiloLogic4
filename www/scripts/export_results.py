#!/usr/bin/env python

import os
import sys
sys.path.append('..')
from functions.wsgi_handler import WSGIHandler
from philologic.DB import DB
from wsgiref.handlers import CGIHandler
from reports.concordance import citation_links, concordance_citation, fetch_concordance
import functions as f
import cgi
import json
import csv
import uuid


def export_results(environ,start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/octet-stream'),("Access-Control-Allow-Origin","*")]
    start_response(status,headers)
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)
    #output_format = request.output_format
    
    if request.report == "concordance" or not request.report:
        export_concordance(db, config, request)

    #unique_filename = str(uuid.uuid4())
    #if output_format == "json":
    #    write_json(path, unique_filename, results_string)
    #    link = config.db_url + "/data/exports/" + unique_filename + ".json"
    #elif output_format == "csv":
    #    write_csv(path, unique_filename, flat_list)
    #    link = config.db_url + "/data/exports/" + unique_filename + '.csv'
    #elif output_format == "tab":
    #    write_tab(path, unique_filename, flat_list)
    #    link = config.db_url + "/data/exports/" + unique_filename + '.tab'
    #yield link

def export_concordance(db, config, q):
    hits = db.query(q["q"],q["method"],q["arg"],**q.metadata)
    results_list = []
    flat_list = [["citation", "text"]]
    for hit in hits:
        citation_hrefs = citation_links(db, config, hit)
        citation = concordance_citation(hit, citation_hrefs).encode('utf-8')
        text = fetch_concordance(db, hit, config.db_path, config.concordance_length).encode('utf-8')
        if q.output_format == "json":
            print json.dumps({"text": text, "citation": citation})
        elif q.output_format == "tab":
            print citation + '\t' + text

    
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
