def __GetFileData(filePath):
	fileObject = open(filePath,'rb')
	fileData = fileObject.read()
	fileObject.close()
	return fileData

def __PackData(data, contentType):
	return {'data': data, 'type': contentType}

def __OutputPage(query):
	pageName = query['FileName']
	# pageName = 'index' if not pageName else pageName
	pageName = 'index' if not pageName else pageName
	data = __GetFileData('./html/%s.html'%(pageName));
	return __PackData(data, 'text/html; charset=utf-8')

def __OutputTemplate(query):
	pageName = query['FileName']
	data = __GetFileData('./html/%s.xml'%(pageName));
	return __PackData(data, 'text/html; charset=utf-8')

def __OutputImage(query):
	typeList = {
		'jpg': 'jpeg',
		'png': 'png',
		'gif': 'gif',
		'bmp': 'bmp',
		'svn': "svg",
	}
	fileName = query['FileName']
	imageType = query['ImageType']
	data = __GetFileData('./html/images/%s'%(fileName))
	return __PackData(data, 'image/%s'%(typeList[imageType]))
	#return __GetFileData('./html/images/%s.jpg'%(imageName))

def __OutputStyleSheet(query):
	cssName = query['FileName']
	data = __GetFileData('./html/css/%s'%(cssName))
	return __PackData(data, 'text/css; charset=utf-8')

def __OutputJavascript(query):
	scriptName = query['FileName']
	data = __GetFileData('./html/scripts/%s'%(scriptName))
	return __PackData(data, 'text/javascript; charset=utf-8')

def ProcessGET(function, query):
	functions = {
		'html': __OutputPage,
		'temp': __OutputTemplate,
		'image': __OutputImage,
		'css': __OutputStyleSheet,
		'script': __OutputJavascript,
	}
	try:		
		if function not in functions:
			raise Exception('function %s is not exist'%(function))
		result = functions[function](query)
	except KeyError as exception:
		raise KeyError('%s: key %s is not exsit'%(function, str(exception)))
	except Exception as exception:
		raise type(exception)( '%s: %s' %(function, str(exception)))
	return result

