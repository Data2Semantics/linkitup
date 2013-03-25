$(function () {
	$('#{{ f.id }}_progress').hide();
    $('#fileupload').fileupload({
        dataType: 'json',
        add: function (e, data) {
            $.each(data.files, function (index, file) {
            	$('#{{ f.id }}_bar').text('Uploading ' + file.name);
            });
            $("#fileupload").prop('disabled', true);
            $('#fileupload').hide();
            $('#{{ f.id }}_progress').show();
        	data.submit();
        },
        done: function (e, data) {
        	$('#{{ f.id }}_bar').text('Extracting references...');
        	$('#{{ f.id }}_bar').css('width','50%');
        	
        	$.get('crossref/extract/{{ article_id }}/{{ f.id }}',function(data) {
        		$('#{{ f.id }}_bar').text('Extraction complete!');
        		$('#{{ f.id }}_bar').css('width','100%');
        		$("#{{ f.id }}_results").html(data);
        	});
        } 
    });
});