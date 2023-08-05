function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        var csrftoken = $.cookie('csrftoken');
       
        console.log(csrftoken);
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


/** DISPLAY CHILD PAGES FUNCITONS **/

function update_childpages_table_state(){

    var page_id  = cmsentry_object.id //Get the id from the global cmsentry_object
    url = "/cms/api/v1/cmsentries?id="+page_id;
    
}


function get_child_categories(){
    /**  Get the list of child categories via AJAX. **/
    var parent_id = cmsentry_object.id;
    var page_type_id = cmsentry_object.page_type;

    url = "/cms/api/v1/cmsentries?parent=" + parent_id + "&expand=True&page_type=" + page_type_id; 
    
     $.get(url, function(data) {
        /** Code here gets executed when success. **/
        console.log(data);
        html = new EJS({url: '/static/yacms/js/templates/category_table.ejs'}).render({ cmsentry_objects : data });
        console.log(html);
        $("#category_table").html(html);
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
        /** This code will always execute after a request **/
        console.log( "finished" );
        })

    

}


$(function() {
    /** Update the category table list on document load.**/
    get_child_categories();    
});



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


function create_cmsentry(title, slug, page_type, path){
    /** 
    Creates a page given a title, slug, page_type and the path of the 
    current page.
    **/
    
    console.log(title);
    
    var data = { title: title, slug: slug, page_type: page_type, path: path};
    console.log("Going to send: " + data);
    url = "/cms/api/v1/cmsentries";
    $.ajax({
              type: "POST",
              url: url,
              data: data, // serializes the form's elements.
              success: function(data)
              {
                   console.log("created cmsentries: " +  data);
                   get_child_categories();
                   
                   //set notification that we have created succesfully.
                   //var template = 
                   //html = html = new EJS({text: template}).render(data) 
                    var message = "Succesfully created : " + title;
                    alertsuccess(message, "notifications");
                    asdfd
                   
                   
              }
        });
          
}


$("#createpage_button").click(function() {
    /**
    The createpage form button click handler. When the user clicks the button,
    we want to post the  contents of the form to  the api backend.
    
    This also calls create_cmsentry after it has created the new path    
    **/
    
    
    console.log("#createpage_button clicked.");
    var csrf = $.cookie()
    var data = $("#createpage_form").serialize();
    
    var title =  $('#createpage_title').val();    
    var slug  =  $('#createpage_slug').val();
    var page_type = $('#createpage_pagetype_select').val();
    console.log("Page_type ", page_type);
     
    var path = ""
    
    console.log("CMSENTRY: ", cmsentry_object);
    if (cmsentry_object.path_str == "/"){
        path = "/" + slug;        
    } else{
        path = cmsentry_object.path_str + "/" + slug;    
    }
    
    data = { path : path , parent : cmsentry_object.path , csrf:csrf};
    console.log(data);
    
    var url = "/cms/api/v1/cmspaths/"; // the script where you handle the form input.

    $.ajax({
           type: "POST",
           url: url,
           data: data, // serializes the form's elements.
           success: function(data)
           {
                console.log("created path: " +  data.path);
                create_cmsentry(title, slug, page_type, data.id);                
           }
         
         });

    return false; // avoid to execute the actual submit of the form.
});


(function($, window) {
  $.fn.replaceOptions = function(options) {
    var self, $option;

    this.empty();
    self = this;

    $.each(options, function(index, option) {
      $option = $("<option></option>")
        .attr("value", option.value)
        .text(option.text);
      self.append($option);
    });
  };
})(jQuery, window);


$(function() {
    /** Initialize the state when the page is loaded.
    
    This loads these category editor form and these required information 
    to create new pages.
    
    In these future, we should be able to choose what kind of page_type's 
    to also list form this particular page.
    **/   
   
    var url = "/cms/api/v1/cmspagetypes";
    
    $.get(url, function(data) {
        /** Code here gets executed when success. **/
        
        var option_array = [];
        
        for ( x=0 ;x < data.length; x++) {
            
            option_array.push({text: data[x].text, value: data[x].id})
           
        }
        console.log(option_array);
        $('#createpage_pagetype_select').empty();
        $('#createpage_pagetype_select').replaceOptions(option_array);
        
    })
   
   
});


