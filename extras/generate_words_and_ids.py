#!/usr/bin/env python3
"""Script to generate words and their corresponding ids post-load"""

from json import dumps
import os
import sys

from philologic.DB import DB

def main(db_path):
    """Grab words from words table and dump to file"""
    philo_db = DB(db_path)
    words_and_ids_path = os.path.join(db_path, "words_and_philo_ids")
    status = os.system("mkdir -p %s" % words_and_ids_path)
    if status != 0:
        print("Could not create %s. Please check your write permissions to the parent directory" % words_and_ids_path)
        sys.exit(status)
    # Get all doc ids
    cursor = philo_db.dbh.cursor()
    cursor.execute('SELECT philo_id from toms where philo_type="doc" order by rowid')
    docs = [i["philo_id"].split()[0] for i in cursor.fetchall()]

    for doc_id in docs:
        words = []
        query = "{} %".format(doc_id)
        cursor.execute("SELECT philo_name, philo_id, philo_type from words where philo_id like ? order by rowid", (query,))
        for word, philo_id, philo_type in cursor.fetchall():
            if philo_type == "word" and word != "philo_virtual":
                words.append(dumps({"token": word, "position": philo_id}))
        with open(os.path.join(words_and_ids_path, doc_id), "w") as output:
            output.write("\n".join(words))
        print("Processed document %s" % doc_id)


if __name__ == '__main__':
    DB_PATH = os.path.join(sys.argv[1], "data")
    main(DB_PATH)

