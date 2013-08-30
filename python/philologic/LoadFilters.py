#!/usr/bin/env python

import os
import re
import cPickle
import unicodedata
from philologic.OHCOVector import Record
from ast import literal_eval as eval


## Default filters
def normalize_unicode_raw_words(loader_obj, text):
    tmp_file = open(text["raw"] + ".tmp","w")
    for line in open(text["raw"]):
        rec_type, word, id, attrib = line.split('\t')
        id = id.split()
        if rec_type == "word":
            word = word.decode("utf-8").lower().encode("utf-8")
        record = Record(rec_type, word, id)
        record.attrib = eval(attrib)
        print >> tmp_file, record
    os.remove(text["raw"])
    os.rename(text["raw"] + ".tmp",text["raw"])

def make_word_counts(loader_obj, text, depth=4):
    object_types = ['doc', 'div1', 'div2', 'div3', 'para', 'sent', 'word']
    counts = [0 for i in range(depth)]
    temp_file = text['raw'] + '.tmp'
    output_file = open(temp_file, 'w')
    for line in open(text['raw']):
        type, word, id, attrib = line.split('\t')
        id = id.split()
        record = Record(type, word, id)
        record.attrib = eval(attrib)
        for d,count in enumerate(counts):
            if type == 'word':
                counts[d] += 1
            elif type == object_types[d]:
                record.attrib['word_count'] = counts[d]
                counts[d] = 0
        print >> output_file, record
    output_file.close()
    os.remove(text['raw'])
    os.rename(temp_file, text['raw'])
    
def fix_pages(loader_obj,text,depth=4):
    """Unfinished, do not use"""
    object_types = ['doc', 'div1', 'div2', 'div3', 'para', 'sent', 'word'][:depth]
    current_page = 0;
    temp_file = open(text["sortedtoms"] + ".tmp","w")
    for line in open(text["sortedtoms"]):
        type, word, id, attrib = line.split('\t')
        id = id.split()
        record = Record(type, word, id)
        record.attrib = eval(attrib) 
                

def prev_next_obj(loader_obj, text, depth=4):
    object_types = ['doc', 'div1', 'div2', 'div3', 'para', 'sent', 'word'][:depth]
    record_dict = {}
    temp_file = text['raw'] + '.tmp'
    output_file = open(temp_file, 'w')
    for line in open(text['sortedtoms']):
        type, word, id, attrib = line.split('\t')
        id = id.split()
        record = Record(type, word, id)
        record.attrib = eval(attrib) 
        if type in record_dict:
            record_dict[type].attrib['next'] = ' '.join(id)
            if type in object_types:
                print >> output_file, record_dict[type]
            else:
                del record_dict[type].attrib['next']
                del record_dict[type].attrib['prev']
                print >> output_file, record_dict[type]
            record.attrib['prev'] = ' '.join(record_dict[type].id)
            record_dict[type] = record
        else:
            record.attrib['prev'] = ''
            record_dict[type] = record
    object_types.reverse()
    for obj in object_types:
        record_dict[obj].attrib['next'] = ''
        print >> output_file, record_dict[obj]
    output_file.close()
    os.remove(text['sortedtoms'])
    type_pattern = "|".join("^%s" % t for t in loader_obj.types)
    tomscommand = "cat %s | egrep \"%s\" | sort %s > %s" % (temp_file,type_pattern,loader_obj.sort_by_id,text["sortedtoms"])
    os.system(tomscommand)
    os.remove(temp_file)

def generate_words_sorted(loader_obj, text):
    wordcommand = "cat %s | egrep \"^word\" | sort %s %s > %s" % (text["raw"],loader_obj.sort_by_word,loader_obj.sort_by_id,text["words"])
    os.system(wordcommand)        

def make_sorted_toms(*types):
    def sorted_toms(loader_obj, text):
        type_pattern = "|".join("^%s" % t for t in types)
        tomscommand = "cat %s | egrep \"%s\" | sort %s > %s" % (text["raw"],type_pattern,loader_obj.sort_by_id,text["sortedtoms"])
        os.system(tomscommand)
    return sorted_toms
    
def old_sorted_toms(loader_obj, text):
    # should be entirely superseded by make_sorted_toms
    type_pattern = "|".join("^%s" % t for t in loader_obj.types)
    tomscommand = "cat %s | egrep \"%s\" | sort %s > %s" % (text["raw"],type_pattern,loader_obj.sort_by_id,text["sortedtoms"])
    os.system(tomscommand)
    
