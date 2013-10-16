#! /usr/bin/env python

#### USAGE ####
#
#./removeHtml3.py file1 file2 file3 ... > out
#
#The "out" file will contain essential statistics about unknown
#entities that were encountered
#
###############

import os, getopt, sys, re
import fnmatch
import shutil
import codecs
import string
#import ents2
import otherentitydefs
import htmlentitydefs
import difflib
#import greek2unicode

"""Other character entity references."""

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
#dgreek = greekentitydefs.name2betacode.copy()

ents_to_ignore = ["quot","amp","lt","gt","apos"]

ents_unknown = []
all_unknown_counts = {}
unknown_counts_per_file = {}

def readFile (fileName):
	fileL = []
	file = codecs.open(fileName, "r")
	s = file.read()
	fileL = string.split(s, '\n')
	return (fileL)

def convert(s):
    """Take an input string s, find all things that look like SGML character
    entities, and replace them with the Unicode equivalent.

    Function is from:
http://stackoverflow.com/questions/1197981/convert-html-entities-to-ascii-in-python/1582036#1582036

    """
    matches = re.findall("&#\d+;", s)
    if len(matches) > 0:
        hits = set(matches)
        for hit in hits:
            name = hit[2:-1]
            try:
                entnum = int(name)
                s = s.replace(hit, unichr(entnum).encode("utf-8"))
            except ValueError:
                ents_unknown.append(name)
    matches = re.findall("&\w+;", s)
    hits = set(matches)
    for hit in hits:
        name = hit[1:-1]
        if name in d and name not in ents_to_ignore:
            s = s.replace(hit, unichr(d[name]).encode('utf-8'))
        elif name in dother and name not in ents_to_ignore:
            s = s.replace(hit, unichr(dother[name]).encode('utf-8'))
#        elif name in dgreek and name not in ents_to_ignore:
#            s = s.replace(hit, dgreek[name])
#        elif name not in d and name not in dother and name not in dgreek:
        elif name not in d and name not in dother:
                ents_unknown.append(name)

    return (ents_unknown, s)


# Iterate through every TEI file passed to script and remove HTML objects

totalfiles = len(sys.argv) - 1
filecount = 0

for file in sys.argv[1:]:

	filecount += 1
	filerange = str(filecount) + "/" + str(totalfiles)

	if file.lower().endswith((('.tei',".xml"))):
		newfilepath = file + ".utf8"

		# check if file exists

		if os.path.isfile(newfilepath):
			print >> sys.stderr, "%s %s (exists)" % (newfilepath, filerange)
		else:
			sys.stderr.write(newfilepath)
			sys.stderr.write(" " + filerange)

			newfile = codecs.open(newfilepath, "w")

			count = 1
			errorLines = []
			ents_unknown = []
			file_contents = []

			file_contents = readFile(file)
			for line in file_contents:

				# test if there's any Latin-1
				try:
					unicode(line,"utf-8","strict")
				except UnicodeError:
					errorLines.append(str(count))

				# Convert HTML entities
#				(ents_unknown, s) = (ents2.convert(line))
				(ents_unknown, s) = (convert(line))
					
				# convert any Greek present
#				s = greek2unicode.convert(s)

				newfile.write(s)
				if count != len(file_contents):
					newfile.write('\n')

				count += 1

			if len(ents_unknown) > 0:
				a = sorted(ents_unknown)
				unknown_counts = {}
				for x in a:
					if x in unknown_counts:
						unknown_counts[x] += 1
					else:
						unknown_counts[x] = 1

					if x in all_unknown_counts:
						all_unknown_counts[x] += 1
					else:
						all_unknown_counts[x] = 1

					if file in unknown_counts_per_file:
						unknown_counts_per_file[file] += 1
					else:
						unknown_counts_per_file[file] = 1

				b = sorted(unknown_counts, key=unknown_counts.get, reverse=True)
				sys.stdout.write("\nunknown XML entities in " + file + ": ")
				for i in range(len(b)):
					sys.stderr.write('.')
					sys.stdout.write(str(b[i]) + " (" + str(unknown_counts[b[i]]) + "), ")
				ents_unknown[:] = []

			if len(errorLines) > 0:
				tmp = ', '.join(errorLines)
				sys.stdout.write("\nLatin-1 in " + file + ": " + tmp)

			sys.stderr.write('\n')

print >> sys.stdout, "Unknown entities:"
for token in all_unknown_counts:
	print >> sys.stdout, "%s: %s" % (token, all_unknown_counts[token])
print >> sys.stdout, "Unknown entities per file:"
for token in unknown_counts_per_file:
	print >> sys.stdout, "%s: %s" % (token, unknown_counts_per_file[token])
