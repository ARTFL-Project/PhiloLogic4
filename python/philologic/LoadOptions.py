#!/usr/bin env python3


import imp
import os
import sys
from glob import glob
from optparse import OptionParser

from philologic import Loader, LoadFilters, PostFilters, Parser, PlainTextParser
from philologic.utils import pretty_print
import collections


# Load global config
config_path = os.getenv("PHILOLOGIC_CONFIG", "/etc/philologic/philologic5.cfg")
config_file = imp.load_source("philologic5", config_path)

if config_file.url_root is None:
    print("url_root variable is not set in /etc/philologic/philologic5.cfg", file=sys.stderr)
    print("See https://github.com/ARTFL-Project/PhiloLogic5/blob/master/docs/installation.md.", file=sys.stderr)
    exit()
elif config_file.web_app_dir is None:
    print("web_app_dir variable is not set in /etc/philologic/philologic5.cfg", file=sys.stderr)
    print("See https://github.com/ARTFL-Project/PhiloLogic5/blob/master/docs/installation.md.", file=sys.stderr)
    exit()
elif config_file.database_root is None:
    print("database_root variable is not set in /etc/philologic/philologic5.cfg", file=sys.stderr)
    print("See https://github.com/ARTFL-Project/PhiloLogic5/blob/master/docs/installation.md.", file=sys.stderr)
    exit()


class LoadOptions(object):
    def __init__(self):
        self.values = {}
        self.values["database_root"] = config_file.database_root
        self.values["web_app_dir"] = config_file.web_app_dir
        self.values["theme"] = config_file.theme
        self.values["destination"] = "./"
        self.values["load_config"] = ""
        self.values["default_object_level"] = Loader.DEFAULT_OBJECT_LEVEL
        self.values["navigable_objects"] = Loader.NAVIGABLE_OBJECTS
        self.values["load_filters"] = LoadFilters.DefaultLoadFilters
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

    def setup_parser(self):
        usage = "usage: %prog [options] database_name files"
        parser = OptionParser(usage=usage)
        parser.add_option(
            "-a",
            "--app_dir",
            type="string",
            dest="web_app_dir",
            help="Define custom location for the web app directory",
        )
        parser.add_option(
            "-b",
            "--bibliography",
            type="string",
            dest="bibliography",
            help="Defines a file containing the document-level bibliography of the texts",
        )
        parser.add_option("-c", "--cores", type="int", dest="cores", help="define the number of cores used for parsing")
        parser.add_option(
            "--custom_functions",
            type="string",
            dest="custom_functions",
            help="copy contents of path for custom functions",
        )
        parser.add_option(
            "-d", "--debug", action="store_true", default=False, dest="debug", help="add debugging to your load"
        )
        parser.add_option(
            "-D",
            "--force_delete",
            action="store_true",
            default=False,
            dest="force_delete",
            help="overwrite database without confirmation",
        )
        parser.add_option(
            "-F",
            "--file-list",
            action="store_true",
            default=False,
            dest="file_list",
            help="Defines whether the file argument is a file containing fullpaths to the files to load",
        )
        parser.add_option(
            "-H", "--header", type="string", dest="header", help="define header type (tei or dc) of files to parse"
        )
        parser.add_option(
            "-l", "--load_config", type="string", dest="load_config", help="load external config for specialized load"
        )
        parser.add_option(
            "-t",
            "--file-type",
            type="string",
            dest="file_type",
            help="Define file type for parsing: plain_text, xml, or html",
        )
        parser.add_option(
            "-w", "--use-webconfig", type="string", dest="web_config", help="use predefined web_config.cfg file"
        )
        return parser

    def parse(self, argv):
        """Parse command-line arguments."""
        parser = self.setup_parser()
        options, args = parser.parse_args(argv[1:])
        try:
            self.values["dbname"] = args[0]
            args.pop(0)
            if options.file_list:
                with open(args[-1]) as fh:
                    for line in fh:
                        self.values["files"].append(line.strip())
            elif args[-1].endswith("/") or os.path.isdir(args[-1]):
                self.values["files"] = glob(args[-1] + "/*")
            else:
                self.values["files"] = args[:]
            if len(self.values["files"]) == 0:
                print(("\nError: No files found in supplied path\n"), file=sys.stderr)
                exit()

        except IndexError:
            print(
                ("\nError: you did not supply a database name or a path for your file(s) to be loaded\n"),
                file=sys.stderr,
            )
            parser.print_help()
            sys.exit()
        for a in dir(options):
            if not a.startswith("__") and not isinstance(getattr(options, a), collections.Callable):
                value = getattr(options, a)
                if a == "load_config" and value:
                    load_config = LoadConfig()
                    load_config.parse(value)
                    for config_key, config_value in load_config.config.items():
                        if config_value:
                            self.values[config_key] = config_value
                    self.values[a] = os.path.abspath(value)
                elif a == "file_type":
                    if value == "plain_text":
                        self.values["parser_factory"] = PlainTextParser.PlainTextParser
                elif a == "navigable_objects" and value is not None:
                    self.values["navigable_objects"] = [v.strip() for v in value.split(",")]
                elif a == "web_config":
                    if value is not None:
                        with open(value) as f:
                            self.values["web_config"] = f.read()
                else:
                    if value is not None:
                        self.values[a] = value
        self.update()

    def update(self):
        self.values["db_destination"] = os.path.join(self.database_root, self.dbname)
        self.values["data_destination"] = os.path.join(self.db_destination, "data")
        self.values["load_filters"] = LoadFilters.set_load_filters(navigable_objects=self.navigable_objects)
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


class LoadConfig(object):
    """Load a load_config file"""

    def __init__(self):
        self.config = {}

    def parse(self, load_config_file_path):
        load_config_file = imp.load_source("external_load_config", load_config_file_path)
        for a in dir(load_config_file):
            if not a.startswith("__") and not isinstance(getattr(load_config_file, a), collections.Callable):
                value = getattr(config_file, a)
                if value:
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
                    else:
                        self.config[a] = value
            elif a == "parser_factory":
                value = getattr(load_config_file, a)
                self.config["parser_factory"] = value
