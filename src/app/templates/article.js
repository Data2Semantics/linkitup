// Code for showing the selected links modal
$("#show_{{ i.article_id }}").click(function(){
    showSelectedLinks("{{ i.article_id }}", "#links_modalbody_{{ i.article_id }}");
    
    $("#links_{{ i.article_id }}").modal('show');
});



// Download RDF Button handling
$("#rdf_{{ i.article_id }}").click(function(){
    $("#{{ i.article_id }}_form").prop("action","rdf/{{ i.article_id }}");
    $("#{{ i.article_id }}_form").submit();
})


$("#add_to_figshare_{{ i.article_id }}").click(function(){
    showSelectedLinks("{{ i.article_id }}", "#selected_links_list_{{ i.article_id }}");
    $("#figshare_upload_progress_{{ i.article_id }}").hide();
    $("#add_to_figshare_modal_{{ i.article_id }}").modal('show');
})

// Add to Figshare button handling
$("#do_add_to_figshare_{{ i.article_id }}").click(function(){
    
    // Ensure that the form submission has the right target, and does not refresh the page.
    $("#{{ i.article_id }}_form").submit( function () {
	
	// Show the progress bar, and make it active 
	$("#figshare_upload_progress_{{ i.article_id }}").toggleClass("active");
	$("#figshare_upload_progress_{{ i.article_id }}").show();
	
	$.post(
	 'figshare/{{ i.article_id }}',
	  $(this).serialize(),
	  function(data){
	    // Stop the progress bar from moving, and change the text to "Success!"
	    $("#figshare_upload_progress_{{ i.article_id }}").toggleClass("active");
	    $("#figshare_upload_progress_{{ i.article_id }} > div").text("Success!");
	    refreshArticleDetails("{{ i.article_id }}");
	  }
	);
	return false;   
    });
    
    $("#{{ i.article_id }}_form").submit();
})



$("#refresh_{{ i.article_id }}").click( function() {
    
    refreshArticleDetails("{{ i.article_id }}");

});
  
  
  
$("#uncheck_all_{{ i.article_id }}").click( function() {
    $("#{{ i.article_id }}_form :input[type='checkbox']:checked").removeAttr('checked');
    $("#{{ i.article_id }}_form :input[type='checkbox']:checked").parent().toggleClass('alert-warning');
    $("#{{ i.article_id }}_form :input[type='checkbox']:checked").parent().toggleClass('alert-success');
})