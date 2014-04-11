#!/usr/bin/env python

from __future__ import division
import sys
sys.path.append('..')
import functions as f
import sqlite3
import os
from functions.wsgi_handler import wsgi_response
from math import log10, floor
from random import sample
from philologic.DB import DB
from philologic.QuerySyntax import parse_query
from philologic.Query import word_pattern_search
from functions.ObjectFormatter import format_strip, convert_entities, adjust_bytes
from bibliography import fetch_bibliography as bibliography
import re
import subprocess
import unicodedata
from render_template import render_template
from collections import defaultdict


def relevance(environ,start_response):
    db, dbname, path_components, q = wsgi_response(environ,start_response)
    path = os.getcwd().replace('functions/', '')
    
    if q['q'] == '':
        return bibliography(f,path, db, dbname,q,environ)
    else:
        results = retrieve_hits(q, db)
    return render_template(results=results,db=db,dbname=dbname,q=q,fetch_relevance=fetch_relevance,
                           f=f,format=format,path=path, results_per_page=q['results_per_page'],javascript="rankedRelevance.js",
                           template_name='relevance.mako', report='relevance')

def format_query(q, db):
    parsed = parse_query(q)
    parsed_split = []
    for label,token in parsed:
        l,t = label,token
        if l == "QUOTE":
            subtokens = t[1:-1].split(" ")
            parsed_split += [("QUOTE_S",sub_t) for sub_t in subtokens if sub_t]
        else:
            parsed_split += [(l,t)]
    
    output_string = []
    prior_label = "OR"
#        print parsed_split
    for label, token in parsed_split:
        if label == "QUOTE_S":
            output_string += token.split()
        elif label == "TERM":
            expanded = []
            norm_tok = token.decode("utf-8").lower()
            norm_tok = [i for i in unicodedata.normalize("NFKD",norm_tok) if not unicodedata.combining(i)]
            norm_tok = "".join(norm_tok).encode("utf-8")
            matches = word_pattern_search(norm_tok,db.locals["db_path"]+"/frequencies/normalized_word_frequencies")              
            for m in matches:
                if m not in expanded:
                    expanded += [m]                                              
            output_string += expanded
#            print >> sys.stderr, expanded
    return output_string


def filter_hits(q, obj_types, c):
    ## Filter out if necessary
    philo_ids = []
    total_docs = int
    fields = [f for f in q['metadata'] if q['metadata'][f]]
    metadata = [q['metadata'][j] for j in fields]
    query = 'select philo_id from toms where ' + ' and '.join([i + '=?' for i in fields])
    if fields:
        for obj_type in obj_types:
            q = query + 'and philo_type=?'
            c.execute(q, metadata + [obj_type])
            philo_ids = [i[0] for i in c.fetchall()]
        philo_ids = set(philo_ids)
    return philo_ids

def compute_idf(query_words, c, total_docs):
    ## Compute IDF
    idfs = {}
    for word in query_words.split():
        c.execute('select count(*) from ranked_relevance where philo_name=?', (word,))
        docs_with_word = int(c.fetchone()[0]) or 1  ## avoid division by 0
        doc_freq = total_docs / docs_with_word
        if doc_freq == 1:
            doc_freq = (total_docs + 1) / docs_with_word ## The logarithm won't be equal to 0
        idf = log10(doc_freq)
        idfs[word] = idf
    return idfs

def bm25(tf, dl, avg_dl, idf, k1=1.6, b=0.6):
    temp_score = tf * k1
    temp_score2 = tf + k1 * ((1.0 - b) + b * dl / avg_dl)
    score = idf * temp_score / temp_score2
    return score

