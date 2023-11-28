#!/usr/bin/env python3

from collections import defaultdict
import os
import subprocess
import sys
import multiprocessing
import sqlite3
import struct
from itertools import product
from pathlib import Path
import time

import regex as re
from philologic.runtime import HitList
from philologic.runtime.QuerySyntax import group_terms, parse_query
from unidecode import unidecode


OBJECT_LEVEL = {"para": 5, "sent": 6}


def query(
    db,
    terms,
    corpus_file=None,
    corpus_size=0,
    method=None,
    method_arg=None,
    limit=3000,
    filename="",
    query_debug=False,
    sort_order=None,
    raw_results=False,
    ascii_conversion=True,
):
    """Runs concordance queries"""
    parsed = parse_query(terms)
    grouped = group_terms(parsed)
    split = split_terms(grouped)
    words_per_hit = len(split)
    if not filename:
        hfile = str(multiprocessing.current_process().pid) + ".hitlist"
    dir = db.path + "/hitlists/"
    filename = filename or (dir + hfile)
    Path(filename).touch()
    frequency_file = db.path + "/frequencies/normalized_word_frequencies"
    print(len(split), file=sys.stderr)
    # Multiprocessing setup
    if method in ("proxy", None):
        if len(split) == 1:
            print("searching for a single word", file=sys.stderr)
            process = multiprocessing.Process(target=search_word, args=(db.path, split, filename, frequency_file, db))
        else:
            process = multiprocessing.Process(
                target=search_phrase, args=(db.path, split, filename, frequency_file, db, method_arg)
            )
    elif method == "cooc":
        process = multiprocessing.Process(
            target=search_cooccurrence, args=(db.path, split, filename, frequency_file, db, "sent")
        )
    elif method == "phrase":
        process = multiprocessing.Process(
            target=search_phrase, args=(db.path, split, filename, frequency_file, db, method_arg, "sent")
        )
    process.start()
    return HitList.HitList(
        filename,
        words_per_hit,
        db,
        method=method,
        sort_order=sort_order,
        raw=raw_results,
        ascii_conversion=ascii_conversion,
    )


def get_expanded_query(hitlist):
    fn = hitlist.filename + ".terms"
    query = []
    term = []
    try:
        grep_results = open(fn, "r", encoding="utf8")
    except:
        return []
    for line in grep_results:
        if line == "\n":
            query.append(term)
            term = []
        else:
            term.append('"' + line[:-1] + '"')
    if term:
        query.append(term)
    return query


def split_terms(grouped):
    split = []
    for group in grouped:
        if len(group) == 1:
            kind, token = group[0]
            if kind == "QUOTE" and token.find(" ") > 1:  # we can split quotes on spaces if there is no OR
                for split_tok in token[1:-1].split(" "):
                    split.append((("QUOTE", '"' + split_tok + '"'),))
            elif kind == "RANGE":
                split.append((("TERM", token),))
            else:
                split.append(group)
        else:
            split.append(group)
    return split


def get_word_groups(terms_file):
    word_groups = []
    with open(terms_file, "r") as terms_file:
        word_group = []
        for line in terms_file:
            word = line.strip()
            if word:
                word_group.append(word)
            elif word_group:
                word_groups.append(word_group)
                word_group = []
        if word_group:
            word_groups.append(word_group)
    return word_groups


def get_cooccurrence_groups(db_path, word_groups, level="sent"):
    philo_ids_by_object_id = [{} for _ in range(len(word_groups))]
    if level == "sent":
        object_level = 6
    elif level == "para":
        object_level = 5
    with sqlite3.connect(f"{db_path}/words.db") as conn:
        cursor = conn.cursor()
        for group_num, words in enumerate(word_groups):
            cursor.execute(f"SELECT philo_ids FROM words WHERE word IN ({', '.join('?' * len(words))})", words)
            for (philo_ids,) in cursor:
                for philo_id in struct.iter_unpack("9i", philo_ids):
                    object_id = philo_id[:object_level]
                    if object_id not in philo_ids_by_object_id[group_num]:
                        philo_ids_by_object_id[group_num][object_id] = []
                    philo_ids_by_object_id[group_num][object_id].append(philo_id)

    # Identify common object_ids across all groups
    object_id_sets = [set(philo_ids) for philo_ids in philo_ids_by_object_id]
    common_object_ids = sorted(set.intersection(*object_id_sets) if object_id_sets else set())
    return philo_ids_by_object_id, common_object_ids


