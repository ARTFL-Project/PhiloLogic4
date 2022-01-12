#!/usr/bin/python

from lxml import etree
import sys
import regex as re
def promote(el):
    # snips el out of parent, creates it as a sibling of parent under container, and 
    # creates a new copy of parent with type="split" to contain all trailing content
    # of parent after el.  may be called repeatedly.  returns the new, promoted copy
    # of el. 
    parent = el.getparent()
    container = parent.getparent()
    for i,child in enumerate(container):
        if child == parent:
            for j,grandchild in enumerate(child):
                if grandchild == el:
                    # first we make a copy of the element in its grandparent
                    container.insert(i+1,etree.Element(el.tag,attrib={"type":"promoted"}))                                
                    new_el = container[i+1]
                    new_el.text = el.text
                    for e in el.getchildren(): 
                        # untested, since stages have no children in the monk shakespeare.
                        new_el.append(e)                    
                    # then we make a new copy of the parent after that, to hold all the trailing
                    # content and nodes.
                    container.insert(i+2,etree.Element(parent.tag,attrib=parent.attrib))
                    split_parent = container[i+2]
                    split_parent.attrib["type"] = "split"
                    split_parent.text = el.tail # tricky.                   
                    # then we iterate over the children of parent after el, 
                    # and move them to the split_parent
                    for gc in child[j+1:]:
                        split_parent.append(gc) 
                        # although it's undocumented, append() appears to also remove gc from the parent
                        # for us; attempting to do so manually raises a 
                        # ValueError: Element is not a child of this node.
                        # still, should test carefully.
                    split_parent.tail = parent.tail # again tricky.
                    parent.tail = ""
                    parent.remove(el)
                    break
            break
    return new_el

for file in sys.argv[1:]:
    fd = open(file)
        print >> sys.stderr, "reading ", file
    text_string = fd.read()
    root = etree.fromstring(text_string)
    # remove namespaces
    for el in root.getiterator():
        # match clark-style namespace notation
        if el.tag.startswith("{"):
            old_tag = el.tag
            el.tag = re.sub("^[^}]+}","",el.tag)
    for el in root.getiterator():        
        if el.tag == "stage":
            working_el = el
            while "sp" in [a.tag for a in working_el.iterancestors()]:
                working_el = promote(working_el) 
    new_file = file + ".fixed"
        print >> sys.stderr, "writing ", new_file
    new_file = open(new_file,"w")
    new_file.write("<?xml version='1.0' encoding='utf-8'?>")
    tree = etree.ElementTree(root)
    new_string = etree.tostring(tree,encoding="utf-8")
    new_string = new_string.decode("utf-8").encode("utf-8")
    new_file.write(new_string)
