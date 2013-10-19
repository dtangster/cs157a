$(function() {
    $("#tableButtons button").click(function() {
        var id = $(this).attr("id");
        $.post("/", {table: id}, function(result){
            $("#tableContent").html(result).closest("table#table-column-toggle").table("refresh").trigger("create");
        });
    });
});