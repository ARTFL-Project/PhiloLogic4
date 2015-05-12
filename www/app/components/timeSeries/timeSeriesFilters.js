philoApp.filter('filterTimeSeries', function() {
    return function (items) {
        if (typeof(items) !== 'undefined') {
            var barWidth = items[0].width;
            var filter = false;
            if (barWidth < 5) {
                filter = true;
                var filterValue = 9;
            } else if (barWidth < 10) {
                filter = true;
                var filterValue = 4;
            } else if (barWidth < 20) {
               filter = true;
               var filterValue = 1;
            }
            if (filter) {
                var count = filterValue;
                for (var i=0; i < items.length; i++) {
                    if (count < filterValue) {
                        items[i].date = '';
                        count ++;
                    } else {
                        count = 0;
                    }
                }
            }
            return items;
        } else {
            return items;
        }
    };
});