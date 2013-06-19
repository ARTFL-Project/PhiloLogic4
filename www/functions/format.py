#!/usr/bin/env python

import re
import htmlentitydefs
import sys
import ObjectFormatter as Formatter
from custom_object_format import custom_format
from lxml import etree
from StringIO import StringIO

def adjust_bytes(bytes, length):
    """Readjust byte offsets for concordance"""
    bytes = sorted(bytes) # bytes aren't stored in order
    byte_start = bytes[0] - (length / 2)
    first_hit =  length / 2
    if byte_start < 0:
        first_hit = first_hit + byte_start ## this is a subtraction really
        byte_start = 0
    new_bytes = []
    for pos, word_byte in enumerate(bytes):
        if pos == 0:
            new_bytes.append(first_hit)
        else:
            new_bytes.append(word_byte - byte_start)
    return new_bytes, byte_start


def chunkifier(conc_text, bytes, kwic=False, highlight=False):
    """Divides the passage in three:
    * from the beginning to the first hit (not included)
    * from the first hit to the end of the last hit
    * form the end of the last hit to the end of the passage
    Returns a tuple containing all three parts of the passage"""
    #conc_text = re.sub("[ \n\r]+\w*$", "", conc_text) ## no words cut out, or worse, no broken mutiple-byte chars
    conc_start = conc_text[:bytes[0]]
    conc_middle = ''
    end_byte = 0
    for pos, word_byte in enumerate(bytes):
        if highlight: 
            text, end_byte = highlighter(conc_text[word_byte:])
            end_byte = word_byte + end_byte
        else:
            text_chunks = re.split("([^ \.,;:?!\'\-\"\n\r\t\(\)]+)", conc_text[word_byte:])
            end_byte = word_byte + len(text_chunks[1])
            text = text_chunks[1]
        conc_middle += text
        if len(bytes) > pos+1:
            conc_middle += conc_text[end_byte:bytes[pos+1]]
    conc_end = conc_text[end_byte:]
    
    ## Make sure we have no words cut out
    conc_start = re.sub("^[^ ]+ ", "", conc_start)
    conc_end = re.sub(" [^ ]+$", "", conc_end)
    
    return conc_start, conc_middle, conc_end


def highlighter(text):
    """This function highlights a passage based on the hit's byte offset"""

    breaker = re.match(r"([^ \.,;:?!\'\-\"\n\r\t\(\)]+)",text)
    if breaker:
        end_byte = breaker.end()
    else:
        end_byte = len(text)

    r_text = '<span class="highlight">' + text[:end_byte] + '</span>' # 0 element is always an empty string
    return r_text, end_byte


def clean_text(text, notag=True, kwic=False, collocation=False):
    """Cleans your text, and by default removes all tags"""
    text = re.sub("^[^<]*?>","",text)
    text = re.sub("<[^>]*?$","",text)
    if notag:
        text = re.sub("<.*?>","",text)
    if kwic:
        text = text.replace('\n', ' ')
        text = text.replace('\r', '')
        text = text.replace('\t', ' ')
        ## Assuming that the highlight tag is a <span>
        temp_text = re.sub('<(/?span.*?)>', '[\\1]', text)
        temp_text = re.sub('<.*?>', '', temp_text)
        text = re.sub('\[(/?span.*?)\]', '<\\1>', temp_text)
        text = re.sub(' {2,}', ' ', text)
    if collocation:
        text = re.sub("-", " ", text)
        text = re.sub("&dot;", " ", text)
        text = re.sub("&nbsp;", " ", text)
        text = re.sub("&amp;", " ", text)
        text = re.sub("&.aquo;", " ", text)
        text = re.sub("&.squo;", " ", text)
        text = re.sub("&ldquo;", " ", text)
        text = re.sub("&rdquo;", " ", text)
        text = re.sub("&.dash;", " ", text)
        text = re.sub("&lt;", " ", text)
        text = re.sub("&gt;", " ", text)
        text = re.sub("&hyphen;", " ", text)
        text = re.sub("&colon;", " ", text)
        text = re.sub("&excl;", " ", text)
        text = re.sub("\xe2\x80\x9c", "", text) ## ldquo
        text = re.sub("\xe2\x80\x9d", "", text) ## rdquo
        text = re.sub("\"", " ", text)
        text = re.sub(" +", " ", text)
        text = re.sub("^  *", "", text)
        text = re.sub("  *$", "", text)
        text = re.sub("[^a-zA-Z'\177-\344 ]", " ", text) ## getting rid of '&' and ';' from orig.##
        text = text.decode('utf-8', 'ignore')
    return text
  
  
def align_text(text, byte_num, chars=40):
    """This function is meant for formating text for KWIC results"""
    start_hit = text.index('<span class="highlight">')
    end_hit = text.rindex('</span>') + 7
    tag_length = 7 * byte_num
    start_text = convert_entities(text[:start_hit])
    if len(start_text) < chars:
        white_space = ' ' * (chars - len(start_text))
        start_text = white_space + start_text
    start_text = '<span style="white-space:pre-wrap;">' + start_text[-chars:] + '</span>'
    end_text = convert_entities(text[end_hit:])
    match = convert_entities(text[start_hit:end_hit])
    return start_text + match + end_text[:chars+tag_length]
   
    
def clean_word(word):
    """Removes any potential non-word characters"""
    word = re.sub("[0-9]* ", "", word)
    word = re.sub("[\s]*", "", word)
    word = word.replace('\n', '')
    word = word.replace('\r', '')
    return word


def tokenize_text(text):
    """Returns a list of individual tokens"""
    text = text.lower()
    text_tokens = re.split(r"([^ \.,;:?!\'\-\"\n\r\t\(\)]+)|([\.;:?!])", text) ## this splits on whitespaces and punctuation
    text_tokens = [clean_word(token) for token in text_tokens if token] ## remove empty strings
    return text_tokens
 
   
def fix_html(text):
    """Fixes broken HTML tags"""
    html = etree.HTML(text)
    return etree.tostring(html, pretty_print=True, method="html")
 
def convert_entities(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)

def formatter(text):
    """This function calls an external script containing a dictionnary with formatting
    options for proper display in the web browser"""
    return Formatter.format(text)