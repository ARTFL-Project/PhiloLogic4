#!/usr/bin/env python3



import os
import pickle
import sys
import unicodedata
from json import dumps, loads
from subprocess import PIPE, Popen

from philologic.OHCOVector import Record


# Default filters
def normalize_unicode_raw_words(loader_obj, text):
    tmp_file = open(text["raw"] + ".tmp", "w")
    with open(text["raw"]) as filehandle:
        for line in filehandle:
            rec_type, word, philo_id, attrib = line.split('\t')
            philo_id = philo_id.split()
            if rec_type == "word":
                word = word.lower()
            record = Record(rec_type, word, philo_id)
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
    with open(text['raw']) as filehandle:
        for line in filehandle:
            philo_type, word, philo_id, attrib = line.split('\t')
            philo_id = philo_id.split()
            record = Record(philo_type, word, philo_id)
            record.attrib = loads(attrib)
            for d, count in enumerate(counts):
                if philo_type == 'word':
                    counts[d] += 1
                elif philo_type == object_types[d]:
                    record.attrib['word_count'] = counts[d]
                    counts[d] = 0
            print(record, file=output_file)
    output_file.close()
    os.remove(text['raw'])
    os.rename(temp_file, text['raw'])


def generate_words_sorted(loader_obj, text):
    # -a in grep to avoid issues with NULL chars in file
    wordcommand = "cat %s | egrep -a \"^word\" | LANG=C sort %s %s > %s" % (text["raw"], loader_obj.sort_by_word,
                                                                     loader_obj.sort_by_id, text["words"])
    os.system(wordcommand)


def make_object_ancestors(*philo_types):
    # We should add support for a 'div' philo_type in the future
    philo_type_depth = {'doc': 1, 'div1': 2, 'div2': 3, 'div3': 4, 'para': 5, 'sent': 6, 'word': 7, "page": 9}

    def inner_make_object_ancestors(loader_obj, text):
        temp_file = text['words'] + '.tmp'
        output_file = open(temp_file, 'w')
        with open(text['words']) as filehandle:
            for line in filehandle:
                philo_type, word, philo_id, attrib = line.split('\t')
                philo_id = philo_id.split()
                record = Record(philo_type, word, philo_id)
                record.attrib = loads(attrib)
                for philo_type in philo_types:
                    zeros_to_add = ['0' for i in range(7 - philo_type_depth[philo_type])]
                    philo_id = philo_id[:philo_type_depth[philo_type]] + zeros_to_add
                    record.attrib[philo_type + '_ancestor'] = ' '.join(philo_id)
                print(record, file=output_file)
        output_file.close()
        os.remove(text['words'])
        os.rename(temp_file, text['words'])

    return inner_make_object_ancestors


def make_sorted_toms(*philo_types):
    def sorted_toms(loader_obj, text):
        philo_type_pattern = "|".join("^%s" % t for t in philo_types)
        tomscommand = "cat %s | egrep \"%s\" | LANG=C sort %s > %s" % (text["raw"], philo_type_pattern, loader_obj.sort_by_id,
                                                                text["sortedtoms"])
        os.system(tomscommand)

    return sorted_toms


