#!/usr/bin/env python3


import math
import os
import sqlite3
import time
import unicodedata

import lz4.frame
import msgpack
import multiprocess as mp
import numpy as np
from rapidjson import loads
from scipy.sparse import csr_matrix, vstack
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from tqdm import tqdm


def make_sql_table(table, file_in, db_file="toms.db", indices=[], depth=7):
    def inner_make_sql_table(loader_obj):
        print(f"{time.ctime()}: Loading the {table} SQLite table...")
        db_destination = os.path.join(loader_obj.destination, db_file)
        line_count = sum(1 for _ in open(file_in, "rbU"))
        conn = sqlite3.connect(db_destination)
        conn.text_factory = str
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        columns = "philo_type, philo_name, philo_id, philo_seq"
        query = "create table if not exists %s (%s)" % (table, columns)
        cursor.execute(query)
        with tqdm(total=line_count, leave=False) as pbar:
            with open(file_in) as input_file:
                for sequence, line in enumerate(input_file):
                    philo_type, philo_name, id, attrib = line.split("\t", 3)
                    fields = id.split(None, 8)
                    if len(fields) == 9:
                        row = loads(attrib)
                        row["philo_type"] = philo_type
                        row["philo_name"] = philo_name
                        row["philo_id"] = " ".join(fields[:depth])
                        row["philo_seq"] = sequence
                        insert = f"INSERT INTO {table} ({','.join(list(row.keys()))}) values ({','.join('?' for i in range(len(row)))});"
                        try:
                            cursor.execute(insert, list(row.values()))
                        except sqlite3.OperationalError:
                            cursor.execute("PRAGMA table_info(%s)" % table)
                            column_list = [i[1] for i in cursor]
                            for column in row:
                                if column not in column_list:
                                    cursor.execute("ALTER TABLE %s ADD COLUMN %s;" % (table, column))
                            cursor.execute(insert, list(row.values()))
                    pbar.update()
        conn.commit()

        for index in indices:
            try:
                if isinstance(index, str):
                    index = (index,)
                index_name = "%s_%s_index" % (table, "_".join(index))
                index = ",".join(index)
                cursor.execute("create index if not exists %s on %s (%s)" % (index_name, table, index))
                if table == "toms":
                    index_null_name = f"{index}_null_index"  # this is for hitlist stats queries which require indexing philo_id with null metadata values
                    cursor.execute(
                        f"CREATE UNIQUE INDEX IF NOT EXISTS {index_null_name} ON toms(philo_id, {index}) WHERE {index} IS NULL"
                    )
            except sqlite3.OperationalError:
                pass
        conn.commit()
        conn.close()

        if not loader_obj.debug:
            os.system("rm %s" % file_in)

    return inner_make_sql_table


def make_sentences_table(datadir, db_destination):
    """Generate a table where each row is a sentence containing all the words in it"""

    def inner_make_sentences(loader_obj):
        print(f"{time.ctime()}: Loading the sentences SQLite table...")
        with sqlite3.connect(db_destination) as conn:
            conn.text_factory = str
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS sentences(philo_id text, words blob)")
            line_count = sum(
                sum(1 for _ in lz4.frame.open(raw_words.path))
                for raw_words in os.scandir(f"{datadir}/words_and_philo_ids")
            )
            with tqdm(total=line_count, leave=False) as pbar:
                for raw_words in os.scandir(f"{datadir}/words_and_philo_ids"):
                    with lz4.frame.open(raw_words.path) as input_file:
                        current_sentence = None
                        words = []
                        for line in input_file:
                            word_obj = loads(line.decode("utf8"))
                            if word_obj["philo_type"] == "word":
                                sentence_id = " ".join(word_obj["position"].split()[:6]) + " 0"
                                if sentence_id != current_sentence:
                                    if current_sentence is not None:
                                        cursor.execute(
                                            "insert into sentences values(?, ?)",
                                            (current_sentence, lz4.frame.compress(msgpack.dumps(words))),
                                        )
                                        words = []
                                    current_sentence = sentence_id
                                words.append({"word": word_obj["token"], "start_byte": word_obj["start_byte"]})
                            pbar.update()
                        cursor.execute(  # insert last sentence in doc
                            "insert into sentences values(?, ?)",
                            (sentence_id, lz4.frame.compress(msgpack.dumps(words))),
                        )
            cursor.execute("create index sentence_index on sentences (philo_id)")
            conn.commit()

    return inner_make_sentences


def word_frequencies(loader_obj):
    print("%s: Generating word frequencies..." % time.ctime())
    frequencies = loader_obj.destination + "/frequencies"
    os.system("mkdir %s" % frequencies)
    output = open(frequencies + "/word_frequencies", "w")
    for line in open(loader_obj.destination + "/WORK/all_frequencies"):
        count, word = tuple(line.split())
        print(word + "\t" + count, file=output)
    output.close()


def normalized_word_frequencies(loader_obj):
    print("%s: Generating normalized word frequencies..." % time.ctime())
    frequencies = loader_obj.destination + "/frequencies"
    output = open(frequencies + "/normalized_word_frequencies", "w")
    for line in open(frequencies + "/word_frequencies"):
        word, _ = line.split("\t")
        norm_word = word.lower()
        norm_word = [i for i in unicodedata.normalize("NFKD", norm_word) if not unicodedata.combining(i)]
        norm_word = "".join(norm_word)
        print(norm_word + "\t" + word, file=output)
    output.close()


