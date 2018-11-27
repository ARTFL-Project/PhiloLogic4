#!/usr/bin/env python3
"""Standard PhiloLogic5 loader.
Calls all parsing functions and stores data in index"""

import collections
import imp
import math
import os
import pickle
import re
import shutil
import sqlite3
import sys
import time
from glob import glob

from lxml import etree
from philologic.Config import MakeDBConfig, MakeWebConfig
from philologic.PostFilters import make_sql_table
from philologic.utils import convert_entities, pretty_print, sort_list
from multiprocess import Pool


SORT_BY_WORD = "-k 2,2"
SORT_BY_ID = "-k 3,3n -k 4,4n -k 5,5n -k 6,6n -k 7,7n -k 8,8n -k 9,9n"
OBJECT_TYPES = ["doc", "div1", "div2", "div3", "para", "sent", "word"]

BLOCKSIZE = 2048  # index block size.  Don't alter.
INDEX_CUTOFF = 10  # index frequency cutoff.  Don't alter.

DEFAULT_TABLES = ("toms", "pages", "refs", "graphics", "lines", "words")

DEFAULT_OBJECT_LEVEL = "doc"

NAVIGABLE_OBJECTS = ("doc", "div1", "div2", "div3", "para")

PARSER_OPTIONS = [
    "parser_factory",
    "doc_xpaths",
    "token_regex",
    "tag_to_obj_map",
    "metadata_to_parse",
    "suppress_tags",
    "load_filters",
    "break_apost",
    "chars_not_to_index",
    "break_sent_in_line_group",
    "tag_exceptions",
    "join_hyphen_in_words",
    "unicode_word_breakers",
    "abbrev_expand",
    "long_word_limit",
    "flatten_ligatures",
    "sentence_breakers",
    "file_type",
]


