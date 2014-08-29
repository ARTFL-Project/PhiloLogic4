<%include file="header.mako"/>
<%include file="search_form.mako"/>
<div class="container-fluid" id='philologic_response'>
    <div id='object-title'>
        <span class='philologic_cite'>${f.biblio_citation(db,config, obj)}</span>
    </div>
    <div class="row" id="nav-buttons">
        <button type="button" class="btn btn-primary btn-sm" id="back-to-top">
            Back to top
        </button>
        <div class="col-xs-12" style="text-align: center;">
            <div class="btn-group-sm" style="display: inline-block;">
                <button type="button" class="btn btn-primary" id="prev-obj" data-philo-id="${prev}">
                    &lt;
                </button>
                <button type="button" class="btn btn-primary" id="show-toc" style="padding-left: 30px; padding-right: 30px" disabled="disabled">Table of contents</button>
                <button type="button" class="btn btn-primary" id="next-obj" data-philo-id="${next}">
                    &gt;
                </button>
            </div>
        </div>
    </div>
    <div class="row" id="all-content">
        <div id="toc-wrapper" class="col-xs-4">
            <div class="panel panel-default" id="toc-container" data-status="closed">
                <div id="toc-titlebar">
                    <button type="button" class="btn btn-primary btn-xs pull-right" id="hide-toc">
                        <span class="glyphicon glyphicon-remove"></span>
                    </button>
                </div>
                <div id="toc-content"></div>
            </div>
        </div>
        <div class="col-xs-12 col-sm-8 col-sm-offset-2 col-md-offset-2 col-md-8 col-lg-offset-3 col-lg-6" id="center-content">
            <div class="row">
                <div class="col-xs-12">
                    <div id="book-page">
                        <div id="text-obj-content" class="panel panel-default" data-philo-id="${' '.join([str(j) for j in obj.philo_id])}" data-prev="${prev}" data-next="${next}">${obj_text}</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
<%include file="footer.mako"/>