

from philologic import shlaxtree as st
import sys

class TagCensus:
    def __init__(self, debug = False, text_target=None):
        self.tags = {}
        self.debug = debug
        self.text_target = text_target

    def parse(self,text):
        self.tags = {}
        parser = st.ShlaxIngestor(target=self)
        parser.feed(text)
        self.close()

    def __getitem__(self,key):
        return self.tags[key]

    def __setitem__(self,key,value):
        self.tags[key] = value

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
        elif kind == "text" and self.text_target:
            self.text_target.feed(content)
            return
        else:
            return
        if self.debug:
            print(kind, name, content, offset, file=sys.stderr)
        if name not in self.tags:
            self.tags[name] = {"start":0,"end":0,"empty":0,"malformed":0}
        self.tags[name][kind] += 1

    def __iadd__(self,other):
        for tag in list(other.tags.keys()):
            if tag not in self.tags:
                self[tag] = {"start":0,"end":0,"empty":0,"malformed":0}
            self[tag]["start"] += other.tags[tag]["start"]
            self[tag]["end"] += other.tags[tag]["end"]
            self[tag]["empty"] += other.tags[tag]["empty"]
            self[tag]["malformed"] += other.tags[tag]["malformed"]        
        return self
        
    def __sub__(self,other):
        res = {}
        for tag in list(self.tags.keys()):
            if tag not in res:
                res[tag] = {"start":0,"end":0,"empty":0,"malformed":0}
            res[tag]["start"] += self.tags[tag]["start"]
            res[tag]["end"] += self.tags[tag]["end"]
            res[tag]["empty"] += self.tags[tag]["empty"]
            res[tag]["malformed"] += self.tags[tag]["malformed"]
        for tag in list(other.tags.keys()):
            if tag not in res:
                res[tag] = {"start":0,"end":0,"empty":0,"malformed":0}
            res[tag]["start"] -= other.tags[tag]["start"]
            res[tag]["end"] -= other.tags[tag]["end"]
            res[tag]["empty"] -= other.tags[tag]["empty"]
            res[tag]["malformed"] -= other.tags[tag]["malformed"]

        for tag in list(res.keys()):
            if res[tag] == {"start":0,"end":0,"empty":0,"malformed":0}:
                del res[tag]

        return res

    def __str__(self):
        longest = max(len(k) for k in list(self.tags.keys())) + 4 # 3 possible flags + space
        res = "    tag%s\tstart\tend\tempty\tmalformed\n" % (" " * (longest - len("tag")))
        for tag in sorted(self.tags.keys()):
            status = ""
            if self[tag]["start"] != self[tag]["end"]:
                status += "*"
            else:
                status += " "

            if (self[tag]["end"] != 0) and (self[tag]["empty"] != 0):
                status += "E"
            else:
                status += " "

            if self[tag]["malformed"]:
                status += "X"
            else:
                status += " "

            padding = " " * (longest - (len(tag) + len(status) ) )

            res += "%s %s%s\t%d\t%d\t%d\t%d\n" % (status,tag,padding,self[tag]["start"],self[tag]["end"],self[tag]["empty"],self[tag]["malformed"])

        return res
        
    def close(self):
        if self.text_target:
            self.text_target.close()
        pass

if __name__ == "__main__":
    file_count = 0
    total = None
    for fn in sys.argv[1:]:
        file_count += 1
        census = TagCensus()
        census.parse(open(fn).read())
        print(fn)
        print(census)
        if total:
            total += census
        else:
            total = census
    if file_count > 1:
        print("TOTAL: %d FILES" % (file_count))
        print(total)
