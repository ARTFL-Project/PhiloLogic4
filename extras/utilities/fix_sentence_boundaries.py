# -*- coding: utf-8 -*-"
#!/usr/bin/env python

import os
from philologic.OHCOVector import Record


abbreviations = set([
    u"Mr",
    u"Mrs",
    u"Ms",
    u"Mme",
    u"Mlle",
    u"pp",
    u"vol"
])

exceptions = set([
    u"que",
    u"qui",
    u"quoi",
    u"où",
    u"what",
    u"which",
    u"where"
])


def fix_sentence_boundary(loader_obj, text):
    tmp_file = open(text["raw"] + ".tmp","w")
    change_philo_id = False
    prev_sent_id = None
    pre_word_id = None
    prev_rec_type = None
    current_parent_sentence = None
    infile = open(text["raw"]).read().splitlines()
    for line_num, line in enumerate(infile):
        rec_type, word, record  = return_record(line)
        if rec_type == "word":
            if change_philo_id: # we need to change the philo_id of words to correspond to the current sentence
                prev_word_id += 1
                record.id =  record.id[:5] + [prev_sent_id] + [str(prev_word_id)] + record.id[7:] ## Store new philo_id
                record.attrib['parent'] = current_parent_sentence
            prev_rec_type = rec_type
            prev_word = word
            prev_record = record
        if rec_type == "sent":
            if not prev_rec_type: # in case there's no preceding word in the doc
                prev_rec_type, prev_word, prev_record = return_record(infile[line_num-1])
            next_rec_type, next_word, next_record = return_record(infile[line_num+1])
            if next_rec_type != "para" and prev_rec_type == "word": # We make sure this isn't the end of a paragraph
                if len(prev_word) == 1 or prev_word in abbreviations or prev_word.isdigit() or next_word.islower():
                    if next_word not in exceptions:
                        change_philo_id = True
                        current_parent_sentence = prev_record.attrib['parent']
                        prev_word_id = int(prev_record.id[6])
                        prev_sent_id = int(prev_record.id[5])
                        continue # we skip this sentence marker and adjust IDs for words that follow
            if change_philo_id: # We've been changing the current sentence, so we adjust the ID of the sentence marker
                record.id = current_parent_sentence.split() + record.id[7:]
            change_philo_id = False
        print >> tmp_file, record
    os.rename(text["raw"], text['raw'] + '_original')
    os.rename(text["raw"] + ".tmp",text["raw"])
    os.system('cp %s %s_new' % (text['raw'], text['raw']))
    
def return_record(line):
    rec_type, word, id, attrib = line.split('\t')
    id = id.split()
    record = Record(rec_type, word, id)
    record.attrib = eval(attrib)
    return rec_type, word.decode('utf-8'), record