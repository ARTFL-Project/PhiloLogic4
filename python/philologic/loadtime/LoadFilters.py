#!/usr/bin/env python3
"""Load Filters used in Loader"""

import os
import pickle
from rapidjson import dumps, loads
import lz4.frame

from philologic.loadtime.OHCOVector import Record


# Default filters
def get_word_counts(_, text):
    """Lowercase and count words"""
    attrib_set = set()
    with open(text["raw"] + ".tmp", "w") as tmp_file:
        object_types = ["doc", "div1", "div2", "div3", "para", "sent", "word"]
        counts = [0 for i in range(5)]
        with open(text["raw"], encoding="utf8") as fh:
            for line in fh:
                philo_type, word, philo_id, attrib = line.split("\t")
                philo_id = philo_id.split()
                record = Record(philo_type, word, philo_id)
                record.attrib = loads(attrib)
                if philo_type == "word":
                    word = word.lower()
                for d, _ in enumerate(counts):
                    if philo_type == "word":
                        counts[d] += 1
                    elif philo_type == object_types[d]:
                        record.attrib["word_count"] = counts[d]
                        counts[d] = 0
                print(record, file=tmp_file)
                attrib_set.update(record.attrib.keys())
    os.remove(text["raw"])
    os.rename(text["raw"] + ".tmp", text["raw"])
    return attrib_set


def generate_words_sorted(loader_obj, text):
    """Generate sorted words for storing in index"""
    # -a in grep to avoid issues with NULL chars in file
    wordcommand = 'cat %s | egrep -a "^word" | LANG=C sort %s %s > %s' % (
        text["raw"],
        loader_obj.sort_by_word,
        loader_obj.sort_by_id,
        text["words"],
    )
    os.system(wordcommand)


def make_object_ancestors(*philo_types):
    """Find object ancestors for all stored object types"""
    # We should add support for a 'div' philo_type in the future
    philo_type_depth = {"doc": 1, "div1": 2, "div2": 3, "div3": 4, "para": 5, "sent": 6, "word": 7, "page": 9}

    def inner_make_object_ancestors(_, text):
        temp_file = text["words"] + ".tmp"
        output_file = open(temp_file, "w")
        with open(text["words"]) as filehandle:
            for line in filehandle:
                philo_type, word, philo_id, attrib = line.split("\t")
                philo_id = philo_id.split()
                record = Record(philo_type, word, philo_id)
                record.attrib = loads(attrib)
                for philo_type in philo_types:
                    zeros_to_add = ["0" for i in range(7 - philo_type_depth[philo_type])]
                    philo_id = philo_id[: philo_type_depth[philo_type]] + zeros_to_add
                    record.attrib[philo_type + "_ancestor"] = " ".join(philo_id)
                print(record, file=output_file)
        output_file.close()
        os.remove(text["words"])
        os.rename(temp_file, text["words"])

    return inner_make_object_ancestors


def make_sorted_toms(*philo_types):
    """Sort metadata before insertion"""

    def sorted_toms(loader_obj, text):
        philo_type_pattern = "|".join("^%s" % t for t in philo_types)
        tomscommand = 'cat %s | egrep "%s" | LANG=C sort %s > %s' % (
            text["raw"],
            philo_type_pattern,
            loader_obj.sort_by_id,
            text["sortedtoms"],
        )
        os.system(tomscommand)

    return sorted_toms


