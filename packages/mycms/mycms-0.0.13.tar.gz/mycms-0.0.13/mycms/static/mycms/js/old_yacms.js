function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        console.log("Doing ajaxSetup");
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

var csrftoken = Cookies.get('csrftoken');

$('input[name=title]').change(function() {
    var page_title = $("#CreateTitle").val();
    $("#CreateSlug").val(convertToSlug(page_title));

});


function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        var csrftoken = Cookies.get('csrftoken');
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken",csrftoken);
        }
    }
});


function convertToSlug(Text)
{   /**
    A simple sluggifier similar to what django will do.
    **/
    return Text
    .toLowerCase()
    .replace(/ /g,'-')
    .replace(/[^\w-]+/g,'')
    ;
}

function create_cms_entry(path_obj){

    var title = $("#createpage_title").val();
    var slug = $("#createpage_slug").val();
    var page_type = $("#createpage_pagetype_select").val();

    var url = "/cms/api/v1/cmsentries/";
    var data = { path: path_obj.id,
        title: title,
        slig : slug,
        parent: path_obj.parent,
        page_type: page_type ,
        };

    console.log("Going to post cmsentry: ", data);
    $.ajax({
        url: url,
        type: 'POST',
        data: data,

    error: function(){ console.log("Failed to create CMS Entry"); },

    success: function(data){
        console.log("Created CMSEntry: " , data);
        update_child_categories();



    }
});
}


function create_path(parent_path_id){

    url = "/cms/api/v1/cmspaths/";
    var csrftoken = Cookies.get('csrftoken');
    var title = $("#createpage_title").val();
    var slug = $("#createpage_slug").val();
    var page_type = $("#createpage_pagetype_select").val();

    $.ajax({
        url: url,
        type: 'POST',
        data: { path: slug, parent: parent_path_id },

    error: function(){ console.log("Failed to create path"); },

    success: function(data){
        console.log("Created Path: " ,data);

    //When path gets created then we create the content.
    create_cms_entry(data);


    }
});

}


$("#createpage_button").click(function() {

    console.log("#createpage_button clicked.");
    var csrftoken = Cookies.get('csrftoken');
    var title = $("#createpage_title").val();
    var slug = $("#createpage_slug").val();
    var page_type = $("#createpage_pagetype_select").val();

    /**First get the cmsentry_object. Note that cmsentry_id is global var
    that we defined in the header **/

    url = "/cms/api/v1/cmsentries/"+cmsentry_id+"/";

    $.ajax({
        url: url,
        type: 'GET',
        error: function(){
            console.log("Failed to get cmsentry object");
        },
        success: function(data){
            //On Success we create the path
            create_path(data.path);

    }
});




    //Create the CMSPath

    //Create A blank CMSContent

    //Create the CMSEntry

});


function get_cmsentry(){


    //Note the cmsentry_id is global defined in head of the html page.
    url = "/cms/api/v1/cmsentries/"+cmsentry_id+"/";

    $.get(url, function(data) {
        /** Code here gets executed when success. **/
        console.log("Retrieved CMSEntry for this page: ", data);


    })
    .done(function() {
        /** Code here gets executed also on success**/
        console.log( "second success" );
        })

    .fail(function() {
        /** Code here gets executed on fail **/
        alert( "error" );
        })

    .always(function() {
        console.log( "finished" );
    })

}



function update_child_categories(){

    /**
    This updates the child categgories table. It is automagically executed
    whenever the page is loaded.
    **/



    url = "/cms/api/v1/cmsentries/?parent="+cmsentry_id;

    console.log("Getting: ", url);
    $.get(url, function(data) {
        /** Code here gets executed when success. **/
        console.log("Retrieved Child Categories: ", data);

    //var source = $("#category_table_tmpl").html();
    //var compiled = dust.compile(source, "cat_tbl");
    //dust.loadSource(compiled);
    dust.render("category_table", {  values : data } , function(err,out){
    $("#category_table_output").html(out);
    })

    })

    .fail(function() {
        /** Code here gets executed on fail **/
        alert( "error" );
        })

}


