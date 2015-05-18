philoApp.filter('currentObj', function() {
    return function(items, scope) {
        if (typeof(items) !== 'undefined' && typeof(scope.textObject.philo_id) !== 'undefined') {
            var filtered = [];
            var philoId = scope.textObject.philo_id.split(' ').join('-');
            var match = false;
            var count = 0;
            for (var i=0; i < items.length; i++) {
                if (match) {
                    count += 1
                }
                var element = items[i];
                element.philo_id = element.philo_id.split(' ').join('-');
                if (philoId == element.philo_id) {
                    element.currentObj = "current-obj";
                    match = i;
                } else {
                    element.currentObj = "";
                }
                filtered.push(element)
                if (count == 5) {
                    break
                }
            }
            if ((match - 5) < 9) {
                return filtered
            } else {
                return filtered.slice(match - 5);
            }
        } else {
            return items
        }
        
    }
})