def prev_next_obj(*philo_types):
    """Outer function"""
    philo_types = list(philo_types)

    def inner_prev_next_obj(loader_obj, text):
        """Store the previous and next object for every object passed to this function
        By default, this is doc, div1, div2, div3."""
        record_dict = {}
        temp_file = text["raw"] + ".tmp"
        output_file = open(temp_file, "w")
        attrib_set = set()
        with open(text["sortedtoms"]) as filehandle:
            for line in filehandle:
                philo_type, word, philo_id, attrib = line.split("\t")
                philo_id = philo_id.split()
                record = Record(philo_type, word, philo_id)
                record.attrib = loads(attrib)
                if philo_type in record_dict:
                    record_dict[philo_type].attrib["next"] = " ".join(philo_id)
                    if philo_type in philo_types:
                        print(record_dict[philo_type], file=output_file)
                    else:
                        del record_dict[philo_type].attrib["next"]
                        del record_dict[philo_type].attrib["prev"]
                        print(record_dict[philo_type], file=output_file)
                    record.attrib["prev"] = " ".join(record_dict[philo_type].id)
                    record_dict[philo_type] = record
                else:
                    record.attrib["prev"] = ""
                    record_dict[philo_type] = record
                attrib_set.update(record.attrib.keys())

        philo_types.reverse()
        for obj in philo_types:
            try:
                record_dict[obj].attrib["next"] = ""
                print(record_dict[obj], file=output_file)
            except KeyError:
                pass
        output_file.close()
        os.remove(text["sortedtoms"])
        philo_type_pattern = "|".join("^%s" % t for t in loader_obj.types)
        tomscommand = 'cat %s | egrep "%s" | LANG=C sort %s > %s' % (
            temp_file,
            philo_type_pattern,
            loader_obj.sort_by_id,
            text["sortedtoms"],
        )
        os.system(tomscommand)
        os.remove(temp_file)
        return attrib_set

    return inner_prev_next_obj


def generate_pages(_, text):
    """Generate separate page file"""
    pagescommand = 'cat %s | egrep "^page" > %s' % (text["raw"], text["pages"])
    os.system(pagescommand)


def prev_next_page(_, text):
    """Generate previous and next page"""

    def load_record(line):
        philo_type, word, philo_id, attrib = line.split("\t")
        philo_id = philo_id.split()
        record = Record(philo_type, word, philo_id)
        record.attrib = loads(attrib)
        record.attrib["prev"] = ""
        record.attrib["next"] = ""
        return record

    temp_file = text["pages"] + ".tmp"
    output_file = open(temp_file, "w")
    prev_record = None
    next_record = None
    record = None
    with open(text["pages"]) as filehandle:
        whole_file = filehandle.readlines()
        last_pos = len(whole_file) - 1
        for pos, line in enumerate(whole_file):
            if not record:
                record = load_record(line)
            if prev_record:
                record.attrib["prev"] = " ".join(prev_record.id)
            if pos != last_pos:
                next_record = load_record(whole_file[pos + 1])
                record.attrib["next"] = " ".join(next_record.id)
            print(record, file=output_file)
            prev_record = record
            record = next_record
    output_file.close()
    os.remove(text["pages"])
    os.rename(temp_file, text["pages"])


def generate_refs(_, text):
    """Generate ref file"""
    refscommand = 'cat %s | egrep "^ref" > %s' % (text["raw"], text["refs"])
    os.system(refscommand)


def generate_graphics(_, text):
    """Generate graphics file"""
    refscommand = 'cat %s | egrep "^graphic" > %s' % (text["raw"], text["graphics"])
    os.system(refscommand)


def generate_lines(_, text):
    """Generate lines file"""
    lines_command = 'cat %s | egrep "^line" > %s' % (text["raw"], text["lines"])
    os.system(lines_command)


def make_max_id(_, text):
    """Define max id"""
    max_id = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    with open(text["words"]) as filehandle:
        for line in filehandle:
            _, _, philo_id, _ = line.split("\t")
            philo_id = map(int, philo_id.split(" "))
            max_id = [max(new, prev) for new, prev in zip(philo_id, max_id)]
    with open(text["results"], "wb") as rf:
        # write the result out--really just the resulting omax vector, which the parent will merge in below.
        pickle.dump(max_id, rf)


def store_in_plain_text(*philo_types):
    """Store indexed words in plain text"""
    object_types = {"doc": 1, "div1": 2, "div2": 3, "div3": 4, "para": 5, "sent": 6, "word": 7}
    obj_to_track = []
    for obj in philo_types:
        obj_to_track.append(object_types[obj])

    def inner_store_in_plain_text(loader_obj, text):
        files_path = loader_obj.destination + "/plain_text_objects/"
        try:
            os.mkdir(files_path)
        except OSError:
            # Path was already created
            pass
        for obj_depth in obj_to_track:
            old_philo_id = []
            philo_id = []
            words = []
            stored_objects = []
            with open(text["raw"]) as filehandle:
                for line in filehandle:
                    philo_type, word, philo_id, _ = line.split("\t")
                    if word == "__philo_virtual":
                        continue
                    if philo_type == "word" or philo_type == "sent":
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
            for stored_obj in stored_objects:
                path = os.path.join(files_path, "_".join(stored_obj["philo_id"]))
                with open(path, "w") as output:
                    output.write(" ".join(stored_obj["words"]))

    return inner_store_in_plain_text


