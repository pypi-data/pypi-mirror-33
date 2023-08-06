function doProcess(processName, value, callback){

	if (typeof preRequest === 'undefined') {
        preRequest = null;
    }else if(preRequest){
		preRequest.abort();
	}

	var request = function(url, javascriptObject, doneFunction, failFunction){
		preRequest = $.ajax({
			url: url,
			type: 'POST',
		  	contentType: 'application/json; charset=utf-8',
			data: JSON.stringify(javascriptObject||{}),
			datatype:'json',
		}).done(doneFunction).fail(failFunction);
	};

	var updateList = function(){
		request('/rpi/list', null, function(response){
			//console.log(response);
			var data = response;
			callback(data);
		},function(){
			console.log('updateList error');
		});	
	}

	var addRaspberryPI = function(){
		var table = $('#create_rpi_page table');
		var hostName = table.find('input[name="HostName"]').val();
		var memory = table.find('input[name="Memory"]').val();
		var os = table.find('input[name="OS"]').val();
		var ipAddress = table.find('input[name="IPAddress"]').val();

		data = {
			"HostName": hostName,
			"Memory": memory,
			"OS": os,
			"IPAddress": ipAddress,
		}

		request('/rpi/create', data, function(response){
			//check successed
			//console.log(response);
			//updateList();
			callback();
		},function(){
			console.log('addRaspberryPI error');
		});	
	}

	var removeRaspberryPI = function(){
		hostName = value;
		//console.log(hostName);
		data = {
			"HostName": hostName,
		}

		request('/rpi/remove', data, function(response){
			//check successed
			//console.log(response);
			callback();
		},function(){
			console.log('removeRaspberryPI error');
		});	
	}	

	var setupRaspberryPI = function(){
		hostName = value;
		//console.log(hostName);
		data = {
			"HostName": hostName,
		}

		request('/rpi/install', data, function(response){
			//check successed
			//console.log(response);
			callback();
		},function(){
			console.log('setupRaspberryPI error');
		});	
	}	

	var getServicesList = function(){
		hostName = value;
		//console.log(hostName);
		data = {
			"HostName": hostName,
		}

		request('/service/find', data, function(response){
			var data = response;
			//check successed
			//console.log(response);
			callback(data);
		},function(){
			console.log('getServicesList error');
		});	
	}

	var addService = function(){
		var hostName = value[0];
		var service = value[1];

		data = {
			"HostName": hostName,
			"ServiceName": service,
		}

		request('/service/install', data, function(response){
			callback();
		},function(){
			console.log('addService error');
		});	
	}

	var process = {
		'update_list': updateList,
		'add_raspberry_pi': addRaspberryPI,
		'del_raspberry_pi': removeRaspberryPI,
		'setup_raspberry_pi': setupRaspberryPI,
		'get_services_list': getServicesList,
		'add_service': addService,
	}
	
	process[processName]();
}
