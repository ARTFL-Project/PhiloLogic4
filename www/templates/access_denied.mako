<%include file="header.mako"/>
<div id="error_container" style="max-width:530px !important;font-size:150%;">
    <div id="error_message" class="ui-state-error" style="text-align:justify;padding: 5px 5px 5px 5px;">
        <span class="ui-icon ui-icon-alert" style="float: left; margin-right: .3em;"></span>
        Access Restricted to ARTFL subscribing institutions
    </div>
</div>
<div id="password_form" style="max-width:500px !important;font-size:110%;">
    <div id="error_message" class="" style="text-align:justify;padding: 5px 5px 5px 5px;">
        <span class="" style="float: left; margin-right: .3em;"></span>
	<br/>
        <b>If you have a username and password, please enter them here:</b>
    </div>
	<form id="password_access">
	     <div id="enter_user_pass">
	        <table class="table_row">
                <tr class="user_pass" >
                    <td>
                        <span style="margin-right: 10px;">Username:</span>
                    </td>
                    <td class="first_column ">
                        <input type='text' name='username' id='username' class="user_box">
                    </td>
                </tr>
                <tr class="username" >
                    <td>
                        <span style="margin-right: 10px;">Password:</span>
                    </td>
                    <td class="second_column ">
                        <input type='text' name='password' id='password' class="password_box">
                    </td>
                </tr>
                <tr>
                    <td>
                        <span id="password_submit" style="margin-right: 10px;">Submit</span>
                    </td>
                    <td>
                        <span id="password_reset">Clear form</span>
                    </td>
                </tr>
            </table>
	     </div>
	</form>
</div>
<div>
    <p>
        Please <a href="http://artfl-project.uchicago.edu/node/24">contact ARTFL</a>
        for more information or to have your computer enabled if your institution   
        is an <a href="http://artfl-project.uchicago.edu/node/2">ARTFL subscriber</a>
    <p>
        If you belong to a subscribing institution and are attempting to access
        ARTFL from your Internet Service Provider, please note that you should    
        use your institution's <b>proxy server</b> and should contact your
        networking support office.  Your proxy server must be configured to
        include <tt>${hostname}</tt> to access this database.
    <p>
        Please consult   
        <a href="http://artfl-project.uchicago.edu/node/14">Subscription Information</a> to see how your institution can   
        gain access to ARTFL resources.
    <p>
    <hr>The ARTFL Project, University of Chicago <hr>
    <p>Requesting Computer Address: ${client_address}
</div>
<%include file="footer.mako"/>
