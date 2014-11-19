"use strict";

$(document).ready(function() {
    var new_url = window.location.href.replace(/report=concordance/, 'report=bibliography');
    History.pushState(null, '', new_url);
});