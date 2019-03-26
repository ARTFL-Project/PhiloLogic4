#!/usr/bin env python3
"""CLI parser for philoload4 command"""

import collections
import os
import sys
from glob import glob
from argparse import ArgumentParser

from philologic.loadtime import Loader, LoadFilters, Parser, PlainTextParser, PostFilters
from philologic.utils import pretty_print, load_module

# Load global config
CONFIG_PATH = os.getenv("PHILOLOGIC_CONFIG", "/etc/philologic/philologic4.cfg")
CONFIG_FILE = load_module("philologic4", CONFIG_PATH)

if CONFIG_FILE.url_root is None:
    print("url_root variable is not set in /etc/philologic/philologic4.cfg", file=sys.stderr)
    print("See https://github.com/ARTFL-Project/PhiloLogic4/blob/master/docs/installation.md.", file=sys.stderr)
    exit()
elif CONFIG_FILE.web_app_dir is None:
    print("web_app_dir variable is not set in /etc/philologic/philologic4.cfg", file=sys.stderr)
    print("See https://github.com/ARTFL-Project/PhiloLogic4/blob/master/docs/installation.md.", file=sys.stderr)
    exit()
elif CONFIG_FILE.database_root is None:
    print("database_root variable is not set in /etc/philologic/philologic4.cfg", file=sys.stderr)
    print("See https://github.com/ARTFL-Project/PhiloLogic4/blob/master/docs/installation.md.", file=sys.stderr)
    exit()


class LoadOptions:
    """Load Options objects container both the parser and the resulting options selected"""

    def __init__(self):
        self.values = {}
        self.values["database_root"] = CONFIG_FILE.database_root
        self.values["web_app_dir"] = CONFIG_FILE.web_app_dir
        self.values["theme"] = CONFIG_FILE.theme
        self.values["destination"] = "./"
        self.values["load_config"] = ""
        self.values["default_object_level"] = Loader.DEFAULT_OBJECT_LEVEL
        self.values["navigable_objects"] = Loader.NAVIGABLE_OBJECTS
        self.values["load_filters"] = LoadFilters.set_load_filters()
        self.values["post_filters"] = PostFilters.DefaultPostFilters
        self.values["plain_text_obj"] = []
        self.values["parser_factory"] = Parser.XMLParser
        self.values["token_regex"] = Parser.TOKEN_REGEX
        self.values["doc_xpaths"] = Parser.DEFAULT_DOC_XPATHS
        self.values["tag_to_obj_map"] = Parser.DEFAULT_TAG_TO_OBJ_MAP
        self.values["metadata_to_parse"] = Parser.DEFAULT_METADATA_TO_PARSE
        self.values["pseudo_empty_tags"] = []
        self.values["suppress_tags"] = []
        self.values["break_apost"] = True
        self.values["chars_not_to_index"] = Parser.CHARS_NOT_TO_INDEX
        self.values["break_sent_in_line_group"] = False
        self.values["tag_exceptions"] = Parser.TAG_EXCEPTIONS
        self.values["join_hyphen_in_words"] = True
        self.values["abbrev_expand"] = True
        self.values["long_word_limit"] = 200
        self.values["flatten_ligatures"] = True
        self.values["cores"] = 2
        self.values["dbname"] = ""
        self.values["files"] = []
        self.values["sort_order"] = ["year", "author", "title", "filename"]
        self.values["header"] = "tei"
        self.values["debug"] = False
        self.values["force_delete"] = False
        self.values["file_list"] = False
        self.values["bibliography"] = ""
        self.values["words_to_index"] = set([])
        self.values["file_type"] = "xml"
        self.values["sentence_breakers"] = []
        self.values["punctuation"] = Parser.PUNCTUATION
        self.values["pos"] = ""

    def setup_parser(self):
        """Set up parser options"""
        usage = "usage: %(prog)s [options] database_name files"
        parser = ArgumentParser(description="PhiloLogic4 database load command", usage=usage)
        parser.add_argument(
            "-b",
            "--bibliography",
            type=str,
            dest="bibliography",
            help="Defines a file containing the document-level bibliography of the texts",
            default=None,
        )
        parser.add_argument(
            "-c", "--cores", type=int, dest="cores", help="define the number of cores used for parsing", default=4
        )
        parser.add_argument(
            "-d", "--debug", action="store_true", default=False, dest="debug", help="add debugging to your load"
        )
        parser.add_argument(
            "-D",
            "--force_delete",
            action="store_true",
            default=False,
            dest="force_delete",
            help="overwrite database without confirmation",
        )
        parser.add_argument(
            "-F",
            "--file-list",
            action="store_true",
            default=False,
            dest="file_list",
            help="Defines whether the file argument is a file containing fullpaths to the files to load",
        )
        parser.add_argument(
            "-H",
            "--header",
            type=str,
            dest="header",
            help="define header type (tei or dc) of files to parse",
            default="tei",
        )
        parser.add_argument(
            "-l",
            "--load_config",
            type=str,
            dest="load_config",
            help="load external config for specialized load",
            default=None,
        )
        parser.add_argument(
            "-t",
            "--file-type",
            type=str,
            dest="file_type",
            help="Define file type for parsing: plain_text, xml, or html",
            default="xml",
        )
        parser.add_argument(
            "-w",
            "--use-webconfig",
            type=str,
            dest="web_config",
            help="use predefined web_config.cfg file",
            default=None,
        )
        parser.add_argument("dbname", type=str)
        parser.add_argument("files", nargs="*")
        return parser

    def parse(self, argv):
        """Parse command-line arguments."""
        parser = self.setup_parser()
        args = parser.parse_args(argv[1:])
        self.values["dbname"] = args.dbname
        if args.file_list is True:
            with open(args.files) as fh:
                self.values["files"].append([line.strip() for line in fh])
        elif len(args.files) == 1 and os.path.isdir(args.files[0]):
            self.values["files"] = glob(os.path.join(args.files[0], "*"))
        else:
            self.values["files"] = args.files
        if args.bibliography is not None:
            self.values["bibliography"] = args.bibliography
        self.values["cores"] = args.cores
        self.values["debug"] = args.debug
        self.values["header"] = args.header
        if args.load_config is not None:
            load_config = LoadConfig()
            load_config.parse(args.load_config)
            for config_key, config_value in load_config.config.items():
                if config_value:
                    self.values[config_key] = config_value
            self.values["load_config"] = os.path.abspath(args.load_config)
        self.values["file_type"] = args.file_type
        if args.file_type == "plain_text":
            self.values["parser_factory"] = PlainTextParser.PlainTextParser
        if args.web_config is not None:
            with open(args.web_config) as f:
                self.values["web_config"] = f.read()
        self.values["db_destination"] = os.path.join(self.database_root, self.dbname)
        self.values["data_destination"] = os.path.join(self.db_destination, "data")
        if self.plain_text_obj:
            plain_text_filter = LoadFilters.store_in_plain_text(*self.plain_text_obj)
            self.load_filters.append(plain_text_filter)
        if self.debug:
            print(self)

    def __getitem__(self, item):
        return self.values[item]

    def __getattr__(self, attr):
        return self.values[attr]

    def __setitem__(self, attr, value):
        self.values[attr] = value

    def __contains__(self, key):
        if key in self.values:
            return True
        else:
            return False

    def __iter__(self):
        """Iterate over loader config."""
        for i in self.values:
            yield i

    def __str__(self):
        """String representation of parsed loader config."""
        return pretty_print(self.values)


