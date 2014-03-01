## -*- coding: utf-8 -*-
<div id="form_body">
    <form id="search" action="${db.locals['db_url'] + "/dispatcher.py/"}">
        <div id="initial_form">
            <div id="report" class="report" style="margin-top:0px">
                <span id="concordance_button" style="display: none;">
                    <input type="radio" name="report" id="concordance" value='concordance' checked="checked">
                    <label for="concordance">Concordance</label>
                </span>
                <span id="kwic_button" style="display: none;">
                    <input type="radio" name="report" id="kwic" value='kwic'>
                    <label for="kwic">Key Word in Context (KWIC)</label>
                </span>
                <span id="relevance_button" style="display: none;">
                    <input type="radio" name="report" id="relevance" value='relevance'>
                    <label for="relevance">Ranked Relevance</label>
                </span>
                <span id="collocation_button" style="display: none;">
                    <input type="radio" name="report" id="collocation" value='collocation'>
                    <label for="collocation">Collocation</label>
                </span>
                <span id="time_series_button" style="display: none;">
                    <input type="radio" name="report" id="time_series" value='time_series'>
                    <label for="time_series">Time Series</label>
                </span>
                <span id="frequencies_button" style="display: none;">
                    <input type="radio" name="report" id="frequencies" value="frequencies">
                    <label for="frequencies">Frequencies</label>
                </span>
            </div>
            <div id="search_terms_container">
                <div id="search_terms">
                    <span id="search_field">Search Terms:</span>
                    <input type='text' name='q' id='q' class="search_box">
                    <input id="button1" type='submit' value="Search"/>
                    <button type="reset" id="reset_form1">Clear form</button>
                    <span id="more_options">Show search options</span>
                </div>
                <div id="syntax" style="width:514px;">
                    <span id='syntax_title'>
                        Click for tips on the query syntax
                    </span>
                    <div id="syntax_explain" style="display:none;">
                        <p style="margin-top:-5px;">
                            In PhiloLogic4, the search syntax and semantics are largely the same for both word/phrase searching and metadata queries, with a few exceptions. The basic rules are:
                            <ol style="list-style:decimal;padding-left:20px;">
                                <li> plain terms such as <tt>genre humain</tt> or <tt>esprit systematique</tt> are split on the space character and evaluated without regard to case or accent.</li>
                                <li> quoted terms like <tt>"esprit de systeme"</tt> are precise matches against case and accent. In phrases they match individual tokens; in metadata fields they must
                                match the entire string value, i.e., <tt>"Histoire de la philosophie"</tt> or <tt>"Geographie sacree"</tt>.</li>
                                <li> "egrep-style" regular expressions (described below) are permitted in plain terms, but not quoted terms; thus, they cannot cross a token/word boundary, e.g., <tt>libert.</tt> or <tt>nous m[aeiou].*er</tt>
                                <li> the vertical bar symbol <tt>|</tt> (on US keyboards, use the <tt>Shift + \</tt> keys) stands for a logical Boolean OR operator, and can concatenate plain, quoted, or regex terms (e.g., <tt>liberte de penser | parler</tt> or <tt>philosophie eclectique | academique</tt>).</li>
                                <li> a space corresponds to a user-selected phrase operator in word search, controlled by the within/exactly/same-sentence option on the search form.  In metadata queries, it corresponds to the Boolean AND operator (e.g., <tt>diderot mallet</tt>).
                                <li> the Boolean NOT operator is only permitted at the end of metadata fields; it accepts a single term or an OR expression: e.g., <tt>Geographie | Histoire NOT moderne</tt>.</li>
                            </ol>
                        </p>
                        <p>
                            Basic regexp syntax, adapted from
                            <a href="http://www.gnu.org/software/findutils/manual/html_node/find_html/egrep-regular-expression-syntax.html#egrep-regular-expression-syntax">the egrep regular expression syntax</a>.
                            <ul style="margin-left: -25px">
                            <li>The character <tt>.</tt> matches any single character except newline. Bracket expressions can match sets or ranges of characters: [aeiou] or [a-z], but will only match a single character unless followed by one of the quantifiers below.</li>
                            <li> <tt>*</tt> indicates that the regular expression should match zero or more occurrences of the previous character or bracketed group.</li>
                            <li> <tt>+</tt> indicates that the regular expression should match one or more occurrences of the previous character or bracketed group.</li>
                            <li> <tt>?</tt> indicates that the regular expression should match zero or one occurrence of the previous character or bracketed group.</li></ul>
                            <div style="margin-top: -12px;">
                                Thus, <tt>.*</tt> is an approximate "match anything" wildcard operator, rather than the more traditional (but less precise) <tt>*</tt> in many other search engines.
                            </div>
                        </p>
                    </div>
                </div>
            </div>
        </div>
        <div id="search_explain">
            <h3 id="concordance_question">What does a concordance report do?</h3>
            <div id="explain_conc">
               Concordance search finds every single occurrence of the search term(s)
               throughout the database filtered by optional metadata criteria.<p/>

               Metadata-only searches are also permitted; simply leave the main "Search Terms" box empty, and enter your desired metadata criteria as usual.
            </div>
            <h3 id="relev_question">What does a ranked relevance report do?</h3>
            <div id="explain_relev">
                Ranked relevance search ranks documents by pertinence based on the frequency
                of the search term(s).
                <br>Note that this type of search is done on individual words, and therefore will not
                be aware of phrases or expressions.
            </div>
            <h3 id="kwic_question">What does a Key Word in Context (KWIC) report do?</h3>
            <div id="explain_kwic">
  	        Just like the concordance search, Key Word in Context (KWIC) search finds every occurence of the search terms,
                but displays the results in a much more compact format, one line per result item.
            </div>
            <h3 id="colloc_question">What does a collocation report do?</h3>
            <div id='explain_colloc'>
                Collocation report will display words in the immediate vicinity of the search term(s).
                You can define how close these words must be.
            </div>
            <h3 id="time_question">What does a time series report do?</h3>
            <div id='explain_time'>
                Time Series report displays a graph showing the frequency of the search term(s) throughout the database
                during a set time period.
            </div>
        </div>
        <div id="search_elements">
            <h3>Refine your search with the following options and fields:</h3>
            <div id='method'>
                <table>
                    <tr>
                        <td class="first_column">
                            <span class="search_field">Search Terms</span>
                        </td>
                    <td>
                        <input type="radio" name="method" id="method1" value='proxy' checked="checked">
                        <label for="method1">Within</label>
                        <input type='text' name='arg_proxy' id='arg_proxy' style="margin-left:15px !important;width:30px; text-align: center;">
                        <span style="padding-left:5px;">words</span>
                        <br><input type="radio" name="method" id="method2" value='phrase'>
                        <label for="method2">Exactly</label>
                        <input type='text' name='arg_phrase' id='arg_phrase' style="margin-left:11px !important;width:30px; text-align: center;">
                        <span style="padding-left:5px;">words</span>
                        <br><input type="radio" name="method" id="method3" value='cooc'>
                        <label for="method3">In the same sentence</label>
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
                        <tr class="table_row">
							<td class="first_column">
                                <span class="search_field">${alias}:</span>
                            </td>
							<td><input type='text' name='${facet}' id="${facet}" class="search_box"></td>
						</tr>
                    % endfor
                </table>
            </div>
            <table> 
                <tr class="table_row" id="collocation_num">
                    <td class="first_column">Within </td>
                    <td>
                        <label for="word_num"></label>
                        <input id="word_num" name="word_num" />
                        (1-10) words
                    </td>
                </tr>
                <tr class="table_row" id="time_series_num">
					<td class="first_column">Date range:</td>
					<td>
						<span class="search_field">from </span>
						<input type='text' name="start_date" id="start_date" style="width:35px;">
						<span class="search_field"> to </span>
						<input type='text' name="end_date" id="end_date" style="width:35px;">
                <tr class="table_row" id="year_interval">
					<td class="first_column">
						<span class="search_field">Year interval:</span>
					</td>
					<td>
						<span id="year_interval">
							<input type="radio" name="year_interval" id="year1" value="10" checked="checked">
                            <label for="year1">Decade</label>
                            <input type="radio" name="year_interval" id="year3" value="50">
                            <label for="year3">Half Century</label>
							<input type="radio" name="year_interval" id="year2" value="100">
                            <label for="year2">Century</label>
						</span>
					</td>
				</tr>
                <tr class="table_row" id="results_per_page">
                    <td class="first_column">
                        <span class="search_field">Results per page:</span>
                    </td>
                    <td>
                        <span id='page_num'>
                            <input type="radio" name="pagenum" id="pagenum1" value='25' checked="checked">
                            <label for="pagenum1">25</label>
                            <input type="radio" name="pagenum" id="pagenum2" value='50'>
                            <label for="pagenum2">50</label>
                            <input type="radio" name="pagenum" id="pagenum3" value='100'>
                            <label for="pagenum3">100</label>
                        </span>
                    </td>
                </tr>
            </table>
        </div>
		<div id="bottom_search">
			<input id="button2" type='submit' value="Run Task"/>
		</div>
    </form>
</div>
<div id="waiting" style="display:none;z-index:99;position:absolute;">
    <img src="${db.locals['db_url']}/js/gif/ajax-loader.gif" alt="Loading..."/>
</div>