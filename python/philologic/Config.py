#!/usr/bin/env python3


import sys
import os
import json
import imp
from philologic.utils import pretty_print

db_locals_defaults = {
    'metadata_fields': {
        'value': [],
        'comment': '',
        'index': 0
    },
    'metadata_hierarchy': {
        'value': [[]],
        'comment': '',
        'index': 1
    },
    'metadata_types': {
        'value': {},
        'comment': '',
        'index': 2
    },
    'metadata_query_types': {
        'value': {},
        'comment': '''# metadata_query_types determines how these fields are stored in SQLite. Three types are possible:
                      # string, integer, date. By default, all fields are stored as strings unless defined otherwise in the optional
                      # load_config.py file. DISABLED AT THIS TIME.''',
        'index': 3
    },
    'normalized_fields': {
        'value': [],
        'comment': '',
        'index': 4
    },
    'default_object_level': {
        'value': 'doc',
        'comment': '# This defines the default navigation element in your database',
        'index': 7
    },
    'lowercase_index': {
        'value': True,
        'comment':
        '# This defines whether all terms in the index have been lowercased. If so, input searches will be lowercased',
        'index': 8
    },
    'debug': {
        'value': False,
        'comment': '# If set to True, this enabled debugging messages to be printed out to the Apache error log',
        'index': 9
    },
    'secret': {
        'value': '',
        'comment':
        '# The secret value is a random string to be used to generate a secure cookie for access control. The string value can be anything.',
        'index': 10
    }
}
db_locals_header = '''
   # -*- coding: utf-8 -*-\n
   #########################################################\n
   #### Database configuration options for PhiloLogic4 #####\n
   #########################################################\n
   #### All variables must be in valid Python syntax #######\n
   #########################################################\n
   #### Edit with extra care: an invalid          ##########\n
   #### configuration could break your database.  ##########\n
   #########################################################\n\n\n
'''

