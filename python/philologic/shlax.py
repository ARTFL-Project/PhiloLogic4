#!/usr/bin/python3
# ShLaX-- a Shallow Lazy XML tokenizer.  Very useful for dirty, broken XML-like documents.


import re
import sys

TextSE = "(?P<Text>[^<]+)"
UntilHyphen = "[^-]*-"
Until2Hyphens = UntilHyphen + "([^-]" + UntilHyphen + ")*-"
CommentCE = Until2Hyphens + ">?"
UntilRSBs = "[^]]*]([^]]+])*]+"
CDATA_CE = UntilRSBs + "([^]>]" + UntilRSBs + ")*>"
S = "[ \\n\\t\\r]+"
NameStrt = "[A-Za-z_:]|[^\\x00-\\x7F]"
NameChar = "[A-Za-z0-9_:.-]|[^\\x00-\\x7F]"
Name = "(" + NameStrt + ")(" + NameChar + ")*"
QuoteSE = '"[^"]' + "*" + '"' + "|'[^']*'"
DT_IdentSE = S + Name + "(" + S + "(" + Name + "|" + QuoteSE + "))*"
MarkupDeclCE = "([^]\"'><]+|" + QuoteSE + ")*>"
S1 = "[\\n\\r\\t ]"
UntilQMs = "[^?]*\\?+"
PI_Tail = "\\?>|" + S1 + UntilQMs + "([^>?]" + UntilQMs + ")*>"
DT_ItemSE = (
    "<(!(--" + Until2Hyphens + ">|[^-]" + MarkupDeclCE + ")|\\?" + Name + "(" + PI_Tail + "))|%" + Name + "|" + S
)
DocTypeCE = DT_IdentSE + "(" + S + ")?(\\[(" + DT_ItemSE + ")*](" + S + ")?)?>?"
DeclCE = "--(" + CommentCE + ")?|\\[CDATA\\[(" + CDATA_CE + ")?|DOCTYPE(" + DocTypeCE + ")?"
PI_CE = Name + "(" + PI_Tail + ")?"
EndTagCE = "(?P<EndTagName>" + Name + ")(" + S + ")?>?"
AttValSE = '"(?P<DQAttVal>[^<"]' + "*" + ')"' + "|'(?P<SQAttVal>[^<']*)'"
ElemTagCE = Name + "(?P<Attributes>(" + S + Name + "(" + S + ")?=(" + S + ")?(" + AttValSE + "))*)(" + S + ")?/?>?"
MarkupSPE = (
    "<(?P<Decl>!("
    + DeclCE
    + ")?|\\?(?P<PI>"
    + PI_CE
    + ")?|/(?P<EndTag>"
    + EndTagCE
    + ")?|(?P<ElemTag>"
    + ElemTagCE
    + ")?)"
)
XML_SPE = TextSE + "|" + MarkupSPE

ElemTagSPE = (
    "<(?P<ElemName>"
    + Name
    + ")(?P<Attributes>("
    + S
    + Name
    + "("
    + S
    + ")?=("
    + S
    + ")?("
    + AttValSE
    + "))*)("
    + S
    + ")?(?P<Empty>/)?>?"
)
AttributeSPE = S + "(?P<AttName>" + Name + ")(" + S + ")?=(" + S + ")?(?P<AttVal>" + AttValSE + ")"

CharRef = "&#[0-9]+;|&#x[0-9a-fA-F]+;"
EntityRef = "&" + Name + ";"

oldpattern = r"<[^>]+>"
pattern = MarkupSPE


def parsestring(string):
    matches = re.finditer(XML_SPE, string)
    for m in matches:
        att = {}
        name = ""
        empty = False
        match_start = m.start(0)
        match_end = m.end(0)
        content = m.group(0)
        if m.group("Text"):
            type = "text"
        elif m.group("EndTag"):
            type = "EndTag"
            name = m.group("EndTagName")
        elif m.group("ElemTag"):
            type = "StartTag"
            em = re.match(ElemTagSPE, m.group(0))
            if em.group("Empty"):
                empty = True
            name = em.group("ElemName")
            attributes = em.group("Attributes")
            amatches = re.finditer(AttributeSPE, attributes)
            for am in amatches:
                ad = am.groupdict()
                aname = am.group("AttName")
                aval = ad["DQAttVal"] or ad["SQAttVal"]
                att[aname] = aval
        else:
            type = "Markup"
        yield node(m.group(0), type, match_start, name, att)
        if empty:
            yield node("", "EndTag", match_end, name, {})


class parser:
    def __init__(self, file):
        self.f = file
        self.line = 0

    def __iter__(self):
        buffer = ""
        buffer_offset = 0
        self.f.seek(0)
        self.line = 0
        for line in self.f.readlines():
            self.line += 1
            buffer = buffer + line
            last_end = 0
            matches = re.finditer(pattern, buffer)
            for m in matches:
                att = {}
                name = ""
                empty = False
                match_start = buffer_offset + m.start(0)
                match_end = buffer_offset + m.end(0)
                text = buffer[last_end : m.start(0)]
                if text:
                    yield node(text, "text", buffer_offset + last_end)
                if m.group("EndTag"):
                    type = "EndTag"
                    name = m.group("EndTagName")
                elif m.group("ElemTag"):
                    type = "StartTag"
                    em = re.match(ElemTagSPE, m.group(0))
                    if em.group("Empty"):
                        empty = True
                    name = em.group("ElemName")
                    attributes = em.group("Attributes")
                    amatches = re.finditer(AttributeSPE, attributes)
                    for am in amatches:
                        ad = am.groupdict()
                        aname = am.group("AttName")
                        aval = ad["DQAttVal"] or ad["SQAttVal"]
                        att[aname] = aval
                else:
                    type = "Markup"
                yield node(buffer[m.start(0) : m.end(0)], type, match_start, name, att)
                if empty:
                    yield node("", "EndTag", match_end, name, {})
                last_end = m.end(0)
            buffer_offset += last_end
            buffer = buffer[last_end:]
        if buffer:
            yield node(buffer, "text", buffer_offset)
        raise StopIteration


class node:
    def __init__(self, content, type, start, name="", attributes={}):
        self.content = content
        self.type = type
        self.name = name
        self.start = start
        self.attributes = attributes

    def __str__(self):
        return self.content

    def __repr__(self):
        r = "shlax.node(" + repr(self.content) + ", "
        r += self.type
        r += ", " + str(self.start) + ", " + self.name + ", " + repr(self.attributes)
        return r


if __name__ == "__main__":
    for file in sys.argv[1:]:
        f = open(file)
        s = f.read()
        l = []
        f.seek(0)  # reset the filehandle.
        buffer = ""
        buffer_offset = 0
        l2 = []
        s2 = ""
        for line in f.readlines():
            buffer = buffer + line
            matches = re.finditer(pattern, buffer)
            for m in matches:
                l2.append((m.group(0), buffer_offset + m.start(0)))
            buffer_offset += len(line)
        print(len(l2))
        for pair in zip(l, l2):
            if l != l2:
                print(str(l) + str(l2))