def search_word(db_path, split_terms, hitlist_filename, frequency_file, db):
    """Search for a single word in the database."""
    terms_file = open(f"{hitlist_filename}.terms", "w")
    expand_query_not(split_terms, frequency_file, terms_file, db.locals.ascii_conversion, db.locals["lowercase_index"])
    terms_file.close()
    with open(terms_file.name, "r") as terms_file:
        words = terms_file.read().split()
    with sqlite3.connect(f"{db_path}/words.db") as conn, open(hitlist_filename, "wb") as output_file:
        cursor = conn.cursor()
        cursor.execute(f"""SELECT philo_ids FROM words WHERE word IN ({",".join(["?"] * len(words))})""", words)
        for (philo_ids,) in cursor:
            output_file.write(philo_ids)
    with open(hitlist_filename + ".done", "w"):
        pass


def search_phrase(db_path, split_terms, hitlist_filename, frequency_file, db, n, level="sent"):
    """Search for co-occurrences of multiple words within n words of each other in the database."""
    with open(f"{hitlist_filename}.terms", "w") as terms_file:
        expand_query_not(
            split_terms, frequency_file, terms_file, db.locals.ascii_conversion, db.locals["lowercase_index"]
        )

    word_groups = get_word_groups(terms_file.name)
    philo_ids_by_object_id, common_object_ids = get_cooccurrence_groups(db_path, word_groups, level)

    # Find co-occurrences: we need to find all combinations between all groups
    with open(hitlist_filename, "wb") as output_file:
        for object_id in common_object_ids:
            philo_id_groups = (philo_ids_by_object_id[group_num][object_id] for group_num in range(len(word_groups)))
            for group_combination in product(*philo_id_groups):
                # we now need to check if the positions are within n words of each other
                positions = [philo_id[6] for philo_id in group_combination]
                if max(positions) - min(positions) <= n:
                    starting_id = group_combination[0]
                    for group_num in range(1, len(word_groups)):
                        starting_id += (group_combination[group_num][6], group_combination[group_num][-1])
                    output_file.write(struct.pack(f"{len(starting_id)}i", *starting_id))

    with open(hitlist_filename + ".done", "w"):
        pass


def search_cooccurrence(db_path, split_terms, hitlist_filename, frequency_file, db, level):
    """Search for co-occurrences of multiple words in the same sentence in the database."""
    with open(f"{hitlist_filename}.terms", "w") as terms_file:
        expand_query_not(
            split_terms, frequency_file, terms_file, db.locals.ascii_conversion, db.locals["lowercase_index"]
        )
    word_groups = get_word_groups(terms_file.name)
    philo_ids_by_object_id, common_object_ids = get_cooccurrence_groups(db_path, word_groups, level)

    # Find co-occurrences
    with open(hitlist_filename, "wb") as output_file:
        for object_id in common_object_ids:
            starting_id = philo_ids_by_object_id[0][object_id].pop()
            for group_num in range(
                1, len(word_groups)
            ):  # we skip the first group because we already have the starting_id (see below comment)
                for philo_id in philo_ids_by_object_id[group_num][object_id]:
                    starting_id += (philo_id[6], philo_id[-1])
                    break  # we only keep one philo_id per group: we are replicating the limitation of the old core
            output_file.write(struct.pack(f"{len(starting_id)}i", *starting_id))

        output_file.flush()

    with open(hitlist_filename + ".done", "w"):
        pass


def get_object_id(philo_id, level="sent"):
    """Return the object ID for a given level of the philo_id."""
    if level == "sent":
        return f"{philo_id[0]} {philo_id[1]} {philo_id[2]} {philo_id[3]} {philo_id[4]} {philo_id[5]}"
    elif level == "para":
        return f"{philo_id[0]} {philo_id[1]} {philo_id[2]} {philo_id[3]} {philo_id[4]}"


def expand_query_not(split, freq_file, dest_fh, ascii_conversion, lowercase=True):
    """Expand search term"""
    first = True
    grep_proc = None
    for group in split:
        if first == True:
            first = False
        else:  # bare newline starts a new group, except the first
            try:
                dest_fh.write("\n")
            except TypeError:
                dest_fh.write(b"\n")
            dest_fh.flush()

        # find all the NOT terms and separate them out by type
        exclude = []
        for i, g in enumerate(group):
            kind, token = g
            if kind == "NOT":
                exclude = group[i + 1 :]
                group = group[:i]
                break
        cut_proc = subprocess.Popen("cut -f 2 | sort | uniq", stdin=subprocess.PIPE, stdout=dest_fh, shell=True)
        filter_inputs = [cut_proc.stdin]
        filter_procs = [cut_proc]

        # We will chain all NOT operators backward from the main filter.
        for kind, token in exclude:
            if kind == "TERM" and ascii_conversion is True:
                proc = invert_grep(token, subprocess.PIPE, filter_inputs[0], lowercase)
            if kind == "TERM" and ascii_conversion is True:
                proc = invert_grep_exact(token, subprocess.PIPE, filter_inputs[0])
            if kind == "QUOTE":
                token = token[1:-1]
                proc = invert_grep_exact(token, subprocess.PIPE, filter_inputs[0])
            filter_inputs = [proc.stdin] + filter_inputs
            filter_procs = [proc] + filter_procs

        # then we append output from all the greps into the front of that filter chain.
        for kind, token in group:  # or, splits, and ranges should have been taken care of by now.
            if (kind == "TERM" and ascii_conversion is True) or kind == "RANGE":
                grep_proc = grep_word(token, freq_file, filter_inputs[0], lowercase)
                grep_proc.wait()
            elif kind == "TERM" and ascii_conversion is False:
                grep_proc = grep_exact(token, freq_file, filter_inputs[0])
                grep_proc.wait()
            elif kind == "QUOTE":
                token = token[1:-1]
                grep_proc = grep_exact(token, freq_file, filter_inputs[0])
                grep_proc.wait()
        # close all the pipes and wait for procs to finish.
        for pipe, proc in zip(filter_inputs, filter_procs):
            pipe.close()
            proc.wait()


