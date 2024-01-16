import os
import sys
import unicodedata
from io import TextIOWrapper
from typing import List, Union

import regex as re
from philologic.loadtime import OHCOVector

TOKEN_REGEX = r"[\p{L}\p{M}\p{N}]+|[&\p{L};]+"
PUNCTUATION = r"""[;,:=+()"]"""

check_if_char_word = re.compile(r"\p{L}", re.I)
cap_char_or_num = re.compile(r"[A-Z0-9]")  # Capitals


class PlainTextParser:
    """Plain tex parser"""

    def __init__(
        self,
        output,
        docid,
        filesize,
        token_regex: str = TOKEN_REGEX,
        xpaths=[("doc", "./")],
        metadata_xpaths=[],
        suppress_tags=[],
        pseudo_empty_tags=[],
        known_metadata={},
        words_to_index=None,
        paragraph_on_newline=False,  # TODO: make this configurable from load_config.py
        lemmas=None,
        **parse_options,
    ):
        self.types = ["doc", "div1", "div2", "div3", "para", "sent", "word"]
        self.parallel_type = "page"
        self.output = output
        self.docid = docid
        ## Initialize an OHCOVector Stack. operations on this stack produce all parser output.
        self.v = OHCOVector.CompoundStack(
            self.types,
            self.parallel_type,
            docid,
            output,
            ref="ref",
            line="line",
            graphic="graphic",
            punctuation="punct",
        )

        self.filesize = filesize
        self.token_regex = re.compile(rf"({token_regex})", re.I | re.M)
        if "sentence_breakers" in parse_options:
            self.sentence_breakers = parse_options["sentence_breakers"]
        else:
            self.sentence_breakers = []
        if "punctuation" in parse_options:
            self.punct_regex = re.compile(rf"""{parse_options["punctuation"]}""")
        else:
            self.punct_regex = re.compile(rf"{PUNCTUATION}")

        self.paragraph_on_newline = paragraph_on_newline

        self.xpaths = xpaths[:]
        self.metadata_xpaths = metadata_xpaths[:]

        self.suppress_xpaths = suppress_tags
        self.pseudo_empty_tags = pseudo_empty_tags
        self.known_metadata = known_metadata

        self.buffer_position = 0
        self.buffers = []

        self.lemmas = lemmas

        if words_to_index:
            self.words_to_index = words_to_index
            self.defined_words_to_index = True
        else:
            self.defined_words_to_index = False

    def parse(self, input_file: TextIOWrapper):
        """Top level function for reading a file and printing out the output."""
        bytes_read_in: int = 0
        # Begin by creating a document level object, just call it "text" for now.
        self.v.push("doc", "text", bytes_read_in)
        for k, v in list(self.known_metadata.items()):
            # if the parser was created with known_metadata,
            # we can attach it to the newly created doc object here.
            # you can attach metadata to an object at any time between push() and pull().
            self.v["doc"][k] = v
        open_para: bool = False
        previous_line_empty = False
        for line in input_file:  # TODO: recognize divs on lines with all characters in CAPS?
            if line == "\n" or not check_if_char_word.search(line):
                bytes_read_in += len(line.encode("utf8"))
                previous_line_empty = True
                continue
            if previous_line_empty is True or self.paragraph_on_newline is True:
                if open_para is True:
                    self.v.pull("para", bytes_read_in)
                self.v.push("para", "p", bytes_read_in)  # we assume a new paragraph for each line break
                open_para = True
            previous_line_empty = False
            start_byte = bytes_read_in
            last_word = ""
            words: List[Union[str, None]] = self.token_regex.split(line)
            for count, word in enumerate(words):
                is_sent = False
                if word is None:
                    continue
                word_in_utf8 = word.encode("utf8")
                word_length = len(word_in_utf8)
                end_byte = start_byte + word_length
                if check_if_char_word.search(word):
                    # Switch everything to lower case
                    word = word.lower()
                    last_word = word
                    # Check to see if the word is longer than we want. More than 235 characters appear to cause problems in the indexer.
                    if len(word_in_utf8) > 200:
                        print(f"Long word in {input.name}: {word}", file=sys.stderr)
                        print("Removing word from for index since over 200 bytes long...", file=sys.stderr)
                        start_byte += len(word_in_utf8)
                        continue

                    word = "".join(c for c in word if unicodedata.category(c)[0] != "C")  # remove control characters
                    word = word.replace("_", "").strip()
                    word = word.replace(" ", "")
                    if word:
                        if self.defined_words_to_index is True and word not in self.words_to_index:
                            continue
                        self.v.push("word", word, start_byte)
                        if self.lemmas is not None:
                            if word not in self.lemmas:
                                self.v["word"]["lemma"] = self.lemmas.get(word.lower(), word).lower()
                            else:
                                self.v["word"]["lemma"] = self.lemmas[word].lower()
                        self.v.pull("word", end_byte)
                        start_byte += len(word_in_utf8)
                        continue
                if "!" in word or "?" in word:
                    is_sent = True

                # Periods are messy. Let's try by length of previous word and
                # capital letters to avoid hitting abbreviations.
                elif "." in word:
                    is_sent = True
                    if len(last_word) < 3:
                        if cap_char_or_num.search(last_word):
                            is_sent = False

                    # Periods in numbers don't break sentences.
                    try:
                        next_word = words[count + 1]
                        if next_word is None or next_word.islower() or next_word.isdigit():
                            is_sent = False
                    except IndexError:
                        pass
                elif word in self.sentence_breakers:
                    is_sent = True

                if is_sent:
                    # a little hack--we don't know the punctuation mark that will end a sentence
                    # until we encounter it--so instead, we let the push on "word" create a
                    # implicit philo_virtual sentence, then change its name once we actually encounter
                    # the punctuation token.
                    if "sent" not in self.v:
                        self.v.push("sent", word.replace("\t", " ").strip(), start_byte)
                    self.v["sent"].name = word.replace("\t", " ").strip()
                    self.v.pull("sent", start_byte + len(word.encode("utf8")))
                elif self.punct_regex.search(word):
                    punc_pos = start_byte
                    punct = word.strip()
                    punct = punct.replace("\t", " ")
                    punct = "".join(c for c in punct if unicodedata.category(c)[0] != "C")  # remove control characters
                    for single_punct in punct:
                        end_pos = len(single_punct.encode("utf8"))
                        if single_punct != " ":
                            self.v.push("punct", single_punct, punc_pos)
                            self.v.pull("punct", punc_pos + len(single_punct.encode("utf8")))
                        punc_pos = end_pos

                start_byte += len(word_in_utf8)
            bytes_read_in += len(line.encode("utf8"))
        self.v.pull("doc", self.filesize)


if __name__ == "__main__":
    for docid, fn in enumerate(sys.argv[1:], 1):
        print(docid, fn, file=sys.stderr)
        size = os.path.getsize(fn)
        fh = open(fn)
        parser = PlainTextParser(
            sys.stdout,
            docid,
            size,
            known_metadata={"filename": fn},
            paragraph_on_newline=False,
        )
        parser.parse(fh)