function handle_published_clicked(elem){



    console.log("Published clicked: ", elem.id, elem.innerHTML);
    var child_cmsentry_id = elem.getAttribute("child_cmsentry_id");
    var published = false;

    //Update the page with a PUT depending on the current value.
    if (elem.innerHTML == "No"){

    console.log("its a no");
    published = true;
}
else{
    console.log("It's a Yes then")	;
    published = false;
}

    url = "/cms/api/v1/cmsentries/";
    $.ajax({
        url: url,
        type: 'PUT',
        data: { id: child_cmsentry_id,published : published},

    error: function(data){ console.log("Publish Failed with error", data); },

    success: function(data){
        console.log("Updated published status of the page.: " ,data);

    //When path gets created then we create the content.
    update_child_categories()


    }
});
}


function handle_date_changed_clicked(){



    console.log("Date Changed Clicked: ");


    var date_created = $("#date_created").val();
    var date_modified = $("#date_modified").val();

    url = "/cms/api/v1/cmsentries/";
    $.ajax({
        url: url,
        type: 'PUT',
        data: { id: view_json.id , date_modified_str : date_modified, date_created_str : date_created },

    error: function(data){console.log("Change date with error", data); },

    success: function(data){
        console.log("Updated date.: " ,data);
        //When path gets created then we create the content.
        //update_child_categories()
    }
});
}


function handle_frontpage_clicked(elem){

    console.log("Frontpage clicked: ", elem.id, elem.innerHTML);
    var child_cmsentry_id = elem.getAttribute("child_cmsentry_id");
    var frontpage = false;

    //Update the page with a PUT depending on the current value.
    if (elem.innerHTML == "No"){

    console.log("its a no");
    frontpage = true;
}
else{
    console.log("It's a Yes then")	;
    frontpage = false;
}

    url = "/cms/api/v1/cmsentries/";
    $.ajax({
        url: url,
        type: 'PUT',
        data: { id: child_cmsentry_id,frontpage :frontpage},

    error: function(data){ console.log("Failed with error", data); },

    success: function(data){
        console.log("Updated frontpage status of the page.: " ,data);

    //When path gets created then we create the content.
    update_child_categories()


    }
});

}


function handle_frontpage_checked(elem){

    console.log("Frontpage checked: ", elem.id, elem.checked);
    url = "/cms/api/v1/cmsentries/";
    $.ajax({
        url: url,
        type: 'PUT',
        data: { id: view_json.id,frontpage : elem.checked},

    error: function(data){ console.log("Failed with error", data); },

    success: function(data){
        console.log("Updated frontpage status of the page.: " ,data);


    }
});

}

function handle_published_checked(elem){

    console.log("Published checked: ", elem.id);
    url = "/cms/api/v1/cmsentries/";
    $.ajax({
        url: url,
        type: 'PUT',
        data: { id: view_json.id,published : elem.checked},

    error: function(data){ console.log("Publish Failed with error", data); },

    success: function(data){
        console.log("Updated published status of the page.: " ,data);



    }
});

}

function get_content(content_id){

    console.log("Automatically loading content");

    url = "/cms/api/v1/cmscontents/?resource_id=" + content_id;

    console.log(url);
    $.ajax({
        url: url,
        type: 'GET',
        error: function(){
            console.log("Failed to get cmsentry object");
        },
        success: function(data){
            //On Success we create the path
            console.log("get_content: ", data);
            $('#editor_textarea').val(data[0].content);
        }
    });

}







/** CREATE PAGE FUNCTIONS **/
$('#createpage_title').blur(function() {
    /**
    When the user leaves the input we update the slug input with
    a sluggified version of the title.
    **/

    var title =  $('#createpage_title').val();
    slug = convertToSlug(title);
    $('#createpage_slug').val(slug);



});



/** PAGE EDITOR CLICK HANDLERS **/

$('#editor_save_button').click(function() {

    var content = $('#editor_textarea').val();

    url = "/cms/api/v1/cmscontents/?include_html=True";
        $.ajax({
            url: url,
            type: 'PUT',
            data: { id:  view_json.content[0], content : content },

    error: function(data){ console.log("Publish Failed with error", data); },

    success: function(data){
        console.log("Updated published status of the page.: " ,data);

    console.log(data);
    $("#page_body").html(data.html);

    }
});

});






