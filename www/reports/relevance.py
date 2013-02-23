#!/usr/bin/env python

from __future__ import division
import sys
sys.path.append('..')
import functions as f
import sqlite3
import os
from functions.wsgi_handler import wsgi_response
from math import log
from philologic.DB import DB
from functions.format import adjust_bytes, chunkifier, clean_text, align_text
from bibliography import bibliography
import re
from render_template import render_template
import subprocess


def relevance(environ,start_response):
    db, dbname, path_components, q = wsgi_response(environ,start_response)
    path = os.getcwd().replace('functions/', '')
    
    if q['q'] == '':
        return bibliography(f,path, db, dbname,q,environ)
    else:
        results = retrieve_hits(q, db)
    return render_template(results=results,db=db,dbname=dbname,q=q,fetch_relevance=fetch_relevance,f=f,format=format,
                                path=path, results_per_page=q['results_per_page'], template_name='relevance.mako')

def filter_hits(q, obj_types, c):
    ## Filter out if necessary
    philo_ids = []
    total_docs = int
    for field in q['metadata']:
        if field != 'n' and q['metadata'][field] != '':
            for obj_type in obj_types:
                query = 'select philo_id from toms where %s=? and philo_type=?' % field
                c.execute(query, (q['metadata'][field], obj_type))
                results = [i[0] for i in c.fetchall()]
                philo_ids.extend(results)
    if philo_ids:
        philo_ids = set(philo_ids)
        total_docs = len(philo_ids)
    else:
        query = 'select count(*) from toms where '
        query += ' or '.join(['philo_type="%s"' % i for i in obj_types])
        query += ' and philo_name != "__philo_virtual"'
        c.execute(query)
        total_docs = int(c.fetchone()[0])
    return philo_ids, total_docs

def compute_idf(query_words, table, c, total_docs):
    ## Compute IDF
    idfs = {}
    for word in query_words.split():
        c.execute('select count(*) from %s where philo_name=?' % table, (word,))
        docs_with_word = int(c.fetchone()[0]) or 1  ## avoid division by 0
        doc_freq = total_docs / docs_with_word
        if doc_freq == 1:
            doc_freq = (total_docs + 1) / docs_with_word ## The logarithm won't be equal to 0
        idf = log(doc_freq)
        idfs[word] = idf
    return idfs

def retrieve_hits(q, db):
    object_types = ['doc', 'div1', 'div2', 'div3', 'para', 'sent', 'word']
    obj_types = db.locals['ranked_relevance_objects']
    table = "ranked_relevance"
    
    ## Open cursors for sqlite tables
    conn = db.dbh
    c = conn.cursor()
    philo_ids, total_docs = filter_hits(q, obj_types, c)
    
    query_words = q['q'].replace('|', ' ') ## Handle ORs from crapser
    q['q'] = q['q'].replace(' ', '|') ## Add ORs for search links
    
    idfs = compute_idf(query_words, table, c, total_docs)
    
    ## Perform search on the text
    c.execute('select * from %s limit 1' % table)
    fields = ['%s.' % table + i[0] for i in c.description] + ['toms.word_count']
    if len(query_words.split()) > 1:
        query = 'select %s from %s inner join toms on toms.philo_id=%s.philo_id and toms.philo_name!="__philo_virtual" where ' % (','.join(fields), table, table)
        words =  query_words.split()
        query += ' or '.join(['%s.philo_name=?' % table for i in words])
        c.execute(query, words)
    else:
        query = 'select %s from %s inner join toms on toms.philo_id=%s.philo_id and toms.philo_name!="__philo_virtual" where %s.philo_name=?' % (','.join(fields),table, table, table)
        c.execute(query, (query_words,))
    
    results = {}
    for i in c.fetchall():
        philo_id = i['philo_id']
        philo_name = i['philo_name']
        token_counts = i['token_count']
        bytes = i['bytes']
        word_count = i['word_count']
        if not philo_ids or philo_id in philo_ids:
            total_word_count = int(word_count)
            term_frequency = token_counts/total_word_count
            tf_idf = term_frequency * idfs[philo_name]
            if philo_id not in results:
                results[philo_id] = {}
                results[philo_id]['obj_type'] = object_types[philo_id.split().index('0') - 1]
                results[philo_id]['bytes'] = []
                results[philo_id]['tf_idf'] = 0
            results[philo_id]['tf_idf'] += tf_idf
            results[philo_id]['bytes'].extend(bytes.split())
            
    ## Perform search on metadata
    token_regex = db.locals["word_regex"] + "|" + db.locals["punct_regex"] + '| '
    query_words = unicode(query_words, 'utf-8')
    my_words = '|'.join(set([w for w in re.split(token_regex, query_words, re.U) if w]))
    word_reg = re.compile(r"\b%s\b" % my_words, re.U)
    metadata = ','.join([m for m in q['metadata']])
    query = 'select philo_id, %s from metadata_relevance' % metadata
    metadata_list = [i for i in c.execute(query)]
    for i in metadata_list:
        metadata_string = ' '.join([i[m] or '' for m in q['metadata']]).decode('utf-8', 'ignore').lower()
        matches = [w.encode('utf-8', 'ignore') for w in word_reg.findall(metadata_string)]
        if matches:
            philo_id = i['philo_id']
            if philo_id in results:
                for match in matches:
                    results[philo_id]['tf_idf'] += idfs[match] * 100
            elif philo_id in philo_ids or not philo_ids:
                results[philo_id] = {}
                results[philo_id]['obj_type'] = object_types[philo_id.split().index('0') - 1]
                results[philo_id]['bytes'] = []
                results[philo_id]['tf_idf'] = 0
                for match in matches:
                    results[philo_id]['tf_idf'] += idfs[match] * 100
    
    if philo_ids:
        hits = sorted(results.iteritems(), key=lambda x: x[1]['tf_idf'], reverse=False)  ## This is weird...
    else:
        hits = sorted(results.iteritems(), key=lambda x: x[1]['tf_idf'], reverse=True)
    return ResultsWrapper(hits, db)

 
def fetch_relevance(hit, path, q, samples=10):
    length = 75
    text_snippet = []
    byte_sample = hit.bytes[:samples]
    for byte in byte_sample: 
        byte = [int(byte)]
        bytes, byte_start = adjust_bytes(byte, length)
        conc_text = f.get_text(hit, byte_start, length, path)
        conc_start, conc_middle, conc_end = chunkifier(conc_text, bytes, highlight=True)
        conc_start = clean_text(conc_start)
        conc_end = clean_text(conc_end)
        conc_text = (conc_start + conc_middle + conc_end).decode('utf-8', 'ignore')
        text_snippet.append(conc_text)
    text = ' ... '.join(text_snippet)
    return text
    
  
class ResultsWrapper(object):
    
    def __init__(self, sqlhits, db):
        self.sqlhits = sqlhits
        self.db = db
        self.done = True
    
    def __getitem__(self,n):
        if isinstance(n,slice):
            hits = self.sqlhits[n]
            return [f.IRHitWrapper.HitWrapper(philo_id.split(), self.db, hit['bytes'], hit['obj_type']) for philo_id, hit in hits]
    
    def __iter__(self):
        for philo_id, hit in self.sqlhits:
            yield f.IRHitWrapper.HitWrapper(philo_id.split(), self.db, hit['bytes'], hit['obj_type'])
        
    def __len__(self):
        return len(self.sqlhits)  
