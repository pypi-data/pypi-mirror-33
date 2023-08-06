$(".remove").on("click",function(){
	var $row = $(this).parent().parent();
	var id = $row.find(".log_id").val();
	$.ajax({
		url:'/polizas_automaticas/elimina_log/',
		type:'post',
		data:{
			'id': id,
		},
		success:function(data){
			$row.hide();
		},
		error:function(data){
		}
	});
});