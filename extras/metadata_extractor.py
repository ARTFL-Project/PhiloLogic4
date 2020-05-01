#! /usr/bin/env python3

import json
import os
import sqlite3
import sys

from philologic.runtime.DB import DB


object_levels = {"doc": 1, "div1": 2, "div2": 3, "div3": 4, "para": 5}


def main(object_level, db_path):
    metadata_fields = {}
    doc_filenames = {}
    database = DB(os.path.join(db_path, "data"))
    cursor = database.dbh.cursor()
    cursor.execute("SELECT philo_id, filename FROM toms WHERE philo_type='doc'")
    for philo_id, filename in cursor:
        doc_id = philo_id.split()[0]
        doc_filenames[doc_id] = filename
    cursor.execute("SELECT * FROM toms WHERE philo_type=?", (object_level,))
    for result in cursor:
        fields = result
        philo_id = "_".join(fields["philo_id"].split()[: object_levels[object_level]])
        metadata_fields[philo_id] = {}
        for field in database.locals["metadata_fields"]:
            metadata_fields[philo_id][field] = result[field] or ""
        doc_id = result["philo_id"].split()[0]
        metadata_fields[philo_id]["filename"] = doc_filenames[doc_id]
    with open("metadata.json", "w") as metadata_file:
        json.dump(metadata_fields, metadata_file)


if __name__ == "__main__":
    object_level = sys.argv[1]
    db_path = sys.argv[2]
    main(object_level, db_path)
