import os
import sys
import subprocess
import json
import platform
from optparse import OptionParser 
# import pip._internal.commands.show 


#
#搜索 https://pypi.org/search/?q=django
#
#

def set_source():
    #https://www.cnblogs.com/ZhangRuoXu/p/6370107.html
    pass



def platform_info():
    # print (platform.python_version()  )
    # help(platform)
    print (platform.machine())                       #AMD64
    print (platform.node())                          #DESKTOP-H6E40QU
    print (platform.processor())                     #Intel64 Family 6 Model 158 Stepping 9, GenuineIntel
    print (platform.python_branch())                 #v3.6.5
    print (platform.python_build())                  #('v3.6.5:f59c0932b4', 'Mar 28 2018 17:00:18')
    print (platform.python_compiler())               #MSC v.1900 64 bit (AMD64)
    print (platform.python_implementation())         #CPython
    print (platform.python_revision())               #f59c0932b4
    print (platform.python_version())                #3.6.5
    print (platform.python_version_tuple())          #('3', '6', '5')
    print (platform.release())                       #10
    print (platform.system())                        #Windows
    print (platform.uname())                         #uname_result(system='Windows', node='DESKTOP-H6E40QU', release='10', version='10.0.16299', machine='AMD64', processor='Intel64 Family 6 Model 158 Stepping 9, GenuineIntel')
    print (platform.version())                       #10.0.16299
    pass                                             



