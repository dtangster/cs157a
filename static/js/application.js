$(document).ready(function(){
    table = "available_books";

    // Lines below handle websockets to update browser tables when an update is made on the database
    inbox = new ReconnectingWebSocket("ws://"+ location.host + "/receive");
    outbox = new ReconnectingWebSocket("ws://"+ location.host + "/submit");
    
    inbox.onmessage = function(message) {
        var data = JSON.parse(message.data);
        var lookingAt = table;
        var userSpecific = data.userSpecific;

        if (data.table == table) {
            $.get("/ajax/table_request", { table: table, userSpecific: userSpecific }, function(result) {
                $("#tableContent").html(result).table("refresh").trigger("create").show();
            });    
        }
    };

    inbox.onclose = function() {
        inbox = new WebSocket(inbox.url);
    };

    outbox.onclose = function() {
        outbox = new WebSocket(outbox.url);
    };

    // Used only by DBA
    $("#queryButton").click(function() {
        var query = $("#query").val();

        $.post("/query", { sql: query }, function(result) {
            if (result === "True") {
                outbox.send(JSON.stringify({ table: table }));
            }
        });
    });


    $("#profileButton").click(function() {
        $.post("/profile", function(result) {
            if (result != "False") {
                $("#profName").val(result.name);
                $("#profPhone").val(result.phone);
                $("#profPassword").val(result.password);
            }
        });
    });

	
    $("#updateButton").click(function() {
        var name = $("#profName").val();
        var phone = $("#profPhone").val();
        var password = $("#profPassword").val(); 
		
       $.post("/update_profile", { name: name, phone:phone, password: password }, function(result) {
            if (result != "False") {
			    document.getElementById("insertmsg").innerHTML = "Profile is updated successfully!";
            }
            else {
                document.getElementById("insertmsg").innerHML = "Fail to update profile!";
            }
        });		
        $("#profForm").popup("close");
    });
	

    $("#login").click(function() {
        var email = $("#email").val();
        var password = $("#password").val();  
		
       $.post("/login", { email: email, password: password }, function(result) {
            if (result != "False") {
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
        var email = $("#email2").val();
        var name = $("#name").val();
        var phone = $("#phone").val();
        var password = $("#password2").val();  

        $.post("/register", { name: name, email: email, phone: phone, password: password }, function(result) {
            if (result === "True") {
                $("#registerForm").toggle();
                $("#email2").val("");
                $("#name").val("");
                $("#phone").val("");
                $("#password2").val(""); 
                document.getElementById("insertmsg").innerHTML = "You are registered and logged in!";
                location.replace("localhost:5000"); 
                location.reload();  
            }
            else {
                document.getElementById("insertmsg").innerHTML = "Account already exists!";
            }
               
            $("#regForm").popup("close");
        });
    });

    // Lines below handle AJAX request to request new table.
    $("#tableButtons button").click(function() {
        loadTable($(this));
    });
	
	
	
	

	
	//Comment form logic
	$(".commPOP").click(function() {
		$("#commForm").show();
		$("#commentForm").show();
		$("#commentForm").popup();
        $("#commForm").popup();
    });
	
	$("#add_reviewButton").click(function() {
        var bid = $("#bidpop").val();
        var comment = $("#usr_comment").val();
        var star = $("#usr_star").val();  

        $.post("/add_review", { bid: bid, comment: comment, star: star }, function(result) {
            if (result === "True") {
                $("#commentForm").toggle();
                $("#usr_comment").val("");
                $("#usr_star").val("");
                document.getElementById("insertmsg").innerHTML = "You Successfully Commented on Book ID: " + bid;
                outbox.send(JSON.stringify({ table: 'user_inf' })).trigger("create").show();;
            }
            else {
                 document.getElementById("insertmsg").html("Fail to comment on book!");
            }
			    $("#commForm").popup("close");
            
        });
    });
	
	
	//adds bid to popup by replacing input value to selected bid
	$('a[data-rel="popup"]').click(function () {
		var link = $(this);
		var bid = link.attr('id')
	    $('#bidnum').text("Enter Comments for book id: " + bid);
		$('#bidpop').val(bid);
	});
	
	

	
}); 
	
function userAction(button) {
    var bid = button.attr("id");

    if (table == "available_books") {
        $.post("/borrow_book", { bid: bid }, function(result) {
            if (result != "False") {
                outbox.send(JSON.stringify({ table: table, userSpecific: "False" })).trigger("create").show(); 
            }
            else {
            }
        });
    }
    else if (table == "reservable_books") {
        $.post("/reserve_book", { bid: bid }, function(result) {
            if (result != "False") {
                outbox.send(JSON.stringify({ table: table, userSpecific: "False" })).trigger("create").show();  
            }
            else {
            }
        });
    }
    else if (table == "reservation") {
        $.post("/un_reserve_book", { bid: bid }, function(result) {
            if (result != "False") {
                outbox.send(JSON.stringify({ table: table, userSpecific: "True" })).trigger("create").show();   
            }
            else {
            }
        });
    }
    else if (table == "loan") {
        $.post("/un_borrow_book", { bid: bid }, function(result) {
            if (result != "False") {
                outbox.send(JSON.stringify({ table: table, userSpecific: "True" })).trigger("create").show();     
            }
            else {
            }
        });
    }
}

function librarianAction(button) {
    var bid = button.attr("id"); 

    if (table == "something") {

    }
    else {

    }
}


//function loads comments for specific book
function load_bookComment(link) {
    var bid = link.attr("id");
	
    $.get("/ajax/table_request", { table: "review", bookSpecific: "True", userSpecific:"False",  bid:bid }, function(result) {
        $("#loadingImage").toggle();
        $("#tableContent").html(result).table("refresh").trigger("create").show();;      
    });    
}

//waives fee
function waiveFee(link) {
    var email = link.attr("id");
     $.post("/waive_fee", { email: email }, function(result) {
            if (result != "False") {
                outbox.send(JSON.stringify({ table: table, userSpecific: "False" })).trigger("create").show();     
            }
            else {
            }
        });	
}


//extend due date fee
function extendDueDate(link) {
    var email = link.attr("vemail");
	var bid = link.attr("vbid");	
	
     $.post("/extend_dueDate", { email: email , bid:bid }, function(result) {
            if (result != "False") {
                outbox.send(JSON.stringify({ table: 'debtors', userSpecific: "False" })).trigger("create").show();     
            }
            else {
            }
        });	
}


// This function expects an HTML object as a parameter
function loadTable(tableToLoad) {
    $("#loadingImage").toggle();
    table = tableToLoad.attr("id");

    $.get("/ajax/table_request", { table: table, userSpecific: "False" }, function(result) {
        $("#loadingImage").toggle();
        $("#tableContent").html(result).table("refresh").trigger("create").show();;
    });    	
}

// This function expects a string that represents a table name as the parameter
function loadTableUser(tableToLoad) {
    $("#loadingImage").toggle();
    table = tableToLoad;

    $.get("/ajax/table_request", { table: table, userSpecific: "True" }, function(result) {
        $("#loadingImage").toggle();
        $("#tableContent").html(result).table("refresh").trigger("create").show();;      
    });    
}

function logout() {
    $.get("/logout", function(result) {
        location.replace("localhost:5000"); 
        location.reload();  
    });   	
}




