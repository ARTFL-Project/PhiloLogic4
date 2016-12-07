#!/usr/bin/env python
from __future__ import absolute_import
from __future__ import print_function
import six.moves.cPickle
import math
import os
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
from six.moves import zip
from six.moves import input

# Flush buffer output
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

sort_by_word = "-k 2,2"
sort_by_id = "-k 3,3n -k 4,4n -k 5,5n -k 6,6n -k 7,7n -k 8,8n -k 9,9n"
object_types = ['doc', 'div1', 'div2', 'div3', 'para', 'sent', 'word']

blocksize = 2048  # index block size.  Don't alter.
index_cutoff = 10  # index frequency cutoff.  Don't alter.

DEFAULT_TABLES = ('toms', 'pages', 'refs', 'graphics', 'lines', 'words')

DEFAULT_OBJECT_LEVEL = "doc"

NAVIGABLE_OBJECTS = ('doc', 'div1', 'div2', 'div3', 'para')

ParserOptions = ["parser_factory", "doc_xpaths", "token_regex", "tag_to_obj_map", "metadata_to_parse", "suppress_tags",
                 "load_filters", "break_apost", "chars_not_to_index", "break_sent_in_line_group", "tag_exceptions",
                 "join_hyphen_in_words", "unicode_word_breakers", "abbrev_expand", "long_word_limit",
                 "flatten_ligatures", "sentence_breakers"]


