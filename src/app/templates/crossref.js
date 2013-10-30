$(function(){
	$('#{{ f.id }}_progress').hide();
	
	$('#{{ f.id }}_button').on('click', function(){
		$('#{{ f.id }}_bar').text('Downloading {{ f.name }}... ');
		$('#{{ f.id }}_progress').show();
		
		$.get('crossref/upload/{{ article_id }}/{{ f.id }}/{{ f.name }}', function(data){
			$('#{{ f.id }}_bar').css('width','50%');
			$('#{{ f.id }}_bar').text('Extracting references from {{ f.name }}...');
			$.get('crossref/extract/{{ article_id }}/{{ f.id }}', function(data){
				$('#{{ f.id }}_bar').text('Extraction complete!');
        		$('#{{ f.id }}_bar').css('width','100%');
        		$("#{{ f.id }}_results").html(data);
			})
		});
	});
});
