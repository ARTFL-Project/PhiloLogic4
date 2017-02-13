#!/usr/bin/env python
import sys

for fn in sys.argv[1:]:
    print("reading ",fn, file=sys.stderr)
    fh = open(fn)
    new_fh = open(fn + ".clean","w")
    line_no = 0
    for line in fh:
        line_no += 1
        try:
            uniline = line.decode("utf-8")
            print(uniline.encode("utf-8"), file=new_fh)
        except:
            print("\terror on line ",line_no, line, file=sys.stderr)
            # we decode the line in "replace" mode, which leaves the unicode question-mark replacement symbol where the
            # previously garbled bytes were.
            uniline = line.decode("utf-8","replace")
            split_line = uniline.split("\uFFFD")
            raw_byte_fragments = [fragment.encode("utf-8") for fragment in split_line]            
            line_buffer = line[:] # a working copy of the original line, in bytes
            new_line = "" # a new string to work with.  will be unicode.
            while raw_byte_fragments: # we step through the line, looking at the boundaries of correct encoding
                frag_length = len(raw_byte_fragments[0])
                if line_buffer[:frag_length] == raw_byte_fragments[0]: # if it matches a fragment, pop it off the list and 
                    new_line += raw_byte_fragments[0].decode("utf-8")
                    raw_byte_fragments.pop(0)
                    line_buffer = line_buffer[frag_length:]
                else:
                    unicode_char = line_buffer[0].decode("latin-1")
                    new_line += unicode_char
                    line_buffer = line_buffer[1:]                    

            print(new_line.encode("utf-8"), file=sys.stderr)
            print(new_line.encode("utf-8"), file=new_fh)
