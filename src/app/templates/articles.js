$.ajaxSetup ({  
    cache: false,
    beforeSend: function(xhr){
		xhr.withCredentials = true;
	},
	xhrFields: { withCredentials: true },
	crossDomain: true
});

/*
// Initializes the page, clears the local storage, retrieves the list of plugins and available articles
// Stores the results in local storage, and sets the 'ready' flag to true (required for running plugins)
*/
$(document).ready(function() { 
	$.localStorage('ready', false);
	$.localStorage('details', {});
	$.localStorage('articles', {});
	
	$.localStorage('selected', {});
	$.localStorage('results', {});
	
	// Click handlers for standard menu options
	
	$('#preview_selection').on('click', function(e){
		preview_selection();
	})
	
	$('#preview_nanopublication').on('click', function(e){
		preview_nanopublication();
	})
	
	$('#publish_to_figshare').on('click', function(e){
		publish_to_figshare();
	});
	
	$('#refresh').on('click', function(e){
		update_article_details();
	});
	
	$('#uncheck_all').on('click', function(e){
		$.localStorage('selected', {});
	});
	
	initialize_plugins();
	
	initialize_articles();
	
});

// Get the list of plugins, and render the plugin menu.
function initialize_plugins(){	
	$.get("{{ url_for('load_plugins') }}", function(data) {
		$.localStorage ( 'plugins', data.result);
		
		render_plugins(data.result);
	});
}

/*
// Renders the list of available plugins
*/
function render_plugins(plugins){
	$.each(plugins, function(index, value){
		var plugin_link = $('<a id="'+ value.slug +'">'+value.name+'</a>');
		var li = $('<li></li>');
		li.addClass('plugin');
		li.append(plugin_link);
		$('#plugins_header').after(li);
		
		plugin_link.on('click',function(e){
			console.log(value.name + " clicked");
			run_plugin(value.slug, value.name, value.type);
		});
	});	
}

/*
// Initialize the list of articles, and render the first one to #article_details
// Set the 'ready' flag afterwards.
*/
function initialize_articles(){
	var loading = get_progress_bar("Retrieving list of articles from Figshare");
	
	$("#article_details").html(loading);
	
	$.get("{{ url_for('load_articles') }}", function(data){
		// Store the list of article_id/title pairs in local storage
		$.localStorage( 'articles', data.articles );
		// Store the dictionaries of all article details in local storage
		$.localStorage( 'details', data.details );
		
		// Render the list of articles
		render_articles(data.articles);
		
		// Render the details of the first article, and set the 'current' flag to that article_id
		if (data.articles.length > 0) {
			var article_id = data.articles[0].id;
			
			$.localStorage( 'current', article_id );
			
			render_article_details();
		} else {
			$("#article_details").html("Warning: no published or private articles found in your figshare account!")
		}
		
		$.localStorage('ready', true);
	});
}
/*
// Renders the list of available articles
*/
function render_articles(articles) {
	$("#articles").select2({ 
		placeholder: "Start typing..." , 
		allowClear: true,
		data: articles 
	}); 
	
	$("#articles").on('change', function(e){
		console.log("Different article selected");
		var article_id = $("#articles").val();
		$.localStorage('current', article_id);
		
		$.localStorage('selected', {});
		$.localStorage('results', {});
		
		render_article_details();
	});
}

/*
// Retrieves an HTML representation of the article details.
*/
function render_article_details() {
	var loading = get_progress_bar("Rendering article details");
	
	$("#article_details").html(loading);
	
	var url = "{{ url_for('article_details')}}";
	
	var callback = function(html) {
		$('#article_details').html(html);
	};
	
	post_article_html(url, callback);
}

/*
// Posts the article details in JSON to the specified URL, expects HTML in return and then calls the callback function.
*/
function post_article_html(url, callback){
	var details = get_details();
	
		
	post(url, details, "html", callback);
}

/*
// Posts the article details in JSON to the specified URL, expects JSON in return and then calls the callback function.
*/
function post_article_json(url, callback){
	var details = get_details();
	
	post(url, details, "json", callback);
}


/*
// Generic function for POSTing JSON to the backend
*/
function post(url, data, type, callback) {
	var payload = JSON.stringify(data);
	
	$.ajax({
		type: "POST",
		contentType: "application/json; charset=utf-8",
		url: url,
		data: payload,
		dataType: type,
	}).success(callback);
}