class Loader(object):
    """Loader class"""

    def __init__(self, **loader_options):
        self.omax = [1, 1, 1, 1, 1, 1, 1, 1, 1]
        self.parse_pool = None
        self.types = OBJECT_TYPES
        self.tables = DEFAULT_TABLES
        self.sort_by_word = SORT_BY_WORD
        self.sort_by_id = SORT_BY_ID
        self.debug = loader_options["debug"]
        self.default_object_level = loader_options["default_object_level"]
        self.post_filters = loader_options["post_filters"]
        self.words_to_index = loader_options["words_to_index"]
        self.token_regex = loader_options["token_regex"]

        self.parser_config = {}
        for option in PARSER_OPTIONS:
            try:
                self.parser_config[option] = loader_options[option]
            except KeyError:  # option hasn't been set
                pass

        self.setup_dir(loader_options["data_destination"])
        load_config_path = os.path.join(loader_options["data_destination"], "load_config.py")
        # Loading these from a load_config would crash the parser for a number of reasons...
        values_to_ignore = [
            "load_filters",
            "post_filters",
            "parser_factory",
            "data_destination",
            "db_destination",
            "dbname",
        ]
        if loader_options["load_config"]:
            shutil.copy(loader_options["load_config"], load_config_path)
            config_obj = imp.load_source("external_load_config", loader_options["load_config"])
            already_configured_values = {}
            for attribute in dir(config_obj):
                if not attribute.startswith("__") and not isinstance(
                    getattr(config_obj, attribute), collections.Callable
                ):
                    already_configured_values[attribute] = getattr(config_obj, attribute)
            with open(load_config_path, "a") as load_config_copy:
                print("\n\n## The values below were also used for loading ##", file=load_config_copy)
                for option in loader_options:
                    if (
                        option not in already_configured_values
                        and option not in values_to_ignore
                        and option != "web_config"
                    ):
                        print("%s = %s\n" % (option, repr(loader_options[option])), file=load_config_copy)
        else:
            with open(load_config_path, "w") as load_config_copy:
                print("#!/usr/bin/env python3", file=load_config_copy)
                print(
                    '"""This is a dump of the default configuration used to load this database,', file=load_config_copy
                )
                print("including non-configurable options. You can use this file to reload", file=load_config_copy)
                print(
                    'the current database using the -l flag. See load documentation for more details"""\n\n',
                    file=load_config_copy,
                )
                for option in loader_options:
                    if option not in values_to_ignore and option != "web_config":
                        print("%s = %s\n" % (option, repr(loader_options[option])), file=load_config_copy)

        if "web_config" in loader_options:
            web_config_path = os.path.join(loader_options["data_destination"], "web_config.cfg")
            print("\nSaving predefined web_config.cfg file to %s..." % web_config_path)
            with open(web_config_path, "w") as w:
                w.write(loader_options["web_config"])
            self.predefined_web_config = True
        else:
            self.predefined_web_config = False

        self.theme = loader_options["theme"]

        self.metadata_fields = []
        self.metadata_hierarchy = []
        self.metadata_types = {}
        self.normalized_fields = []
        self.metadata_fields_not_found = []

    def setup_dir(self, path):
        """Setup database directory"""
        os.system("mkdir -p %s" % path)
        self.workdir = path + "/WORK/"
        self.textdir = path + "/TEXT/"
        os.mkdir(self.workdir)
        os.mkdir(self.textdir)
        self.destination = path

    def add_files(self, files):
        """Copy files to database directory"""
        print("\nCopying files to database directory...", end=" ")
        self.filenames = []
        for f in files:
            new_file_path = os.path.join(self.textdir, os.path.basename(f).replace(" ", "_").replace("'", "_"))
            shutil.copy2(f, new_file_path)
            os.chmod(new_file_path, 775)
            self.filenames.append(f)
        print("done.\n")

    def parse_bibliography_file(self, bibliography_file, sort_by_field, reverse_sort=True):
        """Parse tab delimited bibliography file"""
        load_metadata = []
        files = set(os.listdir(self.textdir))
        with open(bibliography_file) as input_file:
            metadata_fields = input_file.readline().strip().split("\t")
            filename_index = metadata_fields.index("filename")
            for line in input_file:
                line = line.strip()
                file_metadata = {}
                values = line.split("\t")
                if values[filename_index] not in files:
                    continue
                for pos, field in enumerate(metadata_fields):
                    file_metadata[field] = values[pos]
                load_metadata.append(file_metadata)
        print("Sorting files by the following metadata fields: %s..." % ", ".join([i for i in sort_by_field]), end=" ")

        def make_sort_key(d):
            """Inner sort function"""
            key = [d.get(f, "") for f in sort_by_field]
            return key

        load_metadata.sort(key=make_sort_key, reverse=reverse_sort)
        print("done.")
        return load_metadata

    def parse_tei_header(self):
        """Parse header in TEI files"""
        load_metadata = []
        metadata_xpaths = self.parser_config["doc_xpaths"]
        self.deleted_files = []
        for file in os.scandir(self.textdir):
            data = {"filename": file.name}
            header = ""
            with open(file.path) as text_file:
                try:
                    file_content = "".join(text_file.readlines())
                except UnicodeDecodeError:
                    self.deleted_files.append(file.name)
                    continue
            try:
                start_header_index = re.search(r"<teiheader", file_content, re.I).start()
                end_header_index = re.search(r"</teiheader", file_content, re.I).start()
            except AttributeError:  # tag not found
                self.deleted_files.append(file.name)
                continue
            header = file_content[start_header_index:end_header_index]
            header = convert_entities(header)
            if self.debug:
                print("parsing %s header..." % file.name)
            parser = etree.XMLParser(recover=True)
            try:
                tree = etree.fromstring(header, parser)
                trimmed_metadata_xpaths = []
                for field in metadata_xpaths:
                    for xpath in metadata_xpaths[field]:
                        attr_pattern_match = re.search(r"@([^\/\[\]]+)$", xpath)
                        if attr_pattern_match:
                            xp_prefix = xpath[: attr_pattern_match.start(0)]
                            attr_name = attr_pattern_match.group(1)
                            elements = tree.findall(xp_prefix)
                            for el in elements:
                                if el is not None and el.get(attr_name, ""):
                                    data[field] = el.get(attr_name, "")
                                    break
                        else:
                            el = tree.find(xpath)
                            if el is not None and el.text is not None:
                                data[field] = el.text
                                break
                trimmed_metadata_xpaths = [
                    (metadata_type, xpath, field)
                    for metadata_type in ["div", "para", "sent", "word", "page"]
                    if metadata_type in metadata_xpaths
                    for field in metadata_xpaths[metadata_type]
                    for xpath in metadata_xpaths[metadata_type][field]
                ]
                data = self.create_year_field(data)
                if self.debug:
                    print(pretty_print(data))
                data["options"] = {"metadata_xpaths": trimmed_metadata_xpaths}
                load_metadata.append(data)
            except etree.XMLSyntaxError:
                self.deleted_files.append(file.name)
        if self.deleted_files:
            for f in self.deleted_files:
                print("%s has no valid TEI header or contains invalid data: removing from database load..." % f)
        return load_metadata

    def parse_dc_header(self):
        """Parse Dublin Core header"""
        load_metadata = []
        for file in os.scandir(self.textdir):
            data = {}
            header = ""
            with open(file.path) as fh:
                for line in fh:
                    start_scan = re.search(r"<teiheader>|<temphead>|<head>", line, re.IGNORECASE)
                    end_scan = re.search(r"</teiheader>|<\/?temphead>|</head>", line, re.IGNORECASE)
                    if start_scan:
                        header += line[start_scan.start() :]
                    elif end_scan:
                        header += line[: end_scan.end()]
                        break
                    else:
                        header += line
            matches = re.findall(r'<meta name="DC\.([^"]+)" content="([^"]+)"', header)
            if not matches:
                matches = re.findall(r"<dc:([^>]+)>([^>]+)>", header)
            for metadata_name, metadata_value in matches:
                metadata_value = metadata_value
                metadata_value = convert_entities(metadata_value)
                metadata_name = metadata_name.lower()
                data[metadata_name] = metadata_value
            data["filename"] = file.name  # place at the end in case the value was in the header
            data = self.create_year_field(data)
            if self.debug:
                print(pretty_print(data))
            load_metadata.append(data)
        return load_metadata

    def create_year_field(self, metadata):
        """Create year field from date fields in header"""
        year_finder = re.compile(r"^.*?(\-?\d{1,}).*")  # we are assuming dates from 1000 AC
        earliest_year = 2500
        for field in ["date", "create_date", "pub_date", "period"]:
            if field in metadata:
                year_match = year_finder.search(metadata[field])
                if year_match:
                    year = int(year_match.groups()[0])
                    if field == "create_date":  # this should be the canonical date
                        earliest_year = year
                        break
                    if year < earliest_year:
                        earliest_year = year
        if earliest_year != 2500:
            metadata["year"] = str(earliest_year)
        return metadata

    def parse_metadata(self, sort_by_field, header="tei"):
        """Parsing metadata fields in TEI or Dublin Core headers"""
        print("### Parsing metadata ###", flush=True)
        print("%s: Parsing metadata in %d files..." % (time.ctime(), len(os.listdir(self.textdir))), flush=True)
        if header == "tei":
            load_metadata = self.parse_tei_header()
        elif header == "dc":
            load_metadata = self.parse_dc_header()

        print(
            "%s: Sorting files by the following metadata fields: %s..."
            % (time.ctime(), ", ".join([i for i in sort_by_field])),
            end=" ",
            flush=True,
        )

        self.sort_order = sort_by_field  # to be used for the sort by concordance biblio key in web config
        if sort_by_field:
            return sort_list(load_metadata, sort_by_field)
        sorted_load_metadata = []
        for filename in self.filenames:
            for m in load_metadata:
                if m["filename"] == os.path.basename(filename):
                    sorted_load_metadata.append(m)
                    break
        return sorted_load_metadata

    def parse_files(self, workers, data_dicts=None):
        """Parse all files"""
        print("\n\n### Parsing files ###")
        os.chdir(self.workdir)  # questionable

        if data_dicts is None:
            data_dicts = [{"filename": fn.name} for fn in os.scandir(self.textdir)]
        filequeue = [
            {
                "name": d["filename"],
                "size": os.path.getsize(self.textdir + d["filename"]),
                "id": n + 1,
                "options": d["options"] if "options" in d else {},
                "newpath": self.textdir + d["filename"],
                "raw": self.workdir + d["filename"] + ".raw",
                "words": self.workdir + d["filename"] + ".words.sorted",
                "toms": self.workdir + d["filename"] + ".toms",
                "sortedtoms": self.workdir + d["filename"] + ".toms.sorted",
                "pages": self.workdir + d["filename"] + ".pages",
                "refs": self.workdir + d["filename"] + ".refs",
                "graphics": self.workdir + d["filename"] + ".graphics",
                "lines": self.workdir + d["filename"] + ".lines",
                "results": self.workdir + d["filename"] + ".results",
            }
            for n, d in enumerate(data_dicts)
        ]

        self.raw_files = [f["raw"] + ".lz4" for f in filequeue]

        self.metadata_hierarchy.append([])
        # Adding in doc level metadata
        for d in data_dicts:
            for k in list(d.keys()):
                if k not in self.metadata_fields:
                    self.metadata_fields.append(k)
                    self.metadata_hierarchy[0].append(k)
                if k not in self.metadata_types:
                    self.metadata_types[k] = "doc"
                    # don't need to check for conflicts, since doc is first.

        # Adding non-doc level metadata
        for element_type in self.parser_config["metadata_to_parse"]:
            if element_type != "page" and element_type != "ref" and element_type != "line":
                self.metadata_hierarchy.append([])
                for param in self.parser_config["metadata_to_parse"][element_type]:
                    if param not in self.metadata_fields:
                        self.metadata_fields.append(param)
                        self.metadata_hierarchy[-1].append(param)
                    if param not in self.metadata_types:
                        self.metadata_types[param] = element_type
                    else:  # we have a serious error here!  Should raise going forward.
                        pass

        print("%s: parsing %d files." % (time.ctime(), len(filequeue)))
        pool = Pool(workers)
        for results in pool.imap_unordered(self.__parse_file, zip(filequeue, data_dicts)):
            with open(results, "rb") as proc_fh:
                vec = pickle.load(proc_fh)  # load in the results from the child's parsework() function.
            self.omax = [max(x, y) for x, y in zip(vec, self.omax)]
        print("%s: done parsing" % time.ctime())

    def __parse_file(self, file):
        text, metadata = file
        options = text["options"]
        if "options" in metadata:  # cleanup, should do above.
            del metadata["options"]

        print("%s: parsing %d : %s" % (time.ctime(), text["id"], text["name"]), flush=True)

        if "parser_factory" not in options:
            options["parser_factory"] = self.parser_config["parser_factory"]
        parser_factory = options["parser_factory"]
        del options["parser_factory"]

        if "load_filters" not in options:
            options["load_filters"] = self.parser_config["load_filters"]
        filters = options["load_filters"]
        del options["load_filters"]

        for option in [
            "token_regex",
            "suppress_tags",
            "break_apost",
            "chars_not_to_index",
            "break_sent_in_line_group",
            "tag_exceptions",
            "join_hyphen_in_words",
            "unicode_word_breakers",
            "abbrev_expand",
            "long_word_limit",
            "flatten_ligatures",
            "sentence_breakers",
        ]:
            try:
                options[option] = self.parser_config[option]
            except KeyError:  # option hasn't been set
                pass

        with open(text["raw"], "w") as raw_file:
            parser = parser_factory(
                raw_file,
                text["id"],
                text["size"],
                known_metadata=metadata,
                tag_to_obj_map=self.parser_config["tag_to_obj_map"],
                metadata_to_parse=self.parser_config["metadata_to_parse"],
                words_to_index=self.words_to_index,
                file_type=self.parser_config["file_type"],
                **options,
            )
            with open(text["newpath"], "r", newline="") as input_file:
                try:
                    parser.parse(input_file)
                except RuntimeError:
                    print("parse failure...", file=sys.stderr)
                    exit(1)

        for f in filters:
            f(self, text)

        os.system("lz4 -q %s > %s" % (text["raw"], text["raw"] + ".lz4"))
        os.system("rm %s" % text["raw"])
        os.system("lz4 -q %s > %s" % (text["words"], text["words"] + ".lz4"))
        os.system("rm %s" % text["words"])
        return text["results"]

    def merge_objects(self):
        """Merge all parsed objects"""
        print("\n### Merge parser output ###")
        print("%s: sorting words" % time.ctime())
        self.merge_files("words")

        if "words" in self.tables:
            print("%s: concatenating document-order words file..." % time.ctime(), end=" ")
            for d in self.raw_files:
                os.system('lz4cat {} | egrep -a "^word" >> all_words_ordered'.format(d))
            print("done")

        print("%s: sorting objects" % time.ctime())
        self.merge_files("toms")
        if not self.debug:
            for toms_file in glob(self.workdir + "/*toms.sorted"):
                os.system("rm %s" % toms_file)

        print("%s: joining pages" % time.ctime())
        if self.debug is False:
            os.system(
                'for i in $(find {} -type f -name "*pages"); do cat $i >> {}/all_pages; rm $i; done'.format(
                    self.workdir, self.workdir
                )
            )
        else:
            os.system(
                'for i in $(find {} -type f -name "*pages"); do cat $i >> {}/all_pages; done'.format(
                    self.workdir, self.workdir
                )
            )

        print("%s: joining references" % time.ctime())
        if self.debug is False:
            os.system(
                'for i in $(find {} -type f -name "*refs"); do cat $i >> {}/all_refs; rm $i; done'.format(
                    self.workdir, self.workdir
                )
            )
        else:
            os.system(
                'for i in $(find {} -type f -name "*refs"); do cat $i >> {}/all_refs; done'.format(
                    self.workdir, self.workdir
                )
            )

        print("%s: joining graphics" % time.ctime())
        if self.debug is False:
            os.system(
                'for i in $(find {} -type f -name "*graphics"); do cat $i >> {}/all_graphics; rm $i; done'.format(
                    self.workdir, self.workdir
                )
            )
        else:
            os.system(
                'for i in $(find {} -type f -name "*graphics"); do cat $i >> {}/all_graphics; done'.format(
                    self.workdir, self.workdir
                )
            )

        print("%s: joining lines" % time.ctime())
        if self.debug is False:
            os.system(
                'for i in $(find {} -type f -name "*lines"); do cat $i >> {}/all_lines; rm $i; done'.format(
                    self.workdir, self.workdir
                )
            )
        else:
            os.system(
                'for i in $(find {} -type f -name "*lines"); do cat $i >> {}/all_lines; done'.format(
                    self.workdir, self.workdir
                )
            )

    def merge_files(self, file_type, file_num=1000):
        """This function runs a multi-stage merge sort on words
        Since PhiloLogic can potentially merge thousands of files, we need to split
        the sorting stage into multiple steps to avoid running out of file descriptors"""
        if sys.platform == "darwin":
            file_num = 500
        lists_of_files = []
        files = []
        if file_type == "words":
            suffix = "/*words.sorted.lz4"
            open_file_command = "lz4cat"
            sort_command = "LANG=C sort -S 10% -m -T {} {} {} ".format(self.workdir, self.sort_by_word, self.sort_by_id)
            all_object_file = "all_words_sorted.lz4"
        elif file_type == "toms":
            suffix = "/*.toms.sorted"
            open_file_command = "cat"
            sort_command = "LANG=C sort -S 10% -m -T {} {} ".format(self.workdir, self.sort_by_id)
            all_object_file = "all_toms_sorted.lz4"

        # First we split the sort workload into chunks of 100 (default defined in the file_num keyword)
        for f in glob(self.workdir + suffix):
            f = os.path.basename(f)
            files.append(("<(%s %s)" % (open_file_command, f), self.workdir + "/" + f))
            if len(files) == file_num:
                lists_of_files.append(files)
                files = []
        if len(files) > 0:
            lists_of_files.append(files)

        # Then we run the merge sort on each chunk of 500 files and compress the result
        print("%s: Merging %s in batches of %d..." % (time.ctime(), file_type, file_num))
        already_merged = 0
        os.system("touch %s" % self.workdir + "/sorted.init")
        last_sort_file = self.workdir + "/sorted.init"
        for pos, object_list in enumerate(lists_of_files):
            command_list = " ".join([i[0] for i in object_list])
            file_list = " ".join([i[1] for i in object_list])
            output = self.workdir + "sorted.%d.split" % pos
            args = sort_command + command_list
            command = '/bin/bash -c "%s | lz4 -q > %s"' % (args, output)
            status = os.system(command)
            if status != 0:
                print("%s sorting failed\nInterrupting database load..." % file_type)
                sys.exit()
            already_merged += len(object_list)
            last_sort_file = output
            print("%s: %d files sorted..." % (time.ctime(), already_merged))
            if not self.debug:
                os.system("rm %s" % file_list)

        sorted_files = " ".join(["<(lz4cat -q {})".format(i) for i in glob(f"{self.workdir}/*.split")])
        if file_type == "words":
            output_file = os.path.join(self.workdir, all_object_file)
            command = f'/bin/bash -c "{sort_command} {sorted_files} | lz4 -q > {output_file}"'
        else:
            output_file = os.path.join(self.workdir, "all_toms_sorted")
            command = f'/bin/bash -c "{sort_command} {sorted_files} > {output_file}"'
        print(f"{time.ctime()}: Merging all merged sorted files (this may take a while)...", flush=True, end=" ")

        status = os.system(command)
        if status != 0:
            print("%s sorting failed\nInterrupting database load..." % file_type)
            sys.exit()
        print("done.")

        for sorted_file in glob("{}/*.split".format(self.workdir)):
            os.system("rm {}".format(sorted_file))

    def analyze(self):
        """Create inverted index"""
        print("\n### Create inverted index ###")
        print(self.omax)
        vl = [max(int(math.ceil(math.log(float(x) + 1.0, 2.0))), 1) if x > 0 else 1 for x in self.omax]
        print(vl)
        width = sum(x for x in vl)
        print(str(width) + " bits wide.")

        hits_per_block = (BLOCKSIZE * 8) // width
        freq1 = INDEX_CUTOFF
        freq2 = 0
        offset = 0

        # unix one-liner for a frequency table
        os.system(
            '/bin/bash -c "cut -f 2 <(lz4cat {}) | uniq -c | LANG=C sort -S 10% -rn -k 1,1> {}"'.format(
                self.workdir + "/all_words_sorted.lz4", self.workdir + "/all_frequencies"
            )
        )

        # now scan over the frequency table to figure out how wide (in bits) the frequency fields are,
        # and how large the block file will be.
        for line in open(self.workdir + "/all_frequencies"):
            f, _ = line.rsplit(" ", 1)  # uniq -c pads output on the left side, so we split on the right.
            try:
                f = int(f)
            except ValueError:
                f = int(re.sub(r"(\d+)\D+", r"\1", f.strip()))
            if f > freq2:
                freq2 = f
            if f < INDEX_CUTOFF:
                pass  # low-frequency words don't go into the block-mode index.
            else:
                blocks = 1 + f // (hits_per_block + 1)  # high frequency words have at least one block.
                offset += blocks * BLOCKSIZE

        # take the log base 2 for the length of the binary representation.
        freq1_l = math.ceil(math.log(float(freq1), 2.0))
        freq2_l = math.ceil(math.log(float(freq2), 2.0))
        offset_l = math.ceil(math.log(float(offset), 2.0))

        print("freq1: %d; %d bits" % (freq1, freq1_l))
        print("freq2: %d; %d bits" % (freq2, freq2_l))
        print("offst: %d; %d bits" % (offset, offset_l))

        # now write it out in our legacy c-header-like format.  TODO: reasonable format, or ctypes bindings for packer.
        dbs = open(self.workdir + "dbspecs4.h", "w")
        print("#define FIELDS 9", file=dbs)
        print("#define TYPE_LENGTH 1", file=dbs)
        print("#define BLK_SIZE " + str(BLOCKSIZE), file=dbs)
        print("#define FREQ1_LENGTH " + str(freq1_l), file=dbs)
        print("#define FREQ2_LENGTH " + str(freq2_l), file=dbs)
        print("#define OFFST_LENGTH " + str(offset_l), file=dbs)
        print("#define NEGATIVES {0,0,0,0,0,0,0,0,0}", file=dbs)
        print("#define DEPENDENCIES {-1,0,1,2,3,4,5,0,0}", file=dbs)
        print("#define BITLENGTHS {%s}" % ",".join(str(i) for i in vl), file=dbs)
        dbs.close()
        print("%s: analysis done" % time.ctime())
        os.system(
            '/bin/bash -c "lz4cat ' + self.workdir + "/all_words_sorted.lz4 | pack5 " + self.workdir + 'dbspecs4.h"'
        )
        print("%s: all indices built. moving into place." % time.ctime())
        os.system("mv index " + self.destination + "/index")
        os.system("mv index.1 " + self.destination + "/index.1")
        # if self.clean:
        #    os.system('rm all_words_sorted')

    def setup_sql_load(self):
        """Setup SQL DB creation"""
        for table in self.tables:
            if table == "words":
                file_in = self.destination + "/WORK/all_words_ordered"
                indices = [("philo_name",), ("philo_id",), ("parent",), ("start_byte",), ("end_byte",)]
                depth = 7
            elif table == "pages":
                file_in = self.destination + "/WORK/all_pages"
                indices = [("philo_id",)]
                depth = 9
            elif table == "toms":
                file_in = self.destination + "/WORK/all_toms_sorted"
                indices = [("philo_type",), ("philo_id",), ("img",)] + self.metadata_fields
                depth = 7
            elif table == "refs":
                file_in = self.destination + "/WORK/all_refs"
                indices = [("parent",), ("target",), ("type",)]
                depth = 9
            elif table == "graphics":
                file_in = self.destination + "/WORK/all_graphics"
                indices = [("parent",), ("philo_id",)]
                depth = 9
            elif table == "lines":
                file_in = self.destination + "/WORK/all_lines"
                indices = [("doc_id", "start_byte", "end_byte")]
                depth = 9
            post_filter = make_sql_table(table, file_in, indices=indices, depth=depth)
            self.post_filters.insert(0, post_filter)

    def post_processing(self, *extra_filters):
        """Run important post-parsing functions for frequencies and word normalization"""
        print("\n### Post-processing filters ###")
        for f in self.post_filters:
            f(self)

        if extra_filters:
            print("Running the following additional filters:")
            for f in extra_filters:
                print(f.__name__ + "...", end=" ")
                f(self)

    def finish(self):
        """Write important runtime information to the database directory"""
        print("\n### Finishing up ###")
        os.mkdir(self.destination + "/src/")
        os.mkdir(self.destination + "/hitlists/")
        os.chmod(self.destination + "/hitlists/", 0o777)
        os.system("mv dbspecs4.h ../src/dbspecs4.h")

        # Make data directory inaccessible from the outside
        fh = open(self.destination + "/.htaccess", "w")
        fh.write("deny from all")
        fh.close()

        self.write_db_config()
        if self.predefined_web_config is False:
            self.write_web_config()
        if self.debug is False:
            os.system("rm -f %s/*" % self.workdir)

    def write_db_config(self):
        """ Write local variables used by libphilo"""
        filename = self.destination + "/db.locals.py"
        metadata = [i for i in self.metadata_fields if i not in self.metadata_fields_not_found]
        db_values = {
            "metadata_fields": metadata,
            "metadata_hierarchy": self.metadata_hierarchy,
            "metadata_types": self.metadata_types,
            "normalized_fields": self.normalized_fields,
            "debug": self.debug,
        }
        db_values["token_regex"] = self.token_regex
        db_values["default_object_level"] = self.default_object_level
        db_config = MakeDBConfig(filename, **db_values)
        print(db_config, file=open(filename, "w"))
        print("wrote database info to %s." % (filename))

    def write_web_config(self):
        """ Write configuration variables for the Web application"""
        metadata = [i for i in self.metadata_fields if i not in self.metadata_fields_not_found]
        config_values = {
            "dbname": os.path.basename(re.sub("/data/?$", "", self.destination)),
            "metadata": metadata,
            "facets": metadata,
            "theme": self.theme,
        }
        # Fetch search examples:
        search_examples = {}
        conn = sqlite3.connect(self.destination + "/toms.db")
        conn.text_factory = str
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        for field in metadata:
            object_type = self.metadata_types[field]
            try:
                if object_type != "div":
                    c.execute(
                        'select %s from toms where philo_type="%s" and %s!="" limit 1' % (field, object_type, field)
                    )
                else:
                    c.execute(
                        'select %s from toms where philo_type="div1" or philo_type="div2" or philo_type="div3" and %s!="" limit 1'
                        % (field, field)
                    )
            except sqlite3.OperationalError:
                continue
            try:
                search_examples[field] = c.fetchone()[0]
            except (TypeError, AttributeError):
                continue
        config_values["search_examples"] = search_examples

        config_values["metadata_input_style"] = {f: "text" for f in metadata}

        # Populate kwic metadata sorting and kwic biblio fields variables with metadata
        # Check if title and author are empty, if so, default to filename
        config_values["kwic_metadata_sorting_fields"] = []
        config_values["kwic_bibliography_fields"] = []
        if "author" in config_values["search_examples"]:
            config_values["kwic_metadata_sorting_fields"].append("author")
            config_values["kwic_bibliography_fields"].append("author")
        if "title" in config_values["search_examples"]:
            config_values["kwic_metadata_sorting_fields"].append("title")
            config_values["kwic_bibliography_fields"].append("title")
        if not config_values["kwic_metadata_sorting_fields"]:
            config_values["kwic_metadata_sorting_fields"] = ["filename"]
            config_values["kwic_bibliography_fields"] = ["filename"]

        if "author" in config_values["search_examples"] and "title" in config_values["search_examples"]:
            config_values["concordance_biblio_sorting"] = [("author", "title"), ("title", "author")]

        filename = self.destination + "/web_config.cfg"
        web_config = MakeWebConfig(filename, **config_values)
        print(web_config, file=open(filename, "w"))
        print("wrote Web application info to %s." % (filename))


def shellquote(s):
    """Quote shell commands"""
    return "'" + s.replace("'", "'\\''") + "'"


def setup_db_dir(db_destination, web_app_dir, force_delete=False):
    """Setup database directory"""
    try:
        os.mkdir(db_destination)
    except OSError:
        if force_delete:  # useful to run db loads with nohup
            os.system("rm -rf %s" % db_destination)
            os.mkdir(db_destination)
        else:
            print("The database folder could not be created at %s" % db_destination)
            print("Do you want to delete this database? Yes/No")
            choice = input().lower()
            if choice.startswith("y"):
                os.system("rm -rf %s" % db_destination)
                os.mkdir(db_destination)
            else:
                sys.exit()

    if web_app_dir:
        for f in os.listdir(web_app_dir):
            if f != "data":
                cp_command = "cp -r %s %s" % (web_app_dir + f, db_destination + "/" + f)
                os.system(cp_command)

        os.system("chmod -R 777 %s/app/assets/css" % db_destination)
        os.system("chmod -R 777 %s/app/assets/js" % db_destination)
        os.system("mkdir -p %s/custom_functions" % db_destination)
        os.system("touch %s/custom_functions/__init__.py" % db_destination)
