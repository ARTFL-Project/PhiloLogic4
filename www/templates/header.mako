## -*- coding: utf-8 -*-
<!doctype html>
<html>
<head>
  <title>${dbname}</title>
 <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<link href='http://fonts.googleapis.com/css?family=Droid+Sans+Mono|Averia+Serif+Libre:300,400,700,300italic,400italic,700italic&subset=latin,latin-ext,cyrillic-ext,greek-ext,greek,cyrillic' rel='stylesheet' type='text/css'>
<link type="text/css" href="http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.3/themes/smoothness/jquery-ui.min.css" rel="stylesheet" />
<link rel="stylesheet" href="${db.locals['db_url']}/css/style.css" type="text/css" media="screen, projection">
<link rel="stylesheet" href="${db.locals['db_url']}/css/textObjectNavigation.css" type="text/css" media="screen, projection">
<link rel="stylesheet" href="${db.locals['db_url']}/css/searchForm.css" type="text/css" media="screen, projection">
<script>
    var db_locals = ${db_locals}; /* loading the db_locals Python variable in javascript */
</script>
<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.10.1/jquery.js" type="text/javascript"></script>
<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jqueryui/1.10.3/jquery-ui.min.js"></script>
<script type="text/javascript" src="${db.locals['db_url']}/js/jquery.hoverIntent.minified.js"></script>
<script type="text/javascript" src="${db.locals['db_url']}/js/jquery.scrollTo.min.js"></script>
<script type="text/javascript" src="${db.locals['db_url']}/js/history.js/scripts/bundled/html4+html5/jquery.history.js"></script>
<script type="text/javascript" src="${db.locals['db_url']}/js/philologic.js"></script>
</head>
<body onunload="">
    <div id="container">
        <div id="wrapper">
            <div id="header">
                <div id="top-bar">
                    <div class="region-content">
                        <ul class="links secondary-links">
                            <li class="menu-121 first"><a href="http://humanities.uchicago.edu/orgs/ARTFL/" title="The ARTFL Project">THE ARTFL PROJECT</a></li>
                            <li class="menu-120"><a href="http://philologic.uchicago.edu/manual.php" title="How to use the PhiloLogic Search Engine">PHILOLOGIC4 USER MANUAL</a></li>
                            <li class="menu-118"><a href="http://www.uchicago.edu/" title="University of Chicago">UNIVERSITY OF CHICAGO</a></li>
                        </ul>             
                    </div>
                </div>
                <div id="site-name">
                    <h1><a href="${db.locals['db_url']}/" title="${dbname}">${dbname.title()} Beta 2</a></h1>           
                </div>
                
            </div>
            <div class="main_body">