web_config_defaults = {
    'dbname': {
        'value': 'noname',
        'comment': "# The dbname variable is the title name in the HTML header",
        'index': 0
    },
    'access_control': {
        'value': False,
        'comment': '''
               # Configure access control with True or False.
               # Note that if you want access control, you have to provide a login.txt file inside your /data directory,
               # otherwise access will remain open.''',
        'index': 1
    },
    'access_file': {
        'value': '',
        'comment': '# Location of access file which contains authorized/unauthorized IPs and domain names',
        'index': 2
    },
    'production': {
        'value': True,
        'comment': '# Do not set to False unless you want to make changes in the Web Client in the app/ directory',
        'index': 3
    },
    'link_to_home_page': {
        'value': '',
        'comment': '# If set, link_to_home_page should be a string starting with "http://" pointing to a separate home page for the database',
        'index': 4
    },
    'search_reports': {
        'value': ['concordance', 'kwic', 'collocation', 'time_series'],
        'comment': '''
               # The search_reports variable sets which search report is viewable in the search form
               # Available reports are concordance, kwic, collocation, and time_series''',
        'index': 5
    },
    'metadata': {
        'value': [],
        'comment': "# The metadata variable sets which metadata field is viewable in the search form",
        'index': 6
    },
    'metadata_aliases': {
        'value': {},
        'comment': '''
               # The metadata_aliases variable allows to display a metadata variable under a different name in the HTML
               # For example, you could rename the who metadata to Speaker, and the create_date variable to Date like so:
               # metadata_aliases = {'who': 'Speaker', 'create_date', 'Date'}''',
        'index': 7
    },
    'metadata_input_style': {
        'value': {},
        'comment': '''
               # The metadata_input_style variable defines whether to use an text input field or a dropdown menu for any given
               # metadata field. All fields are set by default to text. If using a dropdown menu, you need to set it to "dropdown"
               # and populate the metadata_dropdown_values variable''',
        'index': 8
    },
    'metadata_dropdown_values': {
        'value': {},
        'comment': '''
               # The metadata_dropdown_values variable defines what values to display in the metadata dropdown. It defaults to an empty dict.
               # If no value is provided for a metadata field which has an input type of dropdown, no value will be displayed. You should
               # provide a list of strings with labels and values for metadata.
               # ex: {"title": [{"label": "Contrat Social", "value": "Du Contrat Social"}, {"label": "Emile", "value": "Emile, ou de l'éducation"}]}''',
        'index': 9
    },
    'facets': {
        'value': [],
        'comment': '''
               # The facets variable sets which metadata field can be used as a facet
               # The object format is a list of metadata like the following: ['author', 'title', 'year'}
               # The dict key should describe what the facets will do, and the dict value, which has to be a list,
               # should list the metadata to be used for the frequency counts''',
        'index': 10
    },
    'words_facets': {
        'value': [],
        'comment': '''
               # The word_facets variable functions much like the facets variable, but describes metadata
               # attached to word or phrases results and stored in the words table. Experimental.''',
        'index': 11
    },
    'concordance_length': {
        'value': 300,
        'comment': "# The concordance_length variable sets the length in bytes of each concordance result",
        'index': 12
    },
    'search_examples': {
        'value': {},
        'comment': '''
               # The search_examples variable defines which examples should be provided for each searchable field in the search form.
               # If None is the value, or there are any missing examples, defaults will be generated at runtime by picking the first
               # result for any given field. If you wish to change these default values, you should configure them here like so:
               # search_examples = {"author": "Jean-Jacques Rousseau", "title": "Du contrat social"}''',
        'index': 13
    },
    'stopwords': {
        'value': '',
        'comment': '''
               # The stopwords variable defines a file path containing a list of words (one word per line) used for filtering out words
               # in the collocation report. The file must be located in the defined path. If the file is not found,
               # no option for using a stopword list will be displayed in collocation searches.''',
        'index': 14
    },
    'theme': {
        'value': 'app/assets/css/split/default_theme.css',
        'comment': '''
               # The theme variable defines the default CSS theme to be used in the WebApp. The default theme called default_theme.css
               # can be edited directly or you can define a new CSS file below. This file must be located in the app/assets/css/split/ directory for the Web App to find it.''',
        'index': 15
    },
    'dictionary': {
        'value': False,
        'comment':
        '# The dictionary variable enables a different search interface with the headword as its starting point. It is turned off by default',
        'index': 16
    },
    'dictionary_bibliography': {
        'value': False,
        'comment':
        '''# The dictionary_bibliography variable enables a different a bibliography report where entries are displayed
                      # in their entirety and grouped under the same title. It is turned off by default''',
        'index': 17
    },
    'dictionary_selection': {
        'value': False,
        'comment':
        '''# If set to True, this option creates a dropdown menu to select searching within only a single volume or title.
                      # This replaces the title field in the search form.
                      # You need to configure the dictionary_selection_options variable below to define your options.''',
        'index': 18
    },
    'dictionary_selection_options': {
        'value': [],
        'comment': '''# If dictionary_selection is set to True, you need to populate this variable as in the following:
                      # [{"label": "DAF 1932", "title": "Dictionnaire de l'Académie Française 1932"}]
                      # Each volume is represented as an object containing the label which is displayed in the search form
                      # and a title value which should either be the exact string stored in the SQL table, or an egrep expression
                      # such as "Dictionnaire de Littre.*" if you wish to match more than one title.''',
        'index': 19
    },
    'landing_page_browsing': {
        'value': 'default',
        'comment': '''
               # The landing_page_browsing variable defines what type of landing page. There are 3 built-in reports available: 'default',
               # 'dictionary' or 'simple'. You can otherwise supply a relative path to a custom HTML template. Note that this path is relative
               # to the database root. The only constraint for custom templates is that the HTML must be encapsulated inside a div''',
        'index': 20
    },
    'default_landing_page_browsing': {
        'value': [
            {"label": "Author",
             "group_by_field": "author",
             "display_count": True,
             "queries": ["A-D", "E-I", "J-M", "N-R", "S-Z"],
             "is_range": True,
             'citation': [
                 {'field': 'author',
                  'object_level': 'doc',
                  'prefix': '',
                  'suffix': '',
                  'separator': ',',
                  'link': True,
                  'style': {"font-variant": "small-caps"}}
             ]},
             {"label": "Title",
              "group_by_field": "title",
              "display_count": False,
              "queries": ["A-D", "E-I", "J-M", "N-R", "S-Z"],
              "is_range": True,
              'citation': [
                  {
                      'field': 'author',
                      'object_level': 'doc',
                      'prefix': '',
                      'suffix': ',&nbsp;',
                      'separator': '',
                      'link': False,
                      'style': {"font-variant": "small-caps"}
                  }, {
                      'field': 'title',
                      'object_level': 'doc',
                      'prefix': '',
                      'suffix': '',
                      'separator': '&gt;',
                      'link': True,
                      'style': {"font-variant": "small-caps",
                                "font-style": "italic",
                                "font-weight": 700}
                  }, {
                      'field': 'year',
                      'object_level': 'doc',
                      'prefix': '&nbsp;&nbsp;[',
                      'suffix': ']',
                      'separator': '&gt;',
                      'link': False,
                      'style': {}
                  }
              ], }
        ],
        'comment': '''
               # The landing_page_browsing variable allows for configuration of navigation by metadata within the landing page.
               # You can choose any document-level metadata (such as author, title, date, genre...) for browsing
               # and define two different types of queries to group your data: ranges and exact matches, i.e. "A-D" or "Comedy".
               # You can define styling with a dictionary of valid CSS property/value such as those in the default values.
               # begin and end keywords define what precedes and follows each field. You can use HTML for these strings.''',
        'index': 21
    },
    'default_landing_page_display': {
        'value': {},
        'comment': '''
               # The default landing page display variable allows you to load content by default. It is configured
               # in the same way as default_landing_page_display objects except that you need to define just one
               # range (the one you wish to display) as a string, such as 'A-D'. An empty dict will disable the feature.''',
        'index': 22
    },
    'simple_landing_citation': {
        'value': [{
            'field': 'author',
            'object_level': 'doc',
            'prefix': '',
            'suffix': ',&nbsp;',
            'separator': ',',
            'link': False,
            'style': {"font-variant": "small-caps"}
        }, {
            'field': 'title',
            'object_level': 'doc',
            'prefix': '',
            'suffix': '',
            'separator': ',',
            'link': True,
            'style': {"font-variant": "small-caps",
                      "font-style": "italic",
                      "font-weight": 700}
        }, {
            'field': 'year',
            'object_level': 'doc',
            'prefix': '&nbsp;&nbsp;[',
            'suffix': ']',
            'separator': '',
            'link': False,
            'style': {}
        }, {
            'field': 'pub_place',
            'object_level': 'doc',
            'prefix': '',
            'suffix': ',&nbsp;',
            'separator': '&gt;',
            'link': False,
            'style': {}
        }, {
            'field': 'publisher',
            'object_level': 'doc',
            'prefix': '',
            'suffix': ',&nbsp;',
            'separator': '&gt;',
            'link': False,
            'style': {}
        }, {
            'field': 'collection',
            'object_level': 'doc',
            'prefix': '',
            'suffix': ',&nbsp;',
            'separator': '&gt;',
            'link': False,
            'style': {}
        }],
        'comment': '# This variable defines the citation for the simple landing page.',
        'index': 23
    },
    'dico_letter_range': {
        'value': ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T",
                  "U", "V", "W", "X", "Y", "Z"],
        'comment': '''
               # If landing_page_browsing is set to dictionary, the dico_letter_range variable allows you to define set of letters corresponding to the first letter of a headword. This generates a set of buttons
               # for browsing the database available on the landing page. The default represents the entire roman alphabet. An empty list hides the table.''',
        'index': 24
    },
    'concordance_citation': {
        'value': [{
            'field': 'author',
            'object_level': 'doc',
            'prefix': '',
            'suffix': '',
            'separator': ',',
            'link': False,
            'style': {"font-variant": "small-caps"}
        }, {
            'field': 'title',
            'object_level': 'doc',
            'prefix': '',
            'suffix': '',
            'separator': '',
            'link': True,
            'style': {"font-variant": "small-caps",
                      "font-style": "italic",
                      "font-weight": 700}
        }, {
            'field': 'year',
            'object_level': 'doc',
            'prefix': '&nbsp;&nbsp;[',
            'suffix': ']',
            'separator': '&gt;',
            'link': False,
            'style': {}
        }, {
            'field': 'head',
            'object_level': 'div1',
            'prefix': '&nbsp;&nbsp;&nbsp;&nbsp;',
            'suffix': '&nbsp;&nbsp;',
            'separator': '&gt;',
            'link': True,
            'style': {"font-variant": "small-caps"}
        }, {
            'field': 'head',
            'object_level': 'div2',
            'prefix': '&nbsp;&nbsp;',
            'suffix': '&nbsp;&nbsp;',
            'separator': '&gt;',
            'link': True,
            'style': {"font-variant": "small-caps"}
        }, {
            'field': 'head',
            'object_level': 'div3',
            'prefix': '&nbsp;&nbsp;',
            'suffix': '&nbsp;&nbsp;',
            'separator': '&gt;',
            'link': True,
            'style': {"font-variant": "small-caps"}
        }, {
            'field': 'who',
            'object_level': 'para',
            'prefix': '&nbsp;&nbsp;',
            'suffix': '&nbsp;&nbsp;',
            'separator': '',
            'link': True,
            'style': {"font-variant": "small-caps"}
        }, {
            'field': 'resp',
            'object_level': 'para',
            'prefix': '&nbsp;&nbsp;',
            'suffix': '&nbsp;&nbsp;',
            'separator': '',
            'link': True,
            'style': {"font-variant": "small-caps"}
        }],
        'comment': '''
               # The concordance_citation variable define how and in what field order citations are displayed in concordance reports.
               # You can define styling with a dictionary of valid CSS property/value such as those in the default values.
               # begin and end keywords define what precedes and follows each field. You can use HTML for these strings.
               # The link key enables linking for that metadata field. It links to the table of contents for title and filename,
               # and to a regular query for all other metadata fields.''',
        'index': 25
    },
    'bibliography_citation': {
        'value': [{
            'field': 'author',
            'object_level': 'doc',
            'prefix': '',
            'suffix': '',
            'separator': ',',
            'link': False,
            'style': {"font-variant": "small-caps"}
        }, {
            'field': 'title',
            'object_level': 'doc',
            'prefix': '',
            'suffix': '',
            'separator': '',
            'link': True,
            'style': {"font-variant": "small-caps",
                      "font-style": "italic",
                      "font-weight": 700}
        }, {
            'field': 'year',
            'object_level': 'doc',
            'prefix': '&nbsp;&nbsp;[',
            'suffix': ']',
            'separator': '&gt;',
            'link': False,
            'style': {}
        }, {
            'field': 'head',
            'object_level': 'div1',
            'prefix': '&nbsp;&nbsp;&nbsp;&nbsp;',
            'suffix': '&nbsp;&nbsp;',
            'separator': '&gt;',
            'link': True,
            'style': {"font-variant": "small-caps"}
        }, {
            'field': 'head',
            'object_level': 'div2',
            'prefix': '&nbsp;&nbsp;',
            'suffix': '&nbsp;&nbsp;',
            'separator': '&gt;',
            'link': True,
            'style': {"font-variant": "small-caps"}
        }, {
            'field': 'head',
            'object_level': 'div3',
            'prefix': '&nbsp;&nbsp;',
            'suffix': '&nbsp;&nbsp;',
            'separator': '&gt;',
            'link': True,
            'style': {"font-variant": "small-caps"}
        }, {
            'field': 'who',
            'object_level': 'para',
            'prefix': '&nbsp;&nbsp;',
            'suffix': '&nbsp;&nbsp;',
            'separator': '',
            'link': True,
            'style': {"font-variant": "small-caps"}
        }, {
            'field': 'resp',
            'object_level': 'para',
            'prefix': '&nbsp;&nbsp;',
            'suffix': '&nbsp;&nbsp;',
            'separator': '',
            'link': True,
            'style': {"font-variant": "small-caps"}
        }],
        'comment': '''
               # The bibligraphy_citation variable define how and in what field order citations are displayed in bibliography reports.
               # You can define styling with a dictionary of valid CSS property/value such as those in the default values.
               # begin and end keywords define what precedes and follows each field. You can use HTML for these strings.
               # The link key enables linking for that metadata field. It links to the table of contents for title and filename,
               # and to a regular query for all other metadata fields.''',
        'index': 26
    },
    'navigation_citation': {
        'value': [{
            'field': 'author',
            'object_level': 'doc',
            'prefix': '',
            'suffix': '',
            'separator': '',
            'link': False,
            'style': {"font-variant": "small-caps"}
        }, {
            'field': 'title',
            'object_level': 'doc',
            'prefix': '',
            'suffix': '',
            'separator': '',
            'link': True,
            'style': {"font-variant": "small-caps",
                      "font-style": "italic",
                      "font-weight": 700}
        }, {
            'field': 'year',
            'object_level': 'doc',
            'prefix': '&nbsp;&nbsp;[',
            'suffix': ']',
            'separator': '',
            'link': False,
            'style': {}
        }, {
            'field': 'pub_place',
            'object_level': 'doc',
            'prefix': '',
            'suffix': '',
            'separator': '<br>',
            'link': False,
            'style': {}
        }, {
            'field': 'publisher',
            'object_level': 'doc',
            'prefix': '',
            'suffix': '',
            'separator': ',',
            'link': False,
            'style': {}
        }, {
            'field': 'collection',
            'object_level': 'doc',
            'prefix': '',
            'suffix': '',
            'separator': '',
            'link': False,
            'style': {}
        }],
        'comment': '''
               # The navigation_citation variable define how and in what field order citations are displayed in navigation reports.
               # You can define styling with a dictionary of valid CSS property/value such as those in the default values.
               # begin and end keywords define what precedes and follows each field. You can use HTML for these strings.
               # The link key enables linking for that metadata field. It links to the table of contents for title and filename,
               # and to a metadata query for all other metadata fields.''',
        'index': 27
    },
    'kwic_bibliography_fields': {
        'value': [],
        'comment': '''
                # The kwic_bibliography_fields variable  defines which bibliography fields will be displayed in the KWIC view. It should be
                # modified with extra care in conjunction with the concordance_citation function located in reports/concordance.py.
                # If the variable is an empty list, filename will be used.
                ''',
        'index': 28
    },
    'concordance_biblio_sorting': {
        'value': [],
        'comment': '''
                # The concordance_biblio_sorting variable allows you to pick wich metadata field can be used for sorting concordance or bibliography results.
                # It is a list of tuples where multiple metadata fields can be used for sorting, such as [('author', 'title'), ('year', 'author', 'title')].
                # Note that these fields must belong to the same object type, such as "doc" or "div".
                ''',
        'index': 29
    },
    'kwic_metadata_sorting_fields': {
        'value': [],
        'comment': '''
                # The kwic_metadata_sorting_fields variable allows you to pick wich metadata field can be used for sorting KWIC results.
                ''',
        'index': 30
    },
    'time_series_year_field': {
        'value': 'year',
        'comment': '''
                # The time_series_year_field variable defines which metadata field to use for time series. The year field is built at load time by finding the earliest 4 digit number
                # in multiple date fields.
                ''',
        'index': 31
    },
    'time_series_interval': {
        'value': 10,
        'comment': '# The time_series_interval variable defines the default year span used for time series.',
        'index': 32
    },
    'external_page_images': {
        'value': False,
        'comment': '# This defines whether the page images should be viewed in a non-PhiloLogic instance',
        "index": 33
    },
    'page_images_url_root': {
        'value': '',
        'comment': '''
                 # The page_images_url_root variable defines a root URL where pages images can be fetched when a filename is provided inside a page tag.
                 # Note that the page image filename must be inside a fac or id attribute such as:
                 # <pb fac="filename.jpg"> or <pb id="filename.jpg">
                 # So a URL of http://my-server.com/images/ will resolve to http://my-server.com/images/filename.jpg.
                 ''',
        'index': 34
    },
    'page_image_extension': {
        'value': '',
        'comment': '''
                 # The page_image_extension value is useful when the image name does not have an extension defined in the markup.
                 # For instance, given <pb n="1" fac="image1">, you could define the extension as ".jpeg" and the browser would fetch
                 # the image at http://some-url/image1.jpeg (where some-url is defined in the above page_images_url_root variable).
                 ''',
        'index': 35
    },
    'logo': {
        'value': '',
        'comment': '''
                  # The logo variable defines the location of an image to display on the landing page, just below the
                  # search form. It can be a relative URL, or an absolute link, in which case you want to make sure
                  # it starts with http://. If no logo is defined, no picture will be displayed.
                  ''',
        'index': 36
    },
    'header_in_toc': {
        'value': False,
        'comment': '''
                  # The header_in_toc variable defines whether to display a button to show the header in the table of contents
                  ''',
        'index': 37
    },
    'search_syntax_template': {
        'value': 'default',
        'comment': '''
                  # You can define a custom HTML template for the search syntax pop-up window, in which case you need to supply the
                  # relative path to the template. Note that this path is relative to the database root. The only constraint
                  # for custom templates is that the HTML must be encapsulated inside a div
                  ''',
        "index": 38
    },
    'concordance_formatting_regex': {
        'value': [],
        'comment': '''
                # A list of pattern with replacement to be run on individual concordances before sending to browser
                # It is constructed as a list of tuples where the first element is the pattern to be matched
                # and the second element is the replacement
                # e.g.: [("<note>", "<span>"), ("</note>", "</span>")]
                ''',
        'index': 39
    },
    'kwic_formatting_regex': {
        'value': [],
        'comment': '''
                # A list of pattern with replacement to be run on individual kwic concordances before sending to browser
                # It is constructed as a list of tuples where the first element is the pattern to be matched
                # and the second element is the replacement
                # e.g.: [("<note>", "<span>"), ("</note>", "</span>")]
                ''',
        'index': 40
    },
    'navigation_formatting_regex': {
        'value': [],
        'comment': '''
                # A list of pattern with replacement to be run on text objects before sending to browser
                # It is constructed as a list of tuples where the first element is the pattern to be matched
                # and the second element is the replacement
                # e.g.: [("<note>", "<span>"), ("</note>", "</span>")]
                ''',
        'index': 41
    },
    'dictionary_lookup': {
        'value': "",
        'comment': '''
                # Dictionary lookup function. You select a word in running text and hit D, and it'll query an external dictionary
                # and return definitions. This is currently hardcoded to ARTFL's dictionary model. To be made more generic at a later date
                ''',
        'index': 42
    }
}

