#!/usr/bin/env python3
"""Script to generate words and their corresponding ids post-load"""

import json
import os
import sys

from philologic.runtime.DB import DB


def main(db_path):
    """Grab words from words table and dump to file"""
    philo_db = DB(db_path)
    words_and_ids_path = os.path.join(db_path, "words_and_philo_ids")
    status = os.system("mkdir -p %s" % words_and_ids_path)
    if status != 0:
        print("Could not create %s. Please check your write permissions to the parent directory" % words_and_ids_path)
        sys.exit(status)
    cursor = philo_db.dbh.cursor()
    cursor.execute('SELECT philo_name, philo_id, start_byte, end_byte from words')
    current_doc_id = "1"
    current_words = []
    for word, philo_id, start_byte, end_byte in cursor:
        doc_id = philo_id.split()[0]
        word_obj = {
            "token": word,
            "position": philo_id,
            "start_byte": start_byte,
            "end_byte": end_byte
        }
        if doc_id != current_doc_id:
            with open(os.path.join(words_and_ids_path, current_doc_id), "w") as output:
                output.write("\n".join(current_words))
                print("Processed document %s" % current_doc_id, flush=True)
            current_words = []
            current_doc_id = doc_id
        current_words.append(json.dumps(word_obj))
    if current_words:
        with open(os.path.join(words_and_ids_path, current_doc_id), "w") as output:
            output.write("\n".join(current_words))
            print("Processed document %s" % current_doc_id, flush=True)

if __name__ == '__main__':
    DB_PATH = os.path.join(sys.argv[1], "data")
    main(DB_PATH)
