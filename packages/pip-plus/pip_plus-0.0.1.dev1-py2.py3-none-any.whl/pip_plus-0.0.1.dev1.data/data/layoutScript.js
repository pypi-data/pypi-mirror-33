function doLayout(layoutName, targetParent, data){
	
	var raspberryListLayout = function(){
		var notFoundPage = $(targetParent).find('.not_found_page');
		var listPage = $(targetParent).find('.list');
			 		
	

		if(data.length <= 0){
			notFoundPage.removeClass('hidden');
			listPage.addClass('hidden');
			return;
		}		
		var appendText = '';
		var contents = [];
		var titles = $(targetParent).find('.list thead th');
		$.each(titles, function(){
			value = $(this).attr('content');
			if(!value){
				return;
			}
			contents.push(value);
		});

		appendText += '<tbody>';
		$.each(data, function(index, item){ 
			appendText += '<tr>';
			$.each(contents, function(key, value){
				appendText += '<td content="' + value + '">' + item[value] + '</td>';
			});
			appendText += '<td>';
			//setup button
			appendText += '<input type="button" name="setup" target="' + item['HostName'] + '" value="setup" ' + (item['Status']=='New'?'':'disabled') + '>';
			//services button
			appendText += '<input type="button" name="services" target="' + item['HostName'] + '" value="services" ' + (item['Status']=='New' || item['Status']=='Setting'?'disabled':'') + '>';
			//remove button
			appendText += '<input type="button" name="remove" target="' + item['HostName'] + '" value="remove">';
			appendText += '</td>';
			appendText += '</tr>';
		});
		appendText += '</tbody>';

		//console.log(appendText);
		$(targetParent).find('.list table tbody').remove();
		$(targetParent).find('.list table').append(appendText);
		listPage.removeClass('hidden');
		notFoundPage.addClass('hidden');
	}

	var servicesListLayout = function(){
		var notFoundPage = $(targetParent).find('.not_found_page');
		var listPage = $(targetParent).find('.list');
			 		
	

		if(data.length <= 0){
			notFoundPage.removeClass('hidden');
			listPage.addClass('hidden');
			return;
		}		
		var appendText = '';
		var contents = [];
		var titles = $(targetParent).find('.list thead th');
		$.each(titles, function(){
			value = $(this).attr('content');
			if(!value){
				return;
			}
			contents.push(value);
		});

		appendText += '<tbody>';
		$.each(data, function(index, item){ 
			appendText += '<tr>';
			$.each(contents, function(key, value){
				appendText += '<td content="' + value + '">' + item[value] + '</td>';
			});
			appendText += '<td>';
			//setup button
			appendText += '<input type="button" name="setup" target="' + item['HostName'] + '" value="setup" ' + (item['Status']=='New'?'':'disabled') + '>';
			//services button
			appendText += '<input type="button" name="services" target="' + item['HostName'] + '" value="services" ' + (item['Status']=='New' || item['Status']=='Setting'?'disabled':'') + '>';
			//remove button
			appendText += '<input type="button" name="remove" target="' + item['HostName'] + '" value="remove">';
			appendText += '</td>';
			appendText += '</tr>';
		});
		appendText += '</tbody>';

		//console.log(appendText);
		$(targetParent).find('.list table tbody').remove();
		$(targetParent).find('.list table').append(appendText);
		listPage.removeClass('hidden');
		notFoundPage.addClass('hidden');
	}

	var dropdownListLayout = function(){
		appendText = '';
		$.each(data, function(index, value){
			appendText += '<option value="' + value + '">' + value + '</option>';
		});

		$(targetParent).find('select').append(appendText);
	}

	var layouts = {
		'rpi_list': raspberryListLayout,
		'dropdown_list': dropdownListLayout,
	}

	layouts[layoutName]();
}
