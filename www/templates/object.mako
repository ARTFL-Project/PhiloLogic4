<%include file="header.mako"/>
<%include file="search_form.mako"/>
<div class="container-fluid" id='philologic_response'>
    <div id='object-title'>
        <span class='philologic_cite'>${f.biblio_citation(db,config, obj)}</span>
    </div>
    <div class="clearfix" style="position: absolute;left: 0;">
        <div id="toc-button" class="pull-left hidden-xs">
            <button class="btn btn-primary btn-sm" id="show-toc" disabled="disabled">Table of contents</button>
        </div>
    </div>
    <div class="row" style="margin-top: 50px">
        <div id="toc-wrapper" class="hidden-xs col-sm-4" style="display: none;">
            <div class="panel panel-default" id="toc-container">
                <button type="button" class="btn btn-primary btn-xs pull-right" id="hide-toc">
                    <span class="glyphicon glyphicon-remove"></span>
                </button>
                <div id="toc-content"></div>
            </div>
        </div>
        <div class="col-xs-12 col-sm-8 col-sm-offset-2" id="center-content">
            <div class="row">
                <div class="col-xs-1 nav-btn">
                    <button type="button" class="btn btn-primary" id="prev-obj" data-philo-id="${prev}" style="height: 34px;"> <!--Fix weird height issue-->
                        <span class="glyphicon glyphicon-chevron-left pull-right"></span>
                    </button>
                </div>
                <div class="col-xs-10">
                    <div id="book-page" class="panel panel-default">
                        <div id="prev_obj_text" data-philo-id="${prev}" style="display:none;"></div>
                        <div id="text-obj-content" data-philo-id="${' '.join([str(j) for j in obj.philo_id])}" data-prev="${prev}" data-next="${next}">${obj_text}</div>
                        <div id="next_obj_text" data-philo-id="${next}" style="display: none;"></div>
                    </div>
                </div>
                <div class="col-xs-1 nav-btn">
                    <button type="button" class="btn btn-primary" id="next-obj" data-philo-id="${next}">
                        <span class="glyphicon glyphicon-chevron-right"></span>
                    </button>
                </div>
            </div>
        </div>
    </div>
</div>
<%include file="footer.mako"/>