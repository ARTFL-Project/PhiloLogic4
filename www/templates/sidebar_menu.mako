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
            script = "%s/scripts/get_frequency.py?%s&frequency_field=%s" % (config.db_url, q['q_string'], repr(facet))
            %>
            <li><a class="sidebar-option" id="side_opt_${facet_name}" data-value='${facet_name}' data-script="${script}">${facet_name}</a></li>
        % endfor
        % if report != 'bibliography':
            <li class="divider"></li>
            <li role="presentation" class="dropdown-header">Display collocates on</li>
            <% script = "%s/scripts/collocation_fetcher.py?%s&full_report=False" % (config.db_url, q['q_string']) %>
            <li><a class="sidebar-option" id="side_opt_collocate" data-value='collocation_report' data-display='on both sides' data-script="${script}">Both sides</a></li>
            <!--<li class="disabled"><a class="sidebar-option" id="side_opt_collocate_left" data-value='collocation_report_left' data-display='on the left side'>On the left side</a></li>-->
            <!--<li class="disabled"><a class="sidebar-option" id="side_opt_collocate_right" data-value='collocation_report_right' data-display='on the right side'>On the right side</a></li>-->
        % endif
    </ul>
    <button type="button" id="hide-sidebar-button" class="btn btn-primary" style="display: none";>
        <span class="glyphicon glyphicon-remove-circle" style="vertical-align: text-top"></span>
    </button>
</div>