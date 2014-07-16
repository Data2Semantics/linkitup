function initialize_crossref(){
	var details = get_details();
	var body = $('#plugin_modal_body');
	
	$.each(details.files, function(i, file){
		if (file.mime_type == "application/pdf") {
			var div = $('<div/>');

			var img = $('<img/>');
			img.attr('src', file.thumb);
			img.attr('style', 'float: left;');
			
			div.append(img);
			div.append('<p><strong>'+file.name+'</strong></p>');
			div.append('<p>'+file.size+'</p>');

			img.on('click', function(e){
				var progress = get_progress_bar('Transferring file '+file.name);
				div.html(progress);
				transfer_file(file);
			});

			body.append(div);
		} 
	});
}


function transfer_file(file){
	var url = '{{ url_for("upload_to_crossref") }}';
	var callback = function(data){
		if (data.success) {
			
			extract_references(data.file);
		} else {
			$('#plugin_modal_body').html(get_info_box('error', 'Could not download '+file.name+' from Figshare...'));
		}
	}
	
	post(url, file, 'json', callback);
}


function extract_references(file){
	var url = '{{ url_for("get_file_and_extract") }}';
	var progress = get_progress_bar('Extracting references from ' + file.name);
	
	$('#plugin_modal_body').html(progress);
	
	
	var callback = function(data){
		var references = data.references
		
		$('#plugin_modal_body').empty();
		console.log(references);
		
		$.each(references, function(i,ref){
			var ref_p = $('<p class="small"><i class="icon-list"></i>&nbsp;'+ref.text+'</p>');
			
			ref_p.on('click', function(e){
				console.log("Matching '"+ref.text+"' for file "+file.name);
				match_references(file, ref, ref_p);
			});
			
			$('#plugin_modal_body').append(ref_p);
		});
		
		
	}
	
	post(url, file, 'json', callback);
}

function match_references(file, ref, target){
	var url = '{{ url_for("match_references") }}';
	
	var payload = {'file': file, 'reference': ref}
	var results_div = $('<div/>');
	target.after(results_div)
	
	var callback = function(data){
		if (data.urls != null ){
			add_results('crossref', data.urls);
			render_urls(results_div, data.urls);
		} else {
			results_div.html(get_info_box('warning','No results found'));
		}
	};
	
	post(url, payload, 'json', callback);
	
	
	
	
}
