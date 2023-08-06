#!/usr/bin/env python
#--coding:utf-8--

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import os
from urllib.parse import urlparse
import json
import pip_plus.core  as core

import webbrowser
from pip_plus.controllor.ProcessGET import ProcessGET
# from controllor.ProcessPOST import ProcessPOST
import time
import socket
import cgi
import re
import sys

#包列表  当前已经安装的包
#pip list
#包信息
#pip  show  django
#过期的包
#pip list --outdated

# subprocess.Popen

#主页  当前安装的包   当前python 的状态 和 pip的状态




#搜索 各种 pip包




#查看 包









curdir = os.path.dirname(os.path.realpath(__file__))
sep = '/'

# MIME-TYPE
mimedic = [
                        ('.html', 'text/html'),
                        ('.htm', 'text/html'),
                        ('.js', 'application/javascript'),
                        ('.css', 'text/css'),
                        ('.json', 'application/json'),
                        ('.png', 'image/png'),
                        ('.svg', 'image/svg'),
                        ('.jpg', 'image/jpeg'),
                        ('.gif', 'image/gif'),
                        ('.txt', 'text/plain'),
                        ('.avi', 'video/x-msvideo'),
                        # favicon.ico
                    ]

class HTTPServer_RequestHandler(BaseHTTPRequestHandler):
    # GET
    def do_GET(self):
