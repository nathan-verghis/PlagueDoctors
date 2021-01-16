$(document).ready(function(){
	var AccountInfo = {

	}
	$('#create-account-button').click(function(){
		$.ajax({
			type:'POST'
			url:'signup'
			data: JSON.stringify(AccountInfo),
			async:true,
			success:function(data){
				if(data.Type == "SQL"){
					//need to load new page on success
				}
				
				else {
					alert(data.content);
				}
		});
	});
});