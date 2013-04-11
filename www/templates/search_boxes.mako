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
                        <tr class="table_row"><td class="first_column"><span class="search_field">${facet.title()}:</span></td><td><input type='text' name='${facet}' id="${facet}" class="search_box"></td></tr>
                    % endfor
                </table>
            </div>
            <table> 
                <tr class="table_row" id="collocation"><td class="first_column">Within </td><td><span id='word_num'>
                <input type="radio" name="word_num" id="wordnum1" value="1"><label for="wordnum1">1</label>
                <input type="radio" name="word_num" id="wordnum2" value="2"><label for="wordnum2">2</label>
                <input type="radio" name="word_num" id="wordnum3" value="3"><label for="wordnum3">3</label>
                <input type="radio" name="word_num" id="wordnum4" value="4"><label for="wordnum4">4</label>
                <input type="radio" name="word_num" id="wordnum5" value="5" checked="checked"><label for="wordnum5">5</label>
                <input type="radio" name="word_num" id="wordnum6" value='6'><label for="wordnum6">6</label>
                <input type="radio" name="word_num" id="wordnum7" value='7'><label for="wordnum7">7</label>
                <input type="radio" name="word_num" id="wordnum8" value='8'><label for="wordnum8">8</label>
                <input type="radio" name="word_num" id="wordnum9" value="9"><label for="wordnum9">9</label>
                <input type="radio" name="word_num" id="wordnum10" value="10"><label for="wordnum10">10</label>
                </span> words</td></tr>
               
                <tr class="table_row" id="frequency"><td class="first_column"><span class="search_field">Frequency by:</span></td><td><span id='field'>
                % for pos, facet in enumerate(db.locals["metadata_fields"]):
                    % if pos == 0:
                        <input type="radio" name="field" id="field${pos}" value='${facet}' checked='checked'><label for="field${pos}">${facet}</label>
                    % else:
                        <input type="radio" name="field" id="field${pos}" value='${facet}'><label for="field${pos}">${facet}</label>
                    % endif
                % endfor
                </span>
                </td></tr>
                
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