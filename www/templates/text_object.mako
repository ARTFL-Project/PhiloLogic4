## -*- coding: utf-8 -*-
<%include file="header.mako"/>
% if not config.dictionary:
    <%include file="search_form.mako"/>
% else:
    <%include file="dictionary_search_form.mako"/>
% endif
<div class="container-fluid" id='philologic_response'>
    <div id='object-title'>
        <span class='philologic_cite'>${text_object['citation']}</span>
    </div>
    <div class="row" id="nav-buttons">
        <button type="button" class="btn btn-primary btn-sm" id="back-to-top">
            Back to top
        </button>
        <div class="col-xs-12" style="text-align: center;">
            <div class="btn-group-sm" role="group">
                <button type="button" class="btn btn-primary" id="prev-obj" data-philo-id="${text_object['prev']}">
                    <span class="glyphicon glyphicon-chevron-left"></span>
                </button>
                <button type="button" class="btn btn-primary" id="show-toc" disabled="disabled">Table of contents</button>
                <button type="button" class="btn btn-primary" id="next-obj" data-philo-id="${text_object['next']}">
                    <span class="glyphicon glyphicon-chevron-right"></span>
                </button>
            </div>
        </div>
    </div>
    <div class="row" id="all-content" data-script="${ajax['get_text_object']}">
        <div id="toc-wrapper" class="col-xs-4" data-script="${ajax['get_table_of_contents']}">
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
                        <div id="text-obj-content" class="panel panel-default" data-philo-id="${' '.join([str(j) for j in obj.philo_id])}" data-prev="${text_object['prev']}" data-next="${text_object['next']}">
                            ${text_object['text']}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
<div id="blueimp-gallery" class="blueimp-gallery blueimp-gallery-controls" data-full-screen="true" data-continuous="false">
    <div class="slides"></div>
    <h3 class="title"></h3>
    <a class="prev">&lt;</a>
    <a class="next">&gt;</a>
    <a class="close">&#10005;</a>
    <ol class="indicator"></ol>
</div>
<%include file="footer.mako"/>