function timestamp2date(timestamp){

    /* This converts a unix timestamp to javascript date format. 
    This should be common to both page_editor and category.js    
    */ 

   console.log("timestamp2date got: ", parseInt(timestamp));
    var date = new Date(parseInt(timestamp));
    console.log("date: ",date);
    var month = date.getMonth();
    var year = date.getFullYear();
    var day = date.getDate();
    var hours = date.getHours();
    var minutes = date.getMinutes();
    var seconds = date.getSeconds();
    
    //We want: 19/03/2015 14:45:19
    
    var date_string = day + "/" + month + "/" + year + " " + hours + ":" + minutes + ":"  + seconds;
    console.log( "19/03/2015 14:45:19   " , date_string );
    
    return date_string;

}


function datetime_editor_save_click_handler(params){

    /** 
    Gets the new date and updates the cmsentry. We do this by getting these slug
    from these params provided.
    
    See below datetime_editor_click_handler which dumps these slug into these Save 
    span  as an attribute. 
    
    We then fetch these new date using these slug value since these datetime editor
    gives it these id of "created_datetime_field_" + slug.
    
    We also fetch these article id from these main span
    **/


    var slug = params.getAttribute("slug");
    var article_id = $("#"+slug).attr("article_id");
    var input_field_id = "created_datetime_field_" + slug;
    var dateString = $("#"+input_field_id).val();
    
    dateParts = dateString.split(' '),
    timeParts = dateParts[1].split(':'),
    dateParts = dateParts[0].split('/');

    var date = new Date(dateParts[2], parseInt(dateParts[1], 10), dateParts[0], timeParts[0], timeParts[1]);
    console.log("Got new date ",date.getTime());   
    
    /** We now have the article_id and then date_str. We do a PUT request
    to these /cms/api/v1/cmsentries endpoint to update these date_created 
    of the article. **/
    
    //Now make an ajax call to save the state.
    $.ajax({
       type: "PUT",
       url: "/cms/api/v1/cmsentries/",
       data:  { date_created_epoch : date.getTime(), id: article_id}, // serializes the form's elements.
       success: function(data)
       {
            console.log("New Epoch: ", data.date_created_epoch);
            /** Now we update these page with the new date**/
            
            $("#span_"+slug).html(timestamp2date(data.date_created_epoch));
            
       }
    });
   
        
}

function datetime_editor_click_handler(params){

    /** 
    Invoked when these <span> for these date under these article title is clicked.
    It replaces these date with these date edit form.
    **/

    console.log("clicked the datetime_editor_button");
    console.log(params);
    console.log(params.getAttribute("class"));
    var slug = params.getAttribute("slug");
    
    
    var jq_slug = "#span_" + slug;
    var span_slug = "span_"+ slug;
    var d = "#"+slug;
    var datetime_str = $(d);
    console.log("SPAN", d)
    
    console.log("DATE: " , $("#"+span_slug).html());

    var span_slug_datetime = span_slug + "datetime";
    var created_datetime_field_slug = "created_datetime_field_" + slug;   
        
    h = "<div id=\"" + span_slug_datetime + "\" class=\"input-append date\">";
    //h = "<div id=\"created_datetime\" class=\"input-append date\">";
    h += "<input data-format=\"dd/MM/yyyy hh:mm:ss\" id=\"" + created_datetime_field_slug  + "\" type=\"text\" value=\""+  $("#"+span_slug).html() +"\"></input>";
    h += "<span class=\"add-on\"><i data-time-icon=\"icon-time\" data-date-icon=\"icon-calendar\"></i></span>";
    h += "</div>";
    h += "<div id=\"created_datetime_save_button\" class=\"input-append date_button\">";
    h += "<span class=\"add-on\"><i id=\"icon_save\" class=\"icon-save\"></i><span slug=\""+ slug + "\"onclick=\"datetime_editor_save_click_handler(this)\">Save</span></span>";
    h += "</div>";
            
            
    $("#"+span_slug).html(h);
    $("#"+span_slug_datetime).datetimepicker({ language: 'pt-BR' });   

}