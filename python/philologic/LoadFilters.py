#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function
import six.moves.cPickle
import os
import re
import sys
import unicodedata
from subprocess import PIPE, Popen

from philologic.OHCOVector import Record
from simplejson import loads, dumps
from six.moves import range
from six.moves import zip


# Default filters
def normalize_unicode_raw_words(loader_obj, text):
    tmp_file = open(text["raw"] + ".tmp", "w")
    with open(text["raw"]) as fh:
        for line in fh:
            rec_type, word, id, attrib = line.split('\t')
            id = id.split()
            if rec_type == "word":
                word = word.decode("utf-8").lower().encode("utf-8")
            record = Record(rec_type, word, id)
            record.attrib = loads(attrib)
            print(record, file=tmp_file)
    tmp_file.close()
    os.remove(text["raw"])
    os.rename(text["raw"] + ".tmp", text["raw"])


def make_word_counts(loader_obj, text, depth=5):
    object_types = ['doc', 'div1', 'div2', 'div3', 'para', 'sent', 'word']
    counts = [0 for i in range(depth)]
    temp_file = text['raw'] + '.tmp'
    output_file = open(temp_file, 'w')
    with open(text['raw']) as fh:
        for line in fh:
            type, word, id, attrib = line.split('\t')
            id = id.split()
            record = Record(type, word, id)
            record.attrib = loads(attrib)
            for d, count in enumerate(counts):
                if type == 'word':
                    counts[d] += 1
                elif type == object_types[d]:
                    record.attrib['word_count'] = counts[d]
                    counts[d] = 0
            print(record, file=output_file)
    output_file.close()
    os.remove(text['raw'])
    os.rename(temp_file, text['raw'])


def generate_words_sorted(loader_obj, text):
    # -a in grep to avoid issues with NULL chars in file
    wordcommand = "cat %s | egrep -a \"^word\" | sort %s %s > %s" % (text["raw"], loader_obj.sort_by_word,
                                                                     loader_obj.sort_by_id, text["words"])
    os.system(wordcommand)


def make_object_ancestors(*types):
    # We should add support for a 'div' type in the future
    type_depth = {'doc': 1, 'div1': 2, 'div2': 3, 'div3': 4, 'para': 5, 'sent': 6, 'word': 7, "page": 9}

    def inner_make_object_ancestors(loader_obj, text):
        temp_file = text['words'] + '.tmp'
        output_file = open(temp_file, 'w')
        with open(text['words']) as fh:
            for line in fh:
                type, word, id, attrib = line.split('\t')
                id = id.split()
                record = Record(type, word, id)
                record.attrib = loads(attrib)
                for type in types:
                    zeros_to_add = ['0' for i in range(7 - type_depth[type])]
                    philo_id = id[:type_depth[type]] + zeros_to_add
                    record.attrib[type + '_ancestor'] = ' '.join(philo_id)
                print(record, file=output_file)
        output_file.close()
        os.remove(text['words'])
        os.rename(temp_file, text['words'])

    return inner_make_object_ancestors


def make_sorted_toms(*types):
    def sorted_toms(loader_obj, text):
        type_pattern = "|".join("^%s" % t for t in types)
        tomscommand = "cat %s | egrep \"%s\" | sort %s > %s" % (text["raw"], type_pattern, loader_obj.sort_by_id,
                                                                text["sortedtoms"])
        os.system(tomscommand)

    return sorted_toms


def prev_next_obj(*types):
    """Outer function"""
    types = list(types)

    def inner_prev_next_obj(loader_obj, text):
        """Store the previous and next object for every object passed to this function
        By default, this is doc, div1, div2, div3."""
        record_dict = {}
        temp_file = text['raw'] + '.tmp'
        output_file = open(temp_file, 'w')
        with open(text['sortedtoms']) as fh:
            for line in fh:
                type, word, id, attrib = line.split('\t')
                id = id.split()
                record = Record(type, word, id)
                record.attrib = loads(attrib)
                if type in record_dict:
                    record_dict[type].attrib['next'] = ' '.join(id)
                    if type in types:
                        print(record_dict[type], file=output_file)
                    else:
                        del record_dict[type].attrib['next']
                        del record_dict[type].attrib['prev']
                        print(record_dict[type], file=output_file)
                    record.attrib['prev'] = ' '.join(record_dict[type].id)
                    record_dict[type] = record
                else:
                    record.attrib['prev'] = ''
                    record_dict[type] = record
        types.reverse()
        for obj in types:
            try:
                record_dict[obj].attrib['next'] = ''
                print(record_dict[obj], file=output_file)
            except KeyError:
                pass
        output_file.close()
        os.remove(text['sortedtoms'])
        type_pattern = "|".join("^%s" % t for t in loader_obj.types)
        tomscommand = "cat %s | egrep \"%s\" | sort %s > %s" % (temp_file, type_pattern, loader_obj.sort_by_id,
                                                                text["sortedtoms"])
        os.system(tomscommand)
        os.remove(temp_file)

    return inner_prev_next_obj