web_config_header = '''
   # -*- coding: utf-8 -*-"
   ####################################################\n
   #### Web configuration options for PhiloLogic4 #####\n
   ####################################################\n
   ### All variables must be in valid Python syntax ###\n
   ####################################################\n\n\n
'''


class Config(object):
    def __init__(self, filename, defaults, header=''):
        self.filename = filename
        abspath = os.path.abspath(filename)
        self.db_path = abspath[:abspath.index("/data/")]
        self.defaults = defaults
        self.header = header
        self.data = {}
        self.sorted_defaults = sorted(list(self.defaults.items()), key=lambda x: x[1]['index'])
        for key, value in self.sorted_defaults:
            self.data[key] = value['value']

        if self.filename and os.path.exists(self.filename):
            exec(compile(open(self.filename, 'rb').read(), self.filename, 'exec'), globals(), self.data)
            # self.config_file = imp.load_source("config", self.filename)
            self.valid_config = True

        self.time_series_status = True

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
        string = "\n".join([line.strip() for line in self.header.splitlines() if line.strip()]) + '\n\n'
        written_keys = []
        for key, value in self.sorted_defaults:
            if value["comment"]:
                string += "\n" + "\n".join(line.strip() for line in value["comment"].splitlines() if line.strip())
            # string += "\n%s = %s\n" % (key,repr(self.data[key]))
            string += "\n%s = %s\n" % (key, pretty_print(self.data[key]))
            written_keys.append(key)
        for key in self.data:
            if key not in written_keys:
                # string += "\n%s = %s\n" % (key,repr(self.data[key]))
                string += "\n%s = %s\n" % (key, pretty_print(self.data[key]))
                written_keys.append(key)
        return string

    def to_json(self):
        out_obj = {}
        written = []
        for key, value in self.sorted_defaults:
            out_obj[key] = self.data[key]
            written.append(key)
        for key in self.data:
            if key not in written:
                out_obj[key] = self.data[key]
                written.append(key)
        if self.time_series_status is False:
            out_obj["search_reports"].remove("time_series")
        return json.dumps(out_obj)


def MakeWebConfig(path, **extra_values):
    web_config = Config(path, web_config_defaults, header=web_config_header)
    if extra_values:
        for key, value in extra_values.items():
            web_config[key] = value
    return web_config


def MakeDBConfig(path, **extra_values):
    db_config = Config(path, db_locals_defaults, header=db_locals_header)
    if extra_values:
        for key, value in extra_values.items():
            db_config[key] = value
    return db_config


if __name__ == "__main__":
    if sys.argv[1].endswith('cfg'):
        conf = Config(sys.argv[1], web_config_defaults)
    else:
        conf = Config(sys.argv[1], db_locals_defaults)
    print(conf, file=sys.stderr)
