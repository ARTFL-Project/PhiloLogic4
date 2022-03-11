#!/usr/bin/env python3
import json
import os
import sqlite3
import sys
from collections import namedtuple

import lz4.frame
from philologic.loadtime.PostFilters import make_sentences_table
from philologic.runtime.DB import DB
from philologic.Config import Config, MakeDBConfig, WEB_CONFIG_DEFAULTS, WEB_CONFIG_HEADER
from philologic.utils import load_module
from philologic.utils import pretty_print
from tqdm import tqdm
from black import format_str, FileMode
from web_config_convert_4_6_to_4_7 import convert_web_config


class CustomConfig(Config):
    def __str__(self):
        string = "\n".join([line.strip() for line in self.header.splitlines() if line.strip()]) + "\n\n"
        written_keys = []
        for key, value in self.defaults.items():
            if value["comment"]:
                string += "\n" + "\n".join(line.strip() for line in value["comment"].splitlines() if line.strip())
            if key == "aggregation_config":
                string += (
                    f"\n{key} = "
                    + "[{"
                    + """"field": "author", "object_level": "doc", "break_up_field": "title",
                        "field_citation": [citations["author"]], "break_up_field_citation": [
                        citations["title"], citations["pub_place"], citations["publisher"], citations["collection"],citations["year"]
                        ],"""
                    + "}, {"
                    + """"field": "title", "object_level": "doc", "field_citation": [citations["title"],
                        citations["pub_place"], citations["publisher"], citations["collection"], citations["year"]],"break_up_field": None,
                        "citation": citations["title"], "break_up_field_citation": None, """
                    + "}]"
                )
            else:
                string += "\n%s = %s\n" % (key, pretty_print(self.data[key]))
            written_keys.append(key)
        for key in self.data:
            if key not in written_keys:
                string += "\n%s = %s\n" % (key, pretty_print(self.data[key]))
                written_keys.append(key)
        return string


def MakeWebConfig(path, **extra_values):
    """Build web_config with non-default arguments"""
    web_config = CustomConfig(path, WEB_CONFIG_DEFAULTS, header=WEB_CONFIG_HEADER)
    if extra_values:
        for key, value in extra_values.items():
            web_config[key] = value
    return web_config


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


def update_toms(toms):
    """Update toms to add object_id values"""
    print("Adding ids in toms db:", flush=True, end=" ")
    obj_levels = {"doc": 1, "div1": 2, "div2": 3, "div3": 4, "para": 5}
    with sqlite3.connect(toms) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("select count(*) from toms")
        count = cursor.fetchone()[0]
        cursor.execute("pragma table_info(toms)")
        ids_to_add = [
            "philo_doc_id",
            "philo_div1_id",
            "philo_div2_id",
            "philo_div3_id",
            "philo_para_id",
        ]
        original_columns = [r[1] for r in cursor]
        columns = original_columns + ids_to_add
        cursor.execute(f"create table new_toms ({','.join(columns)})")
        cursor.execute("select * from toms")
        with open(toms + ".tmp", "w") as outfile:
            for row in cursor:
                print("\t".join(map(str, row)), file=outfile)
        with tqdm(total=count, leave=False, desc="Adding ids") as pbar:
            with open(toms + ".tmp") as infile:
                for line in infile:
                    row = dict(zip(original_columns, line.split("\t")))
                    object_level = row["philo_type"]
                    philo_obj_id = " ".join(row["philo_id"].split()[: obj_levels[object_level]])
                    ids = [None, None, None, None, None]
                    ids[obj_levels[object_level] - 1] = philo_obj_id
                    values = tuple(list(row.values()) + ids)
                    cursor.execute(
                        f"insert into new_toms ({','.join(columns)}) values ({','.join(['?' for _ in range(len(values))])})",
                        values,
                    )
                    pbar.update()
            conn.commit()
            cursor.execute("drop table toms")
            cursor.execute("alter table new_toms rename to toms")
            for index in columns:
                index_name = f"{index}_toms_index"
                cursor.execute("create index if not exists %s on toms (%s)" % (index_name, index))
                index_null_name = f"{index}_null_index"  # this is for hitlist stats queries which require indexing philo_id with null metadata values
                cursor.execute(
                    f"CREATE UNIQUE INDEX IF NOT EXISTS {index_null_name} ON toms(philo_id, {index}) WHERE {index} IS NULL"
                )
            os.remove(toms + ".tmp")


def get_time_series_dates(toms):
    # Find default start and end dates for times series
    with sqlite3.connect(toms_path) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT min(year), max(year) FROM toms")
            min_year, max_year = cursor.fetchone()
            try:
                start_date = int(min_year)
            except (TypeError, ValueError):
                start_date = 0
            try:
                end_date = int(max_year)
            except (TypeError, ValueError):
                end_date = 2100
        except sqlite3.OperationalError:
            return 0, 0
    return start_date, end_date


def citations_filter(citations):
    new_citations = []
    for citation in citations:
        del citation["separator"]
        new_citations.append(citation)
    return new_citations


def convert_landing_page_browsing(landing_page):
    new_landing_page = []
    for l in landing_page:
        l["citation"] = citations_filter(l["citation"])
        new_landing_page.append(l)
    return new_landing_page


if __name__ == "__main__":
    philo_db = sys.argv[1]

    # Deal with TOMS db changes
    data_dir = os.path.join(philo_db, "data")
    os.environ["SQLITE_TMPDIR"] = data_dir
    generate_words_and_philo_ids(data_dir)
    toms_path = os.path.join(philo_db, "data/toms.db")
    with sqlite3.connect(toms_path) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("select philo_doc_id from toms limit 1")
        except sqlite3.OperationalError:
            update_toms(toms_path)

    print("Dropping words table (make take a while)...", end=" ", flush=True)
    with sqlite3.connect(toms_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE words")
    print("Done.", flush=True)
    sentence_table_generator = make_sentences_table(data_dir, toms_path)
    sentence_table_generator(None)
    with sqlite3.connect(toms_path) as conn:
        cursor = conn.cursor()
        cursor.execute("VACUUM")

    # Regenerate new WebConfig file
    convert_web_config(os.path.join(data_dir, "web_config.cfg"), philo_db)

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
    metadata_hierarchy = old_db_locals.metadata_hierarchy
    metadata_hierarchy[0].append("philo_doc_id")
    metadata_hierarchy[1].append("philo_div1_id")
    metadata_hierarchy[2].append("philo_div2_id")
    metadata_hierarchy[3].append("philo_div3_id")
    try:
        metadata_hierarchy[4].append("philo_para_id")
    except:
        pass
    db_values = {
        "metadata_fields": metadata,
        "metadata_hierarchy": metadata_hierarchy,
        "metadata_types": {
            **old_db_locals.metadata_types,
            "philo_doc_id": "doc",
            "philo_div1_id": "div1",
            "philo_div2_id": "div2",
            "philo_div3_id": "div3",
            "philo_para_id": "para",
        },
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

    # Deactivate old custom functions
    for file in os.scandir(os.path.join(philo_db, "custom_functions")):
        if file.name.endswith(".py"):
            os.system(f"mv {file.path} {file.path + '_old'}")
