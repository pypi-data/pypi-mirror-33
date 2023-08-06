$(document).ready(function(){
	//doProcess('update_list');

	$('#main_menu ul a').each(function(key, button){
		$(button).click(function(){
			if($(this).hasClass('active')){
				return;
			}
			targetPage = $(this).attr('targetPage');
			setPage(targetPage);
		});
	});

	setPage('raspberryList');
});