// check if an element exists in array using a comparer function
// comparer : function(currentElement)
Array.prototype.inArray = function(comparer) {
    for(var i=0; i < this.length; i++) {
        if(comparer(this[i])) return true;
    }
    return false;
};

// adds an element to the array if it does not already exist using a comparer
// function
Array.prototype.pushIfNotExist = function(element, comparer) {
    if (!this.inArray(comparer)) {
        this.push(element);

    //Also add the chosen file to the preview.
    previewImage(element);
}
};


var addfiles = document.querySelector('#addfiles');
var upload_files = []


addfiles.addEventListener('change', function () {
    var files = this.files;
    for(var i=0; i<files.length; i++){
        console.log(this.files[i]);
        element = this.files[i];
        upload_files.pushIfNotExist(element,function(e) { return e.name === element.name; });
    }


    for(var i=0; i<files.length; i++){
        console.log(i, upload_files[i]);
    }

}, false);



function previewImage(file) {
    var galleryId = "gallery";

    var gallery = document.getElementById(galleryId);
    var imageType = /image.*/;

    if (!file.type.match(imageType)) {
        throw "File Type must be an image";
    }

    var yacms_gallery = document.getElementById("yacms_gallery");

    var upload_row = document.createElement("div");
    upload_row.classList.add("row-fluid");

    var yacms_thumbnail = document.createElement("div");
    yacms_thumbnail.classList.add("yacms_thumbnail");

    var img = document.createElement("img");
    img.file = file;
    yacms_thumbnail.appendChild(img);

    upload_row.appendChild(yacms_thumbnail);


    var yacms_upload_panel = document.createElement("div");
    yacms_upload_panel.classList.add("span6");
    //yacms_upload_panel.style["padding-top"] = "75px";


    progress_bar_id = "progress_bar_" + file.name.replace(".", "_");

    var progress = document.createElement("div");
    progress.classList.add("progress");
    progress.style["width"] = "100%";
    //progress.id = progress_bar_id;

    yacms_upload_panel.appendChild(progress);

    var bar = document.createElement("div");
    bar.classList.add("bar");
    bar.style["width"] = "0%";
    bar.id = progress_bar_id;
    progress.appendChild(bar);




    upload_row.appendChild(yacms_upload_panel);


    yacms_gallery.appendChild(upload_row);
    yacms_upload_panel.style["padding-top"] = "75px";

    // Using FileReader to display the image content
    var reader = new FileReader();
    reader.onload = (function(aImg) { return function(e) { aImg.src = e.target.result; }; })(img);
    reader.readAsDataURL(file);

    console.log(file);

}


function previewUpload(file){








}

function uploadFile(file){
    var url = "assets_manager/";
    var xhr = new XMLHttpRequest();
    var fd = new FormData();
    xhr.open("POST", url, true);


    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4 && xhr.status == 200) {
            // Every thing ok, file uploaded
            console.log(xhr.responseText); // handle response.
        }
    };

    xhr.upload.addEventListener("progress", function(e) {
        /**
        The e object we get has:

    total - Total bytes being transferred
    loaded - Bytes uploaded thus far
    lengthComputable - Specifies if the total size of the data/file being uploaded is known
    transferSpeed as a long
    timeRemaining as a JavaScript Date object
    **/

    var pc = parseInt(e.loaded / e.total * 100);
    console.log(file.name, e.loaded, e.total, pc)


    progress_bar_id = "progress_bar_" + file.name.replace(".", "_");
    progress = document.getElementById(progress_bar_id);
    //progress.style.backgroundPosition = pc + "% 0";
    progress.style["width"] = pc + "%";



    }, false);

    fd.append("upload_file", file);

    xhr.send(fd);
}

    $("#upload-files").click( function(){

    for(var i=0; i<upload_files.length; i++){
        console.log(upload_files[i]);
        element = upload_files[i];
        uploadFile(element);

    }

});
