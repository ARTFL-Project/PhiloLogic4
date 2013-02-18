## -*- coding: utf-8 -*-
<!doctype html>
<html>
<head>
  <title>${dbname}</title>
 <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<link href='http://fonts.googleapis.com/css?family=Droid+Sans+Mono|Averia+Serif+Libre:300,400,700,300italic,400italic,700italic&subset=latin,latin-ext,cyrillic-ext,greek-ext,greek,cyrillic' rel='stylesheet' type='text/css'>
<link type="text/css" href="${db.locals['db_url']}/css/smoothness/jquery-ui-1.10.0.custom.css" rel="stylesheet" />
<link rel="stylesheet" href="${db.locals['db_url']}/css/style.css" type="text/css" media="screen, projection">
<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.js" type="text/javascript"></script>
<script type="text/javascript" src="${db.locals['db_url']}/js/jquery-ui-1.10.0.custom.min.js"></script>
<script type="text/javascript" src="${db.locals['db_url']}/js/jquery.hoverIntent.minified.js"></script>
<%include file="form_header.js"/>
</head>
<body onunload="">
<div id="container">
<div id="wrapper">
    <div id="header">
      <div id="top-bar">
        <div class="region-content">
          <ul class="links secondary-links">
            <li class="menu-121 first"><a href="http://humanities.uchicago.edu/orgs/ARTFL/" title="The ARTFL Project">THE ARTFL PROJECT</a></li>
			<li class="menu-120"><a href="http://philologic.uchicago.edu/manual.php" title="How to use the PhiloLogic Search Engine">PHILOLOGIC USER MANUAL</a></li>
			<li class="menu-119"><a href="http://www.lib.uchicago.edu/efts/ARTFL/newhome/subscribe/" title="Subscribe to the ARTFL Project">SUBSCRIPTION INFORMATION</a></li>
			<li class="menu-118"><a href="http://www.uchicago.edu/" title="University of Chicago">UNIVERSITY OF CHICAGO</a></li>
			<li class="menu-117 last"><a href="http://www.atilf.fr/" title="Analyse et Traitment Informatique de la Langue Française">ATILF - CNRS</a></li>
		  </ul>             
		</div>
      </div>
            
      <div class="region-content">
        <h1><a href="${db.locals['db_url']}/" title="${dbname}"><span class="site-name">${dbname.title()} alpha5</span></a></h1>           
      </div>
    </div>
  <div class="main_body">
