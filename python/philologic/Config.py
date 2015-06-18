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
    'debug': {
        'value': False,
        'comment': '# If set to True, this enabled debugging messages to be printed out to the Apache error log',
        'index': 7
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
    'production': {
        'value': True,
        'comment': '# Do not set to False unless you want to make changes in the Web Client in the app/ directory',
        'index': 3
    },
    'search_reports': {
        'value': ['concordance', 'kwic', 'collocation', 'time_series'],
        'comment': '''
               # The search_reports variable sets which search report is viewable in the search form
               # Available reports are concordance, kwic, collocation, and time_series''',
        'index': 4
    },
    'metadata': {
        'value': [],
        'comment': "# The metadata variable sets which metadata field is viewable in the search form",
        'index': 5
    },
    'metadata_aliases': {
        'value': {},
        'comment': '''
               #The metadata_aliases variable allows to display a metadata variable under a different name in the HTML
               # For example, you could rename the who metadata to Speaker, and the create_date variable to Date like so:
               # metadata_aliases = {'who': 'Speaker', 'create_date', 'Date'}''',
        'index': 6
    },
    'facets': {
        'value': [],
        'comment': '''
               # The facets variable sets which metadata field can be used as a facet
               # The object format is a list of objects like the following: [{'Author': 'author'}, {'Title': ['title', 'author']}
               # The dict key should describe what the facets will do, and the dict value, which can be a string or a list,
               # should list the metadata to be used for the frequency counts''',
        'index': 7
    },
    'words_facets': {
        'value': [],
        'comment': '''
               # The word_facets variable functions much like the facets variable, but describes metadata
               # attached to word or phrases results and stored in the (optional) words table. Experimental.''',
        'index': 8
    },
    'concordance_length': {
        'value': 300,
        'comment': "# The concordance_length variable sets the length in bytes of each concordance result",
        'index': 9
    },
    'search_examples': {
        'value': {},
        'comment': '''
               # The search_examples variable defines which examples should be provided for each searchable field in the search form.
               # If None is the value, or there are any missing examples, defaults will be generated at runtime by picking the first
               # result for any given field. If you wish to change these default values, you should configure them here like so:
               # search_examples = {"author": "Jean-Jacques Rousseau", "title": "Du contrat social"}''',
        'index': 10
    },
    'stopwords': {
        'value': '',
        'comment': '''
               # The stopwords variable defines a file path containing a list of words (one word per line) used for filtering out words
               # in the collocation report. The file must be located in the defined path. If the file is not found,
               # no option for using a stopword list will be displayed in collocation searches.''',
        'index': 11
    },
    'theme': {
        'value': 'default_theme.css',
        'comment': '''
           # The theme variable defines the default CSS theme to be used in the WebApp. The default theme called default_theme.css
           # can be edited directly or you can define a new CSS file below. This file must be located in the app/assets/css/split/ directory for the Web App to find it.''',
        'index': 12
    },
    'dictionary': {
        'value': False,
        'comment': '# The dictionary variable enables a different search interface with the headword as its starting point. It is turned off by default',
        'index': 13
    },
    'landing_page_browsing_type': {
        'value': 'default',
        'comment': "# The landing_page_browsing_type variable defines what type of landing page. Values available are 'default' or 'dictionary'",
        'index': 14
    },
    'landing_page_browsing': {
        'value': {"author": ["A-D", "E-I", "J-M", "N-R", "S-Z"], "title": ["A-D", "E-I", "J-M", "N-R", "S-Z"], "date": {}, "default_display": {}},
        'comment': '''
               # The landing_page_browsing variable defines which browsing functions are exposed in the landing page. The only options
               # are author, title, date, and default_display. For author and title, you have to define a list of ranges, such as 'author': ['A-L', 'M-Z'],
               # and for date you need to define three variables: start_date, end_date, interval: e.g. "date": {"start": 1600, "end": 1800, "interval": 25}
               # default_display allows you to load content by default. It is a dictionary that contains a type and a range, e.g. = "default_display": {"type": "title", "range": "A-D"}
               # Note that no default is provided for "date" or default_value: they are therefore disabled''',
        'index': 15
    },
    'dico_letter_range': {
        'value': ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"],
        'comment': '''
               # The dico_letter_range variables defines a set of letters corresponding to the first letter of a headword. This generates a set of buttons
               # for browsing the database available on the landing page. The default represents the entire roman alphabet.''',
        'index': 16
    },
    'kwic_bibliography_fields': {
         'value': [],
         'comment': '''
                # The kwic_bibliography_fields variable variable defines which bibliography fields will be displayed in the KWIC view. It should be
                # modified with extra care in conjunction with the concordance_citation function located in reports/concordance.py.                # If the variable is an empty list, the first two fields in the metadata variable will be used.
                ''',
         'index': 17
     },
     'title_prefix_removal': {
          'value': [],
          'comment': '''
                 # The title_prefix_removal variable is only used for displaying titles in a proper order in the landing page browsing function.
                 # It is used to ignore predefined words at the beginning of a title for sorting purposes.
                 # e.g: ["the ", "a "] will ignore "the " and "a " for sorting in titles such as "The First Part of King Henry the Fourth", or "A Midsummer Night's Dream".
                 # Don't forget to add a space after your prefix or the prefix will match partial words.
                 ''',
          'index': 18
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
        self.sorted_defaults = sorted(self.defaults.items(),key=lambda x:x[1]['index'])
        #print >> sys.stderr, "SORTED_DEFAULTS", repr(self.sorted_defaults)
        for key,value in self.sorted_defaults:
            self.data[key] = value['value']

        if self.filename and os.path.exists(self.filename):
            fh = open(self.filename)
            execfile(self.filename,globals(),self.data)

    def __getitem__(self, item):
        return self.data[item]
  
    def __getattr__(self,key):
        return self[key]
   
    def __setitem__(self, item, value):
        self.data[item] = value
  
    def __str__(self):
        string = "\n".join([line.strip() for line in self.header.splitlines() if line.strip()]) + '\n\n'
        written_keys = []
        for key,value in self.sorted_defaults:
            if value["comment"]:
                string += "\n" + "\n".join(line.strip() for line in value["comment"].splitlines() if line.strip())
            string += "\n%s = %s\n" % (key,repr(self.data[key]))
            written_keys.append(key)
        for key in self.data:
            if key not in written_keys:
                string += "\n%s = %s\n" % (key,repr(self.data[key]))
                written_keys.append(key)
        return string
  
    def to_json(self):
        out_obj = {}
        written = []
        for key,value in self.sorted_defaults:
            out_obj[key] = self.data[key]
            written.append(key)
        for key in self.data:
            if key not in written:
                out_obj[key] = self.data[key]
                written.append(key)
        return json.dumps(out_obj)

def MakeWebConfig(path, **extra_values):
    web_config = Config(path, web_config_defaults, header=web_config_header)
    if extra_values:
        for key, value in extra_values.iteritems():
            web_config[key] = value
    return web_config

def MakeDBConfig(path, **extra_values):
    db_config = Config(path, db_locals_defaults, header=db_locals_header)
    if extra_values:
        for key, value in extra_values.iteritems():
            db_config[key] = value
    return db_config

if __name__ == "__main__":
    if sys.argv[1].endswith('cfg'):
        conf = Config(sys.argv[1],web_config_defaults)
    else:
        conf = Config(sys.argv[1],db_locals_defaults)
    print >> sys.stderr, conf
