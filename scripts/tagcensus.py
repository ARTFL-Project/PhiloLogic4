from philologic import shlaxtree as st
import sys

class TagCensus:
    def __init__(self, debug = False):
        self.tags = {}
        self.debug = debug

    def feed(self,*event):
        (kind,content,offset,name,attributes) = event
        if kind == "start":
            if content[-2:] == "/>":
                kind = "empty"
            elif content[-1] == ">":
                pass # a normal start tag
            else:
                kind = "malformed"
        elif kind == "end":
            if content:
                if content[-1] != ">":
                    kind = "malformed"
                else:
                    pass # a normal end tag
            else:
                return # a hypothetical end tag to balance an empty tag
        else:
            return
        if self.debug:
            print >> sys.stderr, kind, name, content
        if name not in self.tags:
            self.tags[name] = {"start":0,"end":0,"empty":0,"malformed":0}
        self.tags[name][kind] += 1
    def close(self):
        pass

def print_census(census):
    print "\ttag\tstart\tend\tempty\tmalformed"
    for tag in sorted(census.tags.keys()):
        status = ""
        if census.tags[tag]["start"] != census.tags[tag]["end"]:
            status += "*"
        if census.tags[tag]["malformed"]:
            status += "X"
        print "%s\t%s\t%d\t%d\t%d\t%d" % (status,tag,census.tags[tag]["start"],census.tags[tag]["end"],census.tags[tag]["empty"],census.tags[tag]["malformed"])


if __name__ == "__main__":
    file_count = 0
    total = None
    for fn in sys.argv[1:]:
        file_count += 1
        census = TagCensus()
        parser = st.ShlaxIngestor(target=census)
        parser.feed(open(fn).read())
        print fn
        print_census(census)
        if total:
            for tag in census.tags.keys():
                if tag not in total.tags:
                    total.tags[tag] = {"start":0,"end":0,"empty":0,"malformed":0}
                total.tags[tag]["start"] += census.tags[tag]["start"]
                total.tags[tag]["end"] += census.tags[tag]["end"]
                total.tags[tag]["empty"] += census.tags[tag]["empty"]
                total.tags[tag]["malformed"] += census.tags[tag]["malformed"]

        else:
            total = census
    if file_count > 1:
        print "TOTAL: %d FILES" % (file_count)
        print_census(total)