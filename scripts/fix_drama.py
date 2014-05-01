#!/usr/bin/python

from lxml import etree
import sys

def walk(root,depth=-1):
    yield (root,depth)
    depth = depth + 1
    for tag in root:
        for el,d in walk(tag,depth):
            yield (el,d)
    return

for file in sys.argv[1:]:
    fd = open(file)
    print >> sys.stderr, "opening ",file
    tree = etree.fromstring(fd.read())
    for el,d in walk(tree):
        if el.tag == "stage":
            parent = el.getparent()
            if parent.tag == "sp":
                container = parent.getparent()
                if container.text: 
                    pass
                for i,child in enumerate(container):
                    if child == parent:
                        for j,grandchild in enumerate(child):
                            if grandchild == el:
                                container.insert(i+1,etree.Element("stage",attrib={"type":"split"}))                                
                                new_stage = container[i+1]
                                new_stage.text = el.text
                                container.insert(i+2,etree.Element("sp",attrib=parent.attrib))
                                new_sp = container[i+2]
                                new_sp.text = el.tail
                                for gc in child[j+1:]:
                                    new_sp.append(gc)
                                new_sp.tail = parent.tail
                                parent.tail = ""
                                parent.remove(el)
                                print >> sys.stderr, "  SUCCESS: fixed nested stage"
                                break
                        break
            elif "sp" in [a.tag for a in el.iterancestors()]:
                print >> sys.stderr, "  ERROR: Stage deeply nested within sp"
    new_file = file + ".fixed"
    new_string = etree.tostring(tree,encoding="latin-1")
    new_string = new_string.replace("<?xml version='1.0' encoding='latin-1'?>","<?xml version='1.0' encoding='utf-8'?>",1)
#    print new_string.decode("utf-8").encode("utf-8")
    print >> sys.stderr, "  wrote ",new_file
    open(new_file,"w").write(new_string)