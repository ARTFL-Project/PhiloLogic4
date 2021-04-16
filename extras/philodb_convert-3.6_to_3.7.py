#!/usr/bin/env python3
import json
import os
import sqlite3
import sys
from collections import namedtuple

import lz4.frame
from philologic.loadtime.PostFilters import make_sentences_table, tfidf_per_word
from philologic.runtime.DB import DB
from tqdm import tqdm


Loader = namedtuple("Loader", "destination")


def compress_file(filename):
    with open(f"{filename}.lz4", "wb") as compressed_file:
        with open(filename, "rb") as input_file:
            compressed_file.write(lz4.frame.compress(input_file.read(), compression_level=4))
        os.remove(filename)


def generate_words_and_philo_ids(db_path):
    """Grab words from words table and dump to file"""
    philo_db = DB(db_path)
    words_and_ids_path = os.path.join(db_path, "words_and_philo_ids")
    if os.path.exists(words_and_ids_path):
        os.system(f"rm -rf {words_and_ids_path}")
    status = os.system("mkdir -p %s" % words_and_ids_path)
    if status != 0:
        print("Could not create %s. Please check your write permissions to the parent directory" % words_and_ids_path)
        sys.exit(status)
    cursor = philo_db.dbh.cursor()
    cursor.execute("SELECT COUNT(distinct filename) from toms")
    count = int(cursor.fetchone()[0])
    cursor.execute("SELECT philo_name, philo_id, start_byte, end_byte from words")
    current_doc_id = "1"
    current_sentence_id = None
    word_obj = {}
    current_words = []
    with tqdm(total=count, leave=False, desc="Regenerating words_and_philo_ids files...") as pbar:
        for word, philo_id, start_byte, end_byte in cursor:
            doc_id = philo_id.split()[0]
            sentence_id = " ".join(philo_id.split()[:6]) + " 0"
            if doc_id == current_doc_id and sentence_id != current_sentence_id and word_obj:
                position = " ".join(word_obj["position"].split()[:6]) + f"{int(word_obj['position'].split()[-1]) + 1}"
                sentence_obj = {
                    **word_obj,
                    "philo_type": "sent",
                    "token": ".",
                    "start_byte": word_obj["end_byte"],
                    "position": position,
                }
                current_words.append(json.dumps(sentence_obj))
            word_obj = {
                "token": word,
                "position": philo_id,
                "start_byte": start_byte,
                "end_byte": end_byte,
                "philo_type": "word",
            }
            if doc_id != current_doc_id:
                with open(os.path.join(words_and_ids_path, current_doc_id), "w") as output:
                    output.write("\n".join(current_words))
                compress_file(os.path.join(words_and_ids_path, current_doc_id))
                pbar.update()
                current_words = []
                current_doc_id = doc_id
            current_sentence_id = sentence_id
            current_words.append(json.dumps(word_obj))
        if current_words:
            with open(os.path.join(words_and_ids_path, current_doc_id), "w") as output:
                output.write("\n".join(current_words))
            compress_file(os.path.join(words_and_ids_path, current_doc_id))
            pbar.update()


if __name__ == "__main__":
    philo_db = sys.argv[1]

    # Deal with TOMS db changes
    data_dir = os.path.join(philo_db, "data")
    generate_words_and_philo_ids(data_dir)
    toms_path = os.path.join(philo_db, "data/toms.db")
    with sqlite3.connect(toms_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE words")
    sentence_table_generator = make_sentences_table(data_dir, toms_path)
    sentence_table_generator(None)
    with sqlite3.connect(toms_path) as conn:
        cursor = conn.cursor()
        cursor.execute("VACUUM")

    # Deal with web app changes
    os.system(f"rm -rf {philo_db}/scripts/*")
    os.system(f"rm -rf {philo_db}/reports/*")
    os.system(f"rm -rf {philo_db}/app/*")
    os.system(f"cp -R /var/lib/philologic4/web_app/* {philo_db}/")
    web_app_path = os.path.join(philo_db, "app")
    os.system(
        f"cd {web_app_path}; npm install > {web_app_path}/web_app_build.log 2>&1 && npm run build >> {web_app_path}/web_app_build.log 2>&1"
    )

    # TF-IDF generation
    loader = Loader(data_dir)
    print(loader.destination)
    tfidf_per_word(loader)