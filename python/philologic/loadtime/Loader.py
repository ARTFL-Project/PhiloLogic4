#!/usr/bin/env python3
"""Standard PhiloLogic4 loader.
Calls all parsing functions and stores data in index"""

import collections
import csv
import datetime
import math
import os
import pickle
import shutil
import sqlite3
import sys
import time
from glob import iglob
from json import dump
from orjson import loads
import msgpack

import lxml.etree
import regex as re
from black import FileMode, format_str
from multiprocess import Pool
from philologic.Config import MakeDBConfig, MakeWebConfig
from philologic.loadtime.PostFilters import make_sentences_table, make_sql_table
from philologic.utils import convert_entities, extract_full_date, extract_integer, load_module, pretty_print, sort_list
from tqdm import tqdm
import lz4.frame

SORT_BY_WORD = "-k 2,2"
SORT_BY_ID = "-k 3,3n -k 4,4n -k 5,5n -k 6,6n -k 7,7n -k 8,8n -k 9,9n"
OBJECT_TYPES = ["doc", "div1", "div2", "div3", "para", "sent", "word"]

BLOCKSIZE = 2048  # index block size.  Don't alter.
INDEX_CUTOFF = 10  # index frequency cutoff.  Don't alter.

DEFAULT_TABLES = ("toms", "pages", "refs", "graphics", "lines", "sentences")

DEFAULT_OBJECT_LEVEL = "doc"

NAVIGABLE_OBJECTS = ("doc", "div1", "div2", "div3", "para")

ASCII_CONVERSION = True

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
    "metadata_sql_types",
    "lowercase_index",
]


class ParserError(Exception):
    """Parser exception"""

    def __init___(self, *error_args):
        super().__init__(error_args)


