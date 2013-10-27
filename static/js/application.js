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
        $("#login").toggle();
    });

    $("#login").click(function() {
        // Need to implement
    });

    $("#register").click(function() {
        // Need to implement
    });

    // Lines below handle AJAX request to request new table.
    $("#tableButtons button").click(function() {
        table = $(this).attr("id");

        $.get("/ajax/table_request", { table: table }, function(result) {
            $("#tableContent").html(result).table("refresh");
        });
    });

    $(document).ajaxStart(function(){
        $("#loadingImage").toggle();
    });

    $(document).ajaxStop(function(){
        $("#loadingImage").toggle();
    });
}); 