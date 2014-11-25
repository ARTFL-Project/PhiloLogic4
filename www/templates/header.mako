## -*- coding: utf-8 -*-
<!DOCTYPE html>
<html>
<head>
    <title>${config.dbname.decode('utf-8', 'ignore')}</title>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
 
    <!--Load the web config and global_report variable to use in the JavaScript code-->
    <script>
        var webConfig = ${config.toJSON()}; /* loading the web_config in javascript */
        var global_report = "${report}";    
    </script>
    
    <link href='http://fonts.googleapis.com/css?family=Droid+Sans+Mono|Averia+Serif+Libre:300,400,700,300italic,400italic,700italic&subset=latin,latin-ext,cyrillic-ext,greek-ext,greek,cyrillic' rel='stylesheet' type='text/css'>
    
    <!--Load all required CSS-->
    <link rel="shortcut icon" href="${config.db_url}/favicon.ico" type="image/x-icon">
    <link rel="icon" href="${config.db_url}/favicon.ico" type="image/x-icon">
    <!-- Bootstrap core CSS -->
    <link href="${config.db_url}/css/bootstrap/bootstrap.min.css" rel="stylesheet">  
    <!-- PhiloLogic4 CSS -->
    ${css}
    
    <!-- HTML5 shim and Respond.js IE8 support of HTML5 elements and media queries -->
    <!--[if lt IE 9]>
      <script src="https://oss.maxcdn.com/html5shiv/3.7.2/html5shiv.min.js"></script>
      <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
    <![endif]-->
    
</head>
<body onunload="">
        <div id="wrapper">
            <div id="header">
                <div class="navbar navbar-inverse navbar-static-top" role="navigation">
                    <div class="container-fluid">
                        <div class="navbar-right">
                            <a href="http://artfl-project.uchicago.edu">The ARTFL Project</a>
                            <a href="http://www.uchicago.edu">University of Chicago</a>
                        </div>
                        <div class="navbar-header">
                            <a href="${config.db_url}/" class="navbar-brand" title="${config.dbname.decode('utf-8', 'ignore')}">${config.dbname.decode('utf-8', 'ignore')}</a>
                        </div>
                    </div>
                </div>
            </div>
            <div id="main-body">
                <div class="container-fluid">            
