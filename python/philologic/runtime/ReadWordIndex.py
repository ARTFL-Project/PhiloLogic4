"""Read inverted index from lmdb database."""

from itertools import combinations
from collections import defaultdict
import time
import struct
import sqlite3
import subprocess
from unidecode import unidecode


from philologic.runtime.HitList import HitList

# from philologic.runtime.Query import expand_query_not

import lmdb
import lz4.frame
from msgpack import loads


def get_object_id(philo_id, level="sent"):
    """Return the object ID for a given level of the philo_id."""
    if level == "sent":
        return f"{philo_id[0]} {philo_id[1]} {philo_id[2]} {philo_id[3]} {philo_id[4]} {philo_id[5]}"
    elif level == "para":
        return f"{philo_id[0]} {philo_id[1]} {philo_id[2]} {philo_id[3]} {philo_id[4]}"


def fetch_sorted_philo_ids(db_env, word):
    # Fetch and return sorted philo_ids for a given word
    sorted_hits = []
    with db_env.begin() as txn:
        cursor = txn.cursor()
        if cursor.set_key(word):
            while cursor.key() == word:
                sorted_hits.append(cursor.value())
                if not cursor.next_dup():
                    break
    return sorted_hits


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
        for philo_ids in cursor:
            output_file.write(philo_ids[0])
    with open(hitlist_filename + ".done", "w"):
        pass


def search_cooccurrence(db_path, words, level):
    """Search for co-occurrences of multiple words in the same sentence in the database."""
    db_env = lmdb.open(f"{db_path}/words.lmdb", readonly=True)
    cooccurrences = []

    # Load occurrences for each word and add sentence IDs
    occurrences_by_text_object = defaultdict(lambda: defaultdict(list))
    with db_env.begin() as txn:
        for word in words:
            compressed_data = txn.get(word.encode("utf-8"))  # TODO: use getmulti to account for multiple word forms
            if compressed_data:
                occurrences = loads(lz4.frame.decompress(compressed_data))
                for philo_id, attrib in occurrences:
                    sentence_id = get_object_id(philo_id, level)
                    occurrences_by_text_object[sentence_id][word].append((philo_id, attrib))

    # Find co-occurrences
    for object_id, word_occurrences in occurrences_by_text_object.items():
        if all(word in word_occurrences for word in words):
            cooccurrences.append((object_id, {word: word_occurrences[word] for word in words}))

    db_env.close()
    return cooccurrences


def search_cooccurrence_within_n_words(db_path, words, n):
    """Search for co-occurrences of all specified words within n words of each other in the same sentence."""
    db_env = lmdb.open(f"{db_path}/words.lmdb", readonly=True)
    cooccurrences = []

    # Load occurrences for each word and organize by sentence IDs
    occurrences_by_sentence = defaultdict(lambda: defaultdict(list))
    with db_env.begin() as txn:
        for word in words:
            compressed_data = txn.get(word.encode("utf-8"))
            if compressed_data:
                occurrences = loads(lz4.frame.decompress(compressed_data))
                for philo_id, attrib in occurrences:
                    sentence_id = get_object_id(philo_id)
                    word_position = get_object_id(philo_id)
                    occurrences_by_sentence[sentence_id][word].append((word_position, attrib))

    # Find co-occurrences within n words
    for sentence_id, word_occurrences in occurrences_by_sentence.items():
        if all(word in word_occurrences for word in words):
            # Check word positions for co-occurrence within n words
            for word_combination in combinations(words, 2):
                for occ1 in word_occurrences[word_combination[0]]:
                    for occ2 in word_occurrences[word_combination[1]]:
                        if abs(occ1[0] - occ2[0]) <= n:
                            cooccurrences.append((word_combination, sentence_id, occ1, occ2))

    db_env.close()
    return cooccurrences


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
