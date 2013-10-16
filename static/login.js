$(document).ready(function() {
    $("#loginButton").click( function(event) {
        var mode = $("#loginForm").css("display");

        if (mode == "none") {
            $("#loginForm").css("display", "inline");
        }
        else {
            $("#loginForm").css("display", "none");
        }
    });
});