import sys
import os
import re
import StringIO
from philologic import OHCOVector


class PlainTextParser(object):

    def __init__(self,
                 output,
                 docid,
                 filesize,
                 token_regex=r"(\w+)|([\.\?\!])",
                 xpaths=[("doc", "./")],
                 metadata_xpaths=[],
                 suppress_tags=[],
                 pseudo_empty_tags=[],
                 known_metadata={}):
        self.types = ["doc", "div1", "div2", "div3", "para", "sent", "word"]
        self.parallel_type = "page"
        self.output = output
        self.docid = docid
        ## Initialize an OHCOVector Stack. operations on this stack produce all parser output.
        self.v = OHCOVector.CompoundStack(self.types, self.parallel_type, docid, output)

        self.filesize = filesize

        self.token_regex = token_regex
        self.xpaths = xpaths[:]
        self.metadata_xpaths = metadata_xpaths[:]

        self.suppress_xpaths = suppress_tags
        self.pseudo_empty_tags = pseudo_empty_tags
        self.known_metadata = known_metadata

        self.buffer_position = 0
        self.buffers = []

    def parse(self, input):
        """Top level function for reading a file and printing out the output."""
        #print >> sys.stderr, "SingleParser parsing"
        self.input = input
        content = input.read().decode("utf-8")
        buffer_pos = 0
        byte_pos = 0

        # Begin by creating a document level object, just call it "text" for now.
        self.v.push("doc", "text", 0)
        for k, v in self.known_metadata.items():
            # if the parser was created with known_metadata,
            # we can attach it to the newly created doc object here.
            # you can attach metadata to an object at any time between push() and pull().
            self.v["doc"][k] = v
        for tok in re.finditer(self.token_regex, content, re.U):
            # now just tokenize the entire text and push/pull word and sentence objects.
            if tok.group(1):
                tok_type = "word"
            elif tok.group(2):
                tok_type = "sent"

            tok_length = len(tok.group().encode("utf-8"))
            tok_start = len(content[buffer_pos:tok.start()].encode("utf-8"))
            tok_end = len(content[buffer_pos:tok.end()].encode("utf-8"))

            byte_start = byte_pos + tok_start
            byte_end = byte_pos + tok_end

            # for all tokens, push with byte_start and token content, pull with byte_end
            if tok_type == "word":
                self.v.push("word", tok.group(1).encode("utf-8"), byte_start)
                #                print >> sys.stderr,tok.group(1).encode("utf-8")
                self.v.pull("word", byte_end)
            elif tok_type == "sent":
                # a little hack--we don't know the punctuation mark that will end a sentence
                # until we encounter it--so instead, we let the push on "word" create a
                # implicit philo_virtual sentence, then change its name once we actually encounter
                # the punctuation token.
                if "sent" not in self.v:
                    self.v.push("sent", tok.group(2).encode("utf-8"), byte_start)
                self.v["sent"].name = tok.group(2).encode("utf-8")
                self.v.pull("sent", byte_end)
            buffer_pos = tok.end()
            byte_pos = byte_end
        self.v.pull("doc", self.filesize)


if __name__ == "__main__":
    for docid, fn in enumerate(sys.argv[1:], 1):
        print >> sys.stderr, docid, fn
        size = os.path.getsize(fn)
        fh = open(fn)
        parser = PlainTextParser(sys.stdout,
                                 docid,
                                 size,
                                 token_regex=r"(\w+)|([\.\?\!])",
                                 known_metadata={"filename": fn})
        parser.parse(fh)
