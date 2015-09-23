#!/usr/bin/env python

import sys
sys.path.append('..')
import functions as f
from functions.wsgi_handler import WSGIHandler
from bibliography import bibliography
from functions.ObjectFormatter import format_strip, convert_entities, adjust_bytes
from functions.FragmentParser import parse
import philologic.MetadataQuery as MQ

def make_frequency_query(db,metadata):
    print >> sys.stderr, "METADATA",metadata
    metadata_dicts = [{} for level in db.locals["metadata_hierarchy"]]
#                print >> sys.stderr, "querying %s" % repr(metadata.items())
    for k,v in metadata.items():
        for i, params in enumerate(db.locals["metadata_hierarchy"]):
            if v and (k in params):
                if isinstance(v,str):
                    metadata_dicts[i][k] = [v]
                else:
                    metadata_dicts[i][k] = v
                if k in db.locals["metadata_types"]:
                    this_type = db.locals["metadata_types"][k]
                    if this_type == "div":
                        metadata_dicts[i]["philo_type"] = ['"div"|"div1"|"div2"|"div3"']
                    else:
                        metadata_dicts[i]["philo_type"] = ['"%s"' % db.locals["metadata_types"][k]]
    metadata_dicts = [d for d in metadata_dicts if d]
    print >> sys.stderr, "METDATA_DICTS",metadata_dicts
    if metadata_dicts:
        params = metadata_dicts[0].items()
        vars = []
        clauses = []
        for column,values in params:
#            values = [values]
            norm_path = db.locals["db_path"]+"/frequencies/normalized_" + column + "_frequencies"
            for v in values:
                parsed = MQ.parse_query(v)
                clause,some_vars = MQ.make_clause(column,parsed,norm_path)
                clauses.append(clause)
                vars += some_vars
        print >> sys.stderr, "CLAUSES",clauses
        print >> sys.stderr, "VARS",vars
        if clauses:
            inner_query = "SELECT philo_id FROM toms WHERE " + " AND ".join("(%s)" % c for c in clauses) + ""
            query = "SELECT philo_name,count(*) as c FROM words WHERE doc_ancestor IN (%s) group by philo_name ORDER BY count(*) DESC;" % inner_query
            for row in db.dbh.execute(query,vars):
                print >> sys.stderr, query
                yield row["philo_name"] + " " + str(row["c"]) + "<br/>"
            return
    # only get here if we have no parameters, since we return above.
    for row in open(db.locals["db_path"]+"/frequencies/word_frequencies"):
#            print >> sys.stderr, row
        yield row + "<br/>"

def frequencies(environ,start_response):
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)
#    results = prominent_features(q, db)
    res = ""
    count = 0
    res = []
    for result in make_frequency_query(db,request.metadata):
#        print >> sys.stderr,result
        res.append(result)
        count += 1
        if count > 1000:
            break
    #hits = db.query(q["q"],q["method"],q["arg"],**q["metadata"])
    #return render_template(results=hits,db=db,dbname=dbname,q=q,fetch_concordance=fetch_concordance,
    #                       f=f, path=path, results_per_page=q['results_per_page'],
    #                       template_name="concordance.mako")
    return ""#f.render_template(results=res,db=db,dbname=config.db_name,q=q,f=f,template_name="frequencies.mako", report="frequencies")

def prominent_features(q):
    conn = db.dbh
    c = conn.cursor()
