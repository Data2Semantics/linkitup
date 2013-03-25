


// Default: hide the modal showing the selected links. We'll only populate & show it once the user requests us to do so.
$("#links_{{ i.article_id }}").hide();


// Code for showing the selected links modal
$("#show_{{ i.article_id }}").click(function(){
    $("#links_modalbody_{{ i.article_id }}").empty(); 
    
    var start = "<label class='checkbox alert alert-info'><a href='";
    var middle1 = "' target='_new'>";
    var end = "</a></label>";
    
	$("#{{ i.article_id }}_form :input[type='checkbox']:checked").each( 
			function(){
	        	if ($(this).attr('name') != 'csrfmiddlewaretoken') {
	          		$("#links_modalbody_{{ i.article_id }}").append(start + $(this).attr('web') + middle1 + $(this).attr('show') + end);
	        	}
    });
    
    $("#links_{{ i.article_id }}").modal('show');
});

// Hide the 'successfully updated Figshare' info box until we've actually done so.
$("#{{ i.article_id }}_updated_figshare").hide();

// Download RDF Button handling
$("#rdf_{{ i.article_id }}").click(function(){
	$("#{{ i.article_id }}_form").prop("action","rdf/{{ i.article_id }}");
	$("#{{ i.article_id }}_form").submit();
})

// Add to Figshare button handling
$("#figshare_{{ i.article_id }}").click(function(){
	// Ensure that the form submission has the right target, and does not refresh the page.
	$("#{{ i.article_id }}_form").submit( function () {    
	    $.post(
	     'figshare/{{ i.article_id }}',
	      $(this).serialize(),
	      function(data){
	    	 $("#{{ i.article_id }}_updated_figshare").show();
	      }
	    );
	    return false;   
	}); 

	$("#{{ i.article_id }}_form").submit();
})
