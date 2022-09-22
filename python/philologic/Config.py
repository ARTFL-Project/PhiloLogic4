#!/usr/bin/env python3
"""Configuration module"""

import os
import sys

import orjson as json
from philologic.utils import pretty_print

CITATIONS = {
    "author": {
        "field": "author",
        "object_level": "doc",
        "prefix": "",
        "suffix": "",
        "link": True,
        "style": {"font-variant": "small-caps"},
    },
    "title": {
        "field": "title",
        "object_level": "doc",
        "prefix": "",
        "suffix": "",
        "link": True,
        "style": {"font-variant": "small-caps", "font-style": "italic", "font-weight": 700},
    },
    "year": {
        "field": "year",
        "object_level": "doc",
        "prefix": "",
        "suffix": "",
        "link": False,
        "style": {},
    },
    "pub_place": {
        "field": "pub_place",
        "object_level": "doc",
        "prefix": "",
        "suffix": "",
        "link": False,
        "style": {},
    },
    "publisher": {
        "field": "publisher",
        "object_level": "doc",
        "prefix": "",
        "suffix": "",
        "link": False,
        "style": {},
    },
    "collection": {
        "field": "collection",
        "object_level": "doc",
        "prefix": "",
        "suffix": ",&nbsp;",
        "link": False,
        "style": {},
    },
    "div1_head": {
        "field": "head",
        "object_level": "div1",
        "prefix": "",
        "suffix": "",
        "link": True,
        "style": {"font-variant": "small-caps"},
    },
    "div2_head": {
        "field": "head",
        "object_level": "div2",
        "prefix": "",
        "suffix": "",
        "link": True,
        "style": {"font-variant": "small-caps"},
    },
    "div3_head": {
        "field": "head",
        "object_level": "div3",
        "prefix": "",
        "suffix": "",
        "link": True,
        "style": {"font-variant": "small-caps"},
    },
    "div1_date": {
        "field": "div_date",
        "object_level": "div1",
        "prefix": "",
        "suffix": "",
        "link": False,
        "style": {},
    },
    "div2_date": {
        "field": "div_date",
        "object_level": "div2",
        "prefix": "",
        "suffix": "",
        "link": False,
        "style": {},
    },
    "div3_date": {
        "field": "div_date",
        "object_level": "div3",
        "prefix": "",
        "suffix": "",
        "link": False,
        "style": {},
    },
    "speaker": {
        "field": "speaker",
        "object_level": "para",
        "prefix": "",
        "suffix": "",
        "link": True,
        "style": {"font-variant": "small-caps"},
    },
    "resp": {
        "field": "resp",
        "object_level": "para",
        "prefix": "",
        "suffix": "",
        "link": True,
        "style": {"font-variant": "small-caps"},
    },
    "page": {
        "style": {},
        "suffix": "",
        "object_level": "page",
        "field": "n",
        "prefix": "page ",
        "link": True,
    },
}

DB_LOCALS_DEFAULTS = {
    "metadata_fields": {"value": [], "comment": ""},
    "metadata_hierarchy": {"value": [[]], "comment": ""},
    "metadata_types": {"value": {}, "comment": ""},
    "ascii_conversion": {
        "value": True,
        "comment": "\n".join(
            [
                "# This defines whether text and metadata were converted to an ASCII representation",
                "# Don't change this value post-database load.",
            ]
        ),
    },
    "normalized_fields": {"value": [], "comment": ""},
    "default_object_level": {
        "value": "doc",
        "comment": "# This defines the default navigation element in your database",
    },
    "lowercase_index": {
        "value": True,
        "comment": "# This defines whether all terms in the index have been lowercased. If so, input searches will be lowercased",
    },
    "debug": {
        "value": False,
        "comment": "# If set to True, this enabled debugging messages to be printed out to the Apache error log",
    },
    "secret": {
        "value": "",
        "comment": "# The secret value is a random string to be used to generate a secure cookie for access control. The string value can be anything.",
    },
}
DB_LOCALS_HEADER = """
   #########################################################\n
   #### Database configuration options for PhiloLogic4 #####\n
   #########################################################\n
   #### All variables must be in valid Python syntax #######\n
   #########################################################\n
   #### Edit with extra care: an invalid          ##########\n
   #### configuration could break your database.  ##########\n
   #########################################################\n\n\n
"""

