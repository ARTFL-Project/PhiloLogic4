# PhiloLogic 4 Query Syntax #

PhiloLogic4's query syntax has 5 basic operators:

1. the plain token, essentially, any word at all, split on space, e.g. `token`
2. the quoted token--a string in double quotes, which may contain a space, e.g. `"token"`
3. the range--two tokens separated by a dash, e.g. `a-f`
4. boolean OR, represented grep-style as `|`, e.g. `token | word`
5. boolean NOT, represented SQL-style as `NOT`, e.g. `token.* NOT tokens`

This syntax is the same, but interpreted slightly differently, for the two different types of text query fields: word search and metadata search.  

### Word Searches ###

Full-text word search is unique in having the concept of a "term", which is either a single plain/quoted term, 
or a group of plain/quoted terms joined by `|`, optionally followed by `NOT` and another term-like filter expression.
When specifying a query, one can select a query method to constrain the relation between terms, such as `within k words` or `in the same sentence`

1. plain terms are evaluated without regard to accent.  They are currently sensitive to case, to allow for named entity 
search--this is currently implemented only for Greek, however. Regexes are permitted.
2. quoted terms are case and accent sensitive.  Regexes are permitted.
3. the range is not operational. In the future, stub this out to make hyphenated search terms less of a pain to escape.
4. `OR` can conjoin plain and quoted tokens, and precedes evaluation of phrase distance.
5. `NOT` is a filter on a preceding term, but cannot stand alone: `a.* NOT abalone` is legal, `NOT a.*` is illegal

### Metadata Searches ###

Metadata search does not support phrases, but supports more sophisticated Boolean searching.

1. plain tokens separated by spaces have an implied AND between them, but are treated as position-independent tokens. 
Regexes are permitted, but will not span over the bounds of a token.
2. quoted tokens must now match against the ENTIRE metadata string value in the database, including spaces and punctuations.
It will not match a single term within a larger string, no matter how precise. **Regexes are not permitted**.
3. range allows for numeric and string ranges on all metadata fields.  
4. `OR` can still be used to conjoin plain tokens, preceding the implied Boolean AND, as well as quoted tokens.
5. `NOT` is still available as both a filter, or a stand-alone negation: `diderot NOT rousseau` is legal, so is `NOT rousseau`

Metadata objects also have the unique property of recursion, which creates some unusual consequences for search semantics.  
Searching for a div that has property `NOT x` does not guarantee that the result does not contain a child with property x, 
or a parent with property x.  This can often be handled at the database level by normalizing metadata to a single fine-grained layer, 
but is tricky. Likewise, searches for `NULL` values in recursive objects will often return "virtual" philologic objects, 
which don't exist in the XML but are necessary for balanced tree arithmetic.

### Regexp syntax ###

Basic regexp syntax, adapted from the [**egrep regular expression syntax**](http://www.gnu.org/software/findutils/manual/html_node/find_html/egrep-regular-expression-syntax.html#egrep-regular-expression-syntax).

* The character `.` matches any single character except newline. 
* Bracket expressions can match sets or ranges of characters: `[aeiou]` or `[a-z]`, but will only match a single character unless followed by one of the quantifiers below.
* `*` indicates that the regular expression should match zero or more occurrences of the previous character or bracketed group.
* `+` indicates that the regular expression should match one or more occurrences of the previous character or bracketed group.
* `?` indicates that the regular expression should match zero or one occurrence of the previous character or bracketed group.
Thus, `.*` is an approximate "match anything" wildcard operator, rather than the more traditional (but less precise) `*` in many other search engines.
