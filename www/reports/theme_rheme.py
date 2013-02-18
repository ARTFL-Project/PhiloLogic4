from __future__ import division
import sys
sys.path.append('..')
import functions as f
import os
import re
from functions.wsgi_handler import wsgi_response
from bibliography import bibliography
from render_template import render_template

def theme_rheme(environ,start_response):
    db, dbname, path_components, q = wsgi_response(environ,start_response)
    path = os.getcwd().replace('functions/', '')
    if q['q'] == '':
        return bibliography(f,path, db, dbname,q,environ)
    else:
        hits = db.query(q["q"],q["method"],q["arg"],**q["metadata"])
        new_hits, full_report = adjust_results(hits, path, q)
        return render_template(results=new_hits,full_report=full_report,db=db,dbname=dbname,q=q,f=f,path=path,
                               results_per_page=q['results_per_page'], template_name="theme_rheme.mako")
                                
def theme_rheme_concordance(conc_text, bytes):
    conc_start, conc_middle, conc_end = f.format.chunkifier(conc_text, bytes, highlight=True)
    conc_start = f.format.clean_text(conc_start)
    conc_end = f.format.clean_text(conc_end)
    conc_text = conc_start + conc_middle + conc_end
    conc_text = conc_text.decode('utf-8', 'ignore')
    highlight_index = conc_text.find('<span class="highlight"')
    begin = highlight_index - 200 ## make sure the highlighted term does not get hidden
    end = highlight_index + 200
    first_span = '<span class="begin_concordance" style="display:none;">'
    second_span = '<span class="end_concordance" style="display:none;">'
    conc_text =  first_span + conc_text[:begin] + '</span>' + conc_text[begin:end] + second_span + conc_text[end:] + '</span>'
    return conc_text

def adjust_results(hits, path, q, length=2000):
    front_of_clause = 35
    end_of_clause = 90
    word = q['q']
    punctuation = re.compile('([,|?|;|.|:|!])')
    new_results = []
    full_report = {}
    for hit in hits:
        bytes, byte_start = f.format.adjust_bytes(hit.bytes, length)
        conc_text = f.get_text(hit, byte_start, length, path)
        hit.concordance = theme_rheme_concordance(conc_text, bytes)
        conc_start = conc_text[:bytes[0]]
        clause_start = punctuation.split(conc_start)[-1] # keep only last bit
        conc_end = conc_text[bytes[0]:]
        clause_end = punctuation.split(conc_end)[0] # keep only first bit
        clause = f.format.clean_text(clause_start + clause_end)
        new_clause = [i for i in clause.split() if len(i) > 2 or i.lower() == word]
        if len(new_clause) < 3:
            continue
        word_position = 0
        for pos, w in enumerate(new_clause):
            if w.lower() == word:
                word_position = pos + 1
                break
        clause_len = len(new_clause)
        percentage = round(word_position / clause_len * 100, 2)
        if q['theme_rheme'] == 'front' and percentage <= front_of_clause:
            hit.percentage = str(percentage) + '%'
            hit.score = str(word_position) + '/' + str(clause_len)
            hit.position = 'Front'
            new_results.append(hit)
        elif q['theme_rheme'] == 'end' and percentage >= end_of_clause:
            hit.percentage = str(percentage) + '%'
            hit.score = str(word_position) + '/' + str(clause_len)
            hit.position = 'End'
            new_results.append(hit)
        elif q['theme_rheme'] == 'front_end':
            if percentage <= front_of_clause:
                hit.position = 'Front'
                hit.percentage = str(percentage) + '%'
                hit.score = str(word_position) + '/' + str(clause_len)
                new_results.append(hit)
            elif percentage >= end_of_clause:
                hit.position = 'End'
                hit.percentage = str(percentage) + '%'
                hit.score = str(word_position) + '/' + str(clause_len)
                new_results.append(hit)
        elif q['theme_rheme'] == 'front_middle_end':
            if percentage <= front_of_clause:
                hit.position = 'Front'
                hit.percentage = str(percentage) + '%'
                hit.score = str(word_position) + '/' + str(clause_len)
                new_results.append(hit)
            elif front_of_clause < percentage < end_of_clause:
                hit.position = 'Middle'
                hit.percentage = str(percentage) + '%'
                hit.score = str(word_position) + '/' + str(clause_len)
                new_results.append(hit)
            elif percentage >= end_of_clause:
                hit.position = 'End'
                hit.percentage = str(percentage) + '%'
                hit.score = str(word_position) + '/' + str(clause_len)
                new_results.append(hit)
        elif q['theme_rheme'] == 'full':
            if percentage <= front_of_clause:
                hit.position = 'Front'
                hit.percentage = str(percentage) + '%'
                hit.score = str(word_position) + '/' + str(clause_len)
                new_results.append(hit)
                if 'Front' not in full_report:
                    full_report['Front'] = 0
                full_report['Front'] += 1
            elif front_of_clause < percentage < end_of_clause:
                hit.position = 'Middle'
                hit.percentage = str(percentage) + '%'
                hit.score = str(word_position) + '/' + str(clause_len)
                new_results.append(hit)
                if 'Middle' not in full_report:
                    full_report['Middle'] = 0
                full_report['Middle'] += 1
            elif percentage >= end_of_clause:
                hit.position = 'End'
                hit.percentage = str(percentage) + '%'
                hit.score = str(word_position) + '/' + str(clause_len)
                new_results.append(hit)
                if 'End' not in full_report:
                    full_report['End'] = 0
                full_report['End'] += 1
    return theme_rheme_hitlist(new_results), full_report


class theme_rheme_hitlist(object):
    
    def __init__(self, hitlist):
        self.done = True
        self.hitlist = hitlist
        
    def __getitem__(self, key):
        return self.hitlist[key]
        
    def __getattr__(self, name):
        return self.hitlist[name]
        
    def __len__(self):
        return len(self.hitlist)
    
    