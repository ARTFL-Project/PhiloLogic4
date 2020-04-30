import sys
import re
import os
import html.entities
import traceback
from philologic5 import TagCensus
from optparse import OptionParser
from lxml import etree
from collections import defaultdict
from philologic5.runtime.FragmentParser import parse as FragmentParserParse
from html import unescape as unescape_html


## Build a list of control characters to remove
## http://stackoverflow.com/questions/92438/stripping-non-printable-characters-from-a-string-in-python/93029#93029
all_chars = (chr(i) for i in range(0x110000))
control_chars_range = list(range(0, 32)) + list(range(127, 160))
control_chars_range.remove(9)
control_chars_range.remove(10)
control_chars_range.remove(13)  ## Keeping newlines, carriage returns and tabs
control_chars = "".join(map(chr, control_chars_range))
control_char_re = re.compile("[%s]" % re.escape(control_chars))


##############################################

## Taken from Walt's RemoveHtml3.py script
# maps the SGML entity name to the Unicode codepoint
name2codepoint = {}

# maps the Unicode codepoint to the HTML entity name
codepoint2name = {}

# maps the HTML entity name to the character
# (or a character reference if the character is outside the Latin-1 range)
entitydefs = {}

for (name, codepoint) in name2codepoint.items():
    codepoint2name[codepoint] = name
    if codepoint <= 0xFF:
        entitydefs[name] = chr(codepoint)
    else:
        entitydefs[name] = "&#%d;" % codepoint

"""End of Other character entity references."""

d = html.entities.name2codepoint.copy()
dother = name2codepoint.copy()

ents_to_ignore = ["quot", "amp", "lt", "gt", "apos"]

invalid_entities = defaultdict(int)


def convert_remaining_entities(s, quiet):
    """Take an input string s, find all things that look like SGML character
    entities, and replace them with the Unicode equivalent.

    Function is from:
http://stackoverflow.com/questions/1197981/convert-html-entities-to-ascii-in-python/1582036#1582036

    """

    matches = re.findall(r"&#\d+;", s)
    if len(matches) > 0:
        hits = set(matches)
        for hit in hits:
            name = hit[2:-1]
            try:
                entnum = int(name)
                s = s.replace(hit, chr(entnum))
                if not quiet:
                    print("converted %s entity to '%s'" % (name, chr(entnum).encode("utf-8")), file=sys.stderr)
            except ValueError:
                pass
    matches = re.findall(r"&\w+;", s)
    hits = set(matches)
    for hit in hits:
        name = hit[1:-1]
        if name in d and name not in ents_to_ignore:
            s = s.replace(hit, chr(d[name]))
            if not quiet:
                print("converted %s entity to '%s'" % (name, chr(d[name])), file=sys.stderr)
        elif name in dother and name not in ents_to_ignore:
            s = s.replace(hit, chr(dother[name]))
            if not quiet:
                print("converted %s entity to '%s'" % (name, chr(dother[name])), file=sys.stderr)
        elif name not in d and name not in dother:
            s = s.replace(hit, hit.replace("&", "&amp;"))
            print(
                "converted invalid entity %s to '%s'" % (name, hit.replace("&", "&amp;").encode("utf-8")),
                file=sys.stderr,
            )
            invalid_entities[name] += 1

    return s


#############################################


def parse_command_line(argv):
    usage = "usage: %prog [options] filename"
    parser = OptionParser(usage=usage)
    parser.add_option(
        "-q",
        "--quiet",
        action="store_true",
        default=False,
        dest="quiet",
        help="suppress all output from the tag census",
    )
    parser.add_option(
        "-d",
        "--debug",
        action="store_true",
        default=False,
        dest="debug",
        help="add debugging to print byte locations of each start/end tag",
    )
    parser.add_option(
        "-s",
        "--suffix",
        action="store",
        default="fixed",
        type="string",
        dest="suffix",
        help="define which file extension to use for the cleaned-up file",
    )
    parser.add_option(
        "-o",
        "--output-dir",
        action="store",
        default="./cleaned",
        type="string",
        dest="output_dir",
        help="define an output directory. The default is the source directory",
    )

    ## Parse command-line arguments
    options, args = parser.parse_args(argv[1:])
    if len(args) == 0:
        print("\nError: you did not supply a filename \n", file=sys.stderr)
        parser.print_help()
        sys.exit()
    files = args[:]

    debug = options.debug
    quiet = options.quiet
    output_dir = options.output_dir

    return files, output_dir, debug, quiet


def remove_control_chars(s):
    return control_char_re.sub("", s)


#### CUSTOM TAG REPLACEMENTS ####
"""This is where you define custom tag replacements for your file
For instance, to replace <sp> by <p>, you would do {"sp": "p"}
See http://www.tei-c.org/Vault/P4/migrate.html for some guidelines to convert old XML/TEI to TEI P5
If you wish to make changes to attributes, you should edit the lxml iter loop directly"""

xml_tag_mapping = {
    ## TEI P4 => TEI P5 conversions
    "TEI.2": "TEI",
    "xref": "ref",
    "xptr": "ptr",
}

#################################

if __name__ == "__main__":
    files, output_dir, debug, quiet = parse_command_line(sys.argv)

    if output_dir and not os.path.exists(output_dir):
        os.system("mkdir -p %s" % output_dir)

    total = None

    failed_files = []
    for filename in files:
        print("Cleaning %s" % filename, file=sys.stderr)
        text = open(filename).read()
        text = remove_control_chars(text)

        census = TagCensus()
        census.parse(text)

        if not quiet:
            try:
                print(census, file=sys.stderr)
            except UnicodeEncodeError:
                print(str(census).encode("utf-8"), file=sys.stderr)

        if total:
            total += census
        else:
            total = census

        ## First round of cleanups
        xml = FragmentParserParse(text)
        file_contents = etree.tostring(xml).decode("utf8", "ignore")
        file_contents = convert_remaining_entities(file_contents, quiet)

        # Tag replacements
        try:
            parser = etree.XMLParser(huge_tree=True, remove_blank_text=True, strip_cdata=False)
            tree = etree.fromstring(file_contents, parser=parser)
            for el in tree.iter():
                ## Tags are defined as el.tag, so to change tag, you do: el.tag = "some_other_tag"
                ## Attributes are contained in el.attrib where each attribute is a key. To change the type attribute you do: el.attrib['type'] = "some_other_type"
                if el.tag in xml_tag_mapping:  ## Check if the tag should be replaced according to the xml mapping dict
                    el.tag = xml_tag_mapping[el.tag]
            file_contents = etree.tostring(tree, pretty_print=True).decode("utf8")
        except Exception as e:
            traceback.print_exc()
            print("The clean-up script did not manage to fix all your XML issues", file=sys.stderr)
            print(
                'Try running "xmllint -noout" on the output file to get a more complete error report', file=sys.stderr
            )
            failed_files.append(filename)

        filename = os.path.join(output_dir, os.path.basename(filename))

        # Convert HTML entities:
        file_contents = unescape_html(file_contents)
        with open(filename, "w") as outfile:
            lines = file_contents.split("\n")
            outfile.write("\n".join(lines[1:-1]))

    try:
        print(total, file=sys.stderr)
    except UnicodeEncodeError:
        print(str(total).encode("utf-8"))

    if invalid_entities:
        print("##### Undeclared entities present in files.######", file=sys.stderr)
        print("To resolve, add definitions in this script", file=sys.stderr)
        for k, v in invalid_entities.items():
            print("\t\t".join([k, str(v)]))

    if failed_files:
        print("The following files were not converted due to failure:")
        print("\n".join(failed_files))
