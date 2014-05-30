<%include file="header.mako"/>
<%include file="search_form.mako"/>
<script>
$(document).ready(function() {
    $("#form_body").hide();
    $("#password_submit,#password_reset").button();
    $("#password_submit").click(function(){
	var username=$("#username").val();
	var password=$("#password").val();
	var command="${db.locals['db_url']}/scripts/password_entry.py?username=" + username + "&password=" + password;
	console.log(username, password, command)
	$.getJSON(command, function(data){
		if (data == 'ok') {
			console.log('it worked')
			location.reload();
	 	} else {
			alert('tough, your information has been sent to the NSA')
		}
		});	
	});

    $("#password_reset").click(function(){
	//alert("keep clicking, chump...")
	$("#password_access :text").val("");
	$("#password_access input").empty();
	});
});
</script>
<div id="error_container" style="max-width:500px !important;font-size:120%;">
    <div id="error_message" class="ui-state-error" style="text-align:justify;padding: 5px 5px 5px 5px;">
        <span class="ui-icon ui-icon-alert" style="float: left; margin-right: .3em;"></span>
	You have been deemed unworthy to access this page. Go away and never return.
    </div>
    <center>
    <p>Piss off ${client_address}.</p>
    <img src="http://leahdaly.files.wordpress.com/2013/06/maori-warrior.jpg" style="max-height:400px">
    </center>
</div>

<div id="password_form" style="max-width:500px !important;font-size:110%;">
    <div id="error_message" class="" style="text-align:justify;padding: 5px 5px 5px 5px;">
        <span class="" style="float: left; margin-right: .3em;"></span>
	<br/>
	<center>
        If you have a username and password, please enter them here:
	</center>
    </div>
	<form id="password_access" action="${db.locals['db_url'] + "/scripts/password_entry.py/"}">
	     <div id="enter_user_pass">
	          <table style="margin: 0 auto">
		     <tr class="user_pass" >
			<td><span style="margin-right: 10px;">Username:</span></td>
			<td class="second_column ">
				<input type='text' name='username' id='username' class="user_box"><br>
			</td>
		     </tr>
		     <tr class="username" >
			<td><span style="margin-right: 10px;">Password:</span></td>
			<td class="second_column ">
				<input type='text' name='password' id='password' class="password_box"><br>
			</td>
		     </tr>
		     <tr class="submit_user_pass">
			<td><span style="margin-right: 10px;">
			<td><span id="password_submit">Submit</span>
			<span id="password_reset">Clear form</span></td>
			</span></td>
		     </tr>
		  </table>
	     </div>
	</form>
</div>
<%include file="footer.mako"/>
