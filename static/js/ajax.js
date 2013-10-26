$(function() {
    $("#tableButtons button").click(function() {
        var id = $(this).attr("id");
        $.get("/ajax/table_request/", {table: id}, function(result){
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