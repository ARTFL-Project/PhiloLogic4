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

#del name, codepoint
