$(document).ready(function () {
	$("#clean-btn").click(function(){
		$.ajax({
			url: "/clean_storage",
			data: JSON.stringify({'operation': 'clean'}),
			contentType: "application/json; charset=utf-8",
			type: 'POST',
			success: function(result){
				if (result['success'] == true){
					location.reload();
				}
			},
			error: function(error) {
				console.log(error);
			}
		});
	});


	Dropzone.options.filedrop = {
		init: function () {
			this.on("complete", function (file) {
				if (this.getUploadingFiles().length === 0 && this.getQueuedFiles().length === 0) {
					location.reload();
				}
			});
		}
	};
});