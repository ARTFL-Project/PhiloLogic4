# -*- coding: utf-8 -*-"
#!/usr/bin/env python

import os
from philologic.OHCOVector import Record


abbreviations = set(["Mr", "Mrs", "Ms", "Mme", "Mlle", "pp", "vol"])

exceptions = set(["que", "qui", "quoi", "où", "what", "which", "where"])


def fix_sentence_boundary(loader_obj, text):
    tmp_file = open(text["raw"] + ".tmp", "w")
    change_philo_id = False
    prev_sent_id = None
    pre_word_id = None
    prev_rec_type = None
    prev_parent_sentence = None
    infile = open(text["raw"]).read().splitlines()
    records = []
    for line_num, line in enumerate(infile):
        rec_type, word, record = return_record(line)
        if records:
            prev_record = records[-1]
            if prev_record.type == "page":
                try:
                    prev_record = records[-2]
                except IndexError:
                    prev_record = records[-1]
                    change_philo_id = False
            prev_word = prev_record.name.decode("utf-8")
            prev_rec_type = prev_record.type
        if rec_type == "word":
            if change_philo_id:  # we need to change the philo_id of words to correspond to the current sentence
                prev_word_id += 1
                record.id = record.id[:5] + [prev_sent_id] + [str(prev_word_id)] + record.id[7:]  ## Store new philo_id
                record.attrib["parent"] = prev_parent_sentence
            prev_rec_type = rec_type
            prev_word = word
            prev_record = record
        elif rec_type == "sent":
            sent_type = word
            next_rec_type, next_word, next_record = return_record(infile[line_num + 1])
            if (
                sent_type != "__philo_virtual" and next_rec_type == "word" and prev_rec_type == "word"
            ):  # para and page break sentences
                if len(prev_word) == 1 or prev_word in abbreviations or prev_word.isdigit() or next_word.islower():
                    if next_word not in exceptions:
                        change_philo_id = True
                        prev_word_id = int(prev_record.id[6])
                        prev_sent_id = int(prev_record.id[5])
                        prev_parent_sentence = prev_record.attrib["parent"]
                        continue  # we skip this sentence marker and adjust IDs for words that follow
            if change_philo_id:  # We've been changing the current sentence, so we adjust the ID of the sentence marker
                record.id = prev_record.id[:7] + record.id[7:]
            change_philo_id = False
        elif rec_type == "para":
            change_philo_id = False
        else:
            change_philo_id = False
        records.append(record)
    print("\n".join([str(i) for i in records]), file=tmp_file)
    os.rename(text["raw"] + ".tmp", text["raw"])


def return_record(line):
    rec_type, word, id, attrib = line.split("\t")
    id = id.split()
    record = Record(rec_type, word, id)
    record.attrib = eval(attrib)
    return rec_type, word.decode("utf-8"), record
