## -*- coding: utf-8 -*-
<div id='search_overlay'></div>
<div class="container" style="overflow: hidden;">
    <form id="search" action="${config.db_url + "/dispatcher.py/"}" role="form">
    <div id="form_body">
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
                        <div class="col-xs-12 col-sm-10 col-md-6">
                            <div class="input-group">
                                <span class="input-group-btn">
                                    <button class="btn btn-default" type="button" id="tip-btn" data-toggle="modal" data-target="#syntax">
                                        <span id="tip">?</span><span id="tip-text">Tips</span>
                                    </button>
                                </span>
                                <input type='text' name='q' id='q' class="form-control">
                                <span class="input-group-btn">
                                    <button type="submit" class="btn btn-primary" id="button-search">
                                        <span class="glyphicon glyphicon-search" style="vertical-align:text-top;"></span>
                                    </button>
                                </span> 
                            </div>
                        </div>
                        <div class="col-xs-12 col-sm-12 col-md-4" id="search-buttons">
                            <button type="reset" id="reset_form" class="btn btn-danger">Clear</button>
                            <button type="button" id="show-search-form" class="btn btn-primary" data-display="none" style="display: none">Show search options</button>
                        </div>
                    </div>
                </div>
            </div>
            <div id="search_elements">
                <h5>Refine your search with the following options and fields:
                </h5>             
                <!--This row defines the search method options-->
                <div class="row hidden-xs" id='method'>
                    <div class="col-xs-12 col-sm-2" style="margin-top: 40px;">
                        Search Terms
                    </div>
                    <div class="col-xs-12 col-sm-3 col-lg-2" id="method-buttons">
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
                        <input type='text' name='arg_proxy' id='arg_proxy' class="form-control" style="width:40px; text-align: center;">
                        <span style="padding-left: 10px">words in the same sentence</span><br>  
                        <input type='text' name='arg_phrase' id='arg_phrase' class="form-control" style="width:40px; text-align: center;">
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
        </div>
        <div id="fixed-search" class="row">
            <div class="col-xs-4 col-sm-3">
                <button type="button" id="top-of-page" class="btn btn-primary btn-sm">
                    Back to top
                </button>
            </div>
            <div class="col-xs-8 col-sm-6">
                <div class="input-group">
                    <input type='text' name='q' id='q2' class="form-control input-sm">
                    <span class="input-group-btn">
                        <button type="submit" class="btn btn-primary btn-sm" id="button-search2">
                            <span class="glyphicon glyphicon-search" style="vertical-align:text-top;"></span>
                        </button>
                    </span> 
                </div>
            </div>
            <div class="hidden-xs col-sm-3">
                <button type="button" id="back-to-full-search" class="btn btn-primary btn-sm pull-right">
                    Back to full search form
                </button>
            </div>
        </div>
    </form>
    <div id="waiting" style="display:none;z-index:99;position:absolute;">
        <img src="${config.db_url}/js/gif/ajax-loader.gif" alt="Loading..."/>
    </div>
</div>