def generate_pages(loader_obj, text):
    pagescommand = "cat %s | egrep \"^page\" > %s" % (text["raw"],text["pages"])
    os.system(pagescommand)
    
def make_max_id(loader_obj, text):
    max_id = None
    for line in open(text["words"]):
        (key,type,id,attr) = line.split("\t")
        id = [int(i) for i in id.split(" ")]
        if not max_id:
            max_id = id
        else:
            max_id = [max(new,prev) for new,prev in zip(id,max_id)]
    rf = open(text["results"],"w")
    cPickle.dump(max_id,rf) # write the result out--really just the resulting omax vector, which the parent will merge in below.
    rf.close()
    
## Additional Filters
def make_token_counts(loader_obj, text, depth=4):
    old_word = None
    record_list = []
    temp_file = text['words'] + '.tmp'
    output_file = open(temp_file, 'w')
    for line in open(text['words']):
        type, word, id, attrib = line.split('\t')
        id = id.split()
        record = Record(type, word, id)
        record.attrib = eval(attrib)
        if word == old_word or old_word == None:
            record_list.append(record)
        else:
            count_tokens(record_list, depth, output_file)
            record_list = []
            record_list.append(record)
        old_word = word
    if len(record_list) != 0:
        count_tokens(record_list, depth, output_file)
    record_list = []
    os.remove(text['words'])
    os.rename(temp_file, text['words'])

def normalize_unicode_words(loader_obj, text):
    tmp_file = open(text["words"] + ".tmp","w")
    for line in open(text["words"]):
        type, word, id, attrib = line.split('\t')
        id = id.split()
        word = word.decode("utf-8").lower().encode("utf-8")
        record = Record(type, word, id)
        print >> tmp_file, record
    os.remove(text["words"])
    os.rename(text["words"] + ".tmp",text["words"])   

##Useful for nested metadata.  Should always pair with normalize_divs_post in postFilters
def normalize_divs(*columns):
    def normalize_these_columns(loader_obj,text,depth=5):
        current_values = {}
        tmp_file = open(text["sortedtoms"] + ".tmp","w")
        for column in columns:
            current_values[column] = ""
        for line in open(text["sortedtoms"]):
            type, word, id, attrib = line.split('\t')
            id = id.split()
            record = Record(type, word, id)
            record.attrib = eval(attrib)
            if type == "div1":
                for column in columns:
                    if column in record.attrib:
                        current_values[column] = record.attrib[column]
                    else:
                        current_values[column] = ""
            elif type == "div2":
                for column in columns:
                    if column in record.attrib:
                        current_values[column] = record.attrib[column]
            elif type == "div3":
                for column in columns:
                    if column not in record.attrib:
                        record.attrib[column] = current_values[column]
            print >> tmp_file, record
        tmp_file.close()
        os.remove(text["sortedtoms"])
        os.rename(text["sortedtoms"] + ".tmp",text["sortedtoms"])
    return normalize_these_columns



def normalize_unicode_columns(*columns):
#I should never, ever need to use this now.
    def smash_these_unicode_columns(loader_obj, text):
        tmp_file = open(text["sortedtoms"] + ".tmp","w")
        for line in open(text["sortedtoms"]):
            type, word, id, attrib = line.split('\t')
            id = id.split()
            record = Record(type, word, id)
            record.attrib = eval(attrib)
            for column in columns:
                if column in record.attrib:
#                    print >> sys.stderr, repr(record.attrib)
                    col = record.attrib[column].decode("utf-8")
                    col = col.lower()
                    smashed_col = [c for c in unicodedata.normalize("NFKD",col) if not unicodedata.combining(c)]
                    record.attrib[column + "_norm"] = ''.join(smashed_col).encode("utf-8")
                    #record.attrib[column + "_norm"] = ''.join([c.encode("utf-8") for c in unicodedata.normalize('NFKD',record.attrib[column].decode("utf-8").lower()) if not unicodedata.combining(c)])
            print >> tmp_file, record
        tmp_file.close()
        os.remove(text["sortedtoms"])
        os.rename(text["sortedtoms"] + ".tmp",text["sortedtoms"])
    return smash_these_unicode_columns
    