def metadata_frequencies(loader_obj):
    print("%s: Generating metadata frequencies..." % time.ctime())
    frequencies = loader_obj.destination + "/frequencies"
    conn = sqlite3.connect(loader_obj.destination + "/toms.db")
    cursor = conn.cursor()
    for field in loader_obj.metadata_fields:
        query = "select %s, count(*) from toms group by %s order by count(%s) desc" % (field, field, field)
        try:
            cursor.execute(query)
            output = open(frequencies + "/%s_frequencies" % field, "w")
            for result in cursor:
                if result[0] is not None:
                    val = result[0]
                    clean_val = val.replace("\n", " ").replace("\t", "")
                    print(clean_val + "\t" + str(result[1]), file=output)
            output.close()
        except sqlite3.OperationalError:
            loader_obj.metadata_fields_not_found.append(field)
            if os.path.exists(f"{frequencies}/{field}_frequencies"):
                os.remove(f"{frequencies}/{field}_frequencies")
    if loader_obj.metadata_fields_not_found:
        print(
            "The following fields were not found in the input corpus %s"
            % ", ".join(loader_obj.metadata_fields_not_found)
        )
    conn.close()
    return loader_obj.metadata_fields_not_found


def normalized_metadata_frequencies(loader_obj):
    print("%s: Generating normalized metadata frequencies..." % time.ctime())
    frequencies = loader_obj.destination + "/frequencies"
    for field in loader_obj.metadata_fields:
        try:
            output = open(frequencies + "/normalized_" + field + "_frequencies", "w")
            for line in open(frequencies + "/" + field + "_frequencies"):
                word, _ = line.split("\t")
                norm_word = word.lower()
                norm_word = [i for i in unicodedata.normalize("NFKD", norm_word) if not unicodedata.combining(i)]
                norm_word = "".join(norm_word)
                print(norm_word + "\t" + word, file=output)
            output.close()
        except:
            if os.path.exists(f"{frequencies}/normalized_{field}_frequencies"):
                os.remove(f"{frequencies}/normalized_{field}_frequencies")
            pass


def tfidf_per_word(loader_obj):
    """Get the mean TF-IDF weighting of every word in corpus"""
    print(f"{time.ctime()}: Storing mean TF-IDF of all words in corpus...")
    path = os.path.join(loader_obj.destination, "words_and_philo_ids")
    batches = round(len(os.listdir(path)) / 1000)

    def uniq_word_list(start=-1, end=math.inf):
        with open(os.path.join(loader_obj.destination, "frequencies/word_frequencies")) as fh:
            for pos, line in enumerate(fh):
                if pos >= start and pos < end:
                    yield line.strip().split()[0], pos

    def get_text(doc):
        words = []
        with lz4.frame.open(doc) as text:
            for line in text:
                try:
                    words.append(loads(line.decode("utf8").strip())["token"])
                except:
                    pass
        return " ".join(words)

    def get_all_words(filenames, batch_number):
        pool = mp.Pool(mp.cpu_count() - 1)
        return tqdm(
            pool.imap_unordered(get_text, filenames),
            leave=False,
            total=len(filenames),
            desc=f"Vectorizing file batch {batch_number}/{batches}",
        )

    full_corpus_chunked = []
    filenames = []
    batch_number = 0
    print("Computing mean TF-IDF for each word in corpus...", flush=True)
    for file in os.scandir(path):
        filenames.append(file.path)
        if len(filenames) == 1000:
            batch_number += 1
            vectorizer = CountVectorizer(token_pattern=r"(?u)\b\w+\b", vocabulary=dict(uniq_word_list()))
            full_corpus_chunked.append(vectorizer.fit_transform((get_all_words(filenames, batch_number))))
            filenames = []
    if filenames:
        batch_number += 1
        vectorizer = CountVectorizer(token_pattern=r"(?u)\b\w+\b", vocabulary=dict(uniq_word_list()))
        full_corpus_chunked.append(vectorizer.fit_transform((get_all_words(filenames, batch_number))))
        filenames = []

    transformer = TfidfTransformer(sublinear_tf=True)
    vectorized_corpus = transformer.fit_transform(vstack(full_corpus_chunked).transpose())
    with open(os.path.join(loader_obj.destination, "frequencies/words_mean_tfidf"), "w") as idf_output:
        weighted_words = {}
        word_num = vectorized_corpus.shape[0]
        with tqdm(total=word_num, leave=False, desc="Calculating mean TF-IDF...") as pbar:
            for start in range(0, word_num, 10000):
                tf_idf_mean = csr_matrix.mean(vectorized_corpus[start : start + 10000], axis=1)
                for word, word_id in uniq_word_list(start=start, end=start + 10000):
                    weighted_words[word] = tf_idf_mean[word_id - start][0, 0]
                    pbar.update()
        for word, idf in sorted(weighted_words.items(), key=lambda x: x[1], reverse=True):
            print(f"{word}\t{idf}", file=idf_output)


DefaultPostFilters = [
    word_frequencies,
    normalized_word_frequencies,
    metadata_frequencies,
    normalized_metadata_frequencies,
    tfidf_per_word,
]


def set_default_postfilters(postfilters=DefaultPostFilters):
    filters = []
    for postfilter in postfilters:
        filters.append(postfilter)
    return filters
