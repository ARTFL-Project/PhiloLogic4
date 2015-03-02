philoApp.filter('currentObj', function() {
    return function(items, scope) {
        if (typeof(items) !== 'undefined' && typeof(scope.textObject.philo_id) !== 'undefined') {
            var filtered = [];
            var philoId = scope.textObject.philo_id.split(' ').join('-');
            for (var i=0; i < items.length; i++) {
                var element = items[i];
                element.philo_id = element.philo_id.split(' ').join('-');
                if (philoId == element.philo_id) {
                    element.currentObj = "current-obj";
                } else {
                    element.currentObj = "";
                }
                filtered.push(element)
            }
            return filtered;
        } else {
            return items
        }
        
    }
})