/*
// Gets the results for a specific plugin:
// * either from local storage for JSON-style plugins, or 
// * by calling the plugin, if a JSON-style plugin has not ran yet, or if the plugin is HTML-style (e.g. Crossref)
// prepares the modal window, and then calls render_plugin_results (JSON-style) to retrieve HTML content, and shows the modal.
*/
function run_plugin(plugin, name, type){
	var ready = $.localStorage('ready');
	
	if (ready) {
		var article_id = $.localStorage('current');
		
		/// Check whether the results are already in!
		
		var results = get_results(plugin);
		if (results != null && type == 'json') {
			render_urls($('#plugin_modal_body'), results);
			$('#plugin_modal').modal('show');
		} else {
			var loading = get_progress_bar("Retrieving links from " + name);
		
			$('#plugin_modal_name').html(name);
			$('#plugin_modal_body').html(loading);
			$('#plugin_modal').modal('show');
		
			var url = "/" + plugin ;
		
			if (type == 'json') {
				var callback = function(data){
					
					if (data.urls != null){
						add_results(plugin, data.urls);
					
						var body = $('#plugin_modal_body');
						render_urls(body, data.urls);
						
						$('#'+plugin).toggleClass('active');
					} else {
						$('#plugin_modal_body').html('No results...');
					}
				};
		
				post_article_json(url, callback);
			} else if (type == 'html') {
				var callback = function(html){
					$('#plugin_modal_body').html(html);
					$('#'+plugin).toggleClass('active');
				};
			
				post_article_html(url, callback);
			} else {
				alert('Plugin has unknown type!');
			}
		}
		
	}
	
}

/*
// Gets the list of selected urls, and shows them in the modal.
*/
function preview_selection(){
	var loading = get_progress_bar("Retrieving selections");

	$('#plugin_modal_name').html("Selected links");
	$('#plugin_modal_body').html(loading);
	$('#plugin_modal').modal('show');
	
	var selected = get_selected();
	var body = $('#plugin_modal_body');
	
	render_urls(body, selected);
}

function preview_nanopublication(){
	var loading = get_progress_bar("Retrieving nanopublication");

	$('#plugin_modal_name').html("Nanopublication Preview");
	$('#plugin_modal_body').html(loading);
	$('#plugin_modal').modal('show');
	
	var callback = function(data){
		var pre = $('<pre/>');
		var code = $('<code/>');
		
		pre.text(data);
		code.append(pre);
		
		$('#plugin_modal_body').html(code);
	}
	
	var details = get_details();
	var selected = get_selected();
	
	var payload = {'details' :  details, 'selected' : selected};
	
	post('{{ url_for("nanopublication")}}', payload, 'html', callback);
}

function publish_to_figshare(){
	$('#plugin_modal_name').html("Publish to Figshare");
	
	var body = $('#plugin_modal_body');
	body.empty();
	
	body.append('<p>This is where you can update your Figshare article with the links you selected through the various <strong>Linki</strong>tup plugins.</p>');
	
	var info = $('<div class="alert alert-info alert-block"/>');
	info.append('<button type="button" class="close" data-dismiss="alert">&times;</button>');
	var info_header = $('<p><strong>What will happen...</strong></p>');
	var info_text = $('<p>When you click the \'Add to Figshare\' button below, Linkitup will do the following:</p>'
	+ '<ul>'
        + '<li>The \'links\' section of your article will list all the URIs of the links you selected in Linkitup (see below).</li>'
        + '<li>A nanopublication with enriched metadata for your article will be published on Figshare.</li>'
        + '<li>A tag of the form "<code>RDF=[some number]</code>" will be added to your article. This tag <strong>links your article to the corresponding nanopublication</strong>.</li>'
        + '<li>The URI of the nanopublication will be added to the \'links\' section of your article.</li>'
    + '</ul>');
	info.on('click', function(e){
		info_text.toggle();
	})
	
	info.append(info_header);
	info.append(info_text);

	body.append(info);
	
	var warning = $('<div class="alert alert-warning alert-block">');
	warning.append('<button type="button" class="close" data-dismiss="alert">&times;</button>');
	var warning_header = $('<p><strong>What will not happen...</strong></p>');
	var warning_text = $('<ul>'
        + '<li>Unfortunately <strong>Linki</strong>tup can not (yet) publish the nanopublication together with the original article.</li>'
        + '<li><strong>Linki</strong>tup also can not (yet) reconstruct your links from the nanopublication when you revisit your article in Linkitup.</li>'
    + '</ul>');

	warning.on('click', function(e){
		warning_text.toggle();
	})
	
	warning.append(warning_header);
	warning.append(warning_text);

	body.append(warning);
	
	var links_header = $('<h4>Selected Links <small>(you can still remove them)</small></h4>');
	
	body.append(links_header);
	
	var links_body = $('<div/>');
	var selected = get_selected();
	
	// Render the list of selected URLs
	render_urls(links_body, selected);
	body.append(links_body);
	
	var publish_button_div = $('<div style="text-align: center;"></div>');
	var publish_button = $('<a class="btn-large btn-primary">Add to Figshare!</a>');
	// <a id="show_yasgui" class="btn-large btn-default"></a>'
	
	publish_button.on('click', function(e){
		var progress = get_progress_bar("Publishing to Figshare");
		publish_button_div.html(progress);
		
		var details = get_details();
		var selected = get_selected();
		
		var payload = {'details': details, 'selected': selected};
		
		var callback = function(data){
			if (data.success) {
				publish_button_div.html(get_info_box('success','Succesfully updated your Figshare publication'));
				links_body.toggle();
				// update_article_details();
			} else {
				publish_button_div.html(get_info_box('error','Something went wrong!'));
			}
		};
		
		post('{{ url_for("publish") }}', payload, "json", callback);
	});
	
	
	publish_button_div.append(publish_button);
	body.append(publish_button_div);
	
	$('#plugin_modal').modal('show');
	
	info_text.toggle();
	warning_text.toggle();
}

