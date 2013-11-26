var table = "available_books";

$(document).ready(function(){
    // DISABLING WEBSOCKETS FOR NOW
    /*
    // Lines below handle websockets to update browser tables when an update is made on the database
    var inbox = new ReconnectingWebSocket("ws://"+ location.host + "/receive");
    var outbox = new ReconnectingWebSocket("ws://"+ location.host + "/submit");
    
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
    */
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
        $("#loginForm").show();   
    });

    $("#registerButton").click(function() {
        $("#registerForm").show();
    });

    $("#login").click(function() {
        email = $("#email").val();
        password = $("#password").val();  
		
       $.post("/login", { email: email, password: password }, function(result) {
            if (result != "False") {
                console.log(result);
                location.replace("localhost:5000");	
                location.reload();	
            }
            else {
                document.getElementById("insertmsg").html("Incorrect username or password");
            }

            $("#loginForm").toggle();
            $("#email").val("");
            $("#password").val("");
            $("#logForm").popup("close");
        });
    });	
	
    $("#register").click(function() {
        email = $("#email2").val();
        name = $("#name").val();
        phone = $("#phone").val();
        password = $("#password2").val();  

        $.post("/register", { name: name, email: email, phone: phone, password: password }, function(result) {
            if (result === "True") {
                $("#registerForm").toggle();
                $("#email2").val("");
                $("#name").val("");
                $("#phone").val("");
                $("#password2").val(""); 
                document.getElementById("insertmsg").innerHTML = "You are registered and logged in!";
                outbox.send(JSON.stringify({ table: 'user_inf' }));
                $("#regForm").popup("close");
            }
            else {
                document.getElementById("insertmsg").html("Account already exists!");
            }
               
            $("#regForm").popup("close");
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
	
function userAction(button) {
    bid = button.attr("id");

    if (table == "available_books") {
        $.post("/borrow_book", { bid: bid }, function(result) {
            if (result != "False") {
                loadTable(button);    
            }
            else {
            }
        });
    }
    else if (table == "reservable_books") {
        $.post("/reserve_book", { bid: bid }, function(result) {
            if (result != "False") {
                loadTable(button);    
            }
            else {
            }
        });
    }
    else if (table == "reservation") {
        $.post("/un_reserve_book", { bid: bid }, function(result) {
            if (result != "False") {
                loadTableUser(table);    
            }
            else {
            }
        });
    }
    else if (table == "loan") {
        $.post("/un_borrow_book", { bid: bid }, function(result) {
            if (result != "False") {
                loadTableUser(table);    
            }
            else {
            }
        });
    }
}

function librarianAction(button) {
    bid = button.attr("id"); 

    if (table == "something") {

    }
    else {

    }
}

// This function expects an HTML object as a parameter
function loadTable(tableToLoad) {
    $("#loadingImage").toggle();
    table = tableToLoad.attr("id");

    $.get("/ajax/table_request", { table: table }, function(result) {
        $("#loadingImage").toggle();
        $("#tableContent").html(result).table("refresh").trigger("create").show();
    });    	
}

// This function expects a string that represents a table name as the parameter
function loadTableUser(tableToLoad) {
    $("#loadingImage").toggle();
    table = tableToLoad

    $.get("/ajax/table_request", { table: table, userSpecific: "True" }, function(result) {
        $("#loadingImage").toggle();
        $("#tableContent").html(result).table("refresh").trigger("create").show();      
    });    
}

function logout() {
    $.get("/logout", function(result) {
        location.replace("localhost:5000"); 
        location.reload();  
    });   
}







