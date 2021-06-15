#!/usr/bin/env python3
import json
import os
import sqlite3
import sys
from collections import namedtuple

import lz4.frame
from philologic.loadtime.PostFilters import make_sentences_table, tfidf_per_word
from philologic.runtime.DB import DB
from philologic.Config import MakeWebConfig, MakeDBConfig
from philologic.utils import load_module
from tqdm import tqdm
from black import format_str, FileMode

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
    print("Regenerating words_and_philo_ids files... done.")


def get_time_series_dates(toms):
    # Find default start and end dates for times series
    with sqlite3.connect(toms_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT min(year), max(year) FROM toms")
        min_year, max_year = cursor.fetchone()
        try:
            start_date = int(min_year)
        except TypeError:
            start_date: 0
        try:
            end_date = int(max_year)
        except TypeError:
            end_date = 2100
    return start_date, end_date


if __name__ == "__main__":
    philo_db = sys.argv[1]

    # Deal with TOMS db changes
    data_dir = os.path.join(philo_db, "data")
    os.environ["SQLITE_TMPDIR"] = data_dir
    generate_words_and_philo_ids(data_dir)
    toms_path = os.path.join(philo_db, "data/toms.db")
    print("Dropping words table (make take a while)...", end=" ")
    with sqlite3.connect(toms_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE words")
    print("Done.")
    sentence_table_generator = make_sentences_table(data_dir, toms_path)
    sentence_table_generator(None)
    with sqlite3.connect(toms_path) as conn:
        cursor = conn.cursor()
        cursor.execute("VACUUM")

    # # TF-IDF generation
    loader = Loader(data_dir)
    tfidf_per_word(loader)

    # # Regenerate new WebConfig file
    old_config = load_module("old_config", os.path.join(philo_db + "/data/web_config.cfg"))
    start_date, end_date = get_time_series_dates(toms_path)
    config_values = {
        "dbname": old_config.dbname,
        "metadata": old_config.metadata,
        "facets": old_config.facets,
        "theme": old_config.theme,
        "time_series_start_end_date": {"start_date": start_date, "end_date": end_date},
        "search_examples": old_config.search_examples,
        "metadata_input_style": old_config.metadata_input_style,
        "kwic_metadata_sorting_fields": old_config.kwic_metadata_sorting_fields,
        "kwic_bibliography_fields": old_config.kwic_bibliography_fields,
        "concordance_biblio_sorting": old_config.concordance_biblio_sorting,
        "metadata_choice_values": old_config.metadata_dropdown_values,
    }
    os.system(
        f'mv {os.path.join(philo_db + "/data/web_config.cfg")} {os.path.join(philo_db + "/data/web_config.cfg_old")}'
    )
    filename = os.path.join(data_dir, "web_config.cfg")
    new_config = MakeWebConfig(filename, **config_values)
    with open(filename, "w") as output_file:
        print(format_str(str(new_config), mode=FileMode()), file=output_file)

    # Regenerate new db.locals.py
    old_db_locals = load_module("old_db_locals", os.path.join(data_dir, "db.locals.py"))
    filename = os.path.join(data_dir, "db.locals.py")
    with sqlite3.connect(toms_path) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(toms)")
        metadata = [
            i[1]
            for i in cursor
            if i[1]
            not in (
                "prev",
                "next",
                "philo_id",
                "word_count",
                "parent",
                "start_byte",
                "end_byte",
                "philo_seq",
                "philo_name",
                "philo_type",
                "page",
            )
        ]
    db_values = {
        "metadata_fields": metadata,
        "metadata_hierarchy": old_db_locals.metadata_hierarchy,
        "metadata_types": old_db_locals.metadata_types,
        "normalized_fields": old_db_locals.normalized_fields,
        "debug": False,
    }
    db_values["token_regex"] = old_db_locals.token_regex
    db_values["default_object_level"] = old_db_locals.default_object_level
    db_config = MakeDBConfig(filename, **db_values)
    with open(filename, "w") as output_file:
        print(format_str(str(db_config), mode=FileMode()), file=output_file)

    os.system(f"rm -rf {philo_db}/data/hitlists")
    os.system(f"mkdir {philo_db}/data/hitlists && chmod -R 777 {philo_db}/data/hitlists")

    # Deal with web app changes
    print("Regenerating web app...")
    os.system(f"rm -rf {philo_db}/scripts/*")
    os.system(f"rm -rf {philo_db}/reports/*")
    os.system(f"rm -rf {philo_db}/app/*")
    os.system(f"cp -R /var/lib/philologic4/web_app/* {philo_db}/")
    web_app_path = os.path.join(philo_db, "app")
    os.system(
        f"cd {web_app_path}; npm install > {web_app_path}/web_app_build.log 2>&1 && npm run build >> {web_app_path}/web_app_build.log 2>&1"
    )
    os.system(f"cp /var/lib/philologic4/web_app/.htaccess {philo_db}")