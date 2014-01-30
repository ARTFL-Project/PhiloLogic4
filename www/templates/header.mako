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
% endif

<!--Load all required JavaScript-->
<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.js" type="text/javascript"></script>
<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.3/jquery-ui.min.js"></script>
<script type="text/javascript" src="${db.locals['db_url']}/js/common.js"></script>
<script type="text/javascript" src="${db.locals['db_url']}/js/history.js/jquery.history.js"></script>

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
