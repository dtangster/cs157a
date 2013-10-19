$(function() {
    $("#tableButtons button").click(function() {
        var id = $(this).attr("id");
        var xmlhttp;

        if (window.XMLHttpRequest) {// code for IE7+, Firefox, Chrome, Opera, Safari
            xmlhttp = new XMLHttpRequest();
        }

        xmlhttp.onreadystatechange = function() {
            if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
                document.getElementById("tableContent").innerHTML = xmlhttp.responseText;
            }
        }

        xmlhttp.open("POST", "/" + id, true);
        xmlhttp.setRequestHeader("Content-type", "text/html");
        xmlhttp.send();
    });
});

