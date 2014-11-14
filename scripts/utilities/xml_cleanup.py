import sys
import re
import os
import unicodedata
import htmlentitydefs
from BeautifulSoup import BeautifulStoneSoup as bss
from philologic import TagCensus
from optparse import OptionParser

#REQUIRES BeautifulSoup3.  BS4 breaks on Python recursion errors when it gets badly damaged texts.


## Build a list of control characters to remove
## http://stackoverflow.com/questions/92438/stripping-non-printable-characters-from-a-string-in-python/93029#93029
all_chars = (unichr(i) for i in xrange(0x110000))
control_chars = ''.join(map(unichr, range(0,32) + range(127,160)))
control_char_re = re.compile('[%s]' % re.escape(control_chars))


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


if __name__ == '__main__':
    files, suffix, output_dir, debug, quiet = parse_command_line(sys.argv)

    if output_dir and not os.path.exists(output_dir):
        os.system('mkdir -p %s' % output_dir)
    
    total = None
    
    for filename in files:
        print >> sys.stderr, "Cleaning %s" % filename
        text = open(filename).read().decode('latin-1')
        text = remove_control_chars(text)
    
        census = TagCensus()
        census.parse(text)
        
        if not quiet:
            print >> sys.stderr, census
    
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
    #    print >> sys.stderr, self_closing
    #    print >> sys.stderr, repr(fix_case)
        
        soup = bss(text,selfClosingTags=self_closing, convertEntities=bss.HTML_ENTITIES)
        for tag in soup.findAll():
            if tag.name in fix_case:
                tag.name = fix_case[tag.name]

        if output_dir:
            filename = output_dir + '/' + os.path.basename(filename) + suffix
        else:
            filename = filename + suffix

        outfile = open(filename, 'w')
        print >> outfile, soup.prettify()
        outfile.close()
    
    #print >> sys.stderr, total
    