#        sendReply = False
#        querypath = urlparse(self.path)
#        filepath, query = querypath.path, querypath.query
#        print(filepath)
#        if filepath.endswith('/'):
#            # filepath += 'index.html'
#            filepath += 'html/xiaoming.html'
#
#        if filepath=="favicon.ico":
#            # filepath += 'favicon.ico'
#            pass
#
#        filename, fileext = path.splitext(filepath)
#        for e in mimedic:
#            if e[0] == fileext:
#                mimetype = e[1]
#                sendReply = True
#
#        
#            # self.wfile.write(buf)
#            # return
#
#            pass
#        if sendReply == True:
#            try:
#                with open(path.realpath(curdir + sep + filepath),'rb') as f:
#                    content = f.read()
#                    self.send_response(200)
#                    self.send_header('Content-type',mimetype)
#                    self.end_headers()
#                    self.wfile.write(content)
#            except IOError:
#                self.send_error(404,'File Not Found: %s' % self.path)





        query_components = parse_qs(urlparse(self.path).query)
        #print('path: ' + self.path)
        pathList = self.path.split('/')
        for name in query_components:
            query_components[name] = query_components[name][0]
        try:
            if len(pathList) > 2:
                fileType = pathList[1]
                fileName = pathList[2]
                query = {'FileName': fileName}
                query.update(query_components)
                result = ProcessGET(fileType, query)
            else:
                fileName = pathList[1] if pathList[1] else None
                result = ProcessGET('html', {'FileName': fileName})

            if result:
                contentType = result['type']
                data = result['data']
                status = 200
            else:
                raise Exception('result is nothing')
        except Exception as exception:
            print('%s: %s'%(type(exception).__name__, str(exception)))
            contentType = 'text/html; charset=utf-8'
            data = b'Page Not Found\n'
            status = 404

        # Begin the response
        self.send_response(status)
        self.send_header('Content-type', contentType)
        self.end_headers()
        self.wfile.write(data)






    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')                
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Requested-With")
        self.end_headers()
        return




    def do_POST(self):



        data = b''
        
        try:
            # load josn
            content_len = -1
            if 'content-length' in self.headers:
                content_len = int(self.headers['content-length'])

            if  content_len > 200:
                
                r, info = self.deal_post_data()
                print(r, info)

                # print(content_len)
                # post_body = self.rfile.read(content_len).decode('utf-8')
                # print(post_body)
                # Content-Disposition: form-data; name="file_data"; filename="views.py"
                # Content-Type: text/plain
                status = 200
                contentType = 'application/json'
                self.send_response(status)
                self.send_header('Content-type', contentType)
                self.end_headers()
                self.wfile.write(data)

                return 


            elif content_len > 0:
                #input json
                post_body = self.rfile.read(content_len).decode('utf-8')
                queryList = json.loads(post_body)
                pass
            else:
                queryList = {}
            #ProcessPOST(self.path, queryList)
            if queryList["type"] == "list":
                if   queryList["list"] == "local":
                    result = core.pip_list(options="local")
                    pass
                elif queryList["list"] == "outdated":
                    result = core.pip_list(options="outdated") 
                    pass
                else:
                    pass
                pass
            elif  queryList["type"] == "install":
                result = core.pip_install(package_name=queryList["package_name"],version=queryList["version"])
                # time.sleep(10)
                result = {"state":True}
                pass
            elif  queryList["type"] == "uninstall":
                result = core.pip_uninstall(package_name=queryList["package_name"])
                # time.sleep(10)
                result = {"state":True}
                pass
            elif  queryList["type"] == "update":
                result = core.pip_update(package_name=queryList["package_name"])
                # time.sleep(10)
                result = {"state":True}
                pass
                
            elif  queryList["type"] == "info":
                result = core.pip_show(package_name=queryList["package_name"])
                pass
            elif  queryList["type"] == "get_freeze":
                result = core.pip_freeze()
                
                pass
            elif  queryList["type"] == "terminal":
                result = core.start_terminal()
                pass

            else:
                pass
            if result:
                #contentType = result['type']
                contentType = 'application/json'
                #print('%s: %s'%(self.path, result))
                #data = json.dumps(result['data']).encode()
                data = json.dumps(result).encode()
                status = 200
            else:
                raise Exception('result is nothing')
        except Exception as exception:
            print('%s: %s'%(type(exception).__name__, str(exception)))
            contentType = 'application/json; charset=utf-8'
            data = b'Bad Request\n'
            status = 400

        # Begin the response
        self.send_response(status)
        self.send_header('Content-type', contentType)
        self.end_headers()
        self.wfile.write(data)



        pass





    def deal_post_data(self):
        content_type = self.headers['content-type']
        if not content_type:
            return (False, "Content-Type header doesn't contain boundary")
        boundary = content_type.split("=")[1].encode()
        remainbytes = int(self.headers['content-length'])
        line = self.rfile.readline()
        remainbytes -= len(line)
        if not boundary in line:
            return (False, "Content NOT begin with boundary")
        line = self.rfile.readline()
        remainbytes -= len(line)
        fn = re.findall(r'Content-Disposition.*name="file"; filename="(.*)"', line.decode())
        if not fn:
            return (False, "Can't find out file name...")
        path = self.translate_path(self.path)
        fn = os.path.join(path, fn[0])
        line = self.rfile.readline()
        remainbytes -= len(line)
        line = self.rfile.readline()
        remainbytes -= len(line)
        try:
            out = open(fn, 'wb')
        except IOError:
            return (False, "Can't create file to write, do you have permission to write?")
                
        preline = self.rfile.readline()
        remainbytes -= len(preline)
        while remainbytes > 0:
            line = self.rfile.readline()
            remainbytes -= len(line)
            if boundary in line:
                preline = preline[0:-1]
                if preline.endswith(b'\r'):
                    preline = preline[0:-1]
                out.write(preline)
                out.close()
                return (True, "File '%s' upload success!" % fn)
            else:
                out.write(preline)
                preline = line
        return (False, "Unexpect Ends of data.")






def run(port = 8080):
    print('starting server, port', port)

    # Server settings
    server_address = ('', port)
    httpd = HTTPServer(server_address, HTTPServer_RequestHandler)
    print('running server...')
    httpd.serve_forever()


def IsOpen(ip,port):
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        s.connect((ip,int(port)))
        s.shutdown(2)
        #利用shutdown()函数使socket双向数据传输变为单向数据传输。shutdown()需要一个单独的参数，
        #该参数表示了如何关闭socket。具体为：0表示禁止将来读；1表示禁止将来写；2表示禁止将来读和写。
        print ('%d is open' % port)
        return True
    except:
        print ('%d is down' % port)
        return False

def check_port():

    port=8080

    for line in range(0,100):
        if IsOpen('127.0.0.1', port) is False:
            break
        port = port +1
    return port



def main():
    # print(__file__)
    # print(os.path.realpath(__file__))


    # print(os.path.realpath(__file__))    # 当前文件的路径
    # print(os.path.dirname(os.path.realpath(__file__)))  # 从当前文件路径中获取目录
    # print(os.path.basename(os.path.realpath(__file__))) # 从当前文件路径中获取文件名

    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    port = check_port()
    webbrowser.open("http://localhost:"+str(port))
    print(os.getcwd())
    run(port)


if __name__ == '__main__':

    main()