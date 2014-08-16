## -*- coding: utf-8 -*-
<!doctype html>
<html>
<head>
    <title>${config.dbname.decode('utf-8', 'ignore')}</title>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1">
 
    <!--Load the web config and global_report variable to use in the JavaScript code-->
    <script>
        var webConfig = ${config.JSONify()}; /* loading the web_config in javascript */
        var global_report = "${report}";    
    </script>
    
    <link href='http://fonts.googleapis.com/css?family=Droid+Sans+Mono|Averia+Serif+Libre:300,400,700,300italic,400italic,700italic&subset=latin,latin-ext,cyrillic-ext,greek-ext,greek,cyrillic' rel='stylesheet' type='text/css'>
    
    <!--Load all required CSS-->
    <link rel="shortcut icon" href="${config.db_url}/favicon.ico" type="image/x-icon">
    <link rel="icon" href="${config.db_url}/favicon.ico" type="image/x-icon">
    <!-- Bootstrap core CSS -->
    <link href="${config.db_url}/css/bootstrap/bootstrap.min.css" rel="stylesheet">
        
    
    <link type="text/css" href="http://code.jquery.com/ui/1.11.0/themes/smoothness/jquery-ui.css" rel="stylesheet" />
    <link rel="stylesheet" href="${config.db_url}/css/style.css" type="text/css" media="screen, projection">
    <link rel="stylesheet" href="${config.db_url}/css/searchForm.css" type="text/css" media="screen, projection">
    % if report == "concordance" or report == "kwic" or report == "concordance_from_collocation" or report == "bibliography":
        <link rel="stylesheet" href="${config.db_url}/css/concordanceKwic.css" type="text/css" media="screen, projection">
    % elif report == "time_series":
        <link rel="stylesheet" href="${config.db_url}/css/timeSeries.css" type="text/css" media="screen, projection">
    % elif report == "navigation" or report == "t_o_c":
        <link rel="stylesheet" href="${config.db_url}/css/textObjectNavigation.css" type="text/css" media="screen, projection">
    % endif
    
    <!--Load all required JavaScript-->
    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js" type="text/javascript"></script>
    <script src="${config.db_url}/js/bootstrap/bootstrap.min.js" type="text/javascript"></script>
    <script type="text/javascript" src="http://code.jquery.com/ui/1.11.0/jquery-ui.min.js"></script>
    <script type="text/javascript" src="${config.db_url}/js/plugins/jquery.history.js"></script>
    <script type="text/javascript" src="${config.db_url}/js/plugins/jquery.velocity.min.js"></script>
    <%
    reports = {"landing_page": ["common.js"], "concordance": ["common.js", "sidebar.js", "/plugins/jquery.hoverIntent.minified.js", "concordanceKwic.js"],
            "kwic": ["common.js", "sidebar.js", "/plugins/jquery.hoverIntent.minified.js", "concordanceKwic.js"], "time_series": ["common.js", "timeSeries.js"],
            "collocation": ["common.js", "plugins/jquery.tagcloud.js", "collocation.js"], "ranked_relevance": ["common.js", "rankedRelevance.js"],
            "bibliography": ["common.js", "sidebar.js", "bibliography.js"], "navigation": ["common.js", "/plugins/jquery.scrollTo.min.js", "textObjectNavigation.js"],
            "concordance_from_collocation": ["common.js", "concordanceFromCollocation.js"], "t_o_c": ["common.js"], "error": [], "access": []}
    %>
    % for script in reports[report]:
        <script type="text/javascript" src="${config.db_url}/js/${script}"></script>
    % endfor

</head>
<body onunload="">
        <div id="wrapper">
            <div id="philo-header">
                <div class="navbar navbar-inverse navbar-static-top" role="navigation">
                  <div class="container-fluid">
                    <div class="navbar-header">
                        <a href="${config.db_url}/" class="navbar-brand" style="font-size: 160%" title="${dbname}">${config.dbname.decode('utf-8', 'ignore')}</a>
                    </div>
                    <div class="navbar-right">
                        <a href="http://artfl-project.uchicago.edu">The ARTFL Project</a>
                        <a href="http://www.uchicago.edu">University of Chicago</a>
                    </div>
                  </div>
                </div>
            </div>
        <div class="container-fluid">
    
            <!--    <div class="region-content">-->
            <!--        <ul class="links secondary-links">-->
            <!--            <li class="menu-121 first"><a href="http://humanities.uchicago.edu/orgs/ARTFL/" title="The ARTFL Project">THE ARTFL PROJECT</a></li>-->
            <!--            <li class="menu-120"><a href="http://philologic.uchicago.edu/manual.php" title="How to use the PhiloLogic Search Engine">PHILOLOGIC4 USER MANUAL</a></li>-->
            <!--            <li class="menu-118"><a href="http://www.uchicago.edu/" title="University of Chicago">UNIVERSITY OF CHICAGO</a></li>-->
            <!--        </ul>             -->
            <!--    </div>-->
            <!--    <div id="site-name">-->
            <!--        <a href="${config.db_url}/" title="${dbname}">${config.dbname.decode('utf-8', 'ignore')}</a>           -->
            <!--    </div>-->
            <!--    -->
            <!--</div>-->
            <div class="main_body">
