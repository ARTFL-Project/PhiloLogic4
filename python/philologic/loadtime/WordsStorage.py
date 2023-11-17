"""Creates an inverted index of words and their locations in the database."""

import subprocess
import lmdb
import lz4.frame
from orjson import loads
from msgpack import dumps
from tqdm import tqdm


def create_inverted_index(file_path, db_path, commit_interval=10000):
    """Creates an inverted index of words and their locations in the database."""
    line_count_process = subprocess.run(f"lz4 -dc {file_path} | wc -l", shell=True, text=True, capture_output=True)
    line_count = int(line_count_process.stdout.strip())
    db_env = lmdb.open(f"{db_path}/words.lmdb", map_size=1024 * 1024 * 1024 * 1024)
    with lz4.frame.open(file_path) as input_file:
        current_word = None
        occurrence_attribs = []
        count = 0
        txn = db_env.begin(write=True)

        for line in tqdm(input_file, total=line_count):
            line = line.decode("utf-8")
            _, word, philo_id, attrib = line.split("\t", 3)
            attrib = loads(attrib)

            if word != current_word:
                if current_word is not None:
                    txn.put(current_word.encode("utf-8"), lz4.frame.compress(dumps(occurrence_attribs)))
                    count += 1
                    if count % commit_interval == 0:
                        txn.commit()
                        txn = db_env.begin(write=True)
                current_word = word
                occurrence_attribs = []

            occurrence_attribs.append(
                (
                    [int(i) for i in philo_id.split()],
                    {"start_byte": attrib["start_byte"], "end_byte": attrib["end_byte"]},
                )
            )

        # Commit any remaining words
        if occurrence_attribs:
            txn.put(current_word.encode("utf-8"), lz4.frame.compress(dumps(occurrence_attribs)))

        txn.commit()
        # print(f"\rCommitted {count} words to the database.")

    db_env.close()
    print("Finished creating inverted index.")
