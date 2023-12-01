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
import signal
from operator import le, eq

from typing import Iterator

import regex as re
from philologic.runtime import HitList
from philologic.runtime.QuerySyntax import group_terms, parse_query
from unidecode import unidecode


OBJECT_LEVEL = {"para": 5, "sent": 6}
os.environ["PATH"] += ":/usr/local/bin/"


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
    object_level="sent",
    exact=1,
):
    """Runs concordance queries"""
    sys.stdout.flush()
    parsed = parse_query(terms)
    grouped = group_terms(parsed)
    split = split_terms(grouped)
    words_per_hit = len(split)
    if not filename:
        hfile = str(multiprocessing.current_process().pid) + ".hitlist"
    dir = db.path + "/hitlists/"
    filename = filename or (dir + hfile)
    if not os.path.exists(filename):
        Path(filename).touch()
    frequency_file = db.path + "/frequencies/normalized_word_frequencies"
    # Handle SIGCHLD to avoid zombie processes
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    pid = os.fork()
    if pid == 0:  # In child process
        with open(f"{filename}.terms", "w") as terms_file:
            expand_query_not(split, frequency_file, terms_file, True, False)
        args = [
            "philosearch",
            f"--db_path={db.path}",
            f"--hitlist={filename}",
            f"--search_type={method}",
            f"--level={object_level}",
            f"--n={method_arg or 1}",
            f"--exact={exact}",
        ]
        if corpus_file is not None:
            args.append(f"--corpus_file={corpus_file}")
        print(" ".join(args), file=sys.stderr)
        subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=os.environ)
        os._exit(0)  # Exit child process
    else:
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


def get_cooccurrence_groups(
    db_path, word_groups, level="sent", corpus_philo_ids=None, object_level=None
) -> Iterator[tuple[bytes]]:
    if level == "sent":
        philo_object = "philo_sent_id"
    elif level == "para":
        philo_object = "philo_para_id"
    with sqlite3.connect(f"{db_path}/words.db") as conn:
        cursor = conn.cursor()
        subqueries = []
        all_args = []
        for i, words in enumerate(word_groups):
            placeholders = ", ".join("?" * len(words))
            subquery = f"(SELECT {philo_object}, philo_ids FROM words WHERE word IN ({placeholders})) AS grp{i}"
            subqueries.append(subquery)
            all_args.extend(words)

        join_conditions = " AND ".join(
            f"grp0.{philo_object} = grp{i}.{philo_object}" for i in range(1, len(word_groups))
        )
        query = f"SELECT grp0.{philo_object}, {', '.join(f'grp{i}.philo_ids AS philo_ids{i}' for i in range(len(word_groups)))} FROM {' INNER JOIN '.join(subqueries)} ON {join_conditions}"

        cursor.execute(query, all_args)
        if corpus_philo_ids is None:
            for group in cursor:
                yield group
        else:
            for group in cursor:
                philo_ids = group[1]
                found = False
                for start_byte in range(0, len(philo_ids), 36):
                    philo_id = philo_ids[start_byte : start_byte + 36]
                    if philo_id[:object_level] in corpus_philo_ids:
                        found = True
                        break
                if found is True:
                    yield group


def search_word(db_path, hitlist_filename, corpus_file=None):
    """Search for a single word in the database."""
    with open(f"{hitlist_filename}.terms", "r") as terms_file:
        words = terms_file.read().split()
    if corpus_file is None:
        # We start writing after 25 hits
        with sqlite3.connect(f"{db_path}/words.db") as conn, open(hitlist_filename, "wb", buffering=900) as output_file:
            cursor = conn.cursor()
            cursor.execute(f"""SELECT philo_ids FROM words WHERE word IN ({",".join(["?"] * len(words))})""", words)
            for (philo_ids,) in cursor:
                output_file.write(philo_ids)
    else:
        corpus_philo_ids, object_level = get_corpus_philo_ids(corpus_file)
        # We now check if the words are in within the corpus philo_ids
        with sqlite3.connect(f"{db_path}/words.db") as conn, open(hitlist_filename, "wb", buffering=900) as output_file:
            cursor = conn.cursor()
            cursor.execute(f"""SELECT philo_ids FROM words WHERE word IN ({",".join(["?"] * len(words))})""", words)
            for (philo_ids,) in cursor:
                for start_byte in range(0, len(philo_ids), 36):
                    philo_id = philo_ids[start_byte : start_byte + 36]
                    if philo_id[:object_level] in corpus_philo_ids:
                        output_file.write(philo_id)
                        break


def search_within_word_span(db_path, hitlist_filename, n, exact_phrase, corpus_file=None):
    """Search for co-occurrences of multiple words within n words of each other in the database."""
    word_groups = get_word_groups(f"{hitlist_filename}.terms")
    common_object_ids = get_cooccurrence_groups(db_path, word_groups, "sent")

    def generate_philo_ids(byte_sequence) -> Iterator[bytes]:
        """Generator that yields 36-byte long philo_ids from the byte sequence"""
        for i in range(0, len(byte_sequence), 36):
            yield byte_sequence[i : i + 36]

    if exact_phrase is True:
        comp = eq  # distance between words equals n
    else:
        comp = le  # distance between words is less than or equal to n
    buffer_size = (36 + 8 * (len(word_groups) - 1)) * 25  # we start writing after 25 hits
    with open(hitlist_filename, "wb", buffering=buffer_size) as output_file:
        for group in common_object_ids:
            philo_id_groups = (generate_philo_ids(group[i]) for i in range(1, len(group)))
            for group_combination in product(*philo_id_groups):
                # we now need to check if the positions are within n words of each other
                positions: list[int] = [struct.unpack("1i", philo_id[28:32])[0] for philo_id in group_combination]
                if comp(max(positions) - min(positions), n):
                    starting_id = group_combination[0]
                    for group_num in range(1, len(word_groups)):
                        starting_id += group_combination[group_num][28:36]
                    output_file.write(starting_id)


def search_within_text_object(db_path, hitlist_filename, level, corpus_file=None):
    """Search for co-occurrences of multiple words in the same sentence in the database."""
    word_groups = get_word_groups(f"{hitlist_filename}.terms")
    common_object_ids = get_cooccurrence_groups(db_path, word_groups, level)
    buffer_size = (36 + 8 * (len(word_groups) - 1)) * 25  # we start writing after 25 hits
    with open(hitlist_filename, "wb", buffering=buffer_size) as output_file:
        for group in common_object_ids:
            starting_id = group[1][:36]
            for philo_ids in group[2:]:
                for i in range(0, len(philo_ids), 36):
                    starting_id += philo_ids[i + 28 : i + 32] + philo_ids[i + 32 : i + 36]
                    break  # we only keep one philo_id per group: we are replicating the limitation of the old core
            output_file.write(starting_id)


def get_corpus_philo_ids(corpus_file):
    corpus_philo_ids = set()
    object_level = 0
    with open(corpus_file, "rb") as corpus:
        buffer = corpus.read(28)
        object_level = len(tuple(i for i in struct.unpack("7i", buffer) if i)) * 4
        while buffer:
            philo_id = tuple(i for i in struct.unpack("7i", buffer) if i)
            corpus_philo_ids.add(struct.pack(f"{len(philo_id)}i", *philo_id))
            corpus_philo_ids.add(philo_id)
            buffer = corpus.read(28)
    return corpus_philo_ids, object_level


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
