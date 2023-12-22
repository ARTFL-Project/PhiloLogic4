#!/usr/bin/env python3

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
import heapq
import numpy as np

from typing import Iterator
import lmdb

import regex as re
from philologic.runtime import HitList
from philologic.runtime.QuerySyntax import group_terms, parse_query
from unidecode import unidecode
from numba import njit, jit


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
    raw_bytes=False,
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
    pid = os.fork()
    if pid == 0:  # In child process
        os.umask(0)
        os.chdir(dir)
        os.setsid()
        pid = os.fork()
        if pid > 0:
            os._exit(0)
        with open(f"{filename}.terms", "w") as terms_file:
            expand_query_not(split, frequency_file, terms_file, True, False)
        args = [
            "philosearch",
            f"--db_path={db.path}",
            f"--hitlist={filename}",
            f"--search_type={method}",
            f"--level={object_level}",
            f"--n={method_arg or 1}",
            f"--exact_span={exact}",
        ]
        if corpus_file is not None:
            args.append(f"--corpus_file={corpus_file}")
        print(" ".join(args), file=sys.stderr)
        subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=os.environ)
        # std_out, std_err = worker.communicate()

        os._exit(0)  # Exit child process
    else:
        hits = HitList.HitList(
            filename,
            words_per_hit,
            db,
            method=method,
            sort_order=sort_order,
            raw=raw_results,
            raw_bytes=raw_bytes,
            ascii_conversion=ascii_conversion,
        )
        return hits


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


def search_word(db_path, hitlist_filename, corpus_file=None):
    """Search for a single word in the database."""
    with open(f"{hitlist_filename}.terms", "r") as terms_file:
        words = terms_file.read().split()
    corpus_philo_ids, object_level = None, None
    if corpus_file is not None:
        corpus_philo_ids, object_level = get_corpus_philo_ids(corpus_file)
    env = lmdb.open(f"{db_path}/words.lmdb", readonly=True, lock=False, readahead=False, max_dbs=2)
    if len(words) == 1:
        with env.begin(buffers=True) as txn, open(hitlist_filename, "wb") as output_file:
            if words[0].startswith("lemma:"):
                db = env.open_db(b"lemmas", txn=txn)
                word = words[0][6:]
            else:
                db = env.open_db(b"words", txn=txn)
                word = words[0]
            if corpus_file is None:
                print(len(txn.get(word.encode("utf8"), db=db)))
                output_file.write(txn.get(word.encode("utf8"), db=db))
            else:
                corpus_philo_ids, object_level = get_corpus_philo_ids(corpus_file)
                cursor = txn.cursor()
                if cursor.set_key(words[0].encode("utf8")):
                    full_array = np.frombuffer(cursor.value(), dtype=">u4").reshape(-1, 9)
                    masks = [np.all(full_array[:, :object_level] == row, axis=1) for row in corpus_philo_ids]
                    combined_mask = np.any(np.stack(masks, axis=0), axis=0)
                    output_file.write(full_array[combined_mask].tobytes())
    else:
        with env.begin(buffers=True) as txn, open(hitlist_filename, "wb") as output_file:
            db = env.open_db(b"words", txn=txn)
            for philo_ids in merge_word_group(txn, db, words):
                if corpus_philo_ids is not None:
                    masks = [np.all(philo_ids[:, :object_level] == row, axis=1) for row in corpus_philo_ids]
                    combined_mask = np.any(np.stack(masks, axis=0), axis=0)
                    output_file.write(philo_ids[combined_mask].tobytes())
                output_file.write(philo_ids.tobytes())
    env.close()


def is_greater(arr1, arr2):
    return arr1[0] > arr2[0] or (arr1[0] == arr2[0] and arr1[1] > arr2[1])