class Loader(object):
    def __init__(self, **loader_options):
        self.omax = [1, 1, 1, 1, 1, 1, 1, 1, 1]
        self.parse_pool = None
        self.types = object_types
        self.tables = DEFAULT_TABLES
        self.sort_by_word = sort_by_word
        self.sort_by_id = sort_by_id

        self.debug = loader_options["debug"]
        self.default_object_level = loader_options["default_object_level"]
        self.post_filters = loader_options["post_filters"]
        self.filtered_words = loader_options["filtered_words"]
        self.token_regex = loader_options["token_regex"]

        self.parser_config = {}
        for option in ParserOptions:
            try:
                self.parser_config[option] = loader_options[option]
            except KeyError:  # option hasn't been set
                pass

        try:
            work_dir = os.path.join(loader_options["data_destination"], "WORK")
            os.stat(work_dir)
            self.destination = loader_options["data_destination"]
            self.is_new = False
        except OSError:
            self.setup_dir(loader_options["data_destination"])  # TO TEST!!!!
            with open(os.path.join(loader_options["data_destination"], "load_config.py"), "w") as l:
                print("#!/usr/bin/env python", file=l)
                print('"""This is a dump of the configuration used to load this database,', file=l)
                print('including non-configurable options. You can use this file to reload', file=l)
                print('the current database using the -l flag. See load documentation for more details"""\n\n', file=l)
                for option in ["default_object_level", "navigable_objects", "plain_text_obj", "doc_xpaths", "tag_to_obj_map",
                               "metadata_to_parse", "token_regex", "filtered_words_list", "sort_order", "suppress_tags",
                               "break_apost", "chars_not_to_index", "break_sent_in_line_group", "tag_exceptions",
                               "unicode_word_breakers", "long_word_limit", "join_hyphen_in_words", "abbrev_expand",
                               "flatten_ligatures"]:
                    if option in loader_options:
                        print("%s = %s" % (option, repr(loader_options[option])), file=l)
            self.is_new = True

        if "web_config" in loader_options:
            web_config_path = os.path.join(loader_options["data_destination"], "web_config.cfg")
            print("\nSaving predefined web_config.cfg file to %s..." % web_config_path)
            with open(web_config_path, "w") as w:
                w.write(loader_options["web_config"])
            self.predefined_web_config = True
        else:
            self.predefined_web_config = False

        self.metadata_fields = []
        self.metadata_hierarchy = []
        self.metadata_types = {}
        self.normalized_fields = []
        self.metadata_fields_not_found = []

    def setup_dir(self, path):
        os.system("mkdir -p %s" % path)
        self.workdir = path + "/WORK/"
        self.textdir = path + "/TEXT/"
        os.mkdir(self.workdir)
        os.mkdir(self.textdir)
        self.destination = path

    def add_files(self, files):
        """Copy files to database directory"""
        print("\nCopying files to database directory...", end=' ')
        self.filenames = []
        for f in files:
            new_file_path = os.path.join(self.textdir, os.path.basename(f).replace(" ", "_").replace("'", "_"))
            shutil.copy(f, new_file_path)
            os.chmod(new_file_path, 775)
            self.filenames.append(f)
        print("done.\n")

    def list_files(self):
        return os.listdir(self.textdir)

    def parse_bibliography_file(self, bibliography_file, sort_by_field, reverse_sort=True):
        load_metadata = []
        files = set(self.list_files())
        with open(bibliography_file) as input_file:
            metadata_fields = input_file.readline().strip().split("\t")
            filename_index = metadata_fields.index("filename")
            for line in input_file:
                file_metadata = {}
                values = line.split("\t")
                if values[filename_index] not in files:
                    continue
                for pos, field in enumerate(metadata_fields):
                    file_metadata[field] = values[pos]
                load_metadata.append(file_metadata)
        print("Sorting files by the following metadata fields: %s..." % ", ".join([i for i in sort_by_field]), end=' ')

        def make_sort_key(d):
            key = [d.get(f, "") for f in sort_by_field]
            return key

        load_metadata.sort(key=make_sort_key, reverse=reverse_sort)
        print("done.")
        return load_metadata

    def parse_tei_header(self):
        load_metadata = []
        metadata_xpaths = self.parser_config["doc_xpaths"]
        deleted_files = []
        for f in self.list_files():
            data = {"filename": f}
            header = ""
            file_content = "".join(open(self.textdir + f).readlines())
            try:
                start_header_index = re.search(r'<teiheader', file_content, re.I).start()
                end_header_index = re.search(r'</teiheader', file_content, re.I).start()
            except AttributeError:  # tag not found
                deleted_files.append(f)
                continue
            header = file_content[start_header_index:end_header_index]
            if self.debug:
                print("parsing %s header..." % f)
            parser = etree.XMLParser(recover=True)
            try:
                tree = etree.fromstring(header, parser)
                trimmed_metadata_xpaths = []
                for field in metadata_xpaths:
                    for xpath in metadata_xpaths[field]:
                        attr_pattern_match = re.search(r"@([^\/\[\]]+)$", xpath)
                        if attr_pattern_match:
                            xp_prefix = xpath[:attr_pattern_match.start(0)]
                            attr_name = attr_pattern_match.group(1)
                            elements = tree.findall(xp_prefix)
                            for el in elements:
                                if el is not None and el.get(attr_name, ""):
                                    data[field] = el.get(attr_name, "").encode("utf-8")
                                    break
                        else:
                            el = tree.find(xpath)
                            if el is not None and el.text is not None:
                                data[field] = el.text.encode("utf-8")
                                break
                trimmed_metadata_xpaths = [
                    (metadata_type, xpath, field)
                    for metadata_type in ["div", "para", "sent", "word", "page"]
                    if metadata_type in metadata_xpaths for field in metadata_xpaths[metadata_type]
                    for xpath in metadata_xpaths[metadata_type][field]
                ]
                data = self.create_year_field(data)
                if self.debug:
                    print(pretty_print(data))
                data["options"] = {"metadata_xpaths": trimmed_metadata_xpaths}
                load_metadata.append(data)
            except etree.XMLSyntaxError:
                deleted_files.append(f)
        if deleted_files:
            for f in deleted_files:
                print("%s has no valid TEI header or contains invalid data: removing from database load..." % f)
        return load_metadata

    def parse_dc_header(self):
        load_metadata = []
        for filename in self.list_files():
            data = {}
            fn = self.textdir + filename
            header = ""
            with open(fn) as fh:
                for line in fh:
                    start_scan = re.search("<teiheader>|<temphead>|<head>", line, re.IGNORECASE)
                    end_scan = re.search("</teiheader>|<\/?temphead>|</head>", line, re.IGNORECASE)
                    if start_scan:
                        header += line[start_scan.start():]
                    elif end_scan:
                        header += line[:end_scan.end()]
                        break
                    else:
                        header += line
            matches = re.findall('<meta name="DC\.([^"]+)" content="([^"]+)"', header)
            if not matches:
                matches = re.findall('<dc:([^>]+)>([^>]+)>', header)
            for metadata_name, metadata_value in matches:
                metadata_value = metadata_value
                metadata_value = convert_entities(metadata_value.decode('utf-8')).encode('utf-8')
                metadata_name = metadata_name.lower()
                data[metadata_name] = metadata_value
            data["filename"] = filename  # place at the end in case the value was in the header
            data = self.create_year_field(data)
            if self.debug:
                print(pretty_print(data))
            load_metadata.append(data)
        return load_metadata

    def create_year_field(self, metadata):
        year_finder = re.compile(r'^.*?(\d{4}).*')
        earliest_year = 2500
        for field in ["date", "create_date", "pub_date", "period"]:
            if field in metadata:
                year_match = year_finder.search(metadata[field])
                if year_match:
                    year = int(year_match.groups()[0])
                    if year < earliest_year:
                        earliest_year = year
        if earliest_year != 2500:
            metadata["year"] = str(earliest_year)
        return metadata

    def parse_metadata(self, sort_by_field, reverse_sort=False, header="tei"):
        """Parsing metadata fields in TEI or Dublin Core headers"""
        print("### Parsing metadata ###")
        print("%s: Parsing metadata in %d files..." % (time.ctime(), len(self.list_files())))
        if header == "tei":
            load_metadata = self.parse_tei_header()
        elif header == "dc":
            load_metadata = self.parse_dc_header()

        print("%s: Sorting files by the following metadata fields: %s..." % (time.ctime(),
                                                                             ", ".join([i for i in sort_by_field])), end=' ')

        self.sort_order = sort_by_field  # to be used for the sort by concordance biblio key in web config
        if sort_by_field:
            return sort_list(load_metadata, sort_by_field)
        else:
            sorted_load_metadata = []
            for filename in self.filenames:
                for m in load_metadata:
                    if m["filename"] == filename:
                        sorted_load_metadata.append(m)
                        break
            return sorted_load_metadata

    def parse_files(self, max_workers, data_dicts=None):
        print("\n\n### Parsing files ###")
        os.chdir(self.workdir)  # questionable

        if not data_dicts:
            data_dicts = [{"filename": self.textdir + fn} for fn in self.list_files()]
            self.filequeue = [{"orig": os.path.abspath(x),
                               "name": os.path.basename(x),
                               "size": os.path.getsize(x),
                               "id": n + 1,
                               "options": {},
                               "newpath": self.textdir + os.path.basename(x),
                               "raw": self.workdir + os.path.basename(x) + ".raw",
                               "words": self.workdir + os.path.basename(x) + ".words.sorted",
                               "toms": self.workdir + os.path.basename(x) + ".toms",
                               "sortedtoms": self.workdir + os.path.basename(x) + ".toms.sorted",
                               "pages": self.workdir + os.path.basename(x) + ".pages",
                               "refs": self.workdir + os.path.basename(x) + ".refs",
                               "graphics": self.workdir + os.path.basename(x) + ".graphics",
                               "lines": self.workdir + os.path.basename(x) + ".lines",
                               "results": self.workdir + os.path.basename(x) + ".results"}
                              for n, x in enumerate(self.list_files())]

        else:
            self.filequeue = [{"orig": os.path.abspath(d["filename"]),
                               "name": os.path.basename(d["filename"]),
                               "size": os.path.getsize(self.textdir + (d["filename"])),
                               "id": n + 1,
                               "options": d["options"] if "options" in d else {},
                               "newpath": self.textdir + os.path.basename(d["filename"]),
                               "raw": self.workdir + os.path.basename(d["filename"]) + ".raw",
                               "words": self.workdir + os.path.basename(d["filename"]) + ".words.sorted",
                               "toms": self.workdir + os.path.basename(d["filename"]) + ".toms",
                               "sortedtoms": self.workdir + os.path.basename(d["filename"]) + ".toms.sorted",
                               "pages": self.workdir + os.path.basename(d["filename"]) + ".pages",
                               "refs": self.workdir + os.path.basename(d["filename"]) + ".refs",
                               "graphics": self.workdir + os.path.basename(d["filename"]) + ".graphics",
                               "lines": self.workdir + os.path.basename(d["filename"]) + ".lines",
                               "results": self.workdir + os.path.basename(d["filename"]) + ".results"}
                              for n, d in enumerate(data_dicts)]

        self.loaded_files = self.filequeue[:]

        self.metadata_hierarchy.append([])
        # Adding in doc level metadata
        for d in data_dicts:
            for k in d.keys():
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

        print("%s: parsing %d files." % (time.ctime(), len(self.filequeue)))
        procs = {}
        workers = 0
        done = 0
        total = len(self.filequeue)

        while done < total:
            while self.filequeue and workers < max_workers:
                # we want to have up to max_workers processes going at once.

                text = self.filequeue.pop(0)  # parent and child will both know the relevant filenames
                metadata = data_dicts.pop(0)
                options = text["options"]
                if "options" in metadata:  # cleanup, should do above.
                    del metadata["options"]

                pid = os.fork()  # fork returns 0 to the child, the id of the child to the parent.
                # so pid is true in parent, false in child.

                if pid:  # the parent process tracks the child
                    procs[pid] = text["results"]  # we need to know where to grab the results from.
                    workers += 1
                    # loops to create up to max_workers children at any one time.

                if not pid:  # the child process parses then exits.

                    i = open(text["newpath"], "r", )
                    o = open(text["raw"], "w", )  # only print out raw utf-8, so we don't need a codec layer now.
                    print("%s: parsing %d : %s" % (time.ctime(), text["id"], text["name"]))

                    if "parser_factory" not in options:
                        options["parser_factory"] = self.parser_config["parser_factory"]
                    parser_factory = options["parser_factory"]
                    del options["parser_factory"]

                    if "load_filters" not in options:
                        options["load_filters"] = self.parser_config["load_filters"]
                    filters = options["load_filters"]
                    del options["load_filters"]

                    for option in ["token_regex", "suppress_tags", "break_apost", "chars_not_to_index",
                                   "break_sent_in_line_group", "tag_exceptions", "join_hyphen_in_words",
                                   "unicode_word_breakers", "abbrev_expand", "long_word_limit", "flatten_ligatures",
                                   "sentence_breakers"]:
                        try:
                            options[option] = self.parser_config[option]
                        except KeyError:  # option hasn't been set
                            pass

                    parser = parser_factory(o,
                                            text["id"],
                                            text["size"],
                                            known_metadata=metadata,
                                            tag_to_obj_map=self.parser_config["tag_to_obj_map"],
                                            metadata_to_parse=self.parser_config["metadata_to_parse"],
                                            filtered_words=self.filtered_words,
                                            **options)
                    try:
                        parser.parse(i)
                    except RuntimeError:
                        print("parse failure: XML stack explosion : %s" % [el.tag for el in parser.stack], file=sys.stderr)
                        exit(1)
                    i.close()
                    o.close()

                    for f in filters:
                        f(self, text)

                    os.system('gzip -c -5 %s > %s' % (text['raw'], text['raw'] + '.gz'))
                    os.system('rm %s' % text['raw'])
                    os.system('gzip -c -5 %s > %s' % (text['words'], text['words'] + '.gz'))
                    os.system('rm %s' % text['words'])

                    exit()

            # if we are at max_workers children, or we're out of texts, the parent waits for any child to exit.
            pid, status = os.waitpid(0,
                                     0)  # this hangs until any one child finishes.  should check status for problems.
            if status:
                print("parsing failed for %s" % procs[pid])
                exit()
            done += 1
            workers -= 1
            with open(procs[pid]) as proc_fh:
                vec = six.moves.cPickle.load(proc_fh)  # load in the results from the child's parsework() function.
            # print vec
            self.omax = [max(x, y) for x, y in zip(vec, self.omax)]
        print("%s: done parsing" % time.ctime())

    def merge_objects(self, file_num=500):
        print("\n### Merge parser output ###")

        # Make all sorting happen in workdir rather than /tmp
        os.system('export TMPDIR=%s/' % self.workdir)

        print("%s: sorting words" % time.ctime())
        words_status = self.merge_files("words")
        print("%s: word sort returned %d" % (time.ctime(), words_status))

        if "words" in self.tables:
            print("%s: concatenating document-order words file..." % time.ctime(), end=' ')
            for d in self.loaded_files:
                os.system('gunzip -c %s | egrep -a "^word" >> all_words_ordered' % (d["raw"] + ".gz"))
            print("done")

        print("%s: sorting objects" % time.ctime())
        toms_status = self.merge_files("toms")
        print("%s: object sort returned %d" % (time.ctime(), toms_status))
        if not self.debug:
            for toms_file in glob(self.workdir + "/*toms.sorted"):
                os.system('rm %s' % toms_file)

        print("%s: joining pages" % time.ctime())
        for page_file in glob(self.workdir + "/*pages"):
            os.system("cat %s >> %s/all_pages" % (page_file, self.workdir))
            if not self.debug:
                os.system("rm %s" % page_file)

        print("%s: joining references" % time.ctime())
        for ref_file in glob(self.workdir + "/*refs"):
            os.system("cat %s >> %s/all_refs" % (ref_file, self.workdir))
            if not self.debug:
                os.system("rm %s" % ref_file)

        print("%s: joining graphics" % time.ctime())
        for graphic_file in glob(self.workdir + "/*graphics"):
            os.system("cat %s >> %s/all_graphics" % (graphic_file, self.workdir))
            if not self.debug:
                os.system("rm %s" % graphic_file)

        print("%s: joining lines" % time.ctime())
        for line_file in glob(self.workdir + "/*lines"):
            os.system("cat %s >> %s/all_lines" % (line_file, self.workdir))
            if not self.debug:
                os.system("rm %s" % line_file)

    def merge_files(self, file_type, file_num=500):
        """This function runs a multi-stage merge sort on words
        Since PhilLogic can potentially merge thousands of files, we need to split
        the sorting stage into multiple steps to avoid running out of file descriptors"""
        lists_of_files = []
        files = []
        if file_type == "words":
            suffix = "/*words.sorted.gz"
            open_file_command = "gunzip -c"
            sort_command = "LANG=C sort -m %s %s " % (sort_by_word, sort_by_id)
            all_object_file = "/all_words_sorted.gz"
        elif file_type == "toms":
            suffix = "/*.toms.sorted"
            open_file_command = "cat"
            sort_command = "LANG=C sort -m %s " % sort_by_id
            all_object_file = "/all_toms_sorted.gz"

        # First we split the sort workload into chunks of 100 (default defined in the file_num keyword)
        for f in glob(self.workdir + suffix):
            f = os.path.basename(f)
            files.append(('<(%s %s)' % (open_file_command, f), self.workdir + '/' + f))
            if len(files) == file_num:
                lists_of_files.append(files)
                files = []
        if len(files):
            lists_of_files.append(files)

        # Then we run the merge sort on each chunk of 500 files and compress the result
        print("%s: Merging %s in batches of %d..." % (time.ctime(), file_type, file_num))
        already_merged = 0
        os.system("touch %s" % self.workdir + "/sorted.init")
        last_sort_file = self.workdir + "/sorted.init"
        for pos, object_list in enumerate(lists_of_files):
            command_list = ' '.join([i[0] for i in object_list])
            file_list = ' '.join([i[1] for i in object_list])
            output = self.workdir + "sorted.%d.split" % pos
            args = sort_command + command_list
            command = '/bin/bash -c "%s | %s - <(gunzip -c %s 2> /dev/null) | gzip -c -5 > %s"' % (
                args, sort_command, last_sort_file, output)
            status = os.system(command)
            if status != 0:
                print("%s sorting failed\nInterrupting database load..." % file_type)
                sys.exit()
            already_merged += len(object_list)
            os.system("rm %s" % last_sort_file)
            last_sort_file = output

            print("%s: %d files merged..." % (time.ctime(), already_merged))
            if not self.debug:
                os.system("rm %s" % file_list)
        status = os.system('mv %s %s' % (last_sort_file, self.workdir + all_object_file))
        if file_type == "toms":
            os.system("gunzip -d %s" % self.workdir + all_object_file)

        if status != 0:
            print("%s sorting failed\nInterrupting database load..." % file_type)
            sys.exit()
        return status

    def analyze(self):
        print("\n### Create inverted index ###")
        print(self.omax)
        vl = [max(int(math.ceil(math.log(float(x) + 1.0, 2.0))), 1) if x > 0 else 1 for x in self.omax]
        print(vl)
        width = sum(x for x in vl)
        print(str(width) + " bits wide.")

        hits_per_block = (blocksize * 8) // width
        freq1 = index_cutoff
        freq2 = 0
        offset = 0

        # unix one-liner for a frequency table
        os.system('/bin/bash -c "cut -f 2 <(gunzip -c %s) | uniq -c | LANG=C sort -rn -k 1,1> %s"' %
                  (self.workdir + "/all_words_sorted.gz", self.workdir + "/all_frequencies"))

        # now scan over the frequency table to figure out how wide (in bits) the frequency fields are,
        # and how large the block file will be.
        for line in open(self.workdir + "/all_frequencies"):
            f, word = line.rsplit(" ", 1)  # uniq -c pads output on the left side, so we split on the right.
            f = int(f)
            if f > freq2:
                freq2 = f
            if f < index_cutoff:
                pass  # low-frequency words don't go into the block-mode index.
            else:
                blocks = 1 + f // (hits_per_block + 1)  # high frequency words have at least one block.
                offset += blocks * blocksize

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
        print("#define BLK_SIZE " + str(blocksize), file=dbs)
        print("#define FREQ1_LENGTH " + str(freq1_l), file=dbs)
        print("#define FREQ2_LENGTH " + str(freq2_l), file=dbs)
        print("#define OFFST_LENGTH " + str(offset_l), file=dbs)
        print("#define NEGATIVES {0,0,0,0,0,0,0,0,0}", file=dbs)
        print("#define DEPENDENCIES {-1,0,1,2,3,4,5,0,0}", file=dbs)
        print("#define BITLENGTHS {%s}" % ",".join(str(i) for i in vl), file=dbs)
        dbs.close()
        print("%s: analysis done" % time.ctime())
        os.system('/bin/bash -c "gunzip -c ' + self.workdir + '/all_words_sorted.gz | pack4 ' + self.workdir +
                  'dbspecs4.h"')
        print("%s: all indices built. moving into place." % time.ctime())
        os.system("mv index " + self.destination + "/index")
        os.system("mv index.1 " + self.destination + "/index.1")
        # if self.clean:
        #    os.system('rm all_words_sorted')

    def setup_sql_load(self):
        for table in self.tables:
            if table == 'words':
                file_in = self.destination + '/WORK/all_words_ordered'
                indices = [("philo_name", ), ('philo_id', ), ('parent', ), ('start_byte', ), ('end_byte', )]
                depth = 7
            elif table == 'pages':
                file_in = self.destination + '/WORK/all_pages'
                indices = [("philo_id", )]
                depth = 9
            elif table == 'toms':
                file_in = self.destination + '/WORK/all_toms_sorted'
                indices = [('philo_type', ), ('philo_id', ), ('img', )] + self.metadata_fields
                depth = 7
            elif table == "refs":
                file_in = self.destination + '/WORK/all_refs'
                indices = [("parent", ), ("target", ), ("type", )]
                depth = 9
            elif table == "graphics":
                file_in = self.destination + '/WORK/all_graphics'
                indices = [("parent", ), ("philo_id", )]
                depth = 9
            elif table == "lines":
                file_in = self.destination + '/WORK/all_lines'
                indices = [("doc_id", "start_byte", "end_byte")]
                depth = 9
            post_filter = make_sql_table(table, file_in, indices=indices, depth=depth)
            self.post_filters.insert(0, post_filter)

    def post_processing(self, *extra_filters):
        """Run important post-parsing functions for frequencies and word normalization"""
        print('\n### Post-processing filters ###')
        for f in self.post_filters:
            f(self)

        if extra_filters:
            print('Running the following additional filters:')
            for f in extra_filters:
                print(f.__name__ + '...', end=' ')
                f(self)

    def finish(self):
        """Write important runtime information to the database directory"""
        print("\n### Finishing up ###")
        os.mkdir(self.destination + "/src/")
        os.mkdir(self.destination + "/hitlists/")
        os.chmod(self.destination + "/hitlists/", 0o777)
        os.system("mv dbspecs4.h ../src/dbspecs4.h")

        # Make data directory inaccessible from the outside
        fh = open(self.destination + "/.htaccess", 'w')
        fh.write('deny from all')
        fh.close()

        self.write_db_config()
        if self.predefined_web_config is False:
            self.write_web_config()

    def write_db_config(self):
        """ Write local variables used by libphilo"""
        filename = self.destination + "/db.locals.py"
        metadata = [i for i in self.metadata_fields if i not in self.metadata_fields_not_found]
        db_values = {'metadata_fields': metadata,
                     'metadata_hierarchy': self.metadata_hierarchy,
                     'metadata_types': self.metadata_types,
                     'normalized_fields': self.normalized_fields,
                     'debug': self.debug}
        db_values["token_regex"] = self.token_regex
        db_values["default_object_level"] = self.default_object_level
        db_config = MakeDBConfig(filename, **db_values)
        print(db_config, file=open(filename, 'w'))
        print("wrote database info to %s." % (filename))

    def write_web_config(self):
        """ Write configuration variables for the Web application"""
        metadata = [i for i in self.metadata_fields if i not in self.metadata_fields_not_found]
        config_values = {'dbname': os.path.basename(re.sub("/data/?$", "", self.destination)),
                         'metadata': metadata,
                         'facets': metadata}
        # Fetch search examples:
        search_examples = {}
        conn = sqlite3.connect(self.destination + '/toms.db')
        conn.text_factory = str
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        for field in metadata:
            object_type = self.metadata_types[field]
            try:
                if object_type != 'div':
                    c.execute('select %s from toms where philo_type="%s" and %s!="" limit 1' %
                              (field, object_type, field))
                else:
                    c.execute(
                        'select %s from toms where philo_type="div1" or philo_type="div2" or philo_type="div3" and %s!="" limit 1'
                        % (field, field))
            except sqlite3.OperationalError:
                continue
            try:
                search_examples[field] = c.fetchone()[0].decode('utf-8', 'ignore')
            except (TypeError, AttributeError):
                continue
        config_values['search_examples'] = search_examples

        config_values["metadata_input_style"] = dict([(f, "text") for f in metadata])

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
        print(web_config, file=open(filename, 'w'))
        print("wrote Web application info to %s." % (filename))


def shellquote(s):
    return "'" + s.replace("'", "'\\''") + "'"


def setup_db_dir(db_destination, web_app_dir, force_delete=False):
    try:
        os.mkdir(db_destination)
    except OSError:
        if force_delete:  # useful to run db loads with nohup
            os.system('rm -rf %s' % db_destination)
            os.mkdir(db_destination)
        else:
            print("The database folder could not be created at %s" % db_destination)
            print("Do you want to delete this database? Yes/No")
            choice = input().lower()
            if choice.startswith('y'):
                os.system('rm -rf %s' % db_destination)
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
