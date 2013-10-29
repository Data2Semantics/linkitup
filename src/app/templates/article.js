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
    $("#show_yasgui_{{ i.article_id }}").hide();
    $("#figshare_upload_progress_{{ i.article_id }}").hide();
    $("#add_to_figshare_modal_{{ i.article_id }}").modal('show');
})

// Add to Figshare button handling
$("#do_add_to_figshare_{{ i.article_id }}").click(function(){
    // Ensure that the form submission has the right target, and does not refresh the page.
    $("#{{ i.article_id }}_form").submit( function () {
	$("#figshare_upload_progress_{{ i.article_id }} > div").text("Updating Figshare...");
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
        // $("#show_yasgui_{{ i.article_id }}").show();
        // 
        // $("#show_yasgui_{{ i.article_id }}").on('click', function(){
        //     var resource_uri = "<http://linkitup.data2semantics.org/resource/nanopublication/{{ i. article_id }}>"
        //     
        //     var request = "http://yasgui.data2semantics.org/?contentTypeConstruct=text%2Fturtle&contentTypeSelect=application%2Fsparql-results%2Bxml&endpoint=http%3A%2F%2Fsemweb.cs.vu.nl%3A8080%2Fopenrdf-sesame%2Frepositories%2Fgoldendemo&outputFormat=table&query=PREFIX+rdf%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23%3E%0APREFIX+rdfs%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23%3E%0A%0ASELECT+*+WHERE+%7B%0A++%7B+%3Fs+%3Fp+%3Chttp%3A%2F%2Flinkitup.data2semantics.org%2Fresource%2Fnanopublication%2Ffigshare_95964%3E+.%0A++++BIND(%3Chttp%3A%2F%2Flinkitup.data2semantics.org%2Fresource%2Fnanopublication%2Ffigshare_95964%3E+as+%3Fo)+%0A++%7D+UNION%0A++%7B+%3Chttp%3A%2F%2Flinkitup.data2semantics.org%2Fresource%2Fnanopublication%2Ffigshare_95964%3E+%3Fp+%3Fo+.%0A++++BIND(%3Chttp%3A%2F%2Flinkitup.data2semantics.org%2Fresource%2Fnanopublication%2Ffigshare_95964%3E+as+%3Fs)+%0A++%7D%0A%7D&requestMethod=POST&tabTitle=Query"
        //     
        // })
	    
	    
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