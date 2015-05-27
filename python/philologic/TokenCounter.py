import re
import sys
from philologic.TagCensus import TagCensus

class TokenCounter(object):
    def __init__(self,token_regex):
        self.buffers = []
        self.totalcount = 0
        self.wordcounts = {}
        self.whitespace = 0
        self.token_regex = token_regex

    def feed(self,text):
        self.buffers += [text.decode("utf-8")]

    def close(self):
        temp_buffer = "".join(buf for buf in self.buffers)
        temp_position = 0
        for tok in re.finditer(self.token_regex,temp_buffer, re.U):
            if tok.group(1):
                tok_type = "word"
                word = tok.group(1)
                if word in self.wordcounts:
                    self.wordcounts[word] += 1
                else:
                    self.wordcounts[word] = 1
            elif tok.group(2):
                tok_type = "sent"
            tok_length = len(tok.group())
            tok_start = len(temp_buffer[:tok.start()])
            tok_end = len(temp_buffer[:tok.end()])
            while (tok_start >= (temp_position + len(self.buffers[0]))):
                temp_position += len(self.buffers[0])
                discard = self.buffers.pop(0)
            start = tok_start - temp_position
            while (tok_end >= (temp_position + len(self.buffers[0]))):
                temp_position += len(self.buffers[0])
                discard = self.buffers.pop(0)
                if self.buffers:
                    pass
                else:
                    break
            end = tok_end - temp_position

if __name__ == "__main__":
    a = sys.argv[1]
    b = sys.argv[2]

    print "start"
    a_tokens = TokenCounter("(\w+)|([\.\!\?])")    
    a_census = TagCensus(text_target=a_tokens)
    a_census.parse(open(a).read())
    print a, "done"
#    print a,a_tokens.wordcounts

    b_tokens = TokenCounter("(\w+)|([\.\!\?])")
    b_census = TagCensus(text_target=b_tokens)
    b_census.parse(open(b).read())
    print b, "done"
#    print b,b_tokens.wordcounts

    for word in a_tokens.wordcounts.keys():
        if word in b_tokens.wordcounts.keys():
            if a_tokens.wordcounts[word] != b_tokens.wordcounts[word]:
                print word,a_tokens.wordcounts[word],b_tokens.wordcounts[word]
        else:
            print word,a_tokens.wordcounts[word],0
    for word in b_tokens.wordcounts.keys():
        if word not in a_tokens.wordcounts.keys():
            print word, 0, b_tokens.wordcounts[word]

    census_diff = a_census - b_census
    for tag in census_diff.keys():
        print tag, census_diff[tag]
