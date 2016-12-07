### A few notes on text encoding ###

* Starting from version 4.5, PhiloLogic will now parse non-valid XML since it no longer relies on an XML lib for document parsing.

* The only requirement is that files are encoded in **UTF-8**.

* We mostly support the TEI spec, though we only index a small reasonable subset of the spec.

* We only support double quotes for attributes, such as `<pb n="1">`.<br>
In other words, we do **NOT** support `<pb n='1'>`.

# Page tags #
* Pages are encoded with the `<pb>` tag.
* Page image filenames should be stored inside the fac attribute, such as in the example below:
```XML
<pb fac="ENC_23-1-1.jpeg"/>
```
* Page numbers should be stored in the n attribute, such as below:
```XML
<pb n="23"/>
```

A page tag with both attributes could look like this:
```XML
<pb n="23" fac="V23/ENC_23-1-1.jpeg"/>
```

# Inline Images #
* Inline images should use the `<graphic>` tag.
* Linnks to images should be stored in the url attribute such as below:
```XML
<graphic url="V23/plate_23_2_2.jpeg">
```

# Notes #
### Important ###
While PhiloLogic will display inline notes, it really only properly supports notes
that are divided into the pointer to the note inside the running text, and the note
itself at the end of a text object or of the document.

#### Pointers to notes ####
* Pointers to notes should use the `<ref>` tag
* The `<ref>` tag should have an attribute type of type "note", such as `type="note"`
* Pointers reference the actual note using the target attribute, such as `target="n1"`.
* Pointers will be displayed in the text using the contents of the n attribute, otherwise default to "note".


Example of a `<ref>` tag pointing to a `<note>` tag:
```xml
<ref type="note" target="n1" n="1"/>
```
#### Note tags ####
* Notes should be stored at the end of the parent `<div>` element or a the end of the doc inside a `<div type="notes">`
* Notes themselves are stored in a `<note>` tag.
* Notes should have an attribute id with the value corresponding to the value of target in the pointer referencing the note.
* Notes are stored as paragraph elements, therefore all `<p>` tags (or any other paragraph level tag) contained within will be ignored though still displayed.

Example of notes inside a `<div1 type="notes">`
```xml
<div1 type="notes">
  <note id="n1">Contents of note....</note>
  <note id="n2">Contents of note....</note>
</div1>
```

# Cross references #
* Cross-references should use the `<ref>` tag
* The `<ref>` tag should have an attribute type of type "cross", such as `type="cross"`
* The type "cross" of `<ref>` triggers direct navigation to the object defined in the id attribute.

Example of a cross-reference:
```xml
<ref type="cross" target="c2">See chapter 2</ref>
```
which  references the following object using its id attribute:
```xml
<div2 type="Chapter" id="c2">
```

# Search references #
* Search references should use the `<ref>` tag
* The `<ref>` tag should have an attribute type of type "search", such as `type="search"`
* The type "search" of `<ref>` triggers a metadata search of the value defined in the target attribute
* The target attribute value contains the metadata field and metadata value to be searched separated by a `:`,<br>
such as `target="who:Hamlett"`

Example of a search reference
```xml
<ref type="search" target="head:Gouverner">Gouverner</ref>
```
