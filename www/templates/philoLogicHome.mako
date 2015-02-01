## -*- coding: utf-8 -*-
<!DOCTYPE html>
<html ng-app="philoApp">
<head>
    <title>${config.dbname.decode('utf-8', 'ignore')}</title>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
 
    <!--Load the web config and global_report variable to use in the JavaScript code-->
    <script>
        var philoConfig = ${config.toJSON()}; /* loading the web_config in javascript */
        var philoReport = "landing_page";
    </script>
    
    <link href='http://fonts.googleapis.com/css?family=Droid+Sans+Mono|Averia+Serif+Libre:300,400,700,300italic,400italic,700italic&subset=latin,latin-ext,cyrillic-ext,greek-ext,greek,cyrillic' rel='stylesheet' type='text/css'>
    
    <!--Load all required CSS-->
    <link rel="shortcut icon" href="favicon.ico" type="image/x-icon">
    <link rel="icon" href="favicon.ico" type="image/x-icon">
    <!-- Bootstrap core CSS -->
    <link href="css/bootstrap/bootstrap.min.css" rel="stylesheet">  
    <!-- PhiloLogic4 CSS -->
    ${css}
    <link href="css/split/landingPage.css" rel="stylesheet">
    <link href="css/split/concordanceKwic.css" rel="stylesheet">
    
    ## Load in header to allow ng-cloak
    <script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.3.10/angular.min.js"></script>
    
