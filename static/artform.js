//pageinit event for first page
//triggers only once
//write all your on-load functions and event handlers pertaining to page1

console.log("working");


// this callback for the artlist-page populates the
// page with a list of all artworks
$(document).on("pageinit", "#artlist-page", function () {
	// retrieve the data of all artworks and format 
	// it into a clickable <ul><li> list
	$.getJSON("/artworks", function(data) {
		var li = ""
		var num_items = data.length;
		var title, date, image_hash;
		for(var i=0; i<num_items; i++) {
			ident = data[i][0]
			title = data[i][1];
			date = data[i][2];
			image_hash =data[i][3];
			// (also store the ident of tha database item  as "id" within each <li>)
			li += '<li><a href="#" id="'+ident+'" class="info-go"><img src="/static/thumbs/' + 
				image_hash+'_tb.jpg" /> '+
				'<h3>'+ title +'</h3> <p>' + date + '</p></a></li>';
			}
		// place that list into the DOM and ...
		$("#artlist").append(li).promise().done( function() {
		   // ... wait until the list is in the DOM and
		   // then set the click event to go to the details
		   // page.
		   
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
		   $(this).listview("refresh");
		});	       
		
	});
  
}); 


   
function populate(form, data) {
   $.each(data, function(key, value) {
       $('[name='+key+']', form).val(value);
   
   });
}

console.log($("#artdetails-page"));

    
$("#artdetails-page").pagecontainer({
    beforechange: function (event, ui) {
        //get from data - you put this here when the "a" wa clicked in the previous page
        var info = $(this).data("info");
        $.getJSON("/artwork/"+info, function(artwork) {
        	var keys = ['title', 'date_created', 'medium', 'dimensions', 'list_price', 'status'];
        	console.log(artwork);
        	keys.forEach(function(key) {
        		$('[name='+'artform-'+ key +']', "#artform").val(artwork[key]);
        	});
        	$('#artform-image').attr('src', '/static/images/'+ artwork['image_hash']+'.jpg');
        });
     } 
});
    
    
    
    
    
    //use pagebeforeshow
//DONT USE PAGEINIT! 
//the reason is you want this to happen every single time
//pageinit will happen only once
$(document).on("pagebeforeshow", "#artdetailssss-page", function () {
    //get from data - you put this here when the "a" wa clicked in the previous page
    var info = $(this).data("info");
    $.getJSON("/artwork/"+info, function(artwork) {
    	var keys = ['title', 'date_created', 'medium', 'dimensions', 'list_price', 'status'];
    	console.log(artwork);
    	keys.forEach(function(key) {
    		$('[name='+'artform-'+ key +']', "#artform").val(artwork[key]);
    	});
    	$('#artform-image').attr('src', '/static/images/'+ artwork['image_hash']+'.jpg');
    }).promise().done();
    
});
    
    