function update_article_details(){
	var article_id = $.localStorage('current');
	
	var payload = {'article_id': article_id}
	
	var callback = function(data){
		var all_details = $.localStorage('details');
		
		all_details[article_id] = data.details
		
		$.localStorage('details', all_details);
		
		render_article_details();
	};
	
	post('{{ url_for("refresh_article") }}', payload, 'json', callback);
}


/*
// For JSON-style plugins or the selected URLs, this function renders the body of the modal that shows the list of urls.
*/
function render_urls(body, urls) {
	body.empty();
	var selected = get_selected();
	
	$.each(urls, function(uindex, url) {
		var label = $('<label></label>');
		label.addClass('checkbox');
		label.addClass('alert');
		
		var input = $('<input type="checkbox"></input>');
		label.append(input);
		
		if (url.uri in selected) {
			label.addClass('alert-success');
			input.attr('checked',true);
		} else {
			label.addClass('alert-warning');
		}
		
		input.on('click', function(){
			label.toggleClass('alert-warning');
			label.toggleClass('alert-success');
			
			if (input.is(':checked')) {

				add_selected(url.uri, url);

			} else {

				remove_selected(url.uri);

			}
			
			console.log(get_selected());
		});
		
		
		var uri = $('<a href="' + url.uri + '"><i class="icon-globe"></i></a>');
		label.append(uri);
		
		var web = $('<a href="' + url.web + '">' + url.show + '</a>');
		label.append(web);
		
		if (url.extra != null){ 
			var extra = $('<span/>').text(' ('+ url.extra + ')');
			label.append(extra);
		}
		
		if (url.subscript != null) {
			var subscript = $('<div><small>' + url.subscript + '</small></div>');
			label.append(subscript);
		}
		
		body.append(label);
		
		if (url.description != null) {
			var description_div = $('<div style="margin-top: -1em; margin-bottom: 1em;"></div>');
			var description = $('<small>' + url.description + '</small>');
			description_div.append(description);
			
			body.append(description_div);
		}
	});
}




/* 
// *****************
// UTILITY FUNCTIONS
// ***************** 
*/

/*
// Get the article details from local storage
*/
function get_details(){
	var article_id = $.localStorage('current');
	
	return $.localStorage('details')[article_id];		
}

/*
// Retrieves the list of selected urls
*/
function get_selected(){
	return $.localStorage('selected');
}

/*
// Adds a selection (url) to the list of selectec/checked urls in local storage
*/
function add_selected(key, value){
	var selected = $.localStorage('selected');
	
	selected[key] = value;
	
	$.localStorage('selected', selected);
}

/*
// Removes a selection from the list of selected/checked urls in local storage
*/
function remove_selected(key){
	var selected = $.localStorage('selected');
	
	delete selected[key]
	
	$.localStorage('selected', selected);
}

/*
// Gets the results (list of urls) for a specific plugin, if already retrieved
*/
function get_results(plugin) {
	var results = $.localStorage('results');
	
	if (plugin in results) {
		return results[plugin];
	} else {
		return null;
	}
}

/*
// Adds the results (list of urls) retrieved for a specific plugin to the local storage
*/
function add_results(plugin, urls){
	var results = $.localStorage('results');
	
	results[plugin] = urls;
	
	$.localStorage('results', results);
}


/*
// Renders a progress bar with the 'label' as label
*/
function get_progress_bar(label){
	return "<div class='progress progress-striped active'>" +
		"<div class='bar' style='width: 100%;'>" + 
		label 
		+ "...</div> " +
		"</div>";
}

/*
// Renders an info box of type 'type', with text 'text'
*/
function get_info_box(type, text){
	return '<div class="alert alert-' + type + '">' + text + '</div>';
}