WEB_CONFIG_DEFAULTS = {
    "dbname": {
        "value": "noname",
        "comment": "\n".join(["# The dbname variable is the title name in the HTML header"]),
    },
    "access_control": {
        "value": False,
        "comment": "\n".join(
            [
                "# Configure access control with True or False.",
                "# Note that if you want access control, you have to provide a logins.txt file inside your /data directory,",
                "# otherwise access will remain open.",
            ]
        ),
    },
    "access_file": {
        "value": "",
        "comment": "\n".join(["# Location of access file which contains authorized/unauthorized IPs and domain names"]),
    },
    "link_to_home_page": {
        "value": "",
        "comment": "\n".join(
            [
                '# If set, link_to_home_page should be a string starting with "http://" pointing to a separate home page for the database'
            ]
        ),
    },
    "search_reports": {
        "value": ["concordance", "kwic", "aggregation", "collocation", "time_series"],
        "comment": "\n".join(
            [
                "# The search_reports variable sets which search report is viewable in the search form",
                "# Available reports are concordance, kwic, aggregation, collocation, and time_series",
            ]
        ),
    },
    "metadata": {
        "value": [],
        "comment": "\n".join(["# The metadata variable sets which metadata field is viewable in the search form"]),
    },
    "metadata_aliases": {
        "value": {},
        "comment": "\n".join(
            [
                "# The metadata_aliases variable allows to display a metadata variable under a different name in the HTML",
                "# For example, you could rename the who metadata to Speaker, and the create_date variable to Date like so:",
                "# metadata_aliases = {'who': 'Speaker', 'create_date', 'Date'}",
            ]
        ),
    },
    "metadata_input_style": {
        "value": {},
        "comment": "\n".join(
            [
                "# The metadata_input_style variable defines whether to use an text input field, a dropdown menu or checkboxes for any given",
                "# metadata field. All fields are set by default to text. Note that dropdowns only allow you to select one value, whereas checkboxes allow you to select more than one."
                '# If using a dropdown menu, you need to set it to "dropdown" and populate the metadata_choice_values variable. If using checkboxes, set to "checkboxes", and populate'
                "# the metadata_choice_values variable",
            ]
        ),
    },
    "metadata_choice_values": {
        "value": {},
        "comment": "\n".join(
            [
                "# The metadata_choice_values variable defines what values to display in the metadata dropdown. It defaults to an empty dict.",
                "# If no value is provided for a metadata field which has an input type of dropdown, no value will be displayed. You should",
                "# provide a list of strings with labels and values for metadata.",
                """# ex: {"title": [{"label": "Contrat Social", "value": "Du Contrat Social"}, {"label": "Emile", "value": "Emile, ou de l'éducation"}]}""",
            ]
        ),
    },
    "autocomplete": {
        "value": ["q"],
        "comment": "# The autocomplete variable determines which fields have autocomplete enabled. Note that the value 'q' is for term autocomplete",
    },
    "facets": {
        "value": [],
        "comment": "\n".join(
            [
                "# The facets variable sets which metadata field can be used as a facet",
                "# The object format is a list of metadata like the following: ['author', 'title', 'year'}",
                "# The dict key should describe what the facets will do, and the dict value, which has to be a list,",
                "# should list the metadata to be used for the frequency counts",
            ]
        ),
    },
    "words_facets": {
        "value": [],
        "comment": "\n".join(
            [
                "# The word_facets variable functions much like the facets variable, but describes metadata",
                "# attached to word or phrases results and stored in the words table. Experimental.",
            ]
        ),
    },
    "skip_table_of_contents": {
        "value": False,
        "comment": "\n".join(
            [
                "# If set to True, disable display of table of contents and go straight to the text. Useful when texts have no internal structure."
            ]
        ),
    },
    "concordance_length": {
        "value": 300,
        "comment": "\n".join(["# The concordance_length variable sets the length in bytes of each concordance result"]),
    },
    "search_examples": {
        "value": {},
        "comment": "\n".join(
            [
                "# The search_examples variable defines which examples should be provided for each searchable field in the search form.",
                "# If None is the value, or there are any missing examples, defaults will be generated at runtime by picking the first",
                "# result for any given field. If you wish to change these default values, you should configure them here like so:",
                '# search_examples = {"author": "Jean-Jacques Rousseau", "title": "Du contrat social"}',
            ]
        ),
    },
    "results_summary": {
        "value": [
            {
                "field": "author",
                "object_level": "doc",
            },
            {
                "field": "title",
                "object_level": "doc",
            },
        ],
        "comment": "# The results_summary variable determins which fields get stats displayed at the top of concordance/KWIC results.",
    },
    "stopwords": {
        "value": "",
        "comment": "\n".join(
            [
                "# The stopwords variable defines a file path containing a list of words (one word per line) used for filtering out words",
                "# in the collocation report. The file must be located in the defined path. If the file is not found,",
                "# no option for using a stopword list will be displayed in collocation searches.",
            ]
        ),
    },
    "citations": {
        "value": CITATIONS,
        "comment": "\n".join(
            [
                "# Define how individual metadata is displayed. The citations variable is reused by default for citations in individual reports.",
                "# You can define styling with a dictionary of valid CSS property/value such as those in the default values.",
                "# prefix and suffix keywords define what precedes and follows each field. You can use HTML for these strings.",
                "# The link key enables linking for that metadata field. It links to the table of contents for title and filename,",
                "# and to a regular query for all other metadata fields.",
            ]
        ),
    },
    "aggregation_config": {
        "value": [
            {
                "field": "author",
                "object_level": "doc",
                "break_up_field": "title",
                "field_citation": [CITATIONS["author"]],
                "break_up_field_citation": [
                    CITATIONS["title"],
                    CITATIONS["year"],
                    CITATIONS["pub_place"],
                    CITATIONS["publisher"],
                    CITATIONS["collection"],
                ],
            },
            {
                "field": "title",
                "object_level": "doc",
                "field_citation": [
                    CITATIONS["title"],
                    CITATIONS["year"],
                    CITATIONS["pub_place"],
                    CITATIONS["publisher"],
                    CITATIONS["collection"],
                ],
                "break_up_field": None,
                "break_up_field_citation": None,
            },
        ],
        "comment": "\n".join(
            [
                "# The aggregation_config variable drives the aggregation report: which fields can be used to group concordances,"
                "# and whether you can further break down these counts by a particular metadata field.",
            ]
        ),
    },
    "dictionary": {
        "value": False,
        "comment": "\n".join(
            [
                "# The dictionary variable enables a different search interface with the headword as a starting point. It is turned off by default"
            ]
        ),
    },
    "dictionary_bibliography": {
        "value": False,
        "comment": "\n".join(
            [
                "# The dictionary_bibliography variable enables a different a bibliography report where entries are displayed",
                "# in their entirety and grouped under the same title. It is turned off by default",
            ]
        ),
    },
    "dictionary_selection": {
        "value": False,
        "comment": "\n".join(
            [
                "# If set to True, this option creates a dropdown menu to select searching within only a single volume or title.",
                "# This replaces the title field in the search form.",
                "# You need to configure the dictionary_selection_options variable below to define your options.",
            ]
        ),
    },
    "dictionary_selection_options": {
        "value": [],
        "comment": "\n".join(
            [
                "# If dictionary_selection is set to True, you need to populate this variable as in the following:",
                """# [{"label": "DAF 1932", "title": "Dictionnaire de l'Académie Française 1932"}]""",
                "# Each volume is represented as an object containing the label which is displayed in the search form",
                "# and a title value which should either be the exact string stored in the SQL table, or an egrep expression",
                '# such as "Dictionnaire de Littre.*" if you wish to match more than one title.',
            ]
        ),
    },
    "landing_page_browsing": {
        "value": "default",
        "comment": "\n".join(
            [
                "# The landing_page_browsing variable defines what type of landing page. There are 3 built-in reports available: 'default',",
                "# 'dictionary' or 'simple'. You can otherwise supply a relative path to a custom HTML template. Note that this path is relative",
                "# to the database root. The only constraint for custom templates is that the HTML must be encapsulated inside a div",
            ]
        ),
    },
    "default_landing_page_browsing": {
        "value": [
            {
                "label": "Author",
                "group_by_field": "author",
                "display_count": True,
                "queries": ["A-D", "E-I", "J-M", "N-R", "S-Z"],
                "is_range": True,
                "citation": [CITATIONS["author"]],
            },
            {
                "label": "Title",
                "group_by_field": "title",
                "display_count": False,
                "queries": ["A-D", "E-I", "J-M", "N-R", "S-Z"],
                "is_range": True,
                "citation": [CITATIONS["author"], CITATIONS["title"], CITATIONS["year"]],
            },
        ],
        "comment": "\n".join(
            [
                "# The landing_page_browsing variable allows for configuration of navigation by metadata within the landing page.",
                "# You can choose any document-level metadata (such as author, title, date, genre...) for browsing",
                '# and define two different types of queries to group your data: ranges and exact matches, i.e. "A-D" or "Comedy".',
                "# You can define styling with a dictionary of valid CSS property/value such as those in the default values.",
                "# begin and end keywords define what precedes and follows each field. You can use HTML for these strings.",
            ]
        ),
    },
    "default_landing_page_display": {
        "value": {},
        "comment": "\n".join(
            [
                "# The default landing page display variable allows you to load content by default. It is configured",
                "# in the same way as default_landing_page_display objects except that you need to define just one",
                "# range (the one you wish to display) as a string, such as 'A-D'. An empty dict will disable the feature.",
            ]
        ),
    },
    "simple_landing_citation": {
        "value": [
            CITATIONS["author"],
            CITATIONS["title"],
            CITATIONS["year"],
            CITATIONS["pub_place"],
            CITATIONS["publisher"],
            CITATIONS["collection"],
        ],
        "comment": "\n".join(["# This variable defines the citation for the simple landing page."]),
    },
    "dico_letter_range": {
        "value": [
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
            "G",
            "H",
            "I",
            "J",
            "K",
            "L",
            "M",
            "N",
            "O",
            "P",
            "Q",
            "R",
            "S",
            "T",
            "U",
            "V",
            "W",
            "X",
            "Y",
            "Z",
        ],
        "comment": "\n".join(
            [
                "# If landing_page_browsing is set to dictionary, the dico_letter_range variable allows you to define set of letters corresponding to the first letter of a headword. This generates a set of buttons",
                "# for browsing the database available on the landing page. The default represents the entire roman alphabet. An empty list hides the table.",
            ]
        ),
    },
    "concordance_citation": {
        "value": [
            CITATIONS["author"],
            CITATIONS["title"],
            CITATIONS["year"],
            CITATIONS["div1_head"],
            CITATIONS["div2_head"],
            CITATIONS["div3_head"],
            CITATIONS["speaker"],
            CITATIONS["resp"],
            CITATIONS["page"],
        ],
        "comment": "\n".join(
            [
                "# The concordance_citation variable define how and in what field order citations are displayed in concordance reports.",
                "# You can define styling with a dictionary of valid CSS property/value such as those in the default values.",
                "# See comments for the citations variable for how to configure citations",
            ]
        ),
    },
    "bibliography_citation": {
        "value": [
            CITATIONS["author"],
            CITATIONS["title"],
            CITATIONS["year"],
            CITATIONS["div1_head"],
            CITATIONS["div2_head"],
            CITATIONS["div3_head"],
            CITATIONS["speaker"],
            CITATIONS["resp"],
            CITATIONS["page"],
        ],
        "comment": "\n".join(
            [
                "# The bibligraphy_citation variable define how and in what field order citations are displayed in bibliography reports.",
                "# You can define styling with a dictionary of valid CSS property/value such as those in the default values.",
                "# See comments for the citations variable for how to configure citations",
            ]
        ),
    },
    "table_of_contents_citation": {
        "value": [],
        "comment": "\n".join(
            [
                "# The table_of_contents_citation variable define how and in what field order citations are displayed within the table of content",
                "# In most cases, this should remain empty, except in the cases of div elements with different metadata values",
            ]
        ),
    },
    "navigation_citation": {
        "value": [
            CITATIONS["author"],
            CITATIONS["title"],
            CITATIONS["year"],
            CITATIONS["pub_place"],
            CITATIONS["publisher"],
            CITATIONS["collection"],
        ],
        "comment": "\n".join(
            [
                "# The navigation_citation variable define how and in what field order citations are displayed in navigation reports.",
                "# You can define styling with a dictionary of valid CSS property/value such as those in the default values.",
                "# See comments for the citations variable for how to configure citations",
            ]
        ),
    },
    "kwic_bibliography_fields": {
        "value": [],
        "comment": "\n".join(
            [
                "# The kwic_bibliography_fields variable  defines which bibliography fields will be displayed in the KWIC view. It should be",
                "# modified with extra care in conjunction with the concordance_citation function located in reports/concordance.py.",
                "# If the variable is an empty list, filename will be used.",
                "",
            ]
        ),
    },
    "concordance_biblio_sorting": {
        "value": [],
        "comment": "\n".join(
            [
                "# The concordance_biblio_sorting variable allows you to pick wich metadata field can be used for sorting concordance or bibliography results.",
                "# It is a list of tuples where multiple metadata fields can be used for sorting, such as [('author', 'title'), ('year', 'author', 'title')].",
                '# Note that these fields must belong to the same object type, such as "doc" or "div".',
                "",
            ]
        ),
    },
    "kwic_metadata_sorting_fields": {
        "value": [],
        "comment": "\n".join(
            [
                "# The kwic_metadata_sorting_fields variable allows you to pick wich metadata field can be used for sorting KWIC results.",
                "",
            ]
        ),
    },
    "time_series_year_field": {
        "value": "year",
        "comment": "\n".join(
            [
                "# The time_series_year_field variable defines which metadata field to use for time series.",
                "",
            ]
        ),
    },
    "time_series_interval": {
        "value": 10,
        "comment": "\n".join(
            ["# The time_series_interval variable defines the default year span used for time series."]
        ),
    },
    "time_series_start_end_date": {
        "value": {"start_date": 0, "end_date": 0},
        "comment": "\n".join(
            [
                "# The time_series_start_end_date variable defines the default start and end dates for time series when no dates are provided."
            ]
        ),
    },
    "external_page_images": {
        "value": False,
        "comment": "\n".join(["# This defines whether the page images should be viewed in a non-PhiloLogic instance"]),
    },
    "page_images_url_root": {
        "value": "",
        "comment": "\n".join(
            [
                "# The page_images_url_root variable defines a root URL where pages images can be fetched when a filename is provided inside a page tag.",
                "# Note that the page image filename must be inside a fac or id attribute such as:",
                '# <pb fac="filename.jpg"> or <pb id="filename.jpg">',
                "# So a URL of http://my-server.com/images/ will resolve to http://my-server.com/images/filename.jpg.",
                "",
            ]
        ),
    },
    "page_image_extension": {
        "value": "",
        "comment": "\n".join(
            [
                "# The page_image_extension value is useful when the image name does not have an extension defined in the markup.",
                '# For instance, given <pb n="1" fac="image1">, you could define the extension as ".jpeg" and the browser would fetch',
                "# the image at http://some-url/image1.jpeg (where some-url is defined in the above page_images_url_root variable).",
                "",
            ]
        ),
    },
    "logo": {
        "value": "",
        "comment": "\n".join(
            [
                "# The logo variable defines the location of an image to display on the landing page, just below the",
                "# search form. It can be a relative URL, or an absolute link, in which case you want to make sure",
                "# it starts with http://. If no logo is defined, no picture will be displayed.",
                "",
            ]
        ),
    },
    "header_in_toc": {
        "value": False,
        "comment": "# The header_in_toc variable defines whether to display a button to show the header in the table of contents",
    },
    "search_syntax_template": {
        "value": "default",
        "comment": "\n".join(
            [
                "# You can define a custom HTML template for the search syntax pop-up window, in which case you need to supply the",
                "# relative path to the template. Note that this path is relative to the database root. The only constraint",
                "# for custom templates is that the HTML must be encapsulated inside a div",
                "",
            ]
        ),
    },
    "concordance_formatting_regex": {
        "value": [],
        "comment": "\n".join(
            [
                "# A list of pattern with replacement to be run on individual concordances before sending to browser",
                "# It is constructed as a list of tuples where the first element is the pattern to be matched",
                "# and the second element is the replacement",
                '# e.g.: [("<note>", "<span>"), ("</note>", "</span>")]',
                "",
            ]
        ),
    },
    "kwic_formatting_regex": {
        "value": [],
        "comment": "\n".join(
            [
                "# A list of pattern with replacement to be run on individual kwic concordances before sending to browser",
                "# It is constructed as a list of tuples where the first element is the pattern to be matched",
                "# and the second element is the replacement",
                '# e.g.: [("<note>", "<span>"), ("</note>", "</span>")]',
                "",
            ]
        ),
    },
    "navigation_formatting_regex": {
        "value": [],
        "comment": "\n".join(
            [
                "# A list of pattern with replacement to be run on text objects before sending to browser",
                "# It is constructed as a list of tuples where the first element is the pattern to be matched",
                "# and the second element is the replacement",
                '# e.g.: [("<note>", "<span>"), ("</note>", "</span>")]',
                "",
            ]
        ),
    },
    "dictionary_lookup": {
        "value": {"url_root": "", "keywords": False},
        "comment": "\n".join(
            [
                "# Dictionary lookup function. You select a word in running text and hit D, and it'll query an external dictionary and return",
                "# definitions. You need to provide the URL root of the dictionary. If keywords is false, the word selected is just appened to",
                "# the URL. Otherwise, if set to True, you need to configure the dictionary_lookup_keywords variable below to construct the full URL."
                "",
            ]
        ),
    },
    "dictionary_lookup_keywords": {
        "value": {
            "immutable_key_values": {},
            "variable_key_values": {},
            "selected_keyword": "",
        },
        "comment": "\n".join(
            [
                "# This defines what keyword/values are appended to the root URL for dico lookup. The immutable_key_values defines key/values which are hardcoded",
                "# The variable_key_values defines a key/value pair where the key is the URL key, and the value is a corresponding metadata field value from the text",
                "# currently displayed. The selected_keyword corresponds to the URL key for the word selected in the text.",
            ]
        ),
    },
    "query_parser_regex": {
        "value": [
            ("-", " "),
            (" OR ", " | "),
            ("'", " "),
            (";", ""),
            (",", ""),
            ("!", ""),
            ("\u3000", " "),
            ("｜", "|"),
            ("”", '"'),
            ("－", "-"),
            ("＊", "*"),
        ],
        "comment": "\n".join(
            [
                "# A list of pattern with replacement to be run on all incoming queries",
                "# It is constructed as a list of tuples where the first element is the regex pattern to be matched",
                "# and the second element is the replacement",
                '# e.g.: [(" OR ", " | "), ("-", " ")]',
                "",
            ]
        ),
    },
    "report_error_link": {
        "value": "",
        "comment": "# The link should start with http:// or https://. This will display an error report link in the header and in document navigation",
    },
    "academic_citation": {
        "value": {"collection": "", "citation": []},
        "comment": "\n".join(
            [
                "# The academic citation use to cite this database. The citation is build with the citation defined (from metadata values) + the collection key (which can be HTML)",
                """# e.g.: {"collection": 'ARTFL-FRANTEXT, University of Chicago: <a href="https://link.to.db/">https://link.to.db/</a>', "citation": [citations["author"], citations["title"], citations["year"]]}""",
            ]
        ),
    },
}

