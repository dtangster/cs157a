$(document).ready(function(){
    // DISABLING WEBSOCKETS FOR NOW
    /*
    // Lines below handle websockets to update browser tables when an update is made on the database
    var inbox = new ReconnectingWebSocket("ws://"+ location.host + "/receive");
    var outbox = new ReconnectingWebSocket("ws://"+ location.host + "/submit");
    //var table = "book";

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
        /* PREVIOUS CHANGE
			if ($("#loginForm").css("display") != "none") {
           $("#registerForm").css("display", "none");    
       }*/
    });

    $("#registerButton").click(function() {
        $("#registerForm").show();
        /*PREVIOUS CHANGE
        if ($("#registerForm").css("display") != "none") {
            $("#loginForm").css("display", "none");    
        }*/
    });

    $("#login").click(function() {
    
        email = $("#email").val();
        password = $("#password").val();  
		
       $.post("/login", { email: email, password: password }, function(result) {
            if (result != "False") {
                location.replace("localhost:5000");	
                location.reload();	
            }
            else {
               // $("#errors").html("*** Username or password incorrect ***").fadeIn(500).fadeOut(5000);
               // document.getElementById("insertmsg").innerHTML = "Sorry please login again!";
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
                //$("#errors").html("*** Your account has been created ***").fadeIn(500).fadeOut(5000);
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
                //$("#errors").html("*** There was a problem registering ***").fadeIn(500).fadeOut(5000);
                document.getElementById("insertmsg").innerHTML = "Please login or register!";
            }
               
                $("#regForm").popup("close");
        });
    });

    /*
    // Lines below handle AJAX request to request new table.
    $("#tableLink a").click(function() {
        $("#loadingImage").toggle();
        table = $(this).attr("id");

        $.get("/ajax/table_request", { table: table }, function(result) {
            $("#loadingImage").toggle();
            $("#tableContent").html(result).table("refresh");
        });
    });
    */	
}); 

function goToBorrow(button) {
    bid = button.attr("id");
	table = button.attr
	
    $.post("/borrow_book", { bid: bid }, function(result) {
        if (result != "False") {
				//$('#message').append("FADSFASDFAS");
        }
        else {
        }
    });
}

function goUnBorrow(button) {
    bid = button.attr("id");
	
    $.post("/un_borrow_book", { bid: bid }, function(result) {
        if (result != "False") {
				//$('#message').append("FADSFASDFAS");
        }
        else {
        }
    });		
}

function goToReserve(button) {
        bid = button.attr("id");
		table = button.attr
		
       $.post("/reserve_book", { bid: bid }, function(result) {
            if (result != "False") {
					//$('#message').append("FADSFASDFAS");
            }
            else {
            }
        });
}

function goUnReserve(button) {
        bid = button.attr("id");
		table = button.attr
		
       $.post("/un_reserve_book", { bid: bid }, function(result) {
            if (result != "False") {
					//$('#message').append("FADSFASDFAS");
            }
            else {
            }
        });
}
	
	

	
function loadTable(table) {
    $("#loadingImage").toggle();
    table = table.attr("id");

    $.get("/ajax/table_request", { table: table }, function(result) {
        $("#loadingImage").toggle();
        $("#tableContent").html(result).table("refresh").trigger("create").show();
		//$( "#divTable table" ).html( result ).table("refresh");

        if (table === "available_books")
            document.getElementById("table_welcome").innerHTML="<h3>Viewing All Available Books</h3>";
        else if (table === "highest_rated_books")
            document.getElementById("table_welcome").innerHTML="<h3>Viewing Highest Rated Books</h3>";
        else if (table === "reserved_books")
            document.getElementById("table_welcome").innerHTML="<h3>Viewing Reserved Books</h3>";
        else if (table === "loan")
            document.getElementById("table_welcome").innerHTML="<h3>Viewing Your Loaned Books</h3>";
        else if (table === "comments")
            document.getElementById("table_welcome").innerHTML="<h3>Viewing Comments Books</h3>";		
    });    	
}

function logout() {
    $.get("/logout", function(result) {
        location.replace("localhost:5000"); 
        location.reload();  
    });   
}







