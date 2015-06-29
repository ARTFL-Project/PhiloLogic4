#!/usr/bin env python

import sys
from philologic.TagCensus import TagCensus
from philologic.TokenCounter import TokenCounter
try:
    from tabulate import tabulate
except ImportError:
    print 'You need to install the tabulate Python module. Run the following:\n pip install tabulate'
    exit()

token_regex = "(\w+)|([\.\!\?])"


if __name__ == '__main__':
    a = sys.argv[1]
    b = sys.argv[2]

    print "\n### Comparing %s to %s ####\n" % (a,b)
    a_tokens = TokenCounter(token_regex)
    a_census = TagCensus(text_target=a_tokens)
    a_census.parse(open(a).read())
    print "TEXT 1:", a, "done parsing..."
    print len(a_tokens.wordcounts), "total word tokens"
    print

    b_tokens = TokenCounter("(\w+)|([\.\!\?])")
    b_census = TagCensus(text_target=b_tokens)
    b_census.parse(open(b).read())
    print "TEXT 2:", b, "done parsing..."
    print len(b_tokens.wordcounts), "total tokens"
    print

    print "### Token differences ###"
    results = []
    for word in a_tokens.wordcounts.keys():
        if word in b_tokens.wordcounts.keys():
            if a_tokens.wordcounts[word] != b_tokens.wordcounts[word]:
                results.append([word, a_tokens.wordcounts[word], b_tokens.wordcounts[word]])
        else:
            results.append([word, a_tokens.wordcounts[word], 0])
    for word in b_tokens.wordcounts.keys():
        if word not in a_tokens.wordcounts.keys():
            results.append([word, 0, b_tokens.wordcounts[word]])

    print tabulate(results, headers=["TOKEN", a, b], tablefmt="grid")

    print "\n### Tag differences ###"
    print "What is in %s compared to %s" % (b, a)
    census_diff = b_census - a_census
    census_table = []
    header = ["TAG", "START", "END", "MALFORMED", "EMPTY"]
    for tag in census_diff.keys():
        row = [tag, census_diff[tag]["start"], census_diff[tag]["end"], census_diff[tag]["malformed"], census_diff[tag]["empty"]]
        census_table.append(row)
    print tabulate(census_table, headers=header, tablefmt="grid")