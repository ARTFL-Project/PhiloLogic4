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
                            <ul style="list-style:decimal;padding-left:20px;">
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
                            <ul style="margin-left: -25px">
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
        
        <!--Load all required JavaScript-->
        <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js" type="text/javascript"></script>
        <script src="${config.db_url}/js/bootstrap/bootstrap.min.js" type="text/javascript"></script>
        <script type="text/javascript" src="http://code.jquery.com/ui/1.11.0/jquery-ui.min.js"></script>
        <script type="text/javascript" src="${config.db_url}/js/plugins/jquery.history.js"></script>
        <script type="text/javascript" src="${config.db_url}/js/plugins/jquery.velocity.min.js"></script>
        % if not db.locals['debug']:
            <script src="${config.db_url}/js/${report}.js" type="text/javascript"></script>
        % else:
            % for script in ressources['js'][report]:
                <script src="${config.db_url}/js/${script}" type="text/javascript"></script>
            % endfor
        % endif
    </body>
</html>