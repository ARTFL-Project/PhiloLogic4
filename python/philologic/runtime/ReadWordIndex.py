"""Read inverted index from lmdb database."""

from itertools import combinations
from collections import defaultdict
import time

from philologic.runtime.HitList import HitList

import lmdb
import lz4.frame
from msgpack import loads


def get_object_id(philo_id, level="sent"):
    """Return the object ID for a given level of the philo_id."""
    if level == "sent":
        return f"{philo_id[0]} {philo_id[1]} {philo_id[2]} {philo_id[3]} {philo_id[4]} {philo_id[5]}"
    elif level == "para":
        return f"{philo_id[0]} {philo_id[1]} {philo_id[2]} {philo_id[3]} {philo_id[4]}"


def search_word(db_path, query):
    """Search for occurrences of a word in the database and return them."""
    words = [w.encode("utf8") for w in query.split()]  # if we have multiple words, they will be separated by spaces
    results = []
    db_env = lmdb.open(f"{db_path}/words.lmdb", readonly=True)
    with db_env.begin() as txn:
        cursor = txn.cursor()
        local_hits = cursor.getmulti(words)
        for _, compressed_data in local_hits:
            occurrence_attribs = loads(lz4.frame.decompress(compressed_data))
            for philo_id, _ in occurrence_attribs:
                results.append(philo_id)
    db_env.close()
    return results


def search_cooccurrence(db_path, words, level):
    """Search for co-occurrences of multiple words in the same sentence in the database."""
    db_env = lmdb.open(f"{db_path}/words.lmdb", readonly=True)
    cooccurrences = []

    # Load occurrences for each word and add sentence IDs
    occurrences_by_text_object = defaultdict(lambda: defaultdict(list))
    with db_env.begin() as txn:
        for word in words:
            compressed_data = txn.get(word.encode("utf-8"))  # TODO: use getmulti to account for multiple word forms
            if compressed_data:
                occurrences = loads(lz4.frame.decompress(compressed_data))
                for philo_id, attrib in occurrences:
                    sentence_id = get_object_id(philo_id, level)
                    occurrences_by_text_object[sentence_id][word].append((philo_id, attrib))

    # Find co-occurrences
    for object_id, word_occurrences in occurrences_by_text_object.items():
        if all(word in word_occurrences for word in words):
            cooccurrences.append((object_id, {word: word_occurrences[word] for word in words}))

    db_env.close()
    return cooccurrences


def search_cooccurrence_within_n_words(db_path, words, n):
    """Search for co-occurrences of all specified words within n words of each other in the same sentence."""
    db_env = lmdb.open(f"{db_path}/words.lmdb", readonly=True)
    cooccurrences = []

    # Load occurrences for each word and organize by sentence IDs
    occurrences_by_sentence = defaultdict(lambda: defaultdict(list))
    with db_env.begin() as txn:
        for word in words:
            compressed_data = txn.get(word.encode("utf-8"))
            if compressed_data:
                occurrences = loads(lz4.frame.decompress(compressed_data))
                for philo_id, attrib in occurrences:
                    sentence_id = get_object_id(philo_id)
                    word_position = get_object_id(philo_id)
                    occurrences_by_sentence[sentence_id][word].append((word_position, attrib))

    # Find co-occurrences within n words
    for sentence_id, word_occurrences in occurrences_by_sentence.items():
        if all(word in word_occurrences for word in words):
            # Check word positions for co-occurrence within n words
            for word_combination in combinations(words, 2):
                for occ1 in word_occurrences[word_combination[0]]:
                    for occ2 in word_occurrences[word_combination[1]]:
                        if abs(occ1[0] - occ2[0]) <= n:
                            cooccurrences.append((word_combination, sentence_id, occ1, occ2))

    db_env.close()
    return cooccurrences


class CustomHitlist(HitList):
    """Custom hitlist"""

    def readhit(self, n):
        """reads hitlist into buffer, unpacks
        should do some work to read k at once, track buffer state."""
        self.update()
        while n >= len(self):
            if self.done:
                raise IndexError
            else:
                time.sleep(0.05)
                self.update()
        if n != self.position:
            offset = self.hitsize * n
            self.fh.seek(offset)
            self.position = n
        buffer = self.fh.read(self.hitsize)
        self.position += 1
        return struct.unpack(self.format, buffer)