def store_words_and_philo_ids(loader_obj, text):
    """Store words and philo ids file for data-mining"""
    files_path = loader_obj.destination + "/words_and_philo_ids/"
    try:
        os.mkdir(files_path)
    except OSError:
        # Path was already created
        pass
    filename = os.path.join(files_path, str(text["id"]))
    with open(filename, "w") as output:
        with open(text["raw"]) as filehandle:
            for line in filehandle:
                philo_type, word, philo_id, attrib = line.split("\t")
                if word == "__philo_virtual":
                    continue
                attrib = loads(attrib)
                if philo_type in ("word", "sent", "punct"):
                    if philo_type == "sent":
                        attrib["start_byte"] = attrib["end_byte"] - len(
                            word.encode("utf8")
                        )  # Parser uses beginning of sent as start_byte
                    word_obj = dumps(
                        {
                            "token": word,
                            "position": philo_id,
                            "start_byte": attrib["start_byte"],
                            "end_byte": attrib["end_byte"],
                            "philo_type": philo_type,
                        }
                    )
                    print(word_obj, file=output)
    with open(f"{filename}.lz4", "wb") as compressed_file:
        with open(filename, "rb") as input_file:
            compressed_file.write(lz4.frame.compress(input_file.read(), compression_level=4))
        os.remove(filename)


def pos_tagger(language):
    """POS Tagger using Spacy"""
    try:
        import spacy
    except ImportError:
        raise ImportError

    nlp = spacy.load(language, disable=["parser", "ner", "textcat"])

    def inner_pos_tagger(_, text):
        with open(text["words"] + ".tmp", "w") as tmp_file:
            with open(text["words"], encoding="utf8") as fh:
                sentence = []
                current_sent_id = None
                for line in fh:
                    philo_type, word, philo_id, attrib = line.split("\t")
                    sent_id = " ".join(philo_id.split()[:6])
                    record = Record(philo_type, word, philo_id.split())
                    record.attrib = loads(attrib)
                    if current_sent_id is not None and sent_id != current_sent_id:
                        parsed_sentence = nlp.tagger(spacy.tokens.Doc(nlp.vocab, [r.name for r in sentence]))
                        for saved_record, parsed_word in zip(sentence, parsed_sentence):
                            saved_record.attrib["pos"] = parsed_word.pos_
                            print(saved_record, file=tmp_file)
                        sentence = []
                    sentence.append(record)
                    current_sent_id = sent_id
            if sentence:
                parsed_sentence = nlp.tagger(spacy.tokens.Doc(nlp.vocab, [r.name for r in sentence]))
                for saved_record, parsed_word in zip(sentence, parsed_sentence):
                    saved_record.attrib["pos"] = parsed_word.pos_
                    print(saved_record, file=tmp_file)
        os.remove(text["words"])
        os.rename(text["words"] + ".tmp", text["words"])

    return inner_pos_tagger


DefaultNavigableObjects = ("doc", "div1", "div2", "div3", "para")
DefaultLoadFilters = [
    get_word_counts,
    generate_words_sorted,
    make_object_ancestors,
    make_sorted_toms,
    prev_next_obj,
    generate_pages,
    prev_next_page,
    generate_refs,
    generate_graphics,
    generate_lines,
    make_max_id,
    store_words_and_philo_ids,
]


def set_load_filters(load_filters=DefaultLoadFilters, navigable_objects=DefaultNavigableObjects):
    """Set default filters to run"""
    filters = []
    for load_filter in load_filters:
        if (
            load_filter.__name__ == "make_object_ancestors"
            or load_filter.__name__ == "make_sorted_toms"
            or load_filter.__name__ == "prev_next_obj"
            or load_filter.__name__ == "store_in_plain_text"
        ):
            filters.append(load_filter(*navigable_objects))
        else:
            filters.append(load_filter)
    return filters
