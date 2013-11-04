$(document).ready(function() {
    // Lines below handle websockets to update browser tables when an update is made on the database
    var inbox = new ReconnectingWebSocket("ws://"+ location.host + "/receive");
    var outbox = new ReconnectingWebSocket("ws://"+ location.host + "/submit");
    var table = "book";

    inbox.onmessage = function(message) {
        var data = JSON.parse(message.data);

        if (data.table == table) {
            $.get("/ajax/table_request", { table: table }, function(result) {
                $("#tableContent").html(result).table("refresh");
            });    
        }
    };

    inbox.onclose = function() {
        inbox = new WebSocket(inbox.url);
    };

    outbox.onclose = function() {
        outbox = new WebSocket(outbox.url);
    };

    $("#queryButton").click(function() {
        query = $("#query").val();

        $.post("/query", { sql: query }, function(result) {
            if (result === "True") {
                outbox.send(JSON.stringify({ table: table }));
            }
        });
    });

    // Lines below handle the login form logic
    $("#loginButton").click(function() {
        $("#loginForm").toggle();

        if ($("#loginForm").css("display") != "none") {
            $("#registerForm").css("display", "none");    
        }
    });

    $("#registerButton").click(function() {
        $("#registerForm").toggle();

        if ($("#registerForm").css("display") != "none") {
            $("#loginForm").css("display", "none");    
        }
    });

    $("#login").click(function() {
        email = $("#email").val();
        password = $("#password").val();  

       $.post("/login", { email: email, password: password }, function(result) {
            if (result != "False") {
                $("#errors").html("*** Authentication Successful ***").fadeIn(500).fadeOut(5000);
                $("#loginForm").toggle();
                $("#email").empty();
                $("#password").empty(); 
            }
            else {
                $("#errors").html("*** Username or password incorrect ***").fadeIn(500).fadeOut(5000);
            }
        });
    });

    $("#register").click(function() {
        email = $("#email2").val();
        name = $("#name").val();
        phone = $("#phone").val();
        password = $("#password2").val();  

        $.post("/register", { name: name, email: email, phone: phone, password: password }, function(result) {
            if (result === "True") {
                $("#errors").html("*** Your account has been created ***").fadeIn(500).fadeOut(5000);
                $("#registerForm").toggle();
                $("#email2").empty();
                $("#name").empty();
                $("#phone").empty();
                $("#password2").empty();  
                outbox.send(JSON.stringify({ table: "user" }));
            }
            else {
                $("#errors").html("*** There was a problem registering ***").fadeIn(500).fadeOut(5000);
            }
        });
    });

    // Lines below handle AJAX request to request new table.
    $("#tableButtons button").click(function() {
        $("#loadingImage").toggle();
        table = $(this).attr("id");

        $.get("/ajax/table_request", { table: table }, function(result) {
            $("#loadingImage").toggle();
            $("#tableContent").html(result).table("refresh");
        });
    });
}); 