def search_phrase(db_path, hitlist_filename, corpus_file=None):
    """Phrase searches where words need to be in a specific order"""
    with open(f"{hitlist_filename}.terms", "r") as terms_file:
        words = terms_file.read().split()
    if corpus_file is None:
        env = lmdb.open(f"{db_path}/words.lmdb", readonly=True, lock=False, readahead=False)
        with env.begin() as txn, open(hitlist_filename, "wb") as output_file:
            results = []
            byte_streams = {}
            philo_id_length = 36  # Length of a full philo_id (9 integers * 4 bytes each)
            cursor = txn.cursor()
            for i, word in enumerate(words):
                if cursor.set_key(word.encode("utf8")):
                    philo_ids = cursor.value()
                    results.append(((philo_ids[i : i + 36], philo_ids[i:24]) for i in range(0, len(philo_ids), 36)))

            # Iterate over both byte streams and write when they are within one word of each other
            # for philo_id_tuples in zip(*results):

            # byte_stream = cursor.value()
            # byte_streams[i] = byte_stream
            # first_philo_id = byte_stream[:36]
            # heapq.heappush(pq, (first_philo_id, i, 0))  # (philo_id, word_index, byte_index)

            # # Iterate and write sorted philo_ids
            # while pq:
            #     philo_id, word_index, byte_index = heapq.heappop(pq)
            #     if word_index == len(words) - 1:
            #         if word_index == 0:
            #             output_file.write(philo_id)
            #         else:
            #             output_file.write(philo_id[28:])
            #     else:
            #         next_byte_index = byte_index + philo_id_length
            #         if next_byte_index < len(byte_streams[word_index]):
            #             next_philo_id = byte_streams[word_index][next_byte_index : next_byte_index + philo_id_length]
            #             heapq.heappush(pq, (next_philo_id, word_index + 1, next_byte_index))
    else:
        corpus_philo_ids, object_level = get_corpus_philo_ids(corpus_file)
        with sqlite3.connect(f"{db_path}/words.db") as conn, open(hitlist_filename, "wb", buffering=900) as output_file:
            cursor = conn.cursor()
            cursor.execute(f"""SELECT philo_ids FROM words WHERE word IN ({",".join(["?"] * len(words))})""", words)
            for (philo_ids,) in cursor:
                philo_ids = extract_philo_ids(philo_ids, 36)
                for i, philo_id in enumerate(philo_ids):
                    if i == len(philo_ids) - 1:
                        output_file.write(philo_id)
                    else:
                        next_philo_id = philo_ids[i]


def search_within_word_span(db_path, hitlist_filename, n, exact_distance, corpus_file=None):
    """Search for co-occurrences of multiple words within n words of each other in the database."""
    word_groups = get_word_groups(f"{hitlist_filename}.terms")
    object_level = None
    corpus_philo_ids = None
    if corpus_file is not None:
        corpus_philo_ids, object_level = get_corpus_philo_ids(corpus_file)
    common_object_ids = get_cooccurrence_groups(
        db_path, word_groups, corpus_philo_ids=corpus_philo_ids, object_level=object_level
    )

    def generate_philo_ids(byte_sequence) -> Iterator[bytes]:
        """Generator that yields 36-byte long philo_ids from the byte sequence"""
        for i in range(0, len(byte_sequence), 36):
            yield byte_sequence[i : i + 36]

    if exact_distance is True:
        comp = eq  # distance between words equals n
    else:
        comp = le  # distance between words is less than or equal to n
    with open(hitlist_filename, "wb") as output_file:
        for group in common_object_ids:
            philo_id_groups = (generate_philo_ids(group[i]) for i in range(len(group)))
            for group_combination in product(*philo_id_groups):
                # we now need to check if the positions are within n words of each other
                positions: list[int] = [struct.unpack(">1I", philo_id[28:32])[0] for philo_id in group_combination]
                if comp(max(positions) - min(positions), n):
                    starting_id = group_combination[0]
                    for group_num in range(1, len(word_groups)):
                        starting_id += group_combination[group_num][28:36]
                    output_file.write(starting_id)


def search_within_text_object(db_path, hitlist_filename, level, corpus_file=None):
    """Search for co-occurrences of multiple words in the same sentence in the database."""
    word_groups = get_word_groups(f"{hitlist_filename}.terms")
    object_level = None
    corpus_philo_ids = None
    if corpus_file is not None:
        corpus_philo_ids, object_level = get_corpus_philo_ids(corpus_file)
    common_object_ids = get_cooccurrence_groups(
        db_path, word_groups, level=level, corpus_philo_ids=corpus_philo_ids, object_level=object_level
    )
    with open(hitlist_filename, "wb") as output_file:
        for group in common_object_ids:
            starting_id = group[0][:36]
            for philo_ids in group[1:]:
                for i in range(0, len(philo_ids), 36):
                    starting_id += philo_ids[i + 28 : i + 32] + philo_ids[i + 32 : i + 36]
                    break  # we only keep one philo_id per group: we are replicating the limitation of the old core
            output_file.write(starting_id)


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


