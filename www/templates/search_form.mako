## -*- coding: utf-8 -*-
<div class="container" style="overflow: hidden;">
    <form id="search" action="dispatcher.py/" role="form">
        <div id="form_body" ng-controller="searchForm">
            <div id="search_overlay" ng-if="formOpen" class="overlay-fadeOut"></div>
            <div id="initial-form">
                <div id="report" class="btn-group btn-group-justified" data-toggle="buttons" ng-click="reportClicked($event)">
                    <label class="btn btn-primary active" ng-if="searchReports.indexOf('concordance') > -1">
                        <input type="radio" name="report" id="concordance" value='concordance' checked="checked">
                        Concordance
                    </label>
                    <label class="btn btn-primary hidden-xs" ng-if="searchReports.indexOf('kwic') > -1">
                        <input type="radio" name="report" id="kwic" value='kwic'>
                        KWIC
                    </label>
                    <label class="btn btn-primary" ng-if="searchReports.indexOf('collocation') > -1">
                        <input type="radio" name="report" id="collocation" value='collocation'>
                        Collocation
                    </label>
                    <label class="btn btn-primary hidden-xs" ng-if="searchReports.indexOf('time_series') > -1">
                        <input type="radio" name="report" id="time_series" value='time_series'>
                        Time Series
                    </label>
                </div>
                <div id="search_terms_container">
                    <div id="search_terms" class="row">
                        <div class="col-xs-12 col-sm-2 text-row">
                            Search Terms:
                        </div>
                        <div class="col-xs-12 col-sm-10 col-md-6">
                            <div class="input-group">
                                <span class="input-group-btn hidden-xs">
                                    <button class="btn btn-default" type="button" id="tip-btn" data-toggle="modal" data-target="#syntax">
                                        <span id="tip">?</span><span id="tip-text">Tips</span>
                                    </button>
                                </span>
                                <input type='text' name='q' id='q' class="form-control" data-script="scripts/autocomplete_term.py">
                                <span class="input-group-btn">
                                    <button type="submit" class="btn btn-primary" id="button-search">
                                        <span class="glyphicon glyphicon-search" style="vertical-align:text-top;"></span>
                                    </button>
                                </span> 
                            </div>
                        </div>
                        <div class="col-xs-12 col-sm-12 col-md-4" id="search-buttons" ng-controller="showSearchForm">
                            <button type="reset" id="reset_form" class="btn btn-danger">Clear</button>
                            <button type="button" id="show-search-form" class="btn btn-primary" data-display="none" ng-click="toggle()">Show search options</button>
                        </div>
                    </div>
                </div>
            </div>
            <div id="search-elements" ng-if="formOpen" class="velocity-opposites-transition-slideDownIn" data-velocity-opts="{ duration: 400 }">
                <h5>Refine your search with the following options and fields:
                </h5>
                <!--This row defines the search method options-->
                <div class="row hidden-xs" id='method' ng-if="report != 'collocation'">
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
                <div id="metadata_fields" data-script="scripts/autocomplete_metadata.py?field=" ng-controller="searchMetadata">
                    <div class="row" ng-repeat="(metadata, displayValue) in metadataFields">
                        <div class="col-xs-12 col-sm-2 col-md-2 text-row">
                            {{ displayValue.value }}:
                        </div>
                        <div class="col-xs-12 col-sm-4 col-md-4">
                            <input type='text' name='{{ metadata }}' id="{{ metadata }}" class="form-control">
                        </div>
                        <div class="col-xs-12 col-sm-4 col-md-6 text-row">
                            (e.g., {{ displayValue.example }})
                        </div>
                    </div>
                </div>
                <div id="collocation-options" class="row" ng-if="report == 'collocation'">
                    <div class="col-xs-12">
                        <div class="row">
                            <div class="col-xs-3 col-sm-2 col-md-2 text-row">
                                Within
                            </div>
                            <div class="col-xs-2 col-sm-1 col-md-1">
                                <select name="word_num" id="word_num" class="form-control" style="width: auto;">
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
                            <div class="col-xs-7 col-sm-5 col-md-7 text-row">
                                (1-10) words
                            </div>
                        </div>
                    </div>
                    <div class="col-xs-12" style="margin-top: 10px;">
                        <div class="row">
                            <div class="col-xs-3 col-sm-2 col-md-2 text-row">
                                Word Filtering
                            </div>
                            <div class="col-xs-2 col-sm-1">
                                <select name="filter_frequency" id="filter_frequency" class="form-control" style="width: auto;">
                                    <option>25</option>
                                    <option>50</option>
                                    <option>75</option>
                                    <option selected>100</option>
                                    <option>125</option>
                                    <option>150</option>
                                    <option>175</option>
                                    <option>200</option>
                                </select>
                            </div>
                            <div class="col-xs-6 col-sm-2">
                                <div class="btn-group-vertical" role="group" data-toggle="buttons" id="colloc_filter_choice" ng-controller="collocationFilter">
                                    <label class="btn btn-primary active" id="colloc-filter-frequency">
                                        <input type="radio" name="colloc_filter_choice" value="frequency" checked="checked">Most frequent terms
                                    </label>
                                    <label class="btn btn-primary" id="colloc-filter-stopwords" ng-if="stopwords">
                                        <input type="radio" name="colloc_filter_choice" value="stopwords">Stopwords
                                    </label>
                                    <label class="btn btn-primary" id="colloc-no-filter">
                                        <input type="radio" name="colloc_filter_choice" value="nofilter">No filtering
                                    </label>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div id="time_series_num" class="row" ng-if="report == 'time_series'">
                    <div class="col-xs-12 col-sm-2 col-md-2 text-row">
                        Date range:
                    </div>
                    <div class="col-xs-12 col-sm-10 col-md-10">
                        from <input type='text' name="start_date" id="start_date" style="width:35px;">
                        to <input type='text' name="end_date" id="end_date" style="width:35px;">
                    </div>
                </div>
                <div id="date_range" class="row" ng-if="report == 'time_series'">
                    <div class="col-xs-12 col-sm-2 col-md-2 text-row">
                        Year interval:
                    </div>
                    <div class="col-xs-12 col-sm-10 col-md-10" ng-controller="timeSeriesInterval">
                        <div id="year_interval" class="btn-group" data-toggle="buttons">
                            <label class="btn btn-primary active">
                                <input type="radio" name="year_interval" id="year0" value="{{ intervals[0].date }}" checked>
                                {{ intervals[0].alias }}
                            </label>
                            <label class="btn btn-primary" ng-repeat="display in intervals.slice(1)">
                                <input type="radio" name="year_interval" id="year{{ $index }}" value="{{ display.date }}">
                                {{ display.alias }}
                            </label>
                        </div>
                    </div>
                </div>
                <div id="results_per_page" class="row" ng-if="report != 'collocation' && report != 'time_series'">
                    <div class="col-xs-12 col-sm-2 col-md-2 text-row">
                        Results per page:
                    </div>
                    <div class="col-xs-12 col-sm-10 col-md-10">
                        <div class="btn-group" id='results_per_page' data-toggle="buttons">
                            <label class="btn btn-primary active">
                                <input type="radio" name="results_per_page" id="pagenum1" value='25' checked="checked">
                                25
                            </label>
                            <label class="btn btn-primary">
                                <input type="radio" name="results_per_page" id="pagenum2" value='50'>
                                50
                            </label>
                            <label class="btn btn-primary">
                                <input type="radio" name="results_per_page" id="pagenum3" value='100'>
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
                    <input type='text' id='q2' class="form-control input-sm">
                    <span class="input-group-btn">
                        <button type="button" class="btn btn-primary btn-sm" id="button-search2">
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
    <div id="waiting">
    </div>
</div>