WEB_CONFIG_HEADER = """
   ####################################################\n
   #### Web configuration options for PhiloLogic4 #####\n
   ####################################################\n
   ### All variables must be in valid Python syntax ###\n
   ####################################################\n\n\n
"""


class Config:
    """Main Config class to build out web_config and db.locals"""

    def __init__(self, filename, defaults, header=""):
        self.filename = filename
        self.db_path = os.path.dirname(os.path.dirname(self.filename))
        self.defaults = defaults
        self.header = header
        self.data = {key: value["value"] for key, value in self.defaults.items()}
        if self.filename and os.path.exists(self.filename):
            exec(compile(open(self.filename, "rb").read(), self.filename, "exec"), globals(), self.data)
            self.valid_config = True
        self.time_series_status = True
        self.converted = False

    def __getitem__(self, item):
        try:
            return self.data[item]
        except KeyError:
            return self.defaults[item]

    def __getattr__(self, key):
        return self[key]

    def __setitem__(self, item, value):
        self.data[item] = value

    def __str__(self):
        string = "\n".join([line.strip() for line in self.header.splitlines() if line.strip()]) + "\n\n"
        written_keys = []
        for key, value in self.defaults.items():
            if value["comment"]:
                string += "\n" + "\n".join(line.strip() for line in value["comment"].splitlines() if line.strip())
            if key == "default_landing_page_browsing":
                string += """\ndefault_landing_page_browsing = [{"label": "Author", "group_by_field": "author",
                "display_count": True, "queries": ["A-D", "E-I", "J-M", "N-R", "S-Z"], "is_range": True,
                "citation": [citations["author"]],}, {"label": "Title", "group_by_field": "title",
                "display_count": False, "queries": ["A-D", "E-I", "J-M", "N-R", "S-Z"], "is_range": True,
                "citation": [citations["author"], citations["title"], citations["year"]]}]"""
            elif key == "concordance_citation":
                string += f"""\n{key} = [
                    citations["author"], citations["title"], citations["year"], citations["div1_head"],
                    citations["div1_date"], citations["div2_head"], citations["div2_date"], citations["div3_head"],
                    citations["div3_date"], citations["speaker"], citations["resp"], citations["page"],
                ]"""
            elif key == "bibliography_citation":
                string += f"""\n{key} = [
                    citations["author"], citations["title"], citations["year"],
                    citations["div1_head"], citations["div2_head"], citations["div3_head"],
                    citations["speaker"], citations["resp"], citations["page"],
                ]"""
            elif key in ("table_of_contents_citation", "navigation_citation", "simple_landing_citation"):
                string += f"""\n{key} = [
                    citations["author"], citations["title"], citations["year"],
                    citations["pub_place"], citations["publisher"], citations["collection"],
                ]"""
            elif key == "aggregation_config":
                string += (
                    f"\n{key} = "
                    + "[{"
                    + """"field": "author", "object_level": "doc",  "field_citation": [citations["author"]],
                       "break_up_field": "title", "break_up_field_citation": [
                        citations["title"], citations["pub_place"], citations["publisher"], citations["collection"],citations["year"]
                        ],"""
                    + "}, {"
                    + """"field": "title", "object_level": "doc", "field_citation": [citations["title"],
                        citations["pub_place"], citations["publisher"], citations["collection"], citations["year"]],"break_up_field": None,
                        "break_up_field_citation": None, """
                    + "}]"
                )
            else:
                string += f"\n{key} = {pretty_print(self.data[key])}\n"
            written_keys.append(key)
        for key, value in self.data.items():
            if key not in written_keys:
                string += f"\n{key} = {pretty_print(value)}\n"
                written_keys.append(key)
        return string

    def to_json(self):
        """Convert Config to JSON representation"""
        out_obj = {"valid_config": True}
        written = []
        for key in self.defaults.keys():
            out_obj[key] = self.data[key]
            written.append(key)
        for key in self.data:
            if key not in written:
                out_obj[key] = self.data[key]
                written.append(key)
        if self.time_series_status is False:
            try:
                out_obj["search_reports"].remove("time_series")
            except ValueError:
                pass
        return json.dumps(out_obj)


def MakeWebConfig(path, **extra_values):
    """Build web_config with non-default arguments"""
    web_config = Config(path, WEB_CONFIG_DEFAULTS, header=WEB_CONFIG_HEADER)
    if extra_values:
        for key, value in extra_values.items():
            web_config[key] = value
    return web_config


def MakeDBConfig(path, **extra_values):
    """Build db.locals with non-default arguments"""
    db_config = Config(path, DB_LOCALS_DEFAULTS, header=DB_LOCALS_HEADER)
    if extra_values:
        for key, value in extra_values.items():
            db_config[key] = value
    return db_config


if __name__ == "__main__":
    if sys.argv[1].endswith("cfg"):
        conf = Config(sys.argv[1], WEB_CONFIG_DEFAULTS)
    else:
        conf = Config(sys.argv[1], DB_LOCALS_DEFAULTS)
    # print(conf, file=sys.stderr)
