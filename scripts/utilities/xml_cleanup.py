import sys
import re
from BeautifulSoup import BeautifulStoneSoup as bss
from philologic import TagCensus
#REQUIRES BeautifulSoup3.  BS4 breaks on Python recursion errors when it gets badly damaged texts.

def cleanup(infile,outfile):
# main routine.  takes a file handle for input and output; called at the bottom of the file.
    text = infile.read()
    # custom regexes for things that BeautifulSoup can't handle go here.  Keep to a minimum.  Below examples are for the Encyc.
    # text = re.sub(r"<\?>",r"<gap reason='omitted' unit='character' />",text)
    # text = re.sub(r"<\->",r"<gap reason='omitted' unit='bracket' />",text)
    # text = re.sub(r"<MVO_PIM=\"(.*?)\">",r'<figure><graphic url="\g<1>"></graphic></figure>',text)
    # text = re.sub(r"<omit=(.*?)>",r"<gap reason='omitted' unit='\g<1>' />",text)
    print len(text)
    soup = bss(text,selfClosingTags=self_closing)
    for tag in soup.findAll():
        if tag.name in fix_case:
            tag.name = fix_case[tag.name]
    print >> outfile,soup
    outfile.close()

#Annoyingly, BeautifulSoup requires you to declare ALL self-closing tags yourself; it will badly mangle your text if you miss one, so get this right.
self_closing = []

#BeautifulSoup lowercases all element names; to get things closer to standard TEI, I've included a list here which I use to restore them after parsing
fix_case = {}

total = None

for filename in sys.argv[1:]:
    print >> sys.stderr, "Cleaning %s" % filename
    text = open(filename).read()    

    census = TagCensus()
    census.parse(text)
    print >> sys.stderr, census

    if total:
        total += census
    else:
        total = census

    for tag in census.tags.keys():    
        fix_case[tag.lower()] = tag
        if census[tag]["empty"] != 0:
            self_closing.append(tag)
#    print >> sys.stderr, self_closing
#    print >> sys.stderr, repr(fix_case)
    
    soup = bss(text,selfClosingTags=self_closing)
    for tag in soup.findAll():
        if tag.name in fix_case:
            tag.name = fix_case[tag.name]
    print soup    
    
#    filenameout = filename + ".xml"

#    outfile = open(filenameout,"w")
#    cleanup(infile,outfile)

print >> sys.stderr, total
    
