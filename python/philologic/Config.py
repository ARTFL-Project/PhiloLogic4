#!/usr/bin/env python
import sys
import os
import json

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
    'normalized_fields': {
        'value': [],
        'comment': '',
        'index': 3
    },
    'word_regex': {
        'value': '([\\w]+)',
        'comment': '# Regex used for tokenizing outgoing text',
        'index': 4
    },
    'punct_regex': {
        'value': '([\\.?!])',
        'comment': '# Regex used for punctuation',
        'index': 5
    },
    'default_object_level': {
        'value': 'doc',
        'comment': '# This defines the default navigation element in your database',
        'index': 6
    },
    'lowercase_index': {
        'value': True,
        'comment':
        '# This defines whether all terms in the index have been lowercased. If so, input searches will be lowercased',
        'index': 7
    },
    'debug': {
        'value': False,
        'comment': '# If set to True, this enabled debugging messages to be printed out to the Apache error log',
        'index': 8
    },
    'secret': {
        'value': '',
        'comment':
        '# The secret value is a random string to be used to generate a secure cookie for access control. The string value can be anything.',
        'index': 9
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
    'db_url': {
        'value': 'localhost',
        'comment': "# The db_url variable is the root URL for your database on the web",
        'index': 1
    },
    'access_control': {
        'value': False,
        'comment': '''
               # Configure access control with True or False.
               # Note that if you want access control, you have to provide a login.txt file inside your /data directory,
               # otherwise access will remain open.''',
        'index': 2
    },
    'access_file': {
        'value': '',
        'comment': '# Location of access file which contains authorized/unauthorized IPs and domain names',
        'index': 3
    },
    'production': {
        'value': True,
        'comment': '# Do not set to False unless you want to make changes in the Web Client in the app/ directory',
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
    'facets': {
        'value': [],
        'comment': '''
               # The facets variable sets which metadata field can be used as a facet
               # The object format is a list of objects like the following: [{'Author': ['author']}, {'Title': ['title', 'author']}
               # The dict key should describe what the facets will do, and the dict value, which has to be a list,
               # should list the metadata to be used for the frequency counts''',
        'index': 8
    },
    'words_facets': {
        'value': [],
        'comment': '''
               # The word_facets variable functions much like the facets variable, but describes metadata
               # attached to word or phrases results and stored in the words table. Experimental.''',
        'index': 9
    },
    'concordance_length': {
        'value': 300,
        'comment': "# The concordance_length variable sets the length in bytes of each concordance result",
        'index': 10
    },
    'search_examples': {
        'value': {},
        'comment': '''
               # The search_examples variable defines which examples should be provided for each searchable field in the search form.
               # If None is the value, or there are any missing examples, defaults will be generated at runtime by picking the first
               # result for any given field. If you wish to change these default values, you should configure them here like so:
               # search_examples = {"author": "Jean-Jacques Rousseau", "title": "Du contrat social"}''',
        'index': 11
    },
    'stopwords': {
        'value': '',
        'comment': '''
               # The stopwords variable defines a file path containing a list of words (one word per line) used for filtering out words
               # in the collocation report. The file must be located in the defined path. If the file is not found,
               # no option for using a stopword list will be displayed in collocation searches.''',
        'index': 12
    },
    'theme': {
        'value': 'default_theme.css',
        'comment': '''
               # The theme variable defines the default CSS theme to be used in the WebApp. The default theme called default_theme.css
               # can be edited directly or you can define a new CSS file below. This file must be located in the app/assets/css/split/ directory for the Web App to find it.''',
        'index': 13
    },
    'dictionary': {
        'value': False,
        'comment':
        '# The dictionary variable enables a different search interface with the headword as its starting point. It is turned off by default',
        'index': 14
    },
    'landing_page_browsing_type': {
        'value': 'default',
        'comment':
        "# The landing_page_browsing_type variable defines what type of landing page. Values available are 'default' or 'dictionary'",
        'index': 15
    },
    'default_landing_page_browsing': {
        'value': [{"label": "Author",
                 "group_by_field": "author",
                 "display_count": True,
                 "queries": ["A-D", "E-I", "J-M", "N-R", "S-Z"],
                 "is_range": True
                },
                {"label": "Title",
                 "group_by_field": "title",
                 "display_count": False,
                 "queries": ["A-D", "E-I", "J-M", "N-R", "S-Z"],
                 "is_range": True
                }],
        'comment': '''
               # The landing_page_browsing variable allows for configuration of navigation by metadata within the landing page.
               # You can choose any document-level metadata (such as author, title, date, genre...) for browsing
               # and define two different types of queries to group your data: ranges and exact matches, i.e. "A-D" or "Comedy".
               # The prepopulated defaults should serve as a guide.''',
        'index': 16
    },
    'default_landing_page_display': {
        'value': {},
        'comment': '''
               # The default landing page display variable allows you to load content by default. It is configured
               # in the same way as default_landing_page_display objects except that you need to define just one
               # range (the one you wish to display) as a string, such as 'A-D'. An empty dict will disable the feature.''',
        'index': 17
    },
    'dico_letter_range': {
        'value': ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T",
                  "U", "V", "W", "X", "Y", "Z"],
        'comment': '''
               # The dico_letter_range variables defines a set of letters corresponding to the first letter of a headword. This generates a set of buttons
               # for browsing the database available on the landing page. The default represents the entire roman alphabet.''',
        'index': 18
    },
    'dico_citation': {
        'value': False,
        'comment': '''
               # The dico_citation variable set to True enables a dictionary citation in concordances. Headword is cited first, followed by author if relevant,
               # or class of knowledge if available.''',
        'index': 19
    },
    'kwic_bibliography_fields': {
        'value': [],
        'comment': '''
                # The kwic_bibliography_fields variable variable defines which bibliography fields will be displayed in the KWIC view. It should be
                # modified with extra care in conjunction with the concordance_citation function located in reports/concordance.py.                # If the variable is an empty list, the first two fields in the metadata variable will be used.
                ''',
        'index': 20
    },
    'kwic_metadata_sorting_fields': {
        'value': [],
        'comment': '''
                # The kwic_metadata_sorting_fields variable allows you to pick wich metadata field can be used for sorting KWIC results.
                ''',
        'index': 21
    },
    'time_series_year_field':{
        'value': 'year',
        'comment': '''
                # The time_series_year_field variable defines which metadata field to use for time series. The year field is built at load time by finding the earliest 4 digit number
                # in multiple date fields.
                ''',
        'index': 22
    }
    'title_prefix_removal': {
        'value': [],
        'comment': '''
                 # The title_prefix_removal variable is only used for displaying titles in a proper order in the landing page browsing function.
                 # It is used to ignore predefined words at the beginning of a title for sorting purposes.
                 # e.g: ["the ", "a "] will ignore "the " and "a " for sorting in titles such as "The First Part of King Henry the Fourth", or "A Midsummer Night's Dream".
                 # Don't forget to add a space after your prefix or the prefix will match partial words.
                 ''',
        'index': 23
    },
    'page_images_url_root': {
        'value': '',
        'comment': '''
                 # The page_images_url_root variable defines a root URL where pages images can be fetched when a filename is provided inside a page tag.
                 # Note that the page image filename must be inside a fac or id attribute such as:
                 # <pb fac="filename.jpg"> or <pb id="filename.jpg">
                 # So a URL of http://my-server.com/images/ will resolve to http://my-server.com/images/filename.jpg.
                 ''',
        'index': 24
    },
    'logo': {
        'value': '',
        'comment': '''
                  # The logo variable defines the location of an image to display on the landing page, just below the
                  # search form. It can be a relative URL, or an absolute link, in which case you want to make sure
                  # it starts with http://. If no logo is defined, no picture will be displayed.
                  ''',
        'index': 25
    },
    'header_in_toc': {
        'value': False,
        'comment': '''
                  # The header_in_toc variable defines whether to display a button to show the header in the table of contents
                  ''',
        'index': 26
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
        #print >> sys.stderr, "INIT", type(self), type(filename), type(defaults)
        self.filename = filename
        abspath = os.path.abspath(filename)
        self.db_path = abspath[:abspath.index("/data/")]
        #print >> sys.stderr, "FILENAME", type(self.filename)
        self.defaults = defaults
        #print >> sys.stderr, "DEFAULTS", type(self.defaults)
        self.header = header
        self.data = {}
        #print >> sys.stderr, "SELF", repr(self)
        self.sorted_defaults = sorted(self.defaults.items(), key=lambda x: x[1]['index'])
        #print >> sys.stderr, "SORTED_DEFAULTS", repr(self.sorted_defaults)
        for key, value in self.sorted_defaults:
            self.data[key] = value['value']

        if self.filename and os.path.exists(self.filename):
            fh = open(self.filename)
            execfile(self.filename, globals(), self.data)
            self.valid_config = True

    def __getitem__(self, item):
        return self.data[item]

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
            string += "\n%s = %s\n" % (key, pretty(self.data[key]))
            written_keys.append(key)
        for key in self.data:
            if key not in written_keys:
                # string += "\n%s = %s\n" % (key,repr(self.data[key]))
                string += "\n%s = %s\n" % (key, pretty(self.data[key]))
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
        return json.dumps(out_obj)


def pretty(value, htchar='\t', lfchar='\n', indent=0):
    '''Pretty printing heavily inspired from a Stack Overflow answer:
    http://stackoverflow.com/questions/3229419/pretty-printing-nested-dictionaries-in-python#answer-26209900.'''
    nlch = lfchar + htchar * (indent + 1)
    if type(value) is dict:
        if value:
            if len(value) == 1:
                return "{%s: %s}" % (repr(value.keys()[0]), pretty(value.values()[0]))
            else:
                items = [nlch + repr(key) + ': ' + pretty(value[key], htchar, lfchar, indent + 1) for key in value]
                return '{%s}' % (','.join(items) + lfchar + htchar * indent)
        else:
            return "{}"
    elif type(value) is list:
        if value:
            if len(value) == 1:
                return "[%s]" % pretty(value[0])
            else:
                items = [nlch + pretty(item, htchar, lfchar, indent + 1) for item in value]
                return '[%s]' % (','.join(items) + lfchar + htchar * indent)
        else:
            return "[]"
    elif type(value) is tuple:
        if value:
            if len(value) == 1:
                return "(%s)" % pretty(value[0])
            else:
                items = [nlch + pretty(item, htchar, lfchar, indent + 1) for item in value]
                return '(%s)' % (','.join(items) + lfchar + htchar * indent)
        else:
            return "()"
    else:
        return repr(value)


def MakeWebConfig(path, **extra_values):
    web_config = Config(path, web_config_defaults, header=web_config_header)
    if extra_values:
        for key, value in extra_values.iteritems():
            if isinstance(key, unicode):
                key = str(key)
            web_config[key] = value
    return web_config


def MakeDBConfig(path, **extra_values):
    db_config = Config(path, db_locals_defaults, header=db_locals_header)
    if extra_values:
        for key, value in extra_values.iteritems():
            if isinstance(key, unicode):
                key = str(key)
            db_config[key] = value
    return db_config


if __name__ == "__main__":
    if sys.argv[1].endswith('cfg'):
        conf = Config(sys.argv[1], web_config_defaults)
    else:
        conf = Config(sys.argv[1], db_locals_defaults)
    print >> sys.stderr, conf
