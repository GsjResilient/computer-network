一、环境
Python 3.9.13


二、所需文件

PacketTCP.py
reversetcpclient.py
reversetcpserver.py
test.docx
test_new.docx

注意：PacketTCP.py在客户端和服务端必须都有；test.docx文件是待翻转的文本，test_new.docx是已翻转的文本

三、所需第三方库或内置库中的模块

socket、threading、select、random、Document   (版本任意)

四、命令行运行

运行server端:  python3 reversetcpserver.py   (虚拟机中 , ubuntu )
运行client端:   python reversetcpclient.py

结束服务器端：end

