
function alertsuccess(message, id){
    console.log("allersuccess: " + message);
    html = '<div class="alert alert-success"><button type="button" class="close" data-dismiss="alert">×</button>' + message + '</div>';
    $("#"+id).append(html);
}

function alertblock(message, id){
    html = '<div class="alert alert-block"><button type="button" class="close" data-dismiss="alert">×</button>' + message + '</div>';
    $("#"+id).append(html);
}

function alerterror(message, id){
    html = '<div class="alert alert-danger"><button type="button" class="close" data-dismiss="alert">×</button>' + message + '</div>';
    $("#"+id).append(html);
}

function alertinfo(message, id){
    html = '<div class="alert alert-info"><button type="button" class="close" data-dismiss="alert">×</button>' + message + '</div>';
    $("#"+id).append(html);
}

