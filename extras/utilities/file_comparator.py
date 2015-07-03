#!/usr/bin env python

import sys
import os
import re
from collections import defaultdict
from philologic.TagCensus import TagCensus
from philologic.TokenCounter import TokenCounter
from BeautifulSoup import BeautifulStoneSoup as bss


token_regex = re.compile("(\w+)|([\.\!\?])", re.U)

def token_counter(text):
    soup = bss(text)
    plain_text = soup.text
    tokens = defaultdict(int)
    for tok in token_regex.finditer(plain_text):
        token = tok.group(1)
        if token:
            token = token.strip()
        tokens[token] += 1
    return tokens


def find_longest_string(str_list):
    longest_term = 0
    for term in str_list:
        try:
            length = len(term)
        except:
            length = len(str(term)) ## integer
        if length > longest_term:
            longest_term = length
    return longest_term
    

if __name__ == '__main__':
    a = sys.argv[1]
    b = sys.argv[2]
    
    output = open("%s_%s_diff" % (os.path.basename(a), os.path.basename(b)), 'w')

    print "\n### Comparing %s to %s ####\n" % (a,b)
    a_text = open(a).read().decode('utf-8', 'ignore')
    a_tokens = token_counter(a_text)
    a_census = TagCensus()
    a_census.parse(a_text)
    print >> output, "TEXT 1:", a, "done parsing..."
    print >> output, len(a_tokens), "total word tokens\n"

    b_text = open(b).read().decode('utf-8', 'ignore')
    b_tokens = token_counter(b_text)
    b_census = TagCensus()
    b_census.parse(b_text)
    print >> output, "TEXT 2:", b, "done parsing..."
    print >> output, len(b_tokens), "total tokens\n"
    
    print >> output, "### Token differences ###\n"
    token_col_length = find_longest_string(set([word for word in a_tokens] + [word for word in b_tokens]))
    num_col_length = find_longest_string(set([a_tokens[i] for i in a_tokens] + [b_tokens[i] for i in b_tokens]))
    results = []
    row_format = "{0:>%d}{1:>%d}{2:>%d}" % (token_col_length + 5, num_col_length + 5, num_col_length + 5)
    print >> output, row_format.format("TOKENS", "TEXT 1", "TEXT 2")
    print >> output, row_format.format("######", "######", "######")
    for word in a_tokens:
        if word in b_tokens:
            if a_tokens[word] != b_tokens[word]:
                results.append([word, str(a_tokens[word]), str(b_tokens[word])])
        else:
            results.append([word, str(a_tokens[word]), '0'])
    for word in b_tokens:
        if word not in a_tokens:
            results.append([word, '0', str(b_tokens[word])])
    
    for result in results:
        try:
            print >> output, row_format.format(*result)
        except UnicodeEncodeError:
            print >> output, row_format.format(result[0].encode('utf-8'), result[1], result[2])
        except:
            print >> output, row_format.format(repr(result[0]), result[1], result[2])
    print >> output, '\n'

    print >> output, "\n### Tag differences ###"
    print >> output, "What is in %s compared to %s\n" % (b, a)
    print >> output, "START and END correspond to start and end tags. Negative means removed, positive means added"
    print >> output, "EMPTY means that the tag contained nothing, and was therefore removed\n"
    
    census_diff = b_census - a_census
    census_table = []
    header = ["TAG", "START", "END", "MALFORMED", "EMPTY"]
    row_format = u"{0:>12}{1:>12}{2:>12}{3:>12}{4:>12}"
    print >> output, row_format.format(*header)
    print >> output, row_format.format("######", "######", "######", "######", "######")
    for tag in census_diff:
        row = [tag, census_diff[tag]["start"], census_diff[tag]["end"], census_diff[tag]["malformed"], census_diff[tag]["empty"]]
        print >> output, row_format.format(*row)
    print >> output, "\n"
    
    print >> output, "\n\n\n### Unix diff output###\n"
    output.close()
    
    os.system('diff -w %s %s >> %s_%s_diff' % (a, b, os.path.basename(a), os.path.basename(b)))