---
title: Configuring the Web Application
---

-   [Layout of the Web Application](#layout)
-   [UI configuration](#ui)
-   [Access control](#access)
-   [Changing web application theme](#changing-theme)

#### <a name="layout"></a>Layout of a PhiloLogic Web Application Instance

This database directory contains:

-   The indexes and other data strutures
-   The web application, which includes server-side Python runtime functions and the AngularJS client application

Here is what the database directory looks like after a load:

<pre><code>
database/
├── app
├── data
│   ├── db.locals.py
│   ├── frequencies
│   ├── index
│   ├── index.1
│   ├── load_config.py
│   ├── src
│   ├── TEXT
│   ├── toms.db
│   └── web_config.cfg
├── reports
└── scripts
</code></pre>

There are four distinct sections inside the application:

-   The `app/` directory: this contains the web client, and is organized according to functionality and shared components.
-   The `data/`directory contains all the indexes and SQLite tables needing for search and retrieval, as well as database and web configuration files.
-   The `reports/` directory, which contains the major search reports which fetch data from the database by interfacing with the core library, and then return a specialized results report as a JSON object. These reports include concordance, KWIC (Key Word In Context), collocation, and time series.
-   The `scripts/` directory, which contains standalone CGI scripts that are called directly from JavaScript code on the client side. These functions have a very specialized purpose, such as returning the total number of hits for any given query.

#### <a name="ui"></a>Modifying the behavior of the Web Application

To change the behavior of the Web Application, you should edit the `web_config.cfg` file contained in the `data/` directory. Refer to the documentation contained in the file for editing options. Note that PhiloLogic uses the Python syntax in the config file.

#### <a name="access"></a>Access control

There are two components in the built-in access control:

-   IP range check
-   user login

In order for access control to be turned on, you first need to set the `access_control` variable in web_config.cfg to `True`.

Once access control has been turned on, PhiloLogic will check the `access_file` variable which defines a file contained in the /data directory which will contain the domain names allowed as well as the IPs addresses to be blocked. If no such file is provided, access will be automatically granted.

#### <a name="changing-theme"></a>Changing the Web Application theme
Changing the Web Application theme requires editing the `theme.module.scss` file which can be found in the database directory under `app/src/assets/styles/`.

The `theme.module.scss` file is a Sass stylesheet which makes use of global variables to define the main colors used in the web app. All you should need to do is edit `$header-color`, `$button-color`, `$button-color-active`, `$link-color`. Once you've edited the theme file, you will need to rebuild the web application. In order to do so, go to the `app/` directory and run the following command in the terminal:
```
npm run build
```

#### <a name="aggregation"></a>Configuring the aggregation report
The aggregation report (much like faceted browsing) sums up results from concordances by metadata fields. What it can also do is break-up results from any metadata field
into smaller groups of results. For instance, you can get results grouped by author, and for each author, you can break up results by title, all within the same results page.

To configure the aggregation report, you need to modify the `aggregation_report` variable. This variable is a list where you define what groupings are possible. Below is an annotated example of such groupings:

Here's a example of a database comprised of novels (with groupings done at the doc level):

```python
aggregation_config = [
    {
        "field": "author",  # what metadata fieds is used for grouping results
        "object_level": "doc", # object level of the metadata field used for grouping
        "field_citation": [citations["author"]], # citation object used for citing this field
        "break_up_field": "title", # define by what metadata field the results can be further broken into
        "break_up_field_citation": [ # define the citation for the break-up field
            citations["title"],
            citations["pub_place"],
            citations["publisher"],
            citations["collection"],
            citations["year"],
        ],
    },
    {
        "field": "title",
        "object_level": "doc",
        "field_citation": [
            citations["title"],
            citations["pub_place"],
            citations["publisher"],
            citations["collection"],
            citations["year"],
        ],
        "break_up_field": None, # set to None if no break-up field (in this case titles are typically unique so doesn't make sense)
        "break_up_field_citation": None, # leave to None for citation as well.
    },
]
```

Here's an example of a database containing articles (with groupings done rather at the div1 level):

```python
aggregation_config = [
    {
        "field": "author",
        "object_level": "div1",
        "break_up_field": "head", # IMPORTANT NOTE: the break-up field MUST be of the same object level as the main metadata field used for grouping
        "field_citation": [citations["author"]],
        "break_up_field_citation": [
            citations["div1_head"],
            citations["class"],
        ],
    },
    {
        "field": "head",
        "object_level": "div1",
        "field_citation": [
            citations["div1_head"],
            citations["class"],
        ],
        "break_up_field": None,
        "break_up_field_citation": None,
    },
    {
        "field": "class",
        "object_level": "div1",
        "field_citation": [
            citations["class"],
        ],
        "break_up_field": "head",
        "break_up_field_citation": [citations["div1_head"], citations["author"]],
    },
]
```
    
