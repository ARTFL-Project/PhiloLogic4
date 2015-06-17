philoApp.filter('isEmpty', function() {
    return function(obj) {
		if ($.isEmptyObject(obj)) {
            return false
        } else {
			return true
		}
    }
})