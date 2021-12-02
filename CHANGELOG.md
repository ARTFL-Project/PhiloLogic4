### 4.7 ###
- New aggregation 
- New metadata stats in search results
- Results bibliography in concordance and KWIC results.
- Database size should be between 50% and 500% (or more) smaller
- Significant speed-ups for:
    * Collocations: in some cases 3X
    * Sorted KWICs: between 6X and 25X (or more) depending on use case, with no more limits on the size of the sort as a result.
    * Faceted browsing (frequencies): anywhere from 3X to 100X or more
- Export results to CSV
- Web config has been simplified with the use of global variables for citations
- Some breaking changes to web config: you should not use a 4.6 config
- Revamped Web UI: move to VueJS and Bootstrap 5.

### 4.6 ###
- Port PhiloLogic4 codebase to Python3
- Switch load time compression from Gzip to LZ4: big speed-up in loading large databases
- Lib reorganization

#### 4.0 => 4.5 ####
- Completely rewritten parser: can now parse broken XML
- Massive lib reorg
- A new system wide config
- Loading process completely revamped: use philoload4 command
- Completely rewritten collocations: faster and accurate
- Added relative frequencies to frequencies in facets
- Added sorted KWIC
- Added support for regexes in quoted term searches (aka exact matches)
- Added ability to filter out words in query expansion through a popup using the NOT syntax
- Added configurable citations for all reports
- Added concordance results sorting by metadata
- Added approximate word searches using Levenshtein distance
- Redesign facets and time series
- Bug fixes and optimizations everywhere...