def get_cooccurrence_groups(db_path, word_groups, level="sent", corpus_philo_ids=None, object_level=None):
    cooc_level = 24
    if level == "para":
        cooc_level = 20
    env = lmdb.open(f"{db_path}/words.lmdb", readonly=True, lock=False, max_dbs=2)
    philo_ids_per_group = []
    group_dicts = []
    philo_id_object_intersection = None
    with env.begin() as txn:
        db = env.open_db(b"words", txn=txn)
        lemma_cursor = None
        cursor = txn.cursor(db=db)
        for group in word_groups:
            philo_ids = b""
            group_dict = {}
            for word in group:
                if word.startswith("lemma:"):
                    if lemma_cursor is None:
                        lemma_cursor = txn.cursor(db=env.open_db(b"lemmas", txn=txn))
                    if lemma_cursor.set_key(word[6:].encode("utf8")):
                        philo_ids += lemma_cursor.value()
                elif cursor.set_key(word.encode("utf8")):
                    philo_ids += cursor.value()
            philo_ids_per_group.append(philo_ids)

    env.close()

    # Sort group by order of philo_id length
    philo_ids_per_group.sort(key=len)
    first_group_set = set()
    for n, philo_id_bytes in enumerate(philo_ids_per_group):
        group_dict = {}
        for start_byte in range(0, len(philo_id_bytes), 36):
            philo_id_object = philo_id_bytes[start_byte : start_byte + cooc_level]
            if n == 0 or philo_id_object in first_group_set:  # We only add the philo_id if it is in the first group
                if philo_id_object not in group_dict:
                    group_dict[philo_id_object] = philo_id_bytes[start_byte : start_byte + 36]
                else:
                    group_dict[philo_id_object] += philo_id_bytes[start_byte : start_byte + 36]
        if n == 0:
            first_group_set = set(group_dict)  # We only need to keep track of the first group's philo_ids
        group_dicts.append(group_dict)

    # We calculate the intersection from the group_dicts using standard set intersection
    philo_id_object_intersection = set(group_dicts[0])
    for group_dict in group_dicts[1:]:
        philo_id_object_intersection.intersection_update(set(group_dict))

    if corpus_philo_ids is not None:
        intersection_array = np.frombuffer(b"".join(philo_id_object_intersection), dtype=">u4").reshape(
            -1, cooc_level // 4
        )
        masks = [np.all(intersection_array[:, : object_level // 4] == row, axis=1) for row in corpus_philo_ids]
        combined_mask = np.any(np.stack(masks, axis=0), axis=0)
        philo_id_object_intersection = set(row.tobytes() for row in intersection_array[combined_mask])

    def isorted(iterable):  # Lazy sort to return results as quickly as they are sorted
        lst = list(iterable)
        heapq.heapify(lst)
        pop = heapq.heappop
        while lst:
            yield pop(lst)

    for philo_object_id in isorted(philo_id_object_intersection):
        yield tuple(group_dict[philo_object_id] for group_dict in group_dicts)


def extract_philo_ids(philo_ids: bytes, byte_length):
    """Generator that yields 36-byte long philo_ids from the byte sequence"""
    for start_byte in range(0, len(philo_ids), byte_length):
        yield philo_ids[start_byte : start_byte + byte_length]


def get_cooccurrence_groups_mun(db_path, word_groups, level="sent", corpus_philo_ids=None, object_level=None):
    cooc_slice = 6
    if level == "para":
        cooc_slice = 5
    env = lmdb.open(f"{db_path}/words.lmdb", readonly=True, lock=False, max_dbs=2)
    # start = time.time()
    with env.begin(buffers=True) as txn:
        db_words = env.open_db(b"words", txn=txn)

        # Determine which group has the smallest byte size
        byte_size_per_group = []
        for group in word_groups:
            byte_size = 0
            for word in group:
                byte_size += len(txn.get(word.encode("utf8"), db=db_words))
            byte_size_per_group.append(byte_size)
        # Perform an argsort on the list to get the indices of the groups sorted by byte size
        sorted_indices = np.argsort(byte_size_per_group)
        # print("Sort", time.time() - start)

        # Process each word group
        first_group_data = None
        group_generators = []
        for index in sorted_indices:
            words = word_groups[index]
            if index == sorted_indices[0]:  # grab the entire first group
                first_group_data = np.frombuffer(
                    b"".join([i for i in merge_word_group(txn, db_words, words, corpus_philo_ids, object_level)]),
                    dtype=">u4",
                ).reshape(-1, 9)
            else:
                group_generators.append(merge_word_group(txn, db_words, words, corpus_philo_ids, object_level))

        # Create a generator function which takes a group of philo_ids and returns an array
        def create_array(philo_id_group):
            try:
                philo_ids = next(philo_id_group)
            except StopIteration:
                raise StopIteration
            array = np.frombuffer(philo_ids, dtype=">u4").reshape(-1, 9)
            return array

        # print("Starting merge", time.time() - start)

        # Go over the remaining groups and add the philo_ids to the group_dicts
        group_data = [None for _ in range(len(word_groups) - 1)]
        break_out = False
        previous_row = None
        for index in first_group_data:
            results = []
            match = True
            philo_id_object = index[:cooc_slice]
            if np.array_equal(philo_id_object, previous_row) and previous_row is not None:
                continue
            previous_row = philo_id_object
            for group_index, philo_id_group in enumerate(group_generators):
                if group_data[group_index] is None:
                    try:
                        philo_id_df = create_array(philo_id_group)
                    except StopIteration:
                        break_out = True
                        break
                else:
                    philo_id_df = group_data[group_index]

                # Is the first row greater than the current philo_id_object?
                if compare_rows(philo_id_df[0][:cooc_slice], philo_id_object) == 1:
                    match = False
                    break

                # Is the last row less than the current philo_id_object?
                while compare_rows(philo_id_df[-1][:cooc_slice], philo_id_object) == -1:
                    try:
                        philo_id_df = create_array(philo_id_group)
                    except StopIteration:
                        break_out = True
                        break

                if break_out is True:
                    break

                equal_rows_mask = np.all(philo_id_df[:, :cooc_slice] == philo_id_object, axis=1)
                matching_rows = philo_id_df[equal_rows_mask]
                if matching_rows.shape[0] == 0:
                    match = False
                    break
                group_data[group_index] = philo_id_df
                results.append(
                    matching_rows[0].tobytes()
                )  # We only keep the first instance of a hit in the first group

            if break_out is True:
                break
            elif match is True:
                results.append(index.tobytes())  # We only keep the first instance of a hit in the first group
                yield tuple(results)

    env.close()


def compare_rows(row1, row2):
    for i in range(len(row1)):
        if row1[i] != row2[i]:
            return 1 if row1[i] > row2[i] else -1
    return 0


def merge_word_group(
    txn,
    db,
    words: list[str],
):
    # Initialize data structures for each word
    start = time.time()
    word_data = {
        word: {"buffer": txn.get(word.encode("utf8"), db=db), "array": None, "index": 0, "start": 0} for word in words
    }
    chunk_size = 36 * 10000  # 10000 hits: happy median between performance and memory usage, potentially reevaluate.

    # Load initial chunks
    for word in words:
        # TODO: Only load 100 hits initially to quickly return results
        word_data[word]["array"] = np.frombuffer(word_data[word]["buffer"][0:3600], dtype=">u4").reshape(-1, 9)

    def is_greater(arr1, arr2):
        return arr1[0] > arr2[0] or (arr1[0] == arr2[0] and arr1[1] > arr2[1])

    # Merge sort and write loop
    while any(word_data[word]["array"].size > 0 for word in words):
        words_first_last_row = [
            (word, word_data[word]["array"][0, ::8], word_data[word]["array"][-1, ::8])
            for word in words
            if word_data[word]["array"].size > 0
        ]

        # Which word finishes first?
        first_word_to_finish, _, first_finishing_row = sorted(words_first_last_row, key=lambda x: (x[2][0], x[2][1]))[0]

        # Determine which words start before the first finishing word ends
        # Save index of first row that exceeds the first finishing word
        words_to_keep = []
        for other_word, other_first_row, _ in words_first_last_row:
            if other_word == first_word_to_finish:
                words_to_keep.append((other_word, None))
                continue
            elif is_greater(
                other_first_row, first_finishing_row
            ):  # dismiss words that start before the first finishing word ends
                continue
            else:
                first_exceeding_indices = np.where(word_data[other_word]["array"][:, 0] > first_finishing_row[0])
                if first_exceeding_indices[0].size != 0:
                    first_exceeding_index = first_exceeding_indices[0][0]
                    remaining_array = word_data[other_word]["array"][:first_exceeding_index]
                else:
                    remaining_array = word_data[other_word]["array"]
                if np.all(remaining_array[:, 0] < first_finishing_row[0]):  # all doc_ids are less than finishing doc id
                    words_to_keep.append((other_word, remaining_array.shape[0]))
                    continue
                # Are there equal doc_ids? If so, we need to break the tie by comparing byte offsets
                equal_doc_rows = np.where(remaining_array[:, 0] == first_finishing_row[0])
                last_equal_index = equal_doc_rows[0][-1] + 1  # +1 to include the last equal row
                remaining_array = word_data[other_word]["array"][:last_equal_index]
                exceeding_rows_mask = (remaining_array[:, 0] == first_finishing_row[0]) & (
                    remaining_array[:, -1] > first_finishing_row[1]
                )
                potential_exceeding_indices = np.where(exceeding_rows_mask)
                if potential_exceeding_indices[0].size != 0:
                    first_exceeding_index = potential_exceeding_indices[0][0]
                    words_to_keep.append((other_word, first_exceeding_index))
                else:
                    words_to_keep.append((other_word, last_equal_index))

        # Merge sort partial philo_id arrays
        combined_arrays = np.concatenate(
            [word_data[word]["array"][:index] for word, index in words_to_keep],
            dtype=">u4",
        )
        sorted_indices = np.lexsort((combined_arrays[:, -1], combined_arrays[:, 0]))  # sort by doc id and byte offset
        yield combined_arrays[sorted_indices]

        # Load next chunks for all words based on the indices we saved
        for word, index in words_to_keep:
            word_data[word]["start"] += word_data[word]["array"][:index].nbytes
            end = word_data[word]["start"] + chunk_size
            word_data[word]["array"] = np.frombuffer(
                word_data[word]["buffer"][word_data[word]["start"] : end], dtype=">u4"
            ).reshape(-1, 9)


def get_corpus_philo_ids(corpus_file, byte_output=False) -> tuple[np.ndarray, int] | tuple[set[bytes], int]:
    object_level = 0
    with open(corpus_file, "rb") as corpus:
        buffer = corpus.read(28)
        object_level = len(tuple(i for i in struct.unpack(">7I", buffer) if i))
        if byte_output is False:
            return np.frombuffer(buffer + corpus.read(), dtype=">u4").reshape(-1, 7)[:, :object_level], object_level
        else:
            object_level *= 4
            philo_ids = {buffer}
            corpus = corpus.read()
            for philo_id in extract_philo_ids(corpus, 28):
                philo_ids.add(philo_id)
            return philo_ids, object_level


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
            elif kind == "LEMMA":
                grep_proc = grep_lemma(token, freq_file, filter_inputs[0])
                grep_proc.wait()
        # close all the pipes and wait for procs to finish.
        for pipe, proc in zip(filter_inputs, filter_procs):
            pipe.close()
            proc.wait()


def grep_lemma(token, freq_file, dest_fh):
    """Grep on lemmas"""
    lemma_file = os.path.join(os.path.dirname(freq_file), "lemmas")
    try:
        grep_proc = subprocess.Popen(["rg", "-a", b"^%s$" % token, lemma_file], stdout=dest_fh)
    except (UnicodeEncodeError, TypeError):
        grep_proc = subprocess.Popen(["rg", "-a", b"^%s$" % token.encode("utf8"), lemma_file], stdout=dest_fh)
    return grep_proc


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
