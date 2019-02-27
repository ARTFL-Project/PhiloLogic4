---
title: Configuring the Web Application
---

-   [Layout of the Web Application](#layout)
-   [UI configuration](#ui)
-   [Access control](#access)
-   [Setting default start/end dates for Time Series](#setting-default-dates-for-time-series)

#### <a name="layout"></a>Layout of a PhiloLogic Web Application Instance

This database directory contains:

-   The indexes and other data strutures
-   The web application, which includes server-side Python runtime functions and the AngularJS client application

Here is what the database directory looks like after a load:

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

### Setting default dates for time series

If you need to set default start and end dates to time series requests (e.g. you have errors in the data such as 176 for the earliest date in an 18th century corpus, or 9999 as the latest date and you know this isn't the 100th century), you need to edit the script `get_start_end_date.py` in the `scripts/` directory of your database. After the `request` variable has been set, override the `request.start_date` or `request.end_date` (depending on your use case) if their values are empty. For example:

```python
request = WSGIHandler(environ, config)
if request.start_date == "":
    request.start_date = 1772
if request.end_date == "":
    request.end_date = 2004
```
