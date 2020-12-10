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

### 4.6 => 5.0 ###
- New aggregation report
- Database size should be 50% or more smaller
- Collocations faster
- Optimized frequency report: much faster for certain use cases
- Web config has been simplified with the use of global variables for citations
- Some breaking changes to web config: you should not use a pre 5.0 config