def generate_pages(loader_obj, text):
    pagescommand = "cat %s | egrep \"^page\" > %s" % (text["raw"], text["pages"])
    os.system(pagescommand)


def prev_next_page(loader_obj, text):
    # Inner function
    def load_record(line):
        type, word, id, attrib = line.split('\t')
        id = id.split()
        record = Record(type, word, id)
        record.attrib = loads(attrib)
        record.attrib["prev"] = ""
        record.attrib["next"] = ""
        return record

    record_dict = {}
    temp_file = text['pages'] + '.tmp'
    output_file = open(temp_file, 'w')
    prev_record = None
    next_record = None
    record = None
    with open(text['pages']) as fh:
        whole_file = fh.readlines()
        last_pos = len(whole_file) - 1
        for pos in range(len(whole_file)):
            if not record:
                record = load_record(whole_file[pos])
            if prev_record:
                record.attrib["prev"] = " ".join(prev_record.id)
            if pos != last_pos:
                next_record = load_record(whole_file[pos+1])
                record.attrib["next"] = " ".join(next_record.id)
            print(record, file=output_file)
            prev_record = record
            record = next_record
    output_file.close()
    os.remove(text['pages'])
    os.rename(temp_file, text["pages"])


def generate_refs(loader_obj, text):
    refscommand = "cat %s | egrep \"^ref\" > %s" % (text["raw"], text["refs"])
    os.system(refscommand)

def generate_graphics(loader_obj, text):
    refscommand = "cat %s | egrep \"^graphic\" > %s" % (text["raw"], text["graphics"])
    os.system(refscommand)

def generate_lines(loader_obj, text):
    lines_command = "cat %s | egrep \"^line\" > %s" % (text["raw"], text["lines"])
    os.system(lines_command)


def make_max_id(loader_obj, text):
    max_id = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    with open(text["words"]) as fh:
        for line in fh:
            (key, type, id, attr) = line.split("\t")
            id = [int(i) for i in id.split(" ")]
            max_id = [max(new, prev) for new, prev in zip(id, max_id)]
    rf = open(text["results"], "w")
    six.moves.cPickle.dump(
        max_id,
        rf)  # write the result out--really just the resulting omax vector, which the parent will merge in below.
    rf.close()


# Useful for nested metadata.  Should always pair with normalize_divs_post
# in postFilters
def normalize_divs(*columns):
    def normalize_these_columns(loader_obj, text):
        current_values = {}
        tmp_file = open(text["sortedtoms"] + ".tmp", "w")
        for column in columns:
            current_values[column] = ""
        for line in open(text["sortedtoms"]):
            type, word, id, attrib = line.split('\t')
            id = id.split()
            record = Record(type, word, id)
            record.attrib = loads(attrib)
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
            print(record, file=tmp_file)
        tmp_file.close()
        os.remove(text["sortedtoms"])
        os.rename(text["sortedtoms"] + ".tmp", text["sortedtoms"])

    return normalize_these_columns


def normalize_unicode_columns(*columns):
    # I should never, ever need to use this now.
    def smash_these_unicode_columns(loader_obj, text):
        tmp_file = open(text["sortedtoms"] + ".tmp", "w")
        for line in open(text["sortedtoms"]):
            type, word, id, attrib = line.split('\t')
            id = id.split()
            record = Record(type, word, id)
            record.attrib = loads(attrib)
            for column in columns:
                if column in record.attrib:
                    #                    print >> sys.stderr, repr(record.attrib)
                    col = record.attrib[column].decode("utf-8")
                    col = col.lower()
                    smashed_col = [c for c in unicodedata.normalize("NFKD", col) if not unicodedata.combining(c)]
                    record.attrib[column + "_norm"] = ''.join(smashed_col).encode("utf-8")
            print(record, file=tmp_file)
        tmp_file.close()
        os.remove(text["sortedtoms"])
        os.rename(text["sortedtoms"] + ".tmp", text["sortedtoms"])

    return smash_these_unicode_columns