class LoadConfig:
    """Load a load_config file"""

    def __init__(self):
        self.config = {}

    def parse(self, load_config_file_path):
        """Parse external config file"""
        load_config_file = load_module("external_load_config", load_config_file_path)
        for a in dir(load_config_file):
            if a == "parser_factory":
                value = getattr(load_config_file, a)
                self.config["parser_factory"] = value
            elif not a.startswith("__") and not isinstance(getattr(load_config_file, a), collections.Callable):
                value = getattr(load_config_file, a)
                if value:
                    if a == "navigable_objects":
                        self.config["load_filters"] = LoadFilters.set_load_filters(navigable_objects=value)
                    if a == "words_to_index":
                        word_list = set([])
                        with open(value) as fh:
                            for line in fh:
                                word_list.add(line.strip())
                        self.config["words_to_index"] = word_list
                    elif a == "plain_text_obj":
                        if "load_filters" not in self.config:
                            self.config["load_filters"] = LoadFilters.DefaultLoadFilters
                        self.config["load_filters"].append(LoadFilters.store_in_plain_text(*value))
                    elif a == "store_words_and_ids":
                        if "load_filters" not in self.config:
                            self.config["load_filters"] = LoadFilters.DefaultLoadFilters
                        self.config["load_filters"].append(LoadFilters.store_words_and_philo_ids)
                    elif a == "pos_tagger":
                        if "load_filters" not in self.config:
                            self.config["load_filters"] = LoadFilters.DefaultLoadFilters
                        self.config["load_filters"].append(LoadFilters.pos_tagger(value))
                    else:
                        self.config[a] = value