def subprocess_cmd(cmd,get_json=False):
    # print (cmd)
    subp=subprocess.Popen(cmd,shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    line_list = []
    c=subp.stdout.readline()
    while c:
        c = c.decode('utf-8')
        line=c.replace("\r\n","")
        # print (line)
        if get_json is True:
            if is_json(line) is True:
                # print (line)
                line_list.append(line)
                return line
            pass
        else:
            line_list.append(line)
            pass
        c = subp.stdout.readline()

    return line_list


def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError as  e:
        return False
    return True

#包列表  当前已经安装的包
#pip list
#包信息
#pip  show  django
#过期的包
#pip list --outdated

# subprocess.Popen
#pip show django  -v

# 包的里列表
# pip list  --format json
def pip_list(options= "local"):
    cmd1 = "pip list  --"+options+"   --format json "
    #p = subprocess.Popen('pip list  --'+options+" -v  --format json", stdout=subprocess.PIPE, shell=True)
    package_list = subprocess_cmd(cmd1 ,get_json=True)

    # package_list_json_byte = p.stdout.read()
    # package_list_json_str  = package_list_json_byte.decode('utf-8')
    # # print(package_list_json)
    # package_list     = json.loads(package_list_json_str)
    # # package_list     = package_list_json_str
    # for line in package_list:
    #     #{'name': 'wheel', 'version': '0.31.0', 'location': 'c:\\python36\\lib\\site-packages', 'installer': 'pip'}
    #     print(line)
    #     # pass
    # print (package_list)
    return {"package_list":package_list}
    # return  bytes(str(package_list), encoding = "utf8")  
    pass




# 查看包的信息   -v 是看支持的版本   还有 运行的脚本，  -f 是列出来 文件啥的
def pip_show(package_name="pip"):
    #pip show django  -v
    line_list = subprocess_cmd("pip show "+package_name+" -v")

    package_info = {}
    package_info["commmand_list"] = []
    package_info["Classifiers"]   = []
    # package_info["Classifiers"]   = {}
    if len(line_list)>0:

        # print(line_list)

        # package_info["Name"]                 
        # package_info["Version"]              
        # package_info["Summary"]              
        # package_info["Home-page"]            
        # package_info["Author"]               
        # package_info["Author-email"]         
        # package_info["License"]              
        # package_info["Location"]             
        # package_info["Requires"]             
        # package_info["Required-by"]          
        # package_info["Metadata-Version"]     
        # package_info["Installer"]            


        for line in line_list:
            # 分类 信息
            if  line.find("::")>0:
                package_info["Classifiers"].append(line)
                continue
                #适用版本
                if line.fine("Programming Language :: Python")>0:
                    pass
                #分类主题
                elif line.fine("Topic :: ")>0:
                    pass
                #认证
                elif line.fine("License :: ")>0:
                    pass
                else:
                    line = line.split("::")
                    if len(line) ==2 :
                        package_info["Classifiers"][line[0].replace(" ","")] = line[1].replace(" ","")
                        pass
                    else:
                        # print (len(line))
                        # print(line)
                        pass
            #一般信息
            elif line.find(": ")>0:
                line = line.split(": ")
                if len(line[1])<=0:
                    package_info[line[0]] = None
                    
                else:
                    pass
                package_info[line[0]] = line[1]

                pass
            # 入口点
            elif  line.find(" = ")>0:
                command_info={}
                line = line.split(" = ")
                command_info["name"]        = line[0].replace(" ","")
                command_info["description"] = line[1]
                package_info["commmand_list"].append(command_info)
                pass
# License :: OSI Approved :: MIT License
# Topic :: Software Development :: Build Tools
# Programming Language :: Python
# Programming Language :: Python :: 2
# Programming Language :: Python :: 2.7
# Programming Language :: Python :: 3
# Programming Language :: Python :: 3.3
# Programming Language :: Python :: 3.4
# Programming Language :: Python :: 3.5
# Programming Language :: Python :: 3.6
# Programming Language :: Python :: Implementation :: CPython
# Programming Language :: Python :: Implementation :: PyPy

            else:

                pass


        # for d in package_info:
        #     print ("%s:%s" %(d, package_info[d])  )
        # print ( package_info["Classifiers"] )
        return {"package_info":package_info}

        pass
    else:
        return {"package_info":False}
        # print("no info")
        pass



# Name: Django
# Version: 1.11.8
# Summary: A high-level Python Web framework that encourages rapid development and clean, pragmatic design.
# Home-page: https://www.djangoproject.com/
# Author: Django Software Foundation
# Author-email: foundation@djangoproject.com
# License: BSD
# Location: c:\users\gin\appdata\local\programs\python\python35\lib\site-packages
# Requires: pytz
# Required-by: django-formtools, django-contrib-comments, channels
# Metadata-Version: 2.0
# Installer: pip
# Classifiers:
#   Development Status :: 5 - Production/Stable
#   Environment :: Web Environment
#   Framework :: Django
#   Intended Audience :: Developers
#   License :: OSI Approved :: BSD License
#   Operating System :: OS Independent
#   Programming Language :: Python
#   Programming Language :: Python :: 2
#   Programming Language :: Python :: 2.7
#   Programming Language :: Python :: 3
#   Programming Language :: Python :: 3.4
#   Programming Language :: Python :: 3.5
#   Programming Language :: Python :: 3.6
#   Topic :: Internet :: WWW/HTTP
#   Topic :: Internet :: WWW/HTTP :: Dynamic Content
#   Topic :: Internet :: WWW/HTTP :: WSGI
#   Topic :: Software Development :: Libraries :: Application Frameworks
#   Topic :: Software Development :: Libraries :: Python Modules
# Entry-points:
#   [console_scripts]
#   django-admin = django.core.management:execute_from_command_line






    pass


# 安装 包
def pip_install(package_name="flask",version=None):

    # print(package_name,version)
    # result= {}
    # result["state"]=True
    # return result
    # pip install django==1.11.3
    # Collecting django==1.11.3
    #   Using cached https://pypi.doubanio.com/packages/fe/ca/a7b35a0f5088f26b1ef3c7add57161a7d387a4cbd30db01c1091aa87e207/Django-1.11.3-py2.py3-none-any.whl
    # Requirement already satisfied: pytz in c:\python36\lib\site-packages (from django==1.11.3)
    # Installing collected packages: django
    # Successfully installed django-1.11.3


# Collecting django==1.11.30
#   Could not find a version that satisfies the requirement django==1.11.30 (from versions: 1.1.3, 1.1.4, 1.2, 1.2.1, 1.2.2, 1.2.3, 1.2.4, 1.2.5, 1.2.6, 1.2.7, 1.3, 1.3.1, 1.3.2, 1.3.3, 1.3.4, 1.3.5, 1.3.6, 1.3.7, 1.4, 1.4.1, 1.4.2, 1.4.3, 1.4.4, 1.4.5, 1.4.6, 1.4.7, 1.4.8, 1.4.9, 1.4.10, 1.4.11, 1.4.12, 1.4.13, 1.4.14, 1.4.15, 1.4.16, 1.4.17, 1.4.18, 1.4.19, 1.4.20, 1.4.21, 1.4.22, 1.5, 1.5.1, 1.5.2, 1.5.3, 1.5.4, 1.5.5, 1.5.6, 1.5.7, 1.5.8, 1.5.9, 1.5.10, 1.5.11, 1.5.12, 1.6, 1.6.1, 1.6.2, 1.6.3, 1.6.4, 1.6.5, 1.6.6, 1.6.7, 1.6.8, 1.6.9, 1.6.10, 1.6.11, 1.7, 1.7.1, 1.7.2, 1.7.3, 1.7.4, 1.7.5, 1.7.6, 1.7.7, 1.7.8, 1.7.9, 1.7.10, 1.7.11, 1.8a1, 1.8b1, 1.8b2, 1.8rc1, 1.8, 1.8.1, 1.8.2, 1.8.3, 1.8.4, 1.8.5, 1.8.6, 1.8.7, 1.8.8, 1.8.9, 1.8.10, 1.8.11, 1.8.12, 1.8.13, 1.8.14, 1.8.15, 1.8.16, 1.8.17, 1.8.18, 1.8.19, 1.9a1, 1.9b1, 1.9rc1, 1.9rc2, 1.9, 1.9.1, 1.9.2, 1.9.3, 1.9.4, 1.9.5, 1.9.6, 1.9.7, 1.9.8, 1.9.9, 1.9.10, 1.9.11, 1.9.12, 1.9.13, 1.10a1, 1.10b1, 1.10rc1, 1.10, 1.10.1, 1.10.2, 1.10.3, 1.10.4, 1.10.5, 1.10.6, 1.10.7, 1.10.8, 1.11a1, 1.11b1, 1.11rc1, 1.11, 1.11.1, 1.11.2, 1.11.3, 1.11.4, 1.11.5, 1.11.6, 1.11.7, 1.11.8, 1.11.9, 1.11.10, 1.11.11, 1.11.12, 1.11.13, 2.0a1, 2.0b1, 2.0rc1, 2.0, 2.0.1, 2.0.2, 2.0.3, 2.0.4, 2.0.5, 2.0.6, 2.1a1, 2.1b1)
# No matching distribution found for django==1.11.30
    result= {}
    # os.system("start  cmd  /c \"pip install flask&&pause\"")
# pip install --cache-dir %LocalAppData%/pip/cache   pyqt5==5.10.1
    if version:
        cmd1 = "start \"install " + package_name +"\" /wait  cmd /c  \"pip install --cache-dir %LocalAppData%/pip/cache "+package_name+"=="+version+" & echo finish &pause\"  & echo end"
        pass
    else:
        cmd1 = "start \"install " + package_name +"\" /wait  cmd /c  \"pip install --cache-dir %LocalAppData%/pip/cache "+package_name+" & echo finish &pause\"  & echo finish"
        pass

    
    line_list = subprocess_cmd(cmd1)
    for line in line_list:
        if line == "finish":
            result["state"]=True
            break

    # result["state"]=True
    return result
    pass


# 卸载 包
def pip_uninstall(package_name="pip"):
    # pip uninstall django  -y
    # Uninstalling Django-1.11.3:
    #   Successfully uninstalled Django-1.11.3

    # line_list = subprocess_cmd("pip uninstall "+package_name+"  -y ")
    # # for line in line_list:
    # #     print (line)
    # result = {}
    # if (line_list[-1].find("Successfully")>=0):
    #     result["state"]=True
    # else:
    #     result["state"]=False
    # print(result)

    result= {}
    result["state"]=False

    package_info  = pip_show(package_name=package_name)
    if package_info["package_info"] == False:
        result["state"]=False
    else:
        cmd1 = "start \"uninstall " + package_name +"\" /wait  cmd /c  \"pip uninstall "+package_name+" -y & echo finish &pause\"  & echo finish"
        line_list = subprocess_cmd(cmd1)
        for line in line_list:
            if line == "finish":
                result["state"]=True
                break

    return result
    pass


# 卸载 包
def pip_update(package_name="pip"):

    result= {}
    result["state"]=False

    package_info  = pip_show(package_name=package_name)
    if package_info["package_info"] == False:
        result["state"]=False
    else:
        cmd1 = "start \"update " + package_name +"\" /wait  cmd /c  \"pip install "+package_name+" -U & echo finish &pause\"  & echo finish"
        line_list = subprocess_cmd(cmd1)
        for line in line_list:
            if line == "finish":
                result["state"]=True
                break

    return result
    pass


# Uninstalling Django-1.11.8:
#   Successfully uninstalled Django-1.11.8

#  check
def pip_check(package_name="pip"):

    pass



def pip_freeze():
    cmd1 = "pip freeze"
    line_list = subprocess_cmd(cmd1)
    for line in line_list:
        print(line)

    return line_list
    pass


def start_terminal():
    cmd1 = "start  & echo \"started\"  &"
    # line_list = subprocess_cmd(cmd1)
    os.system(cmd1)

    return "started"
    # print("11111111")
    # for line in line_list:
    #     print(line)
    # return line_list

def test_main():
    # pip_list()
    # pip_show("pip")
    #
    # print(sys.stdout.isatty())
    # print(os.isatty(sys.stdout.fileno()))
    # print(pip_install("django"))
    # print("start uninstall ")
    # print(pip_uninstall("django"))
    # pip_freeze()
    start_terminal()
#     dict1 = {'trusted_hosts': ['pypi.douban.com'], 'client_cert': None, 'proxy': '', 'verbose': 1, 'log': None, 'no_color': False, 'help': None, 'skip_requirements_regex': '', 'require_venv': False, 'disable_pip_version_check': False, 'timeout': 15, 'files': False, 'retries': 5, 'version': None, 'quiet': 0, 'isolated_mode': False, 'cert': None, 'no_input': False, 'cache_dir': 'C:\\Users\\Gin\\AppData\\Local\\pip\\Cache', 'exists_action': []}
# {
#     'trusted_hosts': ['pypi.douban.com'],
#     'client_cert': None,
#     'proxy': '',
#     'verbose': 1,
#     'log': None,
#     'no_color': False,
#     'help': None,
#     'skip_requirements_regex': '',
#     'require_venv': False,
#     'disable_pip_version_check': False,
#     'timeout': 15,
#     'files': False,
#     'retries': 5,
#     'version': None,
#     'quiet': 0,
#     'isolated_mode': False,
#     'cert': None,
#     'no_input': False,
#     'cache_dir': 'C:\\Users\\Gin\\AppData\\Local\\pip\\Cache',
#     'exists_action': []
# }



#     parser = OptionParser() 
#     parser.add_option("-p", "--pdbk", action="store_true", 
#                       dest="pdcl", 
#                       default=False, 
#                       help="write pdbk data to oracle db") 

#     print(dict1.files)
#     abc = pip._internal.commands.show.ShowCommand()
#     abc = abc.run(dict1,['pip'])
    pass




if __name__ == '__main__':
    test_main()