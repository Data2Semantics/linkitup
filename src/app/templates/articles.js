$.ajaxSetup({  
	cache: false  
});

// data-role functionality
//$(function(){
//    $("[data-role=submit]").click(function(){
//        $(this).closest("form").submit();
//    });
//});
	
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