## Helper functions
def count_tokens(record_list, depth, output_file):
    object_types = ['doc', 'div1', 'div2', 'div3', 'para', 'sent', 'word']
    new_record_list = []
    record_dict = {}
    for new_record in record_list:
        new_record.attrib['doc_token_count'] = len(record_list)
        for d in range(depth):
            philo_id = tuple(new_record.id[:d+1])
            if philo_id not in record_dict:
                record_dict[philo_id] = 1
            else:
                record_dict[philo_id] += 1
    for new_record in record_list:
        for d in range(depth):
            philo_id = tuple(new_record.id[:d+1])
            token_count = object_types[len(philo_id)-1] + '_token_count'
            new_record.attrib[token_count] = record_dict[philo_id]
        print >> output_file, new_record

def word_frequencies_per_obj(*obj_types):
    object_types = ['doc', 'div1', 'div2', 'div3', 'para', 'sent', 'word']
    def inner_word_frequencies_per_obj(loader_obj,text):
        files_path = loader_obj.destination + '/WORK/'
        obj_types = loader_obj.freq_object_levels
        try:
            os.mkdir(files_path)        
        except OSError:
            ## Path was already created                                                                                                                                       
            pass
        for obj in obj_types:
            d = object_types.index(obj)+1
            file = text['name'] + '.%s.freq_counts' % obj
            output = open(files_path + file, 'w')
            old_philo_id = []
            old_word = ''
            records = {}
            for line in open(text['words']):
                type, word, id, attrib = line.split('\t')
                attrib = eval(attrib)
                ## Dismiss all irrelevant fields while making sure we still have 9 fields in the end
                philo_id = id.split()[:d] + [0 for i in range(7-d)] + [0,0]
                record = Record(type, word, philo_id)
                count_key = obj + '_token_count'
                byte = attrib['byte_start']
                del attrib['byte_start']
                record.attrib = {'token_count': attrib[count_key]}
                if philo_id[:d] != old_philo_id[:d] or word != old_word:
                    if records and old_word:
                        for w in records:
                            print >> output, records[w]
                            records = {}
                if word not in records:
                    record.attrib['bytes'] = []
                    record.attrib['bytes']= str(byte)
                    records[word] = record
                else:
                    records[word].attrib['bytes'] += ' ' + str(byte)
                old_philo_id = philo_id
                old_word = word
            for w in records:
                print >> output, records[w]
            output.close()
    
    return inner_word_frequencies_per_obj


def evaluate_word(word, word_pattern):
    word = word.decode('utf-8', 'ignore')
    if word_pattern.search(word) and len(word) > 1:
        return True
    else:
        return False

def store_in_plain_text(*types):
    object_types = {'doc': 1, 'div1': 2, 'div2': 3, 'div3': 4, 'para': 5,
                    'sent': 6, 'word': 7}
    obj_to_track = []
    for obj in types:
        if obj not in object_types:
            print >> sys.stderr, "%s object type not supported",
            print >> sys.stderr, "only 'doc', 'div1', 'div2' and 'div3' are supported"
        obj_to_track.append(object_types[obj])
    
    def inner_store_in_plain_text(loader_obj, text):
        files_path = loader_obj.destination + '/plain_text_objects/'
        word_pattern = re.compile('[^\W\d_]', re.UNICODE)
        try:
            os.mkdir(files_path)
        except OSError:
            ## Path was already created                                                                                                                                       
            pass
        for obj_depth in obj_to_track:
            old_philo_id = []
            philo_id = []
            words = []
            for line in open(text['raw']):
                type, word, id, attrib = line.split('\t')
                if type != 'word':
                    continue
                ## Check if we're in the top level object
                if evaluate_word(word, word_pattern):
                    philo_id = id.split()[:obj_depth]
                    if not old_philo_id:
                        old_philo_id = philo_id
                    if philo_id != old_philo_id: 
                        filename = files_path + '_'.join(old_philo_id)
                        output = open(filename, 'w')
                        print >> output, ' '.join(words)
                        output.close()
                        words = []
                        old_philo_id = philo_id
                    words.append(word)
            if words:
                filename = files_path + '_'.join(philo_id)
                output = open(filename, 'w')
                print >> output, ' '.join(words)
                output.close()
                
    return inner_store_in_plain_text
