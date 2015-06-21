Configuring the Web Application
========================================

* [Layout of the Web Application](#layout)
* [UI configuration](#ui)
* [Access control](#access)

#### <a name="layout"></a>Layout of a PhiloLogic Web Application Instance ####

This database directory contains:
* The indexes and other data strutures
* The web application, which includes server-side Python runtime functions and the AngularJS client application

Here is what the database directory looks like after a load::
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
├── functions
├── reports
└── scripts
</code></pre>

There are four distinct sections inside the application:
* The `app/` directory: this contains the web client, and is organized according to functionality and shared components.
* The `data/`directory contains all the indexes and SQLite tables needing for search and retrieval, as well as database and web configuration files.
* The `reports/` directory, which contains the major search reports which fetch data from the database by interfacing with the core library, and then return a specialized results report as a JSON object. These reports include concordance, KWIC (Key Word In Context), collocation, and time series. 
* The `functions/` directory, which contains all of the generic functions used by individual reports. These functions include parsing the query string, loading web configuration options, access control, etc. 
* The `scripts/` directory, which contains standalone CGI scripts that are called directly from JavaScript code on the client side. These functions have a very specialized purpose, such as returning the total number of hits for any given query.

#### <a name="ui"></a>Modifying the behavior of the Web Application ####

To change the behavior of the Web Application, you should edit the `web_config.cfg` file contained in the `data/` directory. Refer to the documentation contained in the file for editing options. Note that PhiloLogic uses the Python syntax in the config file.

#### <a name="access"></a>Access control ####

There are two components in the built-in access control:
* IP range check
* user login

In order for access control to be turned on, you first need to set the `access_control` variable in web_config.cfg to `True`.
