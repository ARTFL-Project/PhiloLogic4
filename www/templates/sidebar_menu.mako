<div class="btn-group pull-right">
    <button type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown">
        <span id="menu-header">Display frequency by</span>
        <span id="selected-sidebar-option" data-selected="${config['facets'][0].keys()[0]}"></span>
        <span class="caret"></span>
    </button>
    <ul class="dropdown-menu" role="menu" id="frequency_field">
        <li role="presentation" class="dropdown-header">Display frequency by</li>
        % for facet in config["facets"]:
            <%
            facet_name = facet.keys()[0]
            script = ajax["frequency"] + '&frequency_field=' + facet_name
            %>
            <li><a class="sidebar-option" id="side_opt_${facet_name}" data-value='${facet_name}' data-script="${script}">${facet_name}</a></li>
        % endfor
        % if report != 'bibliography':
            <li class="divider"></li>
            <li role="presentation" class="dropdown-header">Display collocates on</li>
			<li><a class="sidebar-option" id="side_opt_collocate" data-value='all_collocates' data-display='both sides' data-script="${ajax['collocation']}">Both sides</a></li>
            <li><a class="sidebar-option" id="side_opt_collocate_left" data-value='left_collocates' data-display='left side' data-script="${ajax['collocation']}">On the left side</a></li>
            <li><a class="sidebar-option" id="side_opt_collocate_right" data-value='right_collocates' data-display='right side' data-script="${ajax['collocation']}">On the right side</a></li>
			% if config["word_facets"]:
				<li class="divider"></li>
				<li role="presentation" class="dropdown-header">Count results by</li>
                % for facet in config["word_facets"]:
                 	<%
                 	  facet_name = facet.keys()[0]
                 	  facet_value = facet[facet_name]
                 	  script = "%s/scripts/get_word_frequency.py?%s&field=%s" % (config.db_url, query_string,facet_value)
                 	%>
	            <li><a class="sidebar-option" id="side_opt_token" data-value="word_frequency_report_${facet_value}" data-display="${facet_value}" data-script="${script}">${facet_name}</a></li>
                % endfor
			%endif 
        % endif
    </ul>
    <button type="button" id="hide-sidebar-button" class="btn btn-primary" style="display: none";>
        <span class="glyphicon glyphicon-remove-circle" style="vertical-align: text-top"></span>
    </button>
</div>
