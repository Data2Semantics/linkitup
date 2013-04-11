$.ajaxSetup({  
	cache: false  
});

$("#articles").change(function() {
	var article_id = $("#articles").val();
	var article_tab = "#" + article_id + "_tab";
	var article_plugins = "#" + article_id + "_plugins";
	
	// Deactivate all active tabs
	$(".details").hide();
	$(".plugins").hide();
	
	// Activate the selected tab
	$(article_tab).show();
	$(article_plugins).show();
});

function showSelectedLinks(articleid, element) {
	$(element).empty();
	
	var start = "<label class='checkbox alert alert-info'><a href='";
	var middle1 = "' target='_new'>";
	var end = "</a></label>";
	
	var selections = $("#"+ articleid +"_form :input[type='checkbox']:checked").length;
	
	if (selections == 0) {
	    $(element).html("<label class='checkbox alert alert-warning'>No links selected</label>");
	} else {
	    $("#"+ articleid +"_form :input[type='checkbox']:checked").each( 
		function(){
		if ($(this).attr('name') != 'csrfmiddlewaretoken') {
			var label = $("<label class='checkbox alert alert-info'>");
			var closeButton = $("<button type='button' target='"+ $(this).attr('id') +"' class='close' data-dismiss='alert'>");
			closeButton.html("&times;");
			
			closeButton.click(function(){
				var target = closeButton.attr('target');
				
				console.debug("Removing 'checked' from "+target);
				$("#"+target).removeAttr("checked");
				console.debug("Toggling alert-success on parent of "+target);
				$("#"+target).parent().toggleClass('alert-success');
				console.debug("Toggling alert-warning on parent of "+target);
				$("#"+target).parent().toggleClass('alert-warning');

				console.debug("done");
			});
			
			label.append(closeButton);
			
			$(this).siblings().clone().appendTo(label);
			
			
			$(element).append(label);
		    // $(element).append(start + $(this).attr('web') + middle1 + $(this).attr('show') + end);
		}
	    });	
	}    
}