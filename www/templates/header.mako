## -*- coding: utf-8 -*-
<!doctype html>
<html>
<head>
    <title>${dbname}</title>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
 
    <!--Load db_locals and global_report variable to use in the JavaScript code-->
    <script>
        var db_locals = ${db_locals}; /* loading the db_locals Python variable in javascript */
        global_report = "${report}";    
    </script>
    
    <link href='http://fonts.googleapis.com/css?family=Droid+Sans+Mono|Averia+Serif+Libre:300,400,700,300italic,400italic,700italic&subset=latin,latin-ext,cyrillic-ext,greek-ext,greek,cyrillic' rel='stylesheet' type='text/css'>
    
    <!--Load all required CSS-->
    <link type="text/css" href="http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.3/themes/smoothness/jquery-ui.min.css" rel="stylesheet" />
    <link rel="stylesheet" href="${db.locals['db_url']}/css/style.css" type="text/css" media="screen, projection">
    <link rel="stylesheet" href="${db.locals['db_url']}/css/searchForm.css" type="text/css" media="screen, projection">
    % if report == "concordance" or report == "kwic" or report == "concordance_from_collocation" or report == "bibliography":
        <link rel="stylesheet" href="${db.locals['db_url']}/css/concordanceKwic.css" type="text/css" media="screen, projection">
    % elif report == "time_series":
        <link rel="stylesheet" href="${db.locals['db_url']}/css/timeSeries.css" type="text/css" media="screen, projection">
    % elif report == "navigation":
        <link rel="stylesheet" href="${db.locals['db_url']}/css/textObjectNavigation.css" type="text/css" media="screen, projection">
    % endif
    
    <!--Load all required JavaScript-->
    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js" type="text/javascript"></script>
    <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.3/jquery-ui.min.js"></script>
    <script type="text/javascript" src="${db.locals['db_url']}/js/plugins/jquery.history.js"></script>
    <%
    reports = {"landing_page": ["common.js"], "concordance": ["common.js", "sidebar.js", "/plugins/jquery.hoverIntent.minified.js", "concordanceKwic.js"],
            "kwic": ["common.js", "sidebar.js", "/plugins/jquery.hoverIntent.minified.js", "concordanceKwic.js"], "time_series": ["common.js", "timeSeries.js"],
            "collocation": ["common.js", "plugins/jquery.tagcloud.js", "collocation.js"], "ranked_relevance": ["common.js", "rankedRelevance.js"],
            "bibliography": ["common.js", "sidebar.js", "bibliography.js"], "navigation": ["common.js", "/plugins/jquery.scrollTo.min.js", "textObjectNavigation.js"],
            "concordance_from_collocation": ["common.js", "concordanceFromCollocation.js"]}
    %>
    % for script in reports[report]:
        <script type="text/javascript" src="${db.locals['db_url']}/js/${script}"></script>
    % endfor

</head>
<body onunload="">
    <div id="container">
        <div id="wrapper">
            <div id="header">
                <div class="region-content">
                    <ul class="links secondary-links">
                        <li class="menu-121 first"><a href="http://humanities.uchicago.edu/orgs/ARTFL/" title="The ARTFL Project">THE ARTFL PROJECT</a></li>
                        <li class="menu-120"><a href="http://philologic.uchicago.edu/manual.php" title="How to use the PhiloLogic Search Engine">PHILOLOGIC4 USER MANUAL</a></li>
                        <li class="menu-118"><a href="http://www.uchicago.edu/" title="University of Chicago">UNIVERSITY OF CHICAGO</a></li>
                    </ul>             
                </div>
                <div id="site-name">
                    <h1><a href="${db.locals['db_url']}/" title="${dbname}">${dbname.title()}</a></h1>           
                </div>
                
            </div>
            <div class="main_body">