</head>
<body onunload="" ng-controller="philoMain" ng-cloak>
    <div id="header">
        <div class="navbar navbar-inverse navbar-static-top" role="navigation">
            <div class="container-fluid">
                <div class="navbar-left">
                     
                </div>
                <div class="navbar-right">
                    <a href="http://artfl-project.uchicago.edu">The ARTFL Project</a>
                    <a href="http://www.uchicago.edu">University of Chicago</a>
                    <a href="http://artfl-project.uchicago.edu/content/contact-us" title="Contact information for the ARTFL Project">Contact Us</a>
                </div>
                <div class="navbar-header">
                    <a href="." class="navbar-brand" title="{{ philoConfig.dbname }}">{{ philoConfig.dbname }}</a>
                </div>
            </div>
        </div>
    </div>
    <div class="container-fluid" id="main-body">
        <div class="container" style="overflow: hidden;" ng-include="'templates/search_form.html'" ng-controller="searchForm"></div>
        <div class="container-fluid" id='philologic_response'>
            <div id="landing-page" ng-if="report === 'landing_page'" ng-include="'templates/landing_page.html'" ng-controller="landingPage" ></div>
            <div id="concordance" ng-if="report === 'concordance' || report === 'kwic'" ng-include="'templates/concordanceKwic.html'" ng-controller="concordanceKwicCtrl"></div>
        </div>
    </div> <!-- /main-body -->
    <div class="container-fluid" id="footer">
        <div class="row" >
            <div class="col-xs-offset-4 col-xs-4 col-sm-offset-5 col-sm-2">
                <hr>
            </div>
            <div class="col-xs-offset-3 col-xs-6" id="footer-content">
                Powered by <br>
                <a href="https://artfl-project.uchicago.edu/node/157" title="Philologic 4: Open Source ARTFL Search and Retrieval Engine">
                    <img src="css/images/philo.png" height="40" width="110"/>
                </a>4
            </div>
            <div class="col-xs-12">
                <!--Add any other content for your footer here-->
            </div>
        </div>
    </div>
    
    <!--Modal dialog-->
    <div id="syntax" class="modal fade" tabindex="-1" role="dialog" aria-labelledby="syntaxLabel" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <button type="button" class="close" data-dismiss="modal"><span aria-hidden="true">&times;</span><span class="sr-only">Close</span></button>
                    <h4 class="modal-title" id="syntaxLabel">Search Syntax</h4>
                </div>
                <div class="modal-body">
                    <p>In PhiloLogic4, the search syntax and semantics are largely the same for both word/phrase searching and metadata queries, with a few exceptions. The basic rules are:
                        <ul>
                            <li> plain terms such as <tt>genre humain</tt> or <tt>esprit systematique</tt> are split on the space character and evaluated without regard to case or accent.</li>
                            <li> quoted terms like <tt>"esprit de systeme"</tt> are precise matches against case and accent. In phrases they match individual tokens; in metadata fields they must
                            match the entire string value, i.e., <tt>"Histoire de la philosophie"</tt> or <tt>"Geographie sacree"</tt>.</li>
                            <li> "egrep-style" regular expressions (described below) are permitted in plain terms, but not quoted terms; thus, they cannot cross a token/word boundary, e.g., <tt>libert.</tt>
                            or <tt>nous m[aeiou].*er</tt>
                            <li> the vertical bar symbol <tt>|</tt> (on US keyboards, use the <tt>Shift + \</tt> keys) stands for a logical Boolean OR operator, and can concatenate plain, quoted, or regex
                            terms (e.g., <tt>liberte de penser | parler</tt> or <tt>philosophie eclectique | academique</tt>).</li>
                            <li> a space corresponds to a user-selected phrase operator in word search, controlled by the within/exactly/same-sentence option on the search form.  In metadata queries,
                            it corresponds to the Boolean AND operator (e.g., <tt>diderot mallet</tt>).
                            <li> the Boolean NOT operator is only permitted at the end of metadata fields; it accepts a single term or an OR expression: e.g., <tt>Geographie | Histoire NOT moderne</tt>.</li>
                        </ul>
                    </p>
                    <p>Basic regexp syntax, adapted from
                        <a href="http://www.gnu.org/software/findutils/manual/html_node/find_html/egrep-regular-expression-syntax.html#egrep-regular-expression-syntax">the egrep regular expression syntax</a>.
                        <ul>
                            <li>The character <tt>.</tt> matches any single character except newline. Bracket expressions can match sets or ranges of characters: [aeiou] or [a-z], but will only match a single character unless followed by one of the quantifiers below.</li>
                            <li> <tt>*</tt> indicates that the regular expression should match zero or more occurrences of the previous character or bracketed group.</li>
                            <li> <tt>+</tt> indicates that the regular expression should match one or more occurrences of the previous character or bracketed group.</li>
                            <li> <tt>?</tt> indicates that the regular expression should match zero or one occurrence of the previous character or bracketed group.</li>
                        </ul>
                        <div>
                            Thus, <tt>.*</tt> is an approximate "match anything" wildcard operator, rather than the more traditional (but less precise) <tt>*</tt> in many other search engines.
                        </div>
                    </p>
                </div>
            </div>
        </div>
    </div>
    <!--End of modal dialog-->
    
    <!-- Export results modal -->
    <div class="modal fade" id="export-dialog" tabindex="-1" role="dialog" aria-labelledby="exportLabel" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <button type="button" class="close" data-dismiss="modal"><span aria-hidden="true">&times;</span><span class="sr-only">Close</span></button>
                    <h4 class="modal-title" id="myModalLabel">Export Results</h4>
                </div>
                <div class="modal-body">
                    % if report != "collocation":
                        Export your results in JSON
                        <h5>Choose the format in which to export your search results:</h5>
                        <div id="export-buttons">
                            <button type="button" class="btn btn-primary" data-format="json">
                                JSON
                            </button>
                            <button type="button" class="btn btn-primary" data-format="csv" disabled>
                                CSV
                            </button>
                            <button type="button" class="btn btn-primary" data-format="tab" disabled>
                                TAB
                            </button>
                            <div>
                                Note: only JSON is currently supported.
                            </div>
                        </div>
                        <div id="export-download-link" style="display:none;margin-top: 20px;">
                            <a><span class="glyphicon glyphicon-download"></span> Download JSON file</a>
                        </div>
                    % else:
                        <h5>We currently don't support exporting results from a collocation report.</h5>
                    % endif
                </div>
            </div>
        </div>
    </div>
    <!--End of modal dialog-->
    
    <!--Load all required JavaScript-->
    <script src="http://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js" type="text/javascript"></script>
    <script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.3.10/angular-route.min.js"></script>
    <script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.3.10/angular-resource.min.js"></script>
    <script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.3.10/angular-route.min.js"></script>
    <script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.3.10/angular-animate.min.js"></script>
    <script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.3.10/angular-touch.min.js"></script>
    <script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.3.10/angular-sanitize.min.js"></script>
    <script src="js/bootstrap/bootstrap.min.js"></script>
    <script src="//cdn.jsdelivr.net/velocity/1.2.1/velocity.min.js"></script>
    <script src="//cdn.jsdelivr.net/velocity/1.2.1/velocity.ui.min.js"></script>
    <script src="js/plugins/angular-velocity.min.js"></script>
    <script>
        var philoApp = angular.module('philoApp', ['ngTouch', 'ngSanitize', 'angular-velocity']);
    </script>
    <script src="js/philoLogicMain.js"></script>
    <script src="js/landingPage.js"></script>
    <script src="js/searchForm.js"></script>
    <script src="js/concordanceKwic.js"></script>
    <!--PhiloLogic4 Javascript-->
</body>
</html>
