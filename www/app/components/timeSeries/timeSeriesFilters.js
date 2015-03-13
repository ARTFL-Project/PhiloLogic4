philoApp.filter('filterTimeSeries', function() {
    return function (items) {
        if (typeof(items) !== 'undefined') {
            var barWidth = items[0].width;
            var filterEveryOther = false;
            if (barWidth < 20) {
               filterEveryOther = true;
            }
            if (filterEveryOther) {
                for (var i = 1; i < items.length; i+=2) {
                    items[i].date = '';
                }
            }
            return items;
        } else {
            return items;
        }
    };
});