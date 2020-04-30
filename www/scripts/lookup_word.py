#!/usr/bin/env python3

import rapidjson
import os
import sqlite3
import sys
from wsgiref.handlers import CGIHandler

from philologic5.runtime.DB import DB
from philologic5.runtime import adjust_bytes

import sys

sys.path.append("..")
import custom_functions

try:
    from custom_functions import WebConfig
except ImportError:
    from philologic5.runtime import WebConfig
try:
    from custom_functions import WSGIHandler
except ImportError:
    from philologic5.runtime import WSGIHandler


def lookup_word_service(environ, start_response):
    status = "200 OK"
    headers = [("Content-type", "application/json; charset=UTF-8"), ("Access-Control-Allow-Origin", "*")]
    start_response(status, headers)
    config = WebConfig(os.path.abspath(os.path.dirname(__file__)).replace("scripts", ""))
    db = DB(config.db_path + "/data/")
    request = WSGIHandler(environ, config)
    cursor = db.dbh.cursor()

    if request.report == "concordance":
        hits = db.query(request["q"], request["method"], request["arg"], **request.metadata)
        context_size = config["concordance_length"] * 3
        hit = hits[int(request.position)]
        bytes = hit.bytes
        hit_span = hit.bytes[-1] - hit.bytes[0]
        length = context_size + hit_span + context_size
        bytes, start_byte = adjust_bytes(bytes, length)
        end_byte = start_byte + length
        filename = hit.filename
        token = request.selected
    elif request.report == "navigation":

        token = request.selected
        philo_id = request.philo_id.split(" ")
        text_obj = db[philo_id]
        start_byte, end_byte = int(text_obj.start_byte), int(text_obj.end_byte)
        filename = text_obj.filename
    #        print >> sys.stderr, "WORD LOOKUP FROM NAVIGATION", request.philo_id,request.selected, start_byte, end_byte, filename
    else:
        pass
    #    print >> sys.stderr, "TOKEN", token, "BYTES: ", start_byte, end_byte, "FILENAME: ", filename, "POSITION", request.position
    token_n = 0
    yield lookup_word(db, cursor, token, token_n, start_byte, end_byte, filename).encode("utf8")


def lookup_word(db, cursor, token, n, start, end, filename):
    i = 0
    query = "select * from words where (start_byte >= ?) and (end_byte <= ?) and (filename = ?);"
    #    print >> sys.stderr, "QUERY", query, (start,end,filename)
    cursor.execute(query, (start, end, filename))
    token_lower = token.decode("utf-8").lower().encode("utf-8")
    for row in cursor.fetchall():
        #        print >> sys.stderr, row['philo_name'], type(row['philo_name'])
        if row["philo_name"] == token_lower:

            best_parse = (row["lemma"], row["pos"])
            #            print >> sys.stderr, "BEST PARSE", best_parse
            all_parses = {}
            authority = ""
            defn = ""
            try:
                tokenid = row["tokenid"]
                lex_connect = sqlite3.connect(db.locals.db_path + "/data/lexicon.db")
                lex_cursor = lex_connect.cursor()
                auth_query = "select authority from parses where authority is not null and tokenid = ?;"
                auth_result = lex_cursor.execute(auth_query, (tokenid,)).fetchone()
                #                print >> sys.stderr, "AUTHORITY", auth_result
                if auth_result:
                    authority = auth_result[0]

                lex_query = "select Lexicon.lemma,Lexicon.code,shortdefs.def from lexicon,shortdefs where token in (select content from tokens where tokenid=?) and shortdefs.lemma=Lexicon.lemma;"
                #                lex_query = "select Lexicon.lemma,Lexicon.code,authority,shortdefs.def from parses,Lexicon,shortdefs where parses.tokenid = ? and parses.lex=Lexicon.lexid and shortdefs.lemma=Lexicon.lemma;"
                #                print >> sys.stderr, "LEX QUERY", lex_query, tokenid, token_lower
                lex_cursor.execute(lex_query, (tokenid,))

                raw_parses = []
                for parse_row in lex_cursor.fetchall():
                    p_lemma, p_pos = parse_row[0].encode("utf-8"), parse_row[1]
                    parse = (p_lemma, p_pos)
                    if not defn and parse_row[2]:
                        defn = parse_row[2]
                    #                        print >> sys.stderr, "DEFINITION:", parse_row[2];

                    if parse != best_parse:
                        #                        print>> sys.stderr, "ALTERNATE",parse, "!=", best_parse
                        raw_parses.append(parse)
                        if p_lemma not in all_parses:
                            all_parses[p_lemma] = [p_pos]
                        else:
                            all_parses[p_lemma].append(p_pos)
                    else:
                        pass
            #                        print >> sys.stderr, "BEST", parse

            except:
                pass
            if i == int(n):
                result_object = {
                    "properties": [
                        {"property": "Form", "value": token},
                        {"property": "Lemma", "value": row["lemma"]},
                        {"property": "Parse", "value": row["pos"]},
                        {"property": "Definition", "value": defn},
                        {"property": "Parsed By", "value": authority},
                    ],
                    "problem_report": "/",
                    "token": token,
                    "lemma": row["lemma"],
                    "philo_id": row["philo_id"],
                    "alt_lemma": [],
                    "dictionary_name": "Logeion",
                    "dictionary_lookup": "http://logeion.uchicago.edu/index.html#" + row["lemma"],
                    "alt_parses": [
                        {
                            "lemma": l,
                            "parse": all_parses[l],
                            "dictionary_lookup": "http://logeion.uchicago.edu/index.html#" + l,
                        }
                        for l, p in list(all_parses.items())
                    ]  # ,
                    # "alt_parses": [
                    #     {
                    #         'lemma': 'x',
                    #         'parse': ["a", "b", "c", "d"],
                    #         "dictionary_lookup":
                    #         "http://logeion.uchicago.edu/index.html#" + 'x'
                    #     }, {
                    #         'lemma': 'y',
                    #         'parse': ["e", "f", "g"],
                    #         "dictionary_lookup":
                    #         "http://logeion.uchicago.edu/index.html#" + 'y'
                    #     }
                    # ]
                }
                return rapidjson.dumps(result_object)
            else:
                i += 1
    return rapidjson.dumps({})


if __name__ == "__main__":
    if len(sys.argv) > 6:
        db = DB(sys.argv[1])
        print(db.dbh, file=sys.stderr)
        cursor = db.dbh.cursor()
        lookup_word(cursor, sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
    else:
        CGIHandler().run(lookup_word_service)