def grep_word(token, freq_file, dest_fh, lowercase=True):
    """Grep on normalized words"""
    if lowercase:
        token = token.lower()
    norm_tok_uni_chars = unidecode(token)
    norm_tok = "".join(norm_tok_uni_chars)
    try:
        grep_command = ["rg", "-a", "^%s[[:blank:]]" % norm_tok, freq_file]
        grep_proc = subprocess.Popen(grep_command, stdout=dest_fh)
    except (UnicodeEncodeError, TypeError):
        grep_command = ["rg", "-a", b"^%s[[:blank:]]" % norm_tok.encode("utf8"), freq_file]
        grep_proc = subprocess.Popen(grep_command, stdout=dest_fh)
    return grep_proc


def invert_grep(token, in_fh, dest_fh, lowercase=True):
    """NOT grep"""
    if lowercase:
        token = token.lower()
    norm_tok_uni_chars = unidecode(token)
    norm_tok = "".join(norm_tok_uni_chars)
    try:
        grep_command = ["rg", "-a", "-v", "^%s[[:blank:]]" % norm_tok]
        grep_proc = subprocess.Popen(grep_command, stdin=in_fh, stdout=dest_fh)
    except (UnicodeEncodeError, TypeError):
        grep_command = ["rg", "-a", "-v", b"^%s[[:blank:]]" % norm_tok.encode("utf8")]
        grep_proc = subprocess.Popen(grep_command, stdin=in_fh, stdout=dest_fh)
    return grep_proc


def grep_exact(token, freq_file, dest_fh):
    """Exact grep"""
    try:
        grep_proc = subprocess.Popen(["rg", "-a", b"[[:blank:]]%s$" % token, freq_file], stdout=dest_fh)
    except (UnicodeEncodeError, TypeError):
        grep_proc = subprocess.Popen(["rg", "-a", b"[[:blank:]]%s$" % token.encode("utf8"), freq_file], stdout=dest_fh)
    return grep_proc


def invert_grep_exact(token, in_fh, dest_fh):
    """NOT exact grep"""
    # don't strip accent or case, exact match only.
    try:
        grep_proc = subprocess.Popen(["rg", "-a", "-v", b"[[:blank:]]%s$" % token], stdin=in_fh, stdout=dest_fh)
    except (UnicodeEncodeError, TypeError):
        grep_proc = subprocess.Popen(
            ["rg", "-a", "-v", b"[[:blank:]]%s$" % token.encode("utf8")], stdin=in_fh, stdout=dest_fh
        )
    # can't wait because input isn't ready yet.
    return grep_proc


def query_parse(query_terms, config):
    """Parse query function."""
    for pattern, replacement in config.query_parser_regex:
        query_terms = re.sub(rf"{pattern}", rf"{replacement}", query_terms, re.U)
    return query_terms


if __name__ == "__main__":
    path = sys.argv[1]
    terms = sys.argv[2:]
    parsed = parse_query(" ".join(terms))
    print("PARSED:", parsed, file=sys.stderr)
    grouped = group_terms(parsed)
    print("GROUPED:", grouped, file=sys.stderr)
    split = split_terms(grouped)
    print("parsed %d terms:" % len(split), split, file=sys.stderr)

    class Fake_DB:
        pass

    fake_db = Fake_DB()
    from philologic.Config import DB_LOCALS_DEFAULTS, DB_LOCALS_HEADER, Config

    fake_db.path = path + "/data/"
    fake_db.locals = Config(fake_db.path + "/db.locals.py", DB_LOCALS_DEFAULTS, DB_LOCALS_HEADER)
    fake_db.encoding = "utf-8"
    freq_file = path + "/data/frequencies/normalized_word_frequencies"
    # expand_query_not(split, freq_file, sys.stdout)
    hits = query(fake_db, " ".join(terms), query_debug=True, raw_results=True)
    hits.finish()
    for hit in hits:
        print(hit)
