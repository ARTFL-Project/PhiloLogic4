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
            script = "%s/scripts/get_frequency.py?%s&frequency_field=%s" % (config.db_url, query_string, facet_name)
            %>
            <li><a class="sidebar-option" id="side_opt_${facet_name}" data-value='${facet_name}' data-script="${script}">${facet_name}</a></li>
        % endfor
        % if report != 'bibliography':
            <li class="divider"></li>
            <li role="presentation" class="dropdown-header">Display collocates on</li>
            <% script = "%s/scripts/get_collocation.py?%s" % (config.db_url, query_string) %>
            <li><a class="sidebar-option" id="side_opt_collocate" data-value='all_collocates' data-display='both sides' data-script="${script}">Both sides</a></li>
            <li><a class="sidebar-option" id="side_opt_collocate_left" data-value='left_collocates' data-display='left side' data-script="${script}">On the left side</a></li>
            <li><a class="sidebar-option" id="side_opt_collocate_right" data-value='right_collocates' data-display='right side' data-script="${script}">On the right side</a></li>
        % endif
    </ul>
    <button type="button" id="hide-sidebar-button" class="btn btn-primary" style="display: none";>
        <span class="glyphicon glyphicon-remove-circle" style="vertical-align: text-top"></span>
    </button>
</div>