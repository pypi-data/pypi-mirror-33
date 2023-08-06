function setPage(pageName, passData){	
	if (typeof recentPage === 'undefined') {
        recentPage = '';
    }else if(pageName == recentPage){
		return;
	}
	recentPage = pageName;
	
	if (typeof preRequest === 'undefined') {
        preRequest = null;
    }else if(preRequest){
		preRequest.abort();
	}

	var request = function(url, javascriptObject, target, doneFunction, failFunction){
		preRequest = $.ajax({
			url: url,
			type: 'GET',
		  	contentType: 'text/html; charset=utf-8',
			context: target || $(this),
			data: null,
			datatype:"json",
		}).done(doneFunction).fail(failFunction);
	};
	
	var raspberryListInitialize = function(){
		var setButtons = function(){
			//remove button clicked
			$('#rpi_list .list input[name="remove"]').each(function(key, item){
				$(item).click(function(){
					var hostName = $(this).attr('target');
					//var row = $(item).parent().parent().remove();
					doProcess('del_raspberry_pi', hostName, function(){
						//row.remove();
						raspberryListInitialize();
					});
				});
			});

			//setup button clicked
			$('#rpi_list .list input[name="setup"]').each(function(key, item){
				$(item).click(function(){
					$(this).attr('disabled', '');
					var hostName = $(this).attr('target');
					doProcess('setup_raspberry_pi', hostName, function(){
						update_list();
					});
				});
			});

			//services button clicked
			$('#rpi_list .list input[name="services"]').each(function(key, item){
				$(item).click(function(){
					var hostName = $(this).attr('target');
					setPage('addService', hostName);
				});
			});
		};

		var update_list = function(){
			doProcess('update_list', null, function(data){
				doLayout('rpi_list', $('#rpi_list'), data);
				setButtons();
			});	
		};

		$('#rpi_list .control_panel input[name="create"]').click(function(){
			setPage('addRaspberry');
		});
		update_list();
		
	};

	var addRaspberryInitialize = function(){
		$('#create_rpi_page input[name="submit"]').click(function(){
			doProcess('add_raspberry_pi', null, function(){
				setPage('raspberryList');
			});
		});
		$('#create_rpi_page input[name="back"]').click(function(){
			setPage('raspberryList');
		});
	};

	var addServiceInitialize = function(){
		var hostName = passData;
		$('#add_service_page div[name="HostName"]').html(hostName);
		doProcess('get_services_list', hostName, function(data){
			doLayout('dropdown_list', $('#add_service_page #service_selector'), data);
		});
		$('#add_service_page input[name="submit"]').click(function(){
			var hostName = $('#add_service_page div[name="HostName"]').html();
			var service = $('#add_service_page  #service_selector select').val();
			var data = [hostName, service];
			doProcess('add_service', data, function(){
				setPage('raspberryList');
			});
		});
		$('#add_service_page input[name="back"]').click(function(){
			setPage('raspberryList');
		});
	};

	//Page Name
	var initialize = {
		'raspberryList': raspberryListInitialize,
		'addRaspberry': addRaspberryInitialize,
		'addService': addServiceInitialize,
	}

	request('/temp/' + pageName, '', $('#pre_content'), function(response){
		$(this).html('');
		$(this).append(response);
		initialize[pageName]();
		var preContent = $('#pre_content');
		$('#main_content').attr('id', 'pre_content');
		preContent.attr('id', 'main_content');
	},function(){
		$(this).html('<h1>Page Not Found!!</h1>');
	});

}
