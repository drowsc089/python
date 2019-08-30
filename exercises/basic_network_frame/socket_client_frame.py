#!/usr/bin/env python
# -*- coding:utf-8 -*-
#socket网络通讯基本框架之二
#服务器_客户端交互模式，启动本客户端后自动发送信息等待服务端返回信息
#python3.7下测试通过

import socket



obj = socket.socket()
obj.connect(('localhost',8341))
# 经python3.7下测试connection.send需要发送bytes的数据格式，而不能是str，否则报错
message = "Hello Server!"
new_message = message.encode()
obj.send(new_message)
server_data = obj.recv(1024)
print (server_data)
obj.close()