Configuring PhiloLogic's Web Application
========================================

#### Layout of a PhiloLogic Web Application Instance ####

This database directory now contains *both* `PhiloLogic` web application, at the root,
with the indexes and other data structures, in a ``data`` subdirectory.
At the end of generation, this directory will look like this tree::
<pre><code>
database/
├── app
│   ├── assets
│   │   ├── css
│   │   └── js
│   ├── components
│   │   ├── collocation
│   │   ├── concordanceKwic
│   │   ├── landingPage
│   │   ├── tableOfContents
│   │   ├── textNavigation
│   │   └── timeSeries
│   └── shared
│       ├── accessControl
│       ├── exportResults
│       ├── searchArguments
│       ├── searchForm
│       └── searchSyntax
├── functions
├── reports
└── scripts
</code></pre>
