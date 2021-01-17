$(document).ready(function(){
	$('#create-account-button').click(function(){
		var AccountInfo = JSON.stringify($('form').serializeArray());
		$.ajax({
			type:'POST',
			url:'http://localhost:5000/signup',
			data: AccountInfo,
			error:function(request, status, error){
				alert(request);
				alert(status);
				alert(error);
			},
			async:false,
			success:function(data){
				if(data.Type == "SQL"){
					//need to load new page on success
					x = 1;
				}
				else {
					alert(data.content);
				}
			},
		});
	});
});