# Optional filters
def tree_tagger(tt_path, param_file, maxlines=20000):
    def tag_words(loader_obj, text):
        # Set up the treetagger process
        tt_args = [tt_path, "-token", "-lemma", "-prob", '-no-unknown', "-threshold", ".01", param_file]
        ttout_fh = open(text["raw"] + ".ttout", "w")
        tt_worker = Popen(tt_args, stdin=PIPE, stdout=ttout_fh)
        raw_fh = open(text["raw"], "r")
        line_count = 0

        # read through the object file, pass the words to treetagger
        for line in raw_fh:
            type, word, id, attrib = line.split('\t')
            id = id.split()
            if type == "word":
                word = word.decode('utf-8', 'ignore').lower().encode('utf-8')
                # close and re-open the treetagger process to prevent garbage
                # output.
                if line_count > maxlines:
                    tt_worker.stdin.close()
                    tt_worker.wait()
                    new_ttout_fh = open(text["raw"] + ".ttout", "a")
                    tt_worker = Popen(tt_args, stdin=PIPE, stdout=new_ttout_fh)
                    line_count = 0
                print(word, file=tt_worker.stdin)
                line_count += 1

        # finish tagging
        tt_worker.stdin.close()
        tt_worker.wait()

        # go back through the object file, and add the treetagger results to
        # each word
        tmp_fh = open(text["raw"] + ".tmp", "w")
        tag_fh = open(text["raw"] + ".ttout", "r")
        for line in open(text["raw"], "r"):
            type, word, id, attrib = line.split('\t')
            id = id.split()
            record = Record(type, word, id)
            record.attrib = loads(attrib)
            if type == "word":
                tag_l = tag_fh.readline()
                next_word, tag = tag_l.split("\t")[0:2]
                pos, lem, prob = tag.split(" ")
                if next_word != word.decode('utf-8', 'ignore').lower().encode('utf-8'):
                    print("TREETAGGER ERROR:", next_word, " != ", word, pos, lem, file=sys.stderr)
                    return
                else:
                    record.attrib["pos"] = pos
                    record.attrib["lemma"] = lem
                    print(record, file=tmp_fh)
            else:
                print(record, file=tmp_fh)
        os.remove(text["raw"])
        os.rename(text["raw"] + ".tmp", text["raw"])
        os.remove(text["raw"] + ".ttout")

    return tag_words


def store_in_plain_text(*types):
    object_types = {'doc': 1, 'div1': 2, 'div2': 3, 'div3': 4, 'para': 5, 'sent': 6, 'word': 7}
    obj_to_track = []
    for obj in types:
        obj_to_track.append((obj, object_types[obj]))

    def inner_store_in_plain_text(loader_obj, text):
        files_path = loader_obj.destination + '/plain_text_objects/'
        try:
            os.mkdir(files_path)
        except OSError:
            # Path was already created
            pass
        for obj, obj_depth in obj_to_track:
            old_philo_id = []
            philo_id = []
            words = []
            stored_objects = []
            with open(text['raw']) as fh:
                for line in fh:
                    type, word, id, attrib = line.split('\t')
                    if word == '__philo_virtual':
                        continue
                    if type == 'word' or type == "sent":
                        philo_id = id.split()[:obj_depth]
                        if not old_philo_id:
                            old_philo_id = philo_id
                        if philo_id != old_philo_id:
                            stored_objects.append({"philo_id": old_philo_id, "words": words})
                            words = []
                            old_philo_id = philo_id
                        words.append(word)
            if words:
                stored_objects.append({"philo_id": philo_id, "words": words})
            filename = files_path + philo_id[0] + '_' + obj
            output = open(filename, 'w')
            for obj in stored_objects:
                print('\n###\t%s\t###' % ' '.join(obj["philo_id"]), file=output)
                print(' '.join(obj["words"]), file=output)
            output.close()

    return inner_store_in_plain_text


def store_words_and_philo_ids(loader_obj, text):
    files_path = loader_obj.destination + '/words_and_philo_ids/'
    try:
        os.mkdir(files_path)
    except OSError:
        # Path was already created
        pass
    with open(os.path.join(files_path, str(text["id"])), "w") as output:
        with open(text['raw']) as filehandle:
            for line in filehandle:
                philo_type, word, philo_id, attrib = line.split('\t')
                attrib = loads(attrib)
                if philo_type == "word" and word != '__philo_virtual':
                    word_obj = dumps(
                        {"token": word, "position": philo_id, "start_byte": attrib["start_byte"], "end_byte": attrib["end_byte"]}
                        )
                    print(word_obj, file=output)


DefaultNavigableObjects = ("div1", "div2", "div3", "para")
DefaultLoadFilters = [normalize_unicode_raw_words, make_word_counts, generate_words_sorted, make_object_ancestors,
                      make_sorted_toms, prev_next_obj, generate_pages, prev_next_page, generate_refs, generate_graphics,
                      generate_lines, make_max_id, store_words_and_philo_ids]


def set_load_filters(load_filters=DefaultLoadFilters, navigable_objects=DefaultNavigableObjects):
    filters = []
    for load_filter in load_filters:
        if load_filter.__name__ == "make_object_ancestors" or load_filter.__name__ == "make_sorted_toms" or load_filter.__name__ == "prev_next_obj":
            filters.append(load_filter(*navigable_objects))
        else:
            filters.append(load_filter)
    return filters
