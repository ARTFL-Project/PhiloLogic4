$(document).ready(function() {
    $("#form_body").hide();
    $("#password_submit,#password_reset").button();
    $("#password_submit").click(function(){
	var username = encodeURIComponent($("#username").val());
	var password = encodeURIComponent($("#password").val());
	var command = webConfig['db_url'] + "/scripts/password_entry.py?username=" + username + "&password=" + password;
	console.log(username, password, command)
	$.getJSON(command, function(data){
		if (data == 'ok') {
			console.log('it worked')
			location.reload();
	 	} else {
			alert('Your username or password is incorrect, please try again.')
		}
		});	
	});

    $("#password_reset").click(function(){
        $("#password_access :text").val("");
        $("#password_access input").empty();
	});
});