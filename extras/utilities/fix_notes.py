"""Move notes to end of TEI file according to PhiloLogic's spec."""

from copy import deepcopy
import sys
from lxml import etree


def update_notes(filename):
    """Add inline notes at the end of the file"""
    with open(filename, "rb") as input_file:
        text = input_file.read()
    parser = etree.XMLParser(remove_blank_text=True)
    root = etree.fromstring(text, parser)
    for el in root.getiterator():
        try:
            if el.tag.startswith("{"):
                el.tag = el.tag.rsplit("}", 1)[-1]
        except AttributeError:
            pass
    note_div = etree.Element("div", type="notes")
    head = etree.Element("head")
    head.text = "Notes"
    head.tail = "\n"
    note_div.insert(0, head)
    note_div.text = "\n"
    note_count = 1
    notes_skipped = 0
    for el in root.iter("note"):
        inHeader = False
        for ancestor in el.iterancestors():
            if ancestor.tag == "teiHeader":
                inHeader = True
                notes_skipped += 1
                break
        if inHeader:
            continue
        new_note = deepcopy(el)
        for attr in new_note.attrib:
            del new_note.attrib[attr]
        new_note.attrib["id"] = f"{note_count}"
        new_note.tail = "\n"
        note_div.append(new_note)
        el.tag = "ref"
        el.attrib["type"] = "note"
        el.attrib["target"] = f"{note_count}"
        for child in el:
            el.remove(child)
        el.text = ""
        note_count += 1
    if note_count > 1:
        root[-1].append(note_div)
    extension = filename.split(".")[-1]
    new_file = f'{filename.replace(f".{extension}", "")}_fixed_notes.{extension}'
    with open(new_file, "w", encoding="utf8") as output:
        tree = etree.ElementTree(root)
        output.write(etree.tostring(tree, encoding="unicode", pretty_print=True))


if __name__ == "__main__":
    update_notes(sys.argv[1])
