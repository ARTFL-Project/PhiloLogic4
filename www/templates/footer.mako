## -*- coding: utf-8 -*-
                </div> <!--container-fluid-->
            </div> <!-- /main_body -->
            <div id="push"></div>
            <div id="footer">
                <div class="navbar navbar-inverse">
                    <div class="container-fluid" style="padding-top: 5px">
                        <div class="navbar-left">
                            <a href="https://artfl-project.uchicago.edu/node/157" title="Philologic 4: Open Source ARTFL Search and Retrieval Engine">PhiloLogic4</a><br>
                            <a href="http://artfl-project.uchicago.edu/content/contact-us" title="Contact information for the ARTFL Project">contact us</a>                   
                        </div>
                        <div class="navbar-right">
                                <img src="${config.db_url}/css/images/philo.png" height="40" width="110"/>
                        </div>
                    </div>
                </div>
            </div> <!-- /footer -->
        </div> <!--wrapper-->
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
    </body>
</html>