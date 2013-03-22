$.ajaxSetup ({  
    cache: false,
    beforeSend: function(xhr){
		xhr.withCredentials = true;
	},
	xhrFields: { withCredentials: true },
	crossDomain: true
});


$("#{{ plugin.slug }}_result_{{ i.article_id }}").hide();


var html = "<div class='progress progress-striped active'>" +
   "<div class='bar' style='width: 100%;'>Loading links from {{ plugin.name }}...</div> " +
   "</div>";

var {{ plugin.slug }}_ajax_load = html;
var {{ plugin.slug }}_loadUrl_{{ i.article_id }} = "/{{ plugin.slug }}/{{ i.article_id }}";


$("#{{ plugin.slug }}_link_{{ i.article_id }}").click(function(){  
	$("#{{ plugin.slug }}_result_{{ i.article_id }}").modal('show');
	
	if($("#{{ plugin.slug }}_modalbody_{{ i.article_id }}").text() == '') {
    	$("#{{ plugin.slug }}_modalbody_{{ i.article_id }}").html({{ plugin.slug }}_ajax_load).load({{ plugin.slug }}_loadUrl_{{ i.article_id }},function(response, status, xhr) {
    		if (status == "success") {
				$('#{{ plugin.slug }}_link_{{ i.article_id }}').toggleClass('active');
    		}
    	}); 
    	
	}
});