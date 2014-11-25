import sys
import re
import os
import unicodedata
import htmlentitydefs
from BeautifulSoup import BeautifulStoneSoup as bss
from philologic import TagCensus
from optparse import OptionParser
from lxml import etree

#REQUIRES BeautifulSoup3.  BS4 breaks on Python recursion errors when it gets badly damaged texts.



## Build a list of control characters to remove
## http://stackoverflow.com/questions/92438/stripping-non-printable-characters-from-a-string-in-python/93029#93029
all_chars = (unichr(i) for i in xrange(0x110000))
control_chars = ''.join(map(unichr, range(0,32) + range(127,160)))
control_char_re = re.compile('[%s]' % re.escape(control_chars))


##############################################

## Taken from Walt's RemoveHtml3.py script
# maps the SGML entity name to the Unicode codepoint
name2codepoint = {
}

# maps the Unicode codepoint to the HTML entity name
codepoint2name = {}

# maps the HTML entity name to the character
# (or a character reference if the character is outside the Latin-1 range)
entitydefs = {}

for (name, codepoint) in name2codepoint.iteritems():
	codepoint2name[codepoint] = name
	if codepoint <= 0xff:
		entitydefs[name] = chr(codepoint)
	else:
		entitydefs[name] = '&#%d;' % codepoint

"""End of Other character entity references."""

d = htmlentitydefs.name2codepoint.copy()
dother = name2codepoint.copy()

ents_to_ignore = ["quot","amp","lt","gt","apos"]

def convert_remaining_entities(s, quiet):
    """Take an input string s, find all things that look like SGML character
    entities, and replace them with the Unicode equivalent.

    Function is from:
http://stackoverflow.com/questions/1197981/convert-html-entities-to-ascii-in-python/1582036#1582036

    """
    s = s.decode('utf-8', 'ignore')
    
    matches = re.findall("&#\d+;", s)
    if len(matches) > 0:
        hits = set(matches)
        for hit in hits:
            name = hit[2:-1]
            try:
                entnum = int(name)
                s = s.replace(hit, unichr(entnum))
                if not quiet:
                    print >> sys.stderr, "converted %s entity to %s" % (name, unichr(entnum).encode('utf-8'))
            except ValueError:
                pass
    matches = re.findall("&\w+;", s)
    hits = set(matches)
    for hit in hits:
        name = hit[1:-1]
        if name in d and name not in ents_to_ignore:
            s = s.replace(hit, unichr(d[name]))
            if not quiet:
                print >> sys.stderr, "converted %s entity to %s" % (name, unichr(d[name]))
        elif name in dother and name not in ents_to_ignore:
            s = s.replace(hit, unichr(dother[name]))
            if not quiet:
                print >> sys.stderr, "converted %s entity to %s" % (name, unichr(dother[name]))
        elif name not in d and name not in dother:
            s = s.replace(hit, hit.replace('&', "&amp;"))
            if not quiet:
                print >> sys.stderr, "converted invalid entity %s to %s" % (name, hit.replace('&', "&amp;").encode('utf-8'))

    return (s.encode('utf-8'))

#############################################

def parse_command_line(argv):
    usage = "usage: %prog [options] filename"
    parser = OptionParser(usage=usage)
    parser.add_option("-q", "--quiet", action="store_true", default=False, dest="quiet", help="suppress all output from the tag census")
    parser.add_option("-d", "--debug", action="store_true", default=False, dest="debug", help="add debugging to print byte locations of each start/end tag")
    parser.add_option("-s", "--suffix", action="store", default="xml", type="string", dest="suffix", help="define which file extension to use for the cleaned-up file")
    parser.add_option("-o", "--output-dir", action="store", default="", type="string", dest="output_dir", help="define an output directory. The default is the source directory")
    
    ## Parse command-line arguments
    options, args = parser.parse_args(argv[1:])
    if len(args) == 0:
        print >> sys.stderr, "\nError: you did not supply a filename \n"
        parser.print_help()
        sys.exit()
    files = args[:]
        
    debug = options.debug
    quiet = options.quiet
    suffix = '.' + options.suffix
    output_dir = options.output_dir
    
    return files, suffix, output_dir, debug, quiet

def remove_control_chars(s):
    return control_char_re.sub('', s)

#### CUSTOM TAG REPLACEMENTS ####
"""This is where you define custom tag replacements for your file
For instance, to replace <sp> by <p>, you would do {"sp": "p"}
See http://www.tei-c.org/Vault/P4/migrate.html for some guidelines to convert old XML/TEI to TEI P5
If you wish to make changes to attributes, you should edit the lxml iter loop directly"""

xml_tag_mapping = {}

#################################

if __name__ == '__main__':
    files, suffix, output_dir, debug, quiet = parse_command_line(sys.argv)

    if output_dir and not os.path.exists(output_dir):
        os.system('mkdir -p %s' % output_dir)
    
    total = None
    
    for filename in files:
        print >> sys.stderr, "Cleaning %s" % filename
        text = open(filename).read().decode('utf-8', 'ignore')
        text = remove_control_chars(text)
    
        census = TagCensus()
        census.parse(text)
        
        if not quiet:
            try:
                print >> sys.stderr, census
            except UnicodeEncodeError:
                print >> sys.stderr, unicode(census).encode('utf-8')
    
        #if total:
        #    total += census
        #else:
        #    total = census
    
        #Annoyingly, BeautifulSoup requires you to declare ALL self-closing tags yourself; it will badly mangle your text if you miss one, so get this right.
        self_closing = []

        #BeautifulSoup lowercases all element names; to get things closer to standard TEI, I've included a list here which I use to restore them after parsing
        fix_case = {}
    
        for tag in census.tags.keys():    
            fix_case[tag.lower()] = tag
            if census[tag]["empty"] != 0:
                self_closing.append(tag)
        
        soup = bss(text,selfClosingTags=self_closing)
        for tag in soup.findAll():
            if tag.name in fix_case:
                tag.name = fix_case[tag.name]
                
        file_contents = soup.prettify()
        file_contents = convert_remaining_entities(file_contents, quiet)
        
        try:
            tree = etree.fromstring(file_contents)
            for el in tree.iter():
                ## Tags are defined as el.tag, so to change tag, you do: el.tag = "some_other_tag"
                ## Attributes are contained in el.attrib where each attribute is a key. To change the type attribute you do: el.attrib['type'] = "some_other_type"
                if el.tag in xml_tag_mapping: ## Check if the tag should be replaced according to the xml mapping dict
                    el.tag = xml_tag_mapping[el.tag]
            file_contents = etree.tostring(tree)
        except:
            print >> sys.stderr, "The clean-up script did not manage to fix all your XML issues"
            print >> sys.stderr, 'Try running "xmllint -noout" on the output file to get a more complete error report'

        if output_dir:
            filename = output_dir + '/' + os.path.basename(filename) + suffix
        else:
            filename = filename + suffix

        outfile = open(filename, 'w')
        print >> outfile, file_contents
        outfile.close()
    
    #print >> sys.stderr, total
    
