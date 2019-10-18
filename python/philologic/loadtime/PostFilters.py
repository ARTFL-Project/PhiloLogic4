#!/usr/bin/env python3


import math
import os
import sqlite3
import time
import unicodedata
from json import loads

import numpy as np
from multiprocess import Pool
from sklearn.feature_extraction.text import TfidfVectorizer
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
        columns = "philo_type,philo_name,philo_id,philo_seq"
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
                        insert = "INSERT INTO %s (%s) values (%s);" % (
                            table,
                            ",".join(list(row.keys())),
                            ",".join("?" for i in range(len(row))),
                        )
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
            except sqlite3.OperationalError:
                pass
        conn.commit()
        conn.close()

        if not loader_obj.debug:
            os.system("rm %s" % file_in)

    return inner_make_sql_table


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
    if loader_obj.metadata_fields_not_found:
        print(
            "The following fields were not found in the input corpus %s"
            % ", ".join(loader_obj.metadata_fields_not_found)
        )
    conn.close()


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
            pass


def tfidf_per_word(loader_obj):
    """Get the mean TF-IDF weighting of every word in corpus"""
    print(f"{time.ctime()}: Storing Inverse Document Frequency of all words in corpus...")

    def get_text(doc):
        words = []
        with open(doc) as text:
            for line in text:
                try:
                    words.append(loads(line.strip())["token"])
                except:
                    pass
        return " ".join(words)

    def get_all_words():
        path = os.path.join(loader_obj.destination, "words_and_philo_ids")
        pool = Pool(32)
        return tqdm(
            pool.imap_unordered(get_text, (i.path for i in os.scandir(path))),
            leave=True,
            total=len(os.listdir(path)),
            desc="Vectorizing words...",
        )

    path = os.path.join(loader_obj.destination, "words_and_philo_ids")
    pool = Pool(loader_obj.cores)
    vectorizer = TfidfVectorizer(sublinear_tf=True, token_pattern=r"(?u)\b\w+\b")
    corpus = vectorizer.fit_transform((get_all_words()))
    mean_tf_idf = np.mean(corpus.toarray(), axis=0)
    weighted_words = {word: mean_tf_idf[vectorizer.vocabulary_[word]] for word in vectorizer.vocabulary_}
    with open(os.path.join(loader_obj.destination, "frequencies/words_mean_tfidf"), "w") as idf_output:
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
