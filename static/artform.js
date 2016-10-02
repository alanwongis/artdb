


function populate(form, data) {
   $.each(data, function(key, value) {
       $('[name='+key+']', form).val(value);
   });
}


console.log("ready");





$(document).on("pageinit", "#artlist-page", function () {

	console.log("init artlist");
			   
   $(this).on("click", ".info-go", function (e) {
	   // this is the click handler. It grabs the id
	   // of the <li> which was clicked(which is also
	   // the ident of the database item) and attaches
	   // it to the "info" of the details page. The
	   // details page can then use the info to perform
	   // a JSON call for the full data of that particular
	   // item
	   e.preventDefault();
	   $("#artdetails-page").data("info", this.id); // attach id info
	   $.mobile.changePage("#artdetails-page");
   });
		   

}); 




$(document).on("pagebeforeshow", "#artlist-page",  function () {
	
	
	// retrieve the data of all artworks and format 
	// it into a clickable <ul><li> list
	$.getJSON("/artworks", function(data) {
		var li = ""
		var num_items = data.length;
		var title, date, image_hash, status;
		for(var i=0; i<num_items; i++) {
			ident = data[i][0]
			title = data[i][1];
			date = data[i][2];
			image_hash =data[i][3];
			status = data[i][4];
			if(status == "Sold") {
			   title = '<h3 style="color: #bbb;">' + title +
			           ' <span style="color: #faa;">(sold)</span></h3>';
			} else {
			   title = '<h3>' + title + '</h3>';
			}
			// (also store the ident of tha database item  as "id" within each <li>)
			li += '<li><a href="#" id="'+
			     ident +
			     '" class="info-go"><img src="/static/thumbs/' + 
				 image_hash+'_tb.jpg" /> '+
				 title +
				'<p>' + date + '</p></a></li>';
			}
		// place that list into the DOM and ...
		$("#artlist li").remove();
		$("#artlist").append(li).listview("refresh");
   });
	
});





var art_details_keys =  ['id', 'title', 'date_created', 'medium', 'dimensions',
						 'list_price', 'status', 'purchaser'];

function save_art_details(event, ui) {

	var status = true;
	var key;
	var value;
	var pair;
	var form_values = $('form').serializeArray();
	
	console.log(form_values);
	
	// compare with the originals...
	/* 
$.getJSON("/artwork/"+form_values['artform-id'], function(artwork) {
		for(var i=0; i<art_details_keys.length; i++)  {
			key = art_details_keys[i];
		}
		
	});
	
 */
 
	// create a json object holding the updated values
	var new_data = {};
	for(var i = 0; i<form_values.length; i ++) {
		pair = form_values[i];
		key = pair.name; 
		key = key.substring(8, key.length);
		value = pair.value;
		new_data[key] = value;
	}
	console.log(new_data);
	
	// send to the server
	$.ajax({
	    url: '/artwork/'+ new_data['id'],
	    headers: {
	        "Accept": "application/json",
	        "Content-Type" : "application/json"
	    },
	    method: 'PUT',
	    dataType: 'json',
	    data: JSON.stringify(new_data),
	    success: function() {
	   	    // on success, display a "Saved" message
			$("#artdetails-saved-message").show().delay(1250).fadeOut();
		}
	});
	
	return status;
}




$('#artdetails-save-btn').bind('click', save_art_details);



//use pagebeforeshow
//DONT USE PAGEINIT! 
//the reason is you want this to happen every single time
//pageinit will happen only once
$(document).on("pagebeforeshow", "#artdetails-page", function () {

	$("#artdetails-saved-message").hide(); // invisible
	
	//get from data - you put this here when the "a" wa clicked in the previous page
	var info = $(this).data("info");
	$.getJSON("/artwork/"+info, function(artwork) {

		art_details_keys.forEach(function(key) {
			$('[name='+'artform-'+ key +']', "#artform").val(artwork[key]);
		});
		$('#artform-image').attr('src', '/static/images/'+ artwork['image_hash']+'.jpg');
	}).promise().done();
	
});
	
	

    
