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