class Loader:
    """Loader class"""

    sort_by_word = SORT_BY_WORD
    sort_by_id = SORT_BY_ID
    types = OBJECT_TYPES
    tables = DEFAULT_TABLES
    omax = [1, 1, 1, 1, 1, 1, 1, 1, 1]
    parser_config = {}
    words_to_index = set()
    data_dicts = []
    filequeue = []
    raw_files = []
    textdir = ""
    workdir = ""
    web_app_dir = ""
    metadata_fields = []
    metadata_types = {}
    metadata_hierarchy = []
    metadata_fields_not_found = []
    debug = False
    default_object_level = "doc"
    post_filters = []
    token_regex = ""
    url_root = ""
    cores = 2
    ascii_conversion = ASCII_CONVERSION
    word_attributes = set()

    @classmethod
    def set_class_attributes(cls, loader_options):
        """Set initial class attributes and return Loader object"""
        cls.post_filters = loader_options["post_filters"]
        cls.debug = loader_options["debug"]
        cls.words_to_index = loader_options["words_to_index"]
        cls.destination = loader_options["data_destination"]
        cls.workdir = os.path.join(loader_options["data_destination"], "WORK/")
        cls.textdir = os.path.join(loader_options["data_destination"], "TEXT/")
        cls.web_app_dir = os.path.join(loader_options["db_destination"], "app/")
        cls.debug = loader_options["debug"]
        cls.default_object_level = loader_options["default_object_level"]
        cls.token_regex = loader_options["token_regex"]
        cls.url_root = loader_options["url_root"]
        cls.cores = loader_options["cores"]
        cls.ascii_conversion = loader_options["ascii_conversion"]
        cls.metadata_sql_types = loader_options["metadata_sql_types"]
        cls.word_attributes = set()
        for option in PARSER_OPTIONS:
            try:
                cls.parser_config[option] = loader_options[option]
            except KeyError:  # option hasn't been set
                pass
        return cls(**loader_options)

    def __init__(self, **loader_options):
        os.system(f"mkdir -p {self.destination}")
        os.mkdir(self.workdir)
        os.mkdir(self.textdir)

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
            config_obj = load_module("external_load_config", loader_options["load_config"])
            already_configured_values = {}
            for attribute in dir(config_obj):
                if not attribute.startswith("__") and not isinstance(
                    getattr(config_obj, attribute), collections.abc.Callable
                ):
                    already_configured_values[attribute] = getattr(config_obj, attribute)
            with open(load_config_path, "a") as load_config_copy:
                print("\n\n## The values below were also used for loading ##", file=load_config_copy)
                for option, option_value in loader_options.items():
                    if (
                        option not in already_configured_values
                        and option not in values_to_ignore
                        and option != "web_config"
                    ):
                        print("%s = %s\n" % (option, repr(option_value)), file=load_config_copy)
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
                for option, option_value in loader_options.items():
                    if option not in values_to_ignore and option != "web_config":
                        print("%s = %s\n" % (option, repr(option_value)), file=load_config_copy)

        if "web_config" in loader_options:
            web_config_path = os.path.join(loader_options["data_destination"], "web_config.cfg")
            print("\nSaving predefined web_config.cfg file to %s..." % web_config_path)
            with open(web_config_path, "w") as w:
                w.write(loader_options["web_config"])
            self.predefined_web_config = True
        else:
            self.predefined_web_config = False

        self.filenames = []
        self.raw_files = []
        self.deleted_files = []
        self.metadata_fields = []
        self.metadata_hierarchy = []
        self.metadata_types = {}
        self.normalized_fields = []
        self.metadata_fields_not_found = []
        self.sort_order = ""

    def add_files(self, files):
        """Copy files to database directory"""
        for f in tqdm(files, total=len(files), leave=False, desc="Copying files to database directory"):
            new_file_path = os.path.join(self.textdir, os.path.basename(f).replace(" ", "_").replace("'", "_"))
            shutil.copy2(f, new_file_path)
            os.chmod(new_file_path, 775)
            self.filenames.append(f)
        os.system(f"chmod -R 775 {self.textdir}")
        print("Copying files to database directory... done.", flush=True)

    def parse_bibliography_file(self, bibliography_file, sort_by_field, reverse_sort=True):
        """Parse tab delimited bibliography file: tsv, tab, or csv"""
        load_metadata = []
        if bibliography_file.endswith(".tab") or bibliography_file.endswith(".tsv"):
            delimiter = "\t"
        else:
            delimiter = ","
        with open(bibliography_file, encoding="utf8") as input_file:
            reader = csv.DictReader(input_file, delimiter=delimiter)
            load_metadata = [metadata for metadata in reader]
        print("Sorting files by the following metadata fields: %s..." % ", ".join([i for i in sort_by_field]), end=" ")

        def make_sort_key(d):
            """Inner sort function"""
            key = [d.get(f, "") for f in sort_by_field]
            return key

        load_metadata.sort(key=make_sort_key, reverse=reverse_sort)
        print("done.")
        return load_metadata

    def parse_tei_header(self, verbose):
        """Parse header in TEI files"""
        load_metadata = []
        metadata_xpaths = self.parser_config["doc_xpaths"]
        doc_count = len(os.listdir(self.textdir))
        if verbose:
            prefix = f"{time.ctime()}: Parsing document level metadata"
        else:
            prefix = "Parsing document level metadata"
        for file in tqdm(
            os.scandir(self.textdir),
            total=doc_count,
            desc=prefix,
            leave=False,
        ):
            data = {"filename": file.name}
            header = ""
            with open(file.path, encoding="utf8") as text_file:
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
            parser = lxml.etree.XMLParser(recover=True)
            try:
                tree = lxml.etree.fromstring(header, parser)
                trimmed_metadata_xpaths = []
                for field in metadata_xpaths:
                    for xpath in metadata_xpaths[field]:
                        xpath = xpath.rstrip("/")  # make sure there are no trailing slashes which make lxml die
                        try:
                            elements = tree.xpath(xpath)
                        except lxml.etree.XPathEvalError:
                            continue
                        for element in elements:
                            if element is not None:
                                value = ""
                                if isinstance(element, lxml.etree._Element) and element.text is not None:
                                    value = element.text.strip()
                                elif isinstance(element, lxml.etree._ElementUnicodeResult):
                                    value = str(element).strip()
                                if value:
                                    if field not in self.parser_config["metadata_sql_types"]:
                                        data[field] = value
                                        if (
                                            field in ("create_date", "pub_date") and re.search(r"\d", value) is None
                                        ):  # make sure we have a number in there
                                            del data[field]
                                            continue
                                    elif self.parser_config["metadata_sql_types"][field] == "int":
                                        data[field] = extract_integer(value)
                                    elif self.parser_config["metadata_sql_types"][field] == "date":
                                        data[field] = extract_full_date(value)
                                    break
                        else:  # only continue looping over xpaths if no break in inner loop
                            continue
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
            except lxml.etree.XMLSyntaxError:
                self.deleted_files.append(file.name)
        print(f"{prefix}... done.", flush=True)
        if self.deleted_files:
            print(
                "\nThe following files have been removed from the load since they have no valid TEI header or contain invalid data:\n",
                ", ".join(self.deleted_files),
            )
        return load_metadata

    def parse_dc_header(self):
        """Parse Dublin Core header"""
        load_metadata = []
        doc_count = len(os.listdir(self.textdir))
        prefix = f"{time.ctime()}: Parsing document level metadata"
        for file in tqdm(os.scandir(self.textdir), total=doc_count, leave=False, desc=prefix):
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
                metadata_value = convert_entities(metadata_value)
                metadata_name = metadata_name.lower()
                data[metadata_name] = metadata_value
            data["filename"] = file.name  # place at the end in case the value was in the header
            data = self.create_year_field(data)
            if self.debug:
                print(pretty_print(data))
            load_metadata.append(data)
        print(f"{prefix}... done.", flush=True)
        return load_metadata

    def create_year_field(self, metadata):
        """Create year field from date fields in header"""
        year_finder = re.compile(r"^.*?(\-?\d{1,}).*")  # we are assuming positive years
        earliest_year = 2500
        metadata_with_year = ""
        for field in ["date", "create_date", "pub_date", "period"]:
            if field in metadata:
                if isinstance(metadata[field], datetime.date):
                    metadata[field] = str(metadata[field].year)
                elif isinstance(metadata[field], int):
                    metadata[field] = str(metadata[field])
                year_match = year_finder.search(metadata[field])  # make sure it's not a datetime or an int.
                if year_match:
                    year = int(year_match.groups()[0])
                    metadata_with_year = field
                    if field == "create_date":  # this should be the canonical date
                        earliest_year = year
                        break
                    if year < earliest_year:
                        earliest_year = year
        if earliest_year != 2500:
            if re.search(r"BC", metadata[metadata_with_year], re.I):
                metadata["year"] = int(f"-{earliest_year}")
            else:
                metadata["year"] = earliest_year
        return metadata

    def parse_metadata(self, sort_by_field, header="tei", verbose=True):
        """Parsing metadata fields in TEI or Dublin Core headers"""
        if verbose is True:  # Turn off output when called from other libs such as TextPAIR
            print("### Parsing metadata ###", flush=True)
        if header == "tei":
            load_metadata = self.parse_tei_header(verbose)
        else:
            load_metadata = self.parse_dc_header()

        print(
            f'{time.ctime()}: Sorting files by the following metadata fields: {", ".join([i for i in sort_by_field])}...',
            end=" ",
            flush=True,
        )

        self.sort_order = sort_by_field  # to be used for the sort by concordance biblio key in web config
        if sort_by_field:
            sorted_load_metadata = sort_list(load_metadata, sort_by_field)
        else:
            sorted_load_metadata = []
            for filename in self.filenames:
                for m in load_metadata:
                    if m["filename"] == os.path.basename(filename):
                        sorted_load_metadata.append(m)
                        break
        if self.debug is True:
            print("Files sorted in following order:")
            for metadata in sorted_load_metadata:
                metadata = collections.defaultdict(str, metadata)
                print(f"File {metadata['filename']}:")
                print({field: metadata[field] for field in sort_by_field}, "\n")
        return sorted_load_metadata

    @classmethod
    def set_file_data(cls, load_metadata, textdir, workdir):
        """Set file data"""
        if load_metadata is None:
            cls.data_dicts = [{"filename": fn.name} for fn in os.scandir(textdir)]
        else:
            cls.data_dicts = load_metadata
        cls.filequeue = [
            {
                "name": d["filename"],
                "size": os.path.getsize(textdir + d["filename"]),
                "id": n + 1,
                "options": d["options"] if "options" in d else {},
                "newpath": textdir + d["filename"],
                "raw": workdir + d["filename"] + ".raw",
                "words": workdir + d["filename"] + ".words.sorted",
                "toms": workdir + d["filename"] + ".toms",
                "sortedtoms": workdir + d["filename"] + ".toms.sorted",
                "pages": workdir + d["filename"] + ".pages",
                "refs": workdir + d["filename"] + ".refs",
                "graphics": workdir + d["filename"] + ".graphics",
                "lines": workdir + d["filename"] + ".lines",
                "results": workdir + d["filename"] + ".results",
            }
            for n, d in enumerate(cls.data_dicts)
        ]
        cls.metadata_hierarchy.append([])
        # Adding in doc level metadata
        for d in cls.data_dicts:
            for k in list(d.keys()):
                if k not in cls.metadata_fields:
                    cls.metadata_fields.append(k)
                    cls.metadata_hierarchy[0].append(k)
                if k not in cls.metadata_types:
                    cls.metadata_types[k] = "doc"
                    # don't need to check for conflicts, since doc is first.

        # Adding non-doc level metadata
        for element_type in cls.parser_config["metadata_to_parse"]:
            if element_type != "page" and element_type != "ref" and element_type != "line":
                cls.metadata_hierarchy.append([])
                for param in cls.parser_config["metadata_to_parse"][element_type]:
                    if param not in cls.metadata_fields:
                        cls.metadata_fields.append(param)
                        cls.metadata_hierarchy[-1].append(param)
                    if param not in cls.metadata_types:
                        cls.metadata_types[param] = element_type
                    else:  # we have a serious error here!  Should raise going forward.
                        pass

        # Add unique philo ids for top level text objects
        cls.metadata_fields.extend(["philo_doc_id", "philo_div1_id", "philo_div2_id", "philo_div3_id"])
        for pos, object_level in enumerate(["doc", "div1", "div2", "div3"]):
            cls.metadata_hierarchy[pos].append(f"philo_{object_level}_id")
            cls.metadata_types[f"philo_{object_level}_id"] = object_level

    @classmethod
    def parse_files(cls, workers, verbose=True):
        """Parse all files
        chunksize is setable from the philoload script and can be helpful when loading
        many small files"""
        os.chdir(cls.workdir)
        if verbose is True:
            print("\n\n### Parsing files ###")
            print("%s: parsing %d files." % (time.ctime(), len(cls.filequeue)))
        with tqdm(total=len(cls.filequeue), smoothing=0, leave=False, desc="Parsing files") as pbar:
            with Pool(workers) as pool:
                for results in pool.imap_unordered(cls.parse_file, range(len(cls.data_dicts))):
                    with open(results, "rb") as proc_fh:
                        vec = pickle.load(proc_fh)
                    cls.omax = [max(x, y) for x, y in zip(vec, cls.omax)]
                    pbar.update()
        if verbose is True:
            print("%s: done parsing" % time.ctime())

    @classmethod
    def parse_file(cls, file_pos):
        """Parse a single file"""
        text = cls.filequeue[file_pos]
        metadata = cls.data_dicts[file_pos]
        options = text["options"]
        if "options" in metadata:  # cleanup, should do above.
            del metadata["options"]

        if "parser_factory" not in options:
            options["parser_factory"] = cls.parser_config["parser_factory"]
        parser_factory = options["parser_factory"]
        del options["parser_factory"]

        if "load_filters" not in options:
            options["load_filters"] = cls.parser_config["load_filters"]
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
            "punctuation",
            "metadata_sql_types",
        ]:
            try:
                options[option] = cls.parser_config[option]
            except KeyError:  # option hasn't been set
                pass

        with open(text["raw"], "w", encoding="utf8") as raw_file:
            parser = parser_factory(
                raw_file,
                text["id"],
                text["size"],
                known_metadata=metadata,
                tag_to_obj_map=cls.parser_config["tag_to_obj_map"],
                metadata_to_parse=cls.parser_config["metadata_to_parse"],
                words_to_index=cls.words_to_index,
                file_type=cls.parser_config["file_type"],
                **options,
            )
            with open(text["newpath"], "r", newline="", encoding="utf8") as input_file:
                try:
                    parser.parse(input_file)
                except RuntimeError:
                    print("parse failure...", file=sys.stderr)
                    exit(1)

        for f in filters:
            try:
                f(cls, text)
            except Exception:
                raise ParserError(f"{text['name']} has caused parser to die.")

        os.system("lz4 --rm -c -q -3 %s > %s" % (text["words"], text["words"] + ".lz4"))
        os.remove(text["raw"])
        return text["results"]

    def merge_objects(self):
        """Merge all parsed objects"""
        print("\n### Merge parser output ###")
        print(f"{time.ctime()}: sorting words")
        self.merge_files("words")

        print(f"{time.ctime()}: sorting objects", flush=True)
        self.merge_files("toms")
        if self.debug is False:
            for toms_file in iglob(self.workdir + "/*toms.sorted"):
                os.system(f"rm {toms_file}")

        for object_type, extension in [
            ("pages", "pages"),
            ("references", "refs"),
            ("graphics", "graphics"),
            ("lines", "lines"),
        ]:
            print(f"{time.ctime()}: joining {object_type}", flush=True)
            if self.debug is False:
                os.system(
                    f'for i in $(find {self.workdir} -type f -name "*{extension}"); do cat $i >> {self.workdir}/all_{extension}; rm $i; done'
                )
            else:
                os.system(
                    f'for i in $(find {self.workdir} -type f -name "*{extension}"); do cat $i >> {self.workdir}/all_{extension}; done'
                )

    def merge_files(self, file_type, file_num=1000, verbose=True):
        """This function runs a multi-stage merge sort on words
        Since PhiloLogic can potentially merge thousands of files, we need to split
        the sorting stage into multiple steps to avoid running out of file descriptors"""
        if sys.platform == "darwin":
            file_num = 250
        lists_of_files = []
        files = []
        if file_type == "words":
            suffix = "/*words.sorted.lz4"
            if self.debug is False:
                open_file_command = "lz4cat --rm"
            else:
                open_file_command = "lz4cat"
            sort_command = f"LANG=C sort -S 25% -m -T {self.workdir} {self.sort_by_word} {self.sort_by_id} "
        else:  # sorting for toms
            suffix = "/*.toms.sorted"
            open_file_command = "cat"
            sort_command = f"LANG=C sort -S 25% -m -T {self.workdir} {self.sort_by_id} "

        # First we split the sort workload into chunks of 1000 (default defined in the file_num keyword)
        for f in iglob(self.workdir + suffix):
            f = os.path.basename(f)
            files.append((f"<({open_file_command} {f})", self.workdir + "/" + f))
            if len(files) == file_num:
                lists_of_files.append(files)
                files = []
        if files:
            lists_of_files.append(files)

        total_files = sum(len(files) for files in lists_of_files)
        # Then we run the merge sort on each chunk of 500 files and compress the result
        if verbose is True:
            print(f"{time.ctime()}: Merging {file_type} in batches of {file_num}...", flush=True)
        else:
            print(f"Merging {file_type} in batches of {file_num}...", flush=True)
        os.system(f"touch {self.workdir}/sorted.init")
        with tqdm(total=total_files, leave=False) as pbar:
            for pos, object_list in enumerate(lists_of_files):
                command_list = " ".join([i[0] for i in object_list])
                output = os.path.join(self.workdir, f"sorted.{pos}.split")
                args = sort_command + command_list
                command = f'/bin/bash -c "{args} | lz4 -3 -q >{output}"'
                status = os.system(command)
                if status != 0:
                    print(f"{file_type} sorting failed\nInterrupting database load...")
                    sys.exit()
                pbar.update(len(object_list))

        # WARNING: we are technically limited by the file descriptor limit (1024), which should be equivalent to 1,024,000 files.
        sorted_files = " ".join([f"<(lz4cat -q --rm {i})" for i in iglob(f"{self.workdir}/*.split")])
        if file_type == "words":
            output_file = os.path.join(self.workdir, "all_words_sorted.lz4")
            command = f'/bin/bash -c "{sort_command} -b --compress-program=lz4 {sorted_files} | lz4 -q > {output_file}"'
        else:
            output_file = os.path.join(self.workdir, "all_toms_sorted")
            command = f'/bin/bash -c "{sort_command} {sorted_files} > {output_file}"'
        if verbose is True:
            print(f"{time.ctime()}: Merging all merged sorted files (this may take a while)...", flush=True, end=" ")

        status = os.system(command)
        if status != 0:
            print(f"{file_type} sorting failed\nInterrupting database load...")
            sys.exit()
        print("done.", flush=True)

        for sorted_file in os.scandir(self.workdir):
            if sorted_file.name.endswith(".split"):
                os.system(f"rm {sorted_file.name}")

    def analyze(self):
        """Create inverted index"""
        print("\n### Create inverted index ###", flush=True)
        print(self.omax, flush=True)
        vl = [max(int(math.ceil(math.log(float(x) + 1.0, 2.0))), 1) if x > 0 else 1 for x in self.omax]
        print(vl, flush=True)
        width = sum(x for x in vl)
        print(str(width) + " bits wide.", flush=True)

        hits_per_block = (BLOCKSIZE * 8) // width
        freq1 = INDEX_CUTOFF
        freq2 = 0
        offset = 0

        # Generate frequency table
        os.system(
            f'/bin/bash -c "cut -f 2 <(lz4cat {self.workdir}/all_words_sorted.lz4) | uniq -c | LANG=C sort -S 25% -rn -k 1,1> {self.workdir}/all_frequencies"'
        )

        # now scan over the frequency table to figure out how wide (in bits) the frequency fields are,
        # and how large the block file will be.
        with open(self.workdir + "/all_frequencies") as frequencies:
            for line in frequencies:
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
        with open(self.workdir + "dbspecs4.h", "w") as dbs:
            print("#define FIELDS 9", file=dbs)
            print("#define TYPE_LENGTH 1", file=dbs)
            print("#define BLK_SIZE " + str(BLOCKSIZE), file=dbs)
            print("#define FREQ1_LENGTH " + str(freq1_l), file=dbs)
            print("#define FREQ2_LENGTH " + str(freq2_l), file=dbs)
            print("#define OFFST_LENGTH " + str(offset_l), file=dbs)
            print("#define NEGATIVES {0,0,0,0,0,0,0,0,0}", file=dbs)
            print("#define DEPENDENCIES {-1,0,1,2,3,4,5,0,0}", file=dbs)
            print("#define BITLENGTHS {%s}" % ",".join(str(i) for i in vl), file=dbs)
        print("%s: analysis done" % time.ctime())
        os.system(
            f'/bin/bash -c "lz4cat {self.workdir}/all_words_sorted.lz4 | pack4 {self.workdir}/dbspecs4.h"',
        )
        print("%s: all indices built. moving into place." % time.ctime())
        os.system("mv index " + self.destination + "/index")
        os.system("mv index.1 " + self.destination + "/index.1")

        print(f"{time.ctime()}: building word attribute index")
        with sqlite3.connect(f"{self.destination}/words.db") as conn:
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE words (word text, word_object blob)")
            cursor.execute("CREATE INDEX word_index ON words (word)")
            current_word = None
            word_objects = []
            for line in lz4.frame.open(f"{self.workdir}/all_words_sorted.lz4"):
                _, word, philo_id, word_object = line.decode("utf8").rstrip().split("\t", 3)
                word_attrib = loads(word_object)
                Loader.word_attributes.update(word_attrib.keys())
                split_philo_id = [int(i) for i in philo_id.split()]
                philo_id = split_philo_id[:6] + [split_philo_id[-1]] + split_philo_id[6:-1]
                word_attrib["philo_id"] = philo_id
                if word is not None and word != current_word:
                    cursor.execute(
                        "INSERT INTO words VALUES (?, ?)",
                        (current_word, lz4.frame.compress(msgpack.dumps(word_objects), compression_level=6)),
                    )
                    word_objects = []
                word_objects.append(word_attrib)
                current_word = word
            if word_objects:
                cursor.execute(
                    "INSERT INTO words VALUES (?, ?)",
                    (current_word, lz4.frame.compress(msgpack.dumps(word_objects))),
                )

    def setup_sql_load(self, verbose=True):
        """Setup SQLite DB creation"""
        for table in self.tables:
            if table == "pages":
                file_in = self.destination + "/WORK/all_pages"
                indices = [("philo_id",)]
                depth = 9
            elif table == "toms":
                file_in = self.destination + "/WORK/all_toms_sorted"
                indices = (
                    [("philo_type",), ("philo_id",), ("img",)]
                    + Loader.metadata_fields
                    + [(f"philo_{philo_type}_id",) for philo_type in ["doc", "div1", "div2", "div3", "para"]]
                )
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
            if table == "sentences":
                db_destination = os.path.join(self.destination, "toms.db")
                post_filter = make_sentences_table(self.destination, db_destination)
            else:
                post_filter = make_sql_table(table, file_in, indices=indices, depth=depth, verbose=verbose)
            self.post_filters.insert(0, post_filter)

    @classmethod
    def post_processing(cls, *extra_filters, verbose=True):
        """Run important post-parsing functions for frequencies and word normalization"""
        if verbose is True:
            print("\n### Storing in database ###")
        for f in cls.post_filters:
            if f.__name__ == "metadata_frequencies":
                cls.metadata_fields_not_found = f(cls)
            else:
                f(cls)
        if extra_filters:
            print("Running the following additional filters:")
            for f in extra_filters:
                print(f.__name__ + "...", end=" ")
                f(cls)

    def finish(self):
        """Write important runtime information to the database directory"""
        print("\n### Finishing up ###")
        os.mkdir(self.destination + "/src/")
        os.mkdir(self.destination + "/hitlists/")
        os.chmod(self.destination + "/hitlists/", 0o777)
        os.chmod(os.path.join(self.destination, "TEXT"), 0o775)
        os.system("mv dbspecs4.h ../src/dbspecs4.h")

        # Make data directory inaccessible from the outside
        fh = open(self.destination + "/.htaccess", "w")
        fh.write("deny from all")
        fh.close()

        self.write_db_config()
        if self.predefined_web_config is False:
            self.write_web_config()
        if self.debug is False:
            os.system(f"rm -rf {self.workdir}")

        print("Building Web Client Application...", end=" ", flush=True)
        os.chdir(self.web_app_dir)
        with open(os.path.join(self.web_app_dir, "appConfig.json"), "w") as app_config:
            dump({"dbUrl": ""}, app_config)
        os.system(
            f"cd {self.web_app_dir}; npm install > {self.web_app_dir}/web_app_build.log 2>&1 && npm run build >> {self.web_app_dir}/web_app_build.log 2>&1"
        )
        print("done.")

    def write_db_config(self):
        """Write local variables used by libphilo"""
        filename = self.destination + "/db.locals.py"
        metadata = [i for i in Loader.metadata_fields if i not in Loader.metadata_fields_not_found]
        metadata_sql_types = {
            "philo_type": "text",
            "philo_id": "text",
            "philo_name": "text",
            "philo_seq": "text",
            "year": "int",
            **{
                field: self.parser_config["metadata_sql_types"].get(field, "text")
                for field in metadata
                if field != "year"
            },
        }
        db_values = {
            "metadata_fields": metadata,
            "metadata_hierarchy": Loader.metadata_hierarchy,
            "metadata_types": Loader.metadata_types,
            "normalized_fields": self.normalized_fields,
            "debug": self.debug,
            "ascii_conversion": Loader.ascii_conversion,
            "metadata_sql_types": metadata_sql_types,
        }
        db_values["token_regex"] = self.token_regex
        db_values["default_object_level"] = self.default_object_level
        db_values["word_attributes"] = [
            i
            for i in Loader.word_attributes
            if i
            not in (
                "start_byte",
                "div3_ancestor",
                "div2_ancestor",
                "parent",
                "end_byte",
                "para_ancestor",
                "div1_ancestor",
                "doc_ancestor",
                "xml_id",
            )
        ]
        db_config = MakeDBConfig(filename, **db_values)
        with open(filename, "w") as db_file:
            try:
                print(format_str(str(db_config), mode=FileMode()), file=db_file)
            except:
                print(str(db_config))
                exit()
        print("wrote database info to %s." % (filename))

    def write_web_config(self):
        """Write configuration variables for the Web application"""
        dbname = os.path.basename(os.path.dirname(self.destination.rstrip("/")))
        metadata = [
            i
            for i in Loader.metadata_fields
            if i not in self.metadata_fields_not_found and not i.startswith("philo_") and i != "filename"
        ]
        config_values = {
            "dbname": dbname,
            "metadata": metadata,
            "facets": metadata,
        }

        # Fetch search examples:
        search_examples = {}
        conn = sqlite3.connect(self.destination + "/toms.db")
        conn.text_factory = str
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        for field in metadata:
            object_type = Loader.metadata_types[field]
            try:
                if object_type != "div":
                    cursor.execute(
                        f'select {field} from toms where philo_type="{object_type}" and {field} !="" limit 1'
                    )
                else:
                    cursor.execute(
                        f'select {field} from toms where philo_type="div1" or philo_type="div2" or philo_type="div3" and {field} !="" limit 1'
                    )
            except sqlite3.OperationalError:
                continue
            try:
                search_examples[field] = cursor.fetchone()[0]
            except (TypeError, AttributeError):
                continue
        config_values["search_examples"] = search_examples

        config_values["metadata_input_style"] = {}
        for field in metadata:
            if field == "year":
                config_values["metadata_input_style"][field] = "int"
            elif field not in self.parser_config["metadata_sql_types"]:
                config_values["metadata_input_style"][field] = "text"
            elif self.parser_config["metadata_sql_types"][field] == "int":
                config_values["metadata_input_style"][field] = "int"
            elif self.parser_config["metadata_sql_types"][field] == "date":
                config_values["metadata_input_style"][field] = "date"

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

        # Find default start and end dates for times series
        try:
            cursor.execute("SELECT min(year), max(year) FROM toms")
            min_year, max_year = cursor.fetchone()
            try:
                start_date = int(min_year)
            except TypeError:
                start_date = 0
            try:
                end_date = int(max_year)
            except TypeError:
                end_date = 2100
            config_values["time_series_start_end_date"] = {"start_date": start_date, "end_date": end_date}
        except sqlite3.OperationalError:  # no year field present
            config_values["time_series_start_end_date"] = {"start_date": "", "end_date": ""}

        config_values["ascii_conversion"] = Loader.ascii_conversion

        filename = self.destination + "/web_config.cfg"
        web_config = MakeWebConfig(filename, **config_values)
        with open(os.path.join(filename), "w") as output_file:
            print(format_str(str(web_config), mode=FileMode()), file=output_file)
        print(f"wrote Web application info to {filename}")


def shellquote(s):
    """Quote shell commands"""
    return "'" + s.replace("'", "'\\''") + "'"


def setup_db_dir(db_destination, web_app_dir, force_delete=False):
    """Setup database directory"""
    try:
        os.mkdir(db_destination)
    except OSError:
        if force_delete is True:  # useful to run db loads with nohup
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
        os.system("mkdir -p %s/custom_functions" % db_destination)
        os.system("touch %s/custom_functions/__init__.py" % db_destination)