def retrieve_hits(q, db):
    object_types = ['doc', 'div1', 'div2', 'div3', 'para', 'sent', 'word']
    obj_types = db.locals['freq_object_levels']
    table = "ranked_relevance"
    
    ## Open cursors for sqlite tables
    conn = db.dbh
    c = conn.cursor()
    
    ## Count all docs in corpus
    c.execute('select count(philo_id) from metadata_relevance')
    total_docs = int(c.fetchone()[0])
    
    ## Limit search according to metadata
    philo_ids = []#filter_hits(q, obj_types, c)
    
    ## TEMPORARY ###
    q['q'] = ' '.join(format_query(q['q'], db))
    #q['q'] = ' '.join(re.split('\s', format_query(q['q'], db))) ## ask Richard about this
    query_words = q['q'][:].strip()
    q['q'] = q['q'].replace(' ', '|') ## Add ORs for search links
    print >> sys.stderr, "QS", repr(query_words)
    
    idfs = compute_idf(query_words, c, total_docs)
    
    ## Compute average doc length
    path = db.locals['db_path'] + '/frequencies/word_frequencies'
    command = ["egrep", "-c", ".*", path]
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    unique_words = int(process.communicate()[0].strip())
    avg_dl = total_docs / unique_words
    
    ## Perform search on the text
    c.execute('select * from %s limit 1' % table)
    fields = ['%s.' % table + i[0] for i in c.description] + ['toms.word_count']
    if len(query_words.split()) > 1:
        query = 'select %s from %s inner join toms on toms.philo_id=%s.philo_id where ' % (','.join(fields), table, table)
        words =  query_words.split()
        query += ' or '.join(['%s.philo_name=?' % table for i in words])
        c.execute(query, words)
    else:
        query = 'select %s from %s inner join toms on toms.philo_id=%s.philo_id where %s.philo_name=?' % (','.join(fields),table, table, table)
        c.execute(query, (query_words,))
    
    results = {}
    intersect = {}
    for i in c.fetchall():
        philo_id = i['philo_id']
        if not philo_ids or philo_id in philo_ids:
            philo_name = i['philo_name']
            tf = int(i['token_count'])
            bytes = i['bytes']
            dl = int(i['word_count'])
            score = bm25(tf, dl, avg_dl, idfs[philo_name])
            if philo_id not in results:
                results[philo_id] = {}
                results[philo_id]['obj_type'] = object_types[philo_id.split().index('0') - 1]
                results[philo_id]['bytes'] = []
                results[philo_id]['score'] = 0
                results[philo_id]['match'] = 0
            results[philo_id]['match'] += 1
            results[philo_id]['score'] += score
            ## Boost score if more than one query word is in the document
            if results[philo_id]['match'] > 1:
                results[philo_id]['score'] *= results[philo_id]['match'] + 1000
            results[philo_id]['bytes'].extend(bytes.split())
        
    ## Perform search on metadata
    # Look for exact matches
    perfect_match = set()
    for q_word in query_words.split():
        for metadata in db.locals["metadata_fields"]:
            query = ('select philo_id from metadata_relevance where %s=? COLLATE NOCASE' % metadata)
            c.execute(query, (q_word,))
            for i in c.fetchall():
                if i['philo_id'] in results:
                    results[i['philo_id']]['score'] = results[i['philo_id']]['score'] * 1000
                else:
                    results[i['philo_id']] = {}
                    results[i['philo_id']]['obj_type'] = object_types[i['philo_id'].split().index('0') - 1]
                    results[i['philo_id']]['bytes'] = []
                    results[i['philo_id']]['score'] = bm25(1, len(q_word), avg_dl, idfs[q_word]) * 1000
                perfect_match.add(i['philo_id'])
    # Look for matches in the metadata string
    token_regex = db.locals["word_regex"] + "|" + db.locals["punct_regex"] + '| '
    query_words = unicode(query_words, 'utf-8')
    my_words = '|'.join(set([w for w in re.split(token_regex, query_words, re.U) if w]))
    if my_words:
        word_reg = re.compile(r"\b%s\b" % my_words, re.U)
        metadata = ','.join([m for m in db.locals["metadata_fields"]])
        query = 'select philo_id, %s from metadata_relevance' % metadata
        metadata_list = [i for i in c.execute(query)]
        for i in metadata_list:
            philo_id = i['philo_id']
            metadata_string = ' '.join([i[m] or '' for m in db.locals["metadata_fields"]]).decode('utf-8', 'ignore').lower()
            matches = [w.encode('utf-8', 'ignore') for w in word_reg.findall(metadata_string)]
            if matches:
                metadata_length = len(metadata_string)
                if philo_id in results:
                    for match in matches:
                        if match: # not an empty string
                            try:
                                results[philo_id]['score'] += bm25(20, metadata_length, avg_dl, idfs[match])
                            except KeyError:
                                pass
                    if len(matches) > 1:
                        results[philo_id]['score'] *= len(matches) + 1000
                elif philo_id in philo_ids or not philo_ids:
                    results[philo_id] = {}
                    results[philo_id]['obj_type'] = object_types[philo_id.split().index('0') - 1]
                    results[philo_id]['bytes'] = []
                    results[philo_id]['score'] = 0
                    for match in matches:
                        if match: # not an empty string
                            try:
                                results[philo_id]['score'] += bm25(100, metadata_length, avg_dl, idfs[match])
                            except KeyError:
                                pass
                    if len(matches) > 1:
                        results[philo_id]['score'] *= len(matches) + 1000
        
        
        hits = sorted(results.iteritems(), key=lambda x: x[1]['score'], reverse=True)
    else:
        hits = []
    return ResultsWrapper(hits, db)


 
def fetch_relevance(hit, path, q, samples=10):
    length = 75
    text_snippet = []
    hit_num = len(hit.bytes)
    if hit_num < samples:
        byte_sample = sorted(sample(hit.bytes, hit_num))
    else:
        byte_sample = sorted(sample(hit.bytes, samples))
    if hit_num and hit_num < samples:
        length = int(length * samples / hit_num)
    for byte in byte_sample: 
        byte = [int(byte)]
        bytes, byte_start = adjust_bytes(byte, length)
        conc_text = f.get_text(hit, byte_start, length, path)
        conc_text = format_strip(conc_text, bytes)
        conc_text = convert_entities(conc_text)
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
