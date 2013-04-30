<div id="form_body" class='form_body'>
    <form id="search" action="${db.locals['db_url'] + "/dispatcher.py/"}">
        <div class="initial_form">
            <table style="margin: 0 auto">
                <tr class="table_row" ><td><span class="search_field" style="margin-right: 10px;">Search Terms:</span></td>
                <td class="second_column"><input type='text' name='q' id='q' class="search_box"></td>
                <td><input id="button1" type='submit' value="Search"/></td>
                <td><span class="more_options">Show search options</span></td>
                </tr>
            </table>
            <div id="report" class="report">
                <h3 style="padding-left: 5px;">Choose a search report:</h3>
                <input type="radio" name="report" id="report1" value='concordance' checked="checked"><label for="report1">Concordance Report</label>
                <input type="radio" name="report" id="report2" value='relevance'><label for="report2">Ranked Relevance Report</label>
                <input type="radio" name="report" id="report4" value='collocation'><label for="report4">Collocation Table</label>
                <input type="radio" name="report" id="report5" value='frequency'><label for="report5">Frequency Table</label>
                <input type="radio" name="report" id="report6" value='time_series'><label for="report6">Time Series Report</label>
            </div>
         </div>
         <div class="search_explain">
            <h3 class="conc_question">What does a concordance report do?</h3>
            <div class="explain_conc">
               Concordance search finds every single occurrence of the search term(s)
               throughout the database filtered by optional metadata criteria.
            </div>
            <h3 class="relev_question">What does a ranked relevance report do?</h3>
            <div class="explain_relev">
                Ranked relevance search ranks documents by pertinence based on the frequency
                of the search term(s).
                <br>Note that this type of search is done on individual words, and therefore will not
                be aware of phrases or expressions.
            </div>
            <h3 class="freq_question">What does a frequency report do?</h3>
            <div class="explain_freq">
                Frequency report will display a table with frequency counts of the search term(s) ordered
                by the selected metadata field.
            </div>
            <h3 class="colloc_question">What does a collocation report do?</h3>
            <div class='explain_colloc'>
                Collocation report will display words in the immediate vicinity of the search term(s).
                You can define how close these words must be.
            </div>
            <h3 class="time_question">What does a time series report do?</h3>
            <div class='explain_time'>
                Time Series report displays a graph showing the frequency of the search term(s) throughout the database
                during a set time period.
            </div>
        </div>
         <div id="search_elements" class="search_elements">
            <h3>Refine your search with the following options and fields:</h3>
            <div id='method'>
                <table>
                    <tr><td class="first_column"><span class="search_field">Search Terms</span></td>
                    <td>
                    <input type="radio" name="method" id="method1" value='proxy' checked="checked"><label for="method1">Within</label>
                    <input type='text' name='arg_proxy' id='arg_proxy' style="margin-left:15px !important;width:30px; text-align: center;">
                    <span style="padding-left:5px;">words</span>
                    <br><input type="radio" name="method" id="method2" value='phrase'><label for="method2">Exactly</label>
                    <input type='text' name='arg_phrase' id='arg_phrase' style="margin-left:11px !important;width:30px; text-align: center;">
                    <span style="padding-left:5px;">words</span>
                    <br><input type="radio" name="method" id="method3" value='cooc'><label for="method3">In the same sentence</label>
                    </td></tr>
                </table>
            </div>
            <div id="metadata_fields">
                <table class="table_row">
                    % for facet in db.locals["metadata_fields"]:
						<%
						if "metadata_aliases" in db.locals and facet in db.locals["metadata_aliases"]:
							alias = db.locals["metadata_aliases"][facet]
						else:
							alias = facet
						%>
                        <tr class="table_row"><td class="first_column"><span class="search_field">${alias}:</span></td><td><input type='text' name='${facet}' id="${facet}" class="search_box"></td></tr>
                    % endfor
                </table>
            </div>
            <table> 
                <tr class="table_row" id="collocation"><td class="first_column">Within </td>
                    <td>
                        <label for="word_num"></label>
                        <input id="word_num" name="word_num" />
                        (1-20) words
                    </td>
                </tr>
               
                <tr class="table_row" id="frequency">
                    <td class="first_column">
                        <span class="search_field">Frequency by:</span>
                    </td>
                    <td>
                        <label class="custom-select">
                            <select id='field' name="field">
                                % for facet in db.locals["metadata_fields"]:
									<%
									if "metadata_aliases" in db.locals and facet in db.locals["metadata_aliases"]:
										alias = db.locals["metadata_aliases"][facet]
									else:
										alias = facet
									%>
                                    <option value='${alias}'>${alias}                                    
                                % endfor
                            </select>
                        </label>
                    </td>
                </tr>
                
                <tr class="table_row" id="time_series">
                <td class="first_column">Date range:</td><td><span class="search_field">from </span><input type='text' name="start_date" id="start_date" style="width:35px;"><span class="search_field"> to </span><input type='text' name="end_date" id="end_date" style="width:35px;">
                <tr class="table_row" id="year_interval"><td class="first_column"><span class="search_field">Year interval:</span></td><td><span id="year_interval">
                <input type="radio" name="year_interval" id="year0" value="1" checked="checked"><label for="year0">every year</label>
                <input type="radio" name="year_interval" id="year1" value="10" checked="checked"><label for="year1">every 10 years</label>
                <input type="radio" name="year_interval" id="year2" value="25"><label for="year2">every 25 years</label>
                </span>
                </td></tr>
                
                <tr class="table_row" id="results_per_page"><td class="first_column"><span class="search_field">Results per page:</span></td>
                <td><span id='page_num'>
                    <input type="radio" name="pagenum" id="pagenum1" value='20'><label for="pagenum1">20</label>
                    <input type="radio" name="pagenum" id="pagenum2" value='50' checked="checked"><label for="pagenum2">50</label>
                    <input type="radio" name="pagenum" id="pagenum3" value='100'><label for="pagenum3">100</label>
                </span></td></tr>
                <tr class="table_row"><td class="first_column"><input id="button" type='submit' value="Search"/></td>
                <td><button type="reset" id="reset_form">Clear form</button></td></tr>
            </table>
        </div>
    </form>
</div>
<div id="waiting" style="display:none;z-index:99;position:absolute;"><img src="http://pantagruel.ci.uchicago.edu/philo4/Frantext_clovis/js/ajax-loader.gif" alt="Loading..."/></div>