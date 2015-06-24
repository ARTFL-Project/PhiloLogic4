#!/usr/bin/env python

import os
from philologic.OHCOVector import Record


abbreviations = set([
    u"Mr",
    u"Mrs",
    u"Ms",
    u"Mme",
    u"Mlle",
    u"pp"
])

def fix_sentence_boundary(loader_obj, text):
    tmp_file = open(text["raw"] + ".tmp","w")
    flagged_word = False
    change_philo_id = False
    prev_sent_id = None
    last_word_id = None
    parent_sent = None
    preceding_type = ""
    preceding_sent_record = ""
    for line in open(text["raw"]):
        rec_type, word, id, attrib = line.split('\t')
        id = id.split()
        record = Record(rec_type, word, id)
        record.attrib = eval(attrib)
        if rec_type == "word":
            unicode_word = word.decode('utf-8')
            if change_philo_id: # we need to change the philo_id of words to correspond to the current sentence
                last_word_id += 1
                record.id =  record.id[:5] + [prev_sent_id] + [str(last_word_id)] + record.id[7:] ## Store new philo_id
                record.attrib['parent'] = parent_sent
            if len(unicode_word) == 1 or unicode_word in abbreviations or unicode_word.isdigit(): # flagged as possible abbreviation
                flagged_word = True
                if not change_philo_id:
                    prev_sent_id = id[5] # we store the sentence id of the current sentence to apply it to the following words
                    last_word_id = int(id[6]) # we store the word id to increment word_ids in the following words
                    parent_sent = record.attrib['parent'] # we store the parent sentence id to pass it to the next words
            else:
                flagged_word = False
        if rec_type == "sent" and flagged_word:
            # the previous word was flagged as an abbreviation, therefore skip this sentence marker
            # and change all word ids in the rest of the sentence
            change_philo_id = True
            preceding_sent_record = record
            preceding_sent_record.id = parent_sent.split() + record.id[7:]
            continue
        if rec_type == "sent" and not flagged_word: # end of sentence and last word was not flagged
            change_philo_id = False
            if parent_sent:
                record.id = parent_sent.split() + record.id[7:]
        if rec_type == "para" and preceding_type != "sent": # Make sure we always end a sentence before a paragraph
            if preceding_sent_record:
                print >> tmp_file, preceding_sent_record
        print >> tmp_file, record
        preceding_type = rec_type
    os.remove(text["raw"])
    os.rename(text["raw"] + ".tmp",text["raw"])
    os.system('cp %s %s_backup' % (text['raw'], text['raw']))