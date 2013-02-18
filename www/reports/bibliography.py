#!/usr/bin/env python

from render_template import render_template

def bibliography(f,path, db, dbname, q, environ):
    if q["no_q"]:
        hits = db.get_all("doc")
    else:
        hits = db.query(**q["metadata"])
    return render_template(results=hits,db=db,dbname=dbname,q=q, template_name='bibliography.mako',f=f)
