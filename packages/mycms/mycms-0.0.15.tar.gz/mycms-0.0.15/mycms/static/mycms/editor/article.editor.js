


function on() {
        console.log("Showing overlay");
    document.getElementById("overlay").style.display = "block";
}

function close_admin_overlay() {
    document.getElementById("overlay").style.display = "none";
}

$("#close-admin-overlay-button").click(function(){
        console.log("close-admin-overlay-button clicked");
        close_admin_overlay();
        });


function formatButtonHandler(label){

    console.log(label);
    
    if (label == 'H1') {
        console.log("H1 Not Implemented yet.")
    }else if (label == "H2"){
        console.log("H2 Not Implemented yet")
    }else if (label == "H3"){
            console.log('H3 Not Implemented yet')
            }      
}
    
    


function readCMSContents(content_id){
/* Does a GET for the content and updates the editor textarea.

API Version 1 defines the endpoint as: 

/cms/api/v1/cmscontents/{resource_id}/
*/
    console.log("readCMSContents called.");

    url = "/cms/api/v2/cmscontents/" + view_json.content[0]+ "/";
    
    $.ajax({
        url: url,
        type: 'GET',
        error: function(){
            console.log("Failed to get cmscontent object");
        },
        success: function(data){
            content = data["content"];
            $("textarea#markup").text(content);
        }
    });
    
}

function updateCMSContents(content_id){

    console.log("updateCMSContents callled");
    url = "/cms/api/v2/cmscontents/"+ view_json.content[0] + "/";
    
    console.log("updateCMSContents: PUT :  " + url);
    
    content = $("textarea#markup").val();
    console.log("updateCMSContents sending " + content);
     $.ajax({
        url: url,
        type: 'PUT',
        data: { content : content, markup: 1},

        error: function(data){ 
            console.log("Publish Failed with error", data); 
        },
        success: function(data){
            console.log("Updated published status of the page.: " ,data);
            /*We also need to update the window.page_content and force a refresh */
            url = "/cms/api/v2/cmscontents/"+ view_json.content[0] + "/html/"
            //url = "/cms/api/v2/utils/cmsformatter/" + view_json.content[0] + "/html/"
           
            $.ajax({
                url: url,
                type: 'GET',
                error: function(error){
                console.log("Error is ", error);
                    var message = "<strong>Failed to get cmscontent object</strong>. The server gave us: " + error.statusText;
                    alerterror(message, "admin-message-panel");
                },
                success: function(data){
                    /*On success we update window.editor_content before going ahead
                    on showing the editor.*/
                    html_content = data["html"];
                    window.page_content = html_content;
                    document.getElementById('page_content').innerHTML = html_content;
                    
                    alertsuccess("Successfully updated page.", "admin-message-panel");
                }
            });
                
            
        }
    });

}


function resizeEditor(){
    $('#slider').width(1024);
}


function insertAtCaret(areaId, text) {
        var txtarea = document.getElementById(areaId);
        if (!txtarea) { return; }

        var scrollPos = txtarea.scrollTop;
        var strPos = 0;
        var br = ((txtarea.selectionStart || txtarea.selectionStart == '0') ?
                "ff" : (document.selection ? "ie" : false ) );
        if (br == "ie") {
                txtarea.focus();
                var range = document.selection.createRange();
                range.moveStart ('character', -txtarea.value.length);
                strPos = range.text.length;
        } else if (br == "ff") {
                strPos = txtarea.selectionStart;
        }

        var front = (txtarea.value).substring(0, strPos);
        var back = (txtarea.value).substring(strPos, txtarea.value.length);
        txtarea.value = front + text + back;
        strPos = strPos + text.length;
        if (br == "ie") {
                txtarea.focus();
                var ieRange = document.selection.createRange();
                ieRange.moveStart ('character', -txtarea.value.length);
                ieRange.moveStart ('character', strPos);
                ieRange.moveEnd ('character', 0);
                ieRange.select();
        } else if (br == "ff") {
                txtarea.selectionStart = strPos;
                txtarea.selectionEnd = strPos;
                txtarea.focus();
        }

        txtarea.scrollTop = scrollPos;
}



/** 

Old functions probably we will not use
**/


function toggleEditor(){
    
    console.log("Editor is: " + window.editor_window);
    if (window.editor_window == true){ 
        console.log("Editor was shown. Going to hide it");
        hideEditor();
        window.editor_window = false;
        }else{
            console.log("Editor was hidden, Going to show");

            showEditor();
            window.editor_window = true;
        } 
    console.log("Editor is now: " + window.editor_window);
}


function hideEditor(){

    /* Load the html back on the editor */ 


    url = "/cms/api/v2/utils/cmsformatter/"+ view_json.content[0] + "/";
    $.ajax({
            url: url,
            type: 'GET',
            error: function(){
                console.log("Failed to get cmscontent object");
            },
            success: function(data){
                /*On success we update window.editor_content before going ahead
                on showing the editor.*/
               
                html_content = data["html"];
                 //console.log("***************************************************************");
                //console.log(html_content);
                document.getElementById('page_content').innerHTML= html_content;
                window.editor_window = false;
                window.page_content = html_content;
                }
        });

}

function showEditor(){
    
    console.log("showEditor called.");
    /* backup the page_content div */
     window.page_content = document.getElementById('page_content').innerHTML;
     
    if  (window.editor_content === null || window.editor_content === undefined ){
        /* 
            We store the page source in window.editor_content. But if this is the 
            first time we are accessing the editor, it could be that we still need 
            to load it first. 
        */
        
        url = "/cms/api/v2/cmscontents/"+ view_json.content[0] + "/";
    
        $.ajax({
            url: url,
            type: 'GET',
            error: function(err, out){
                console.log("Error " + data);
            },
            success: function(data){
                /*On success we update window.editor_content before going ahead
                on showing the editor.*/
                markup_content = data["content"];
                dust.render("yacms\/templates\/yacms\/dustjs_templates\/page_content", 
                            { page_content: markup_content },
                            function(err, out){
                                //console.log(err, out)
                                document.getElementById('page_content').innerHTML = out;
                            });
                            
            }
        });
    }else{
        /*
            The window.editor_content is not null or undefined so we will use 
            what we have in it to render the editor.
        */
    
        console.log("window.editor_content : " + window.editor_content);
        
        /* the page_content html */
        //window.page_content = document.getElementById('page_content').innerHTML;
      
        dust.render("yacms\/templates\/yacms\/dustjs_templates\/page_content", 
                    { page_content: window.editor_content }, function(err, out){
                            //console.log(err, out)
                            document.getElementById('page_content').innerHTML = out;
                    });
        window.editor_window = true;
    }
}