def prev_next_obj(*philo_types):
    """Outer function"""
    philo_types = list(philo_types)

    def inner_prev_next_obj(loader_obj, text):
        """Store the previous and next object for every object passed to this function
        By default, this is doc, div1, div2, div3."""
        record_dict = {}
        temp_file = text['raw'] + '.tmp'
        output_file = open(temp_file, 'w')
        with open(text['sortedtoms']) as filehandle:
            for line in filehandle:
                philo_type, word, philo_id, attrib = line.split('\t')
                philo_id = philo_id.split()
                record = Record(philo_type, word, philo_id)
                record.attrib = loads(attrib)
                if philo_type in record_dict:
                    record_dict[philo_type].attrib['next'] = ' '.join(philo_id)
                    if philo_type in philo_types:
                        print(record_dict[philo_type], file=output_file)
                    else:
                        del record_dict[philo_type].attrib['next']
                        del record_dict[philo_type].attrib['prev']
                        print(record_dict[philo_type], file=output_file)
                    record.attrib['prev'] = ' '.join(record_dict[philo_type].id)
                    record_dict[philo_type] = record
                else:
                    record.attrib['prev'] = ''
                    record_dict[philo_type] = record
        philo_types.reverse()
        for obj in philo_types:
            try:
                record_dict[obj].attrib['next'] = ''
                print(record_dict[obj], file=output_file)
            except KeyError:
                pass
        output_file.close()
        os.remove(text['sortedtoms'])
        philo_type_pattern = "|".join("^%s" % t for t in loader_obj.types)
        tomscommand = "cat %s | egrep \"%s\" | LANG=C sort %s > %s" % (temp_file, philo_type_pattern, loader_obj.sort_by_id,
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
        philo_type, word, philo_id, attrib = line.split('\t')
        philo_id = philo_id.split()
        record = Record(philo_type, word, philo_id)
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
    with open(text['pages']) as filehandle:
        whole_file = filehandle.readlines()
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
    with open(text["words"]) as filehandle:
        for line in filehandle:
            (key, philo_type, philo_id, attr) = line.split("\t")
            philo_id = [int(i) for i in philo_id.split(" ")]
            max_id = [max(new, prev) for new, prev in zip(philo_id, max_id)]
    with open(text["results"], "wb") as rf:
        # write the result out--really just the resulting omax vector, which the parent will merge in below.
        pickle.dump(max_id, rf)

# Useful for nested metadata.  Should always pair with normalize_divs_post
# in postFilters
def normalize_divs(*columns):
    def normalize_these_columns(loader_obj, text):
        current_values = {}
        tmp_file = open(text["sortedtoms"] + ".tmp", "w")
        for column in columns:
            current_values[column] = ""
        for line in open(text["sortedtoms"]):
            philo_type, word, philo_id, attrib = line.split('\t')
            philo_id = philo_id.split()
            record = Record(philo_type, word, philo_id)
            record.attrib = loads(attrib)
            if philo_type == "div1":
                for column in columns:
                    if column in record.attrib:
                        current_values[column] = record.attrib[column]
                    else:
                        current_values[column] = ""
            elif philo_type == "div2":
                for column in columns:
                    if column in record.attrib:
                        current_values[column] = record.attrib[column]
            elif philo_type == "div3":
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
            philo_type, word, philo_id, attrib = line.split('\t')
            philo_id = philo_id.split()
            record = Record(philo_type, word, philo_id)
            record.attrib = loads(attrib)
            for column in columns:
                if column in record.attrib:
                    #                    print >> sys.stderr, repr(record.attrib)
                    col = record.attrib[column]
                    col = col.lower()
                    smashed_col = [c for c in unicodedata.normalize("NFKD", col) if not unicodedata.combining(c)]
                    record.attrib[column + "_norm"] = ''.join(smashed_col)
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
        ttout_filehandle = open(text["raw"] + ".ttout", "w")
        tt_worker = Popen(tt_args, stdin=PIPE, stdout=ttout_filehandle)
        raw_filehandle = open(text["raw"], "r")
        line_count = 0

        # read through the object file, pass the words to treetagger
        for line in raw_filehandle:
            philo_type, word, philo_id, attrib = line.split('\t')
            philo_id = philo_id.split()
            if philo_type == "word":
                word = word.lower()
                # close and re-open the treetagger process to prevent garbage
                # output.
                if line_count > maxlines:
                    tt_worker.stdin.close()
                    tt_worker.wait()
                    new_ttout_filehandle = open(text["raw"] + ".ttout", "a")
                    tt_worker = Popen(tt_args, stdin=PIPE, stdout=new_ttout_filehandle)
                    line_count = 0
                print(word, file=tt_worker.stdin)
                line_count += 1

        # finish tagging
        tt_worker.stdin.close()
        tt_worker.wait()

        # go back through the object file, and add the treetagger results to
        # each word
        tmp_filehandle = open(text["raw"] + ".tmp", "w")
        tag_filehandle = open(text["raw"] + ".ttout", "r")
        for line in open(text["raw"], "r"):
            philo_type, word, philo_id, attrib = line.split('\t')
            philo_id = philo_id.split()
            record = Record(philo_type, word, philo_id)
            record.attrib = loads(attrib)
            if philo_type == "word":
                tag_l = tag_filehandle.readline()
                next_word, tag = tag_l.split("\t")[0:2]
                pos, lem, prob = tag.split(" ")
                if next_word != word.lower():
                    print("TREETAGGER ERROR:", next_word, " != ", word, pos, lem, file=sys.stderr)
                    return
                else:
                    record.attrib["pos"] = pos
                    record.attrib["lemma"] = lem
                    print(record, file=tmp_filehandle)
            else:
                print(record, file=tmp_filehandle)
        os.remove(text["raw"])
        os.rename(text["raw"] + ".tmp", text["raw"])
        os.remove(text["raw"] + ".ttout")

    return tag_words


def store_in_plain_text(*philo_types):
    object_types = {'doc': 1, 'div1': 2, 'div2': 3, 'div3': 4, 'para': 5, 'sent': 6, 'word': 7}
    obj_to_track = []
    for obj in philo_types:
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
            with open(text['raw']) as filehandle:
                for line in filehandle:
                    philo_type, word, philo_id, attrib = line.split('\t')
                    if word == '__philo_virtual':
                        continue
                    if philo_type == 'word' or philo_type == "sent":
                        philo_id = philo_id.split()[:obj_depth]
                        if not old_philo_id:
                            old_philo_id = philo_id
                        if philo_id != old_philo_id:
                            stored_objects.append({"philo_id": old_philo_id, "words": words})
                            words = []
                            old_philo_id = philo_id
                        words.append(word)
            if words:
                stored_objects.append({"philo_id": philo_id, "words": words})
            for obj in stored_objects:
                path = os.path.join(files_path, "_".join(obj["philo_id"]))
                with open(path, "w") as output:
                    output.write(' '.join(obj["words"]))
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
                        {"token": word, "philo_id": philo_id, "start_byte": attrib["start_byte"], "end_byte": attrib["end_byte"]}
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
