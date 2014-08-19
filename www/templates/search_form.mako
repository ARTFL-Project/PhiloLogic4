## -*- coding: utf-8 -*-
<div id='search_overlay'></div>
<div class="container" style="overflow: hidden;">
    <div id="form_body">
        <form id="search" action="${config.db_url + "/dispatcher.py/"}" role="form">
            <div id="initial-form">
                <div id="report" class="btn-group btn-group-justified" data-toggle="buttons">
                    % if "concordance" in config.search_reports:
                        <label class="btn btn-primary active">
                            <input type="radio" name="report" id="concordance" value='concordance' checked="checked">
                            Concordance
                        </label>
                    % endif
                    % if "kwic" in config.search_reports:
                        <label class="btn btn-primary hidden-xs">
                            <input type="radio" name="report" id="kwic" value='kwic'>
                            KWIC
                        </label>
                    % endif
                    % if "collocation" in config.search_reports:
                        <label class="btn btn-primary">
                            <input type="radio" name="report" id="collocation" value='collocation'>
                            Collocation
                        </label>
                    % endif
                    % if "time_series" in config.search_reports:
                        <label class="btn btn-primary hidden-xs">
                            <input type="radio" name="report" id="time_series" value='time_series'>
                            Time Series
                        </label>
                    % endif
                </div>
                <div id="search_terms_container">
                    <div id="search_terms" class="row">
                        <div class="col-xs-12 col-sm-2 text-row">
                            Search Terms:
                        </div>
                        <div class="col-xs-12 col-sm-10 col-md-5">
                            <div class="input-group">
                                <input type='text' name='q' id='q' class="form-control">
                                <span class="input-group-btn">
                                    <button class="btn btn-default" type="button" id="tip-btn" data-toggle="modal" data-target="#syntax">
                                        <span id="tip">?</span><span id="tip-text">Tips</span>
                                    </button>
                                </span>
                            </div>
                        </div>
                        <div class="col-xs-12 col-sm-12 col-md-5" id="search-buttons">
                            <input id="button1" type='submit' class="btn btn-primary" value="Search"/>
                            <button type="reset" id="reset_form1" class="btn btn-danger">Clear form</button>
                            <button type="button" id="show-search-form" class="btn btn-danger" data-display="none">Show search options</button>
                        </div>
                    </div>
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
                </div>
            </div>
            <div id="search_elements">
                <h5>Refine your search with the following options and fields:
                </h5>             
                <!--This row defines the search method options-->
                <div class="row hidden-xs" id='method'>
                    <div class="col-xs-12 col-sm-2">
                        Search Terms
                    </div>
                    <div class="col-xs-12 col-sm-3 col-lg-2">
                        <div class="btn-group-vertical" data-toggle="buttons">
                            <label class="btn btn-primary active">
                                <input type="radio" name="method" id="method1" value='proxy' checked="checked">
                                Within
                            </label>
                            <label class="btn btn-primary">
                                <input type="radio" name="method" id="method2" value='phrase'>
                                Exactly
                            </label>
                            <label class="btn btn-primary">
                                <input type="radio" name="method" id="method3" value='cooc'>
                                In the same sentence
                            </label>
                        </div>
                    </div>
                    <div class="col-xs-12 col-sm-7 col-lg-8">
                        <input type='text' name='arg_proxy' id='arg_proxy' class="form-control" style="width:30px; text-align: center;">
                        <span style="padding-left: 10px">words in the same sentence</span><br>  
                        <input type='text' name='arg_phrase' id='arg_phrase' class="form-control" style="width:30px; text-align: center;">
                        <span style="padding-left: 10px">words in the same sentence</span>
                    </div>
                </div>
                <div id="metadata_fields">
                    % for facet in config.metadata:
                        <%
                        if facet in config.metadata_aliases:
                            alias = config.metadata_aliases[facet]
                        else:
                            alias = facet
                        %>
                        <div class="row">
                            <div class="col-xs-12 col-sm-2 col-md-2 text-row">
                                ${alias}:
                            </div>
                            <div class="col-xs-12 col-sm-4 col-md-4">
                                <input type='text' name='${facet}' id="${facet}" class="form-control">
                            </div>
                            <div class="col-xs-12 col-sm-4 col-md-6 text-row">
                                (e.g., ${config.search_examples[facet]})
                            </div>
                        </div>
                    % endfor
                </div>
                <div id="collocation_num" class="row">
                    <div class="col-xs-6 col-sm-2 col-md-2 text-row">
                        Within
                    </div>
                    <div class="col-xs-6 col-sm-1 col-md-1">
                        <select name="word_num" id="word_num" class="form-control">
                            <option>1</option>
                            <option>2</option>
                            <option>3</option>
                            <option>4</option>
                            <option selected>5</option>
                            <option>6</option>
                            <option>7</option>
                            <option>8</option>
                            <option>9</option>
                            <option>10</option>
                        </select>
                    </div>
                    <div class="col-xs-12 col-sm-5 col-md-9 text-row">
                        (1-10) words
                    </div>
                </div>
                <div id="time_series_num" class="row">
                    <div class="col-xs-12 col-sm-2 col-md-2 text-row">
                        Date range:
                    </div>
                    <div class="col-xs-12 col-sm-10 col-md-10">
                        from <input type='text' name="start_date" id="start_date" style="width:35px;">
                        to <input type='text' name="end_date" id="end_date" style="width:35px;">
                    </div>
                </div>
                <div id="date_range" class="row">
                    <div class="col-xs-12 col-sm-2 col-md-2 text-row">
                        Year interval:
                    </div>
                    <div class="col-xs-12 col-sm-10 col-md-10">
                        <% time_options = {1: "Year", 10: "Decade", 50: "Half Century", 100: "Century"} %>
                        <div id="year_interval" class="btn-group" data-toggle="buttons">
                            % for pos, year in enumerate(config.time_series_intervals):
                                % if pos == 0:
                                    <label class="btn btn-primary active">
                                        <input type="radio" name="year_interval" id="year0" value="${year}" checked>
                                        ${time_options[year]}
                                    </label>
                                % else:
                                    <label class="btn btn-primary">
                                        <input type="radio" name="year_interval" id="year${pos}" value="${year}">
                                        ${time_options[year]}
                                    </label>
                                % endif
                            % endfor
                        </div>
                    </div>
                </div>
                <div id="results_per_page" class="row">
                    <div class="col-xs-12 col-sm-2 col-md-2 text-row">
                        Results per page:
                    </div>
                    <div class="col-xs-12 col-sm-10 col-md-10">
                        <div class="btn-group" id='page_num' data-toggle="buttons">
                            <label class="btn btn-primary active">
                                <input type="radio" name="pagenum" id="pagenum1" value='25' checked="checked">
                                25
                            </label>
                            <label class="btn btn-primary">
                                <input type="radio" name="pagenum" id="pagenum2" value='50'>
                                50
                            </label>
                            <label class="btn btn-primary">
                                <input type="radio" name="pagenum" id="pagenum3" value='100'>
                                100
                            </label>
                        </div>
                    </div>
                </div>
            </div>
            <div id="bottom_search">
                <input id="button2" type='submit' value="Run Task"/>
            </div>
        </form>
    </div>
    <div id="waiting" style="display:none;z-index:99;position:absolute;">
        <img src="${config.db_url}/js/gif/ajax-loader.gif" alt="Loading..."/>
    </div>
</div>