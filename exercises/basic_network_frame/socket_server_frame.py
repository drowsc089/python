#!/usr/bin/env python
# -*- coding:utf-8 -*-


import socket


obj_server = socket.socket()
obj_server.bind(('localhost',8341))
obj_server.listen(5)
while True:
	print ('waiting...')
	conn,addr = obj_server.accept()
	# 最多接受的数据size
	client_data = conn.recv(1024)
	print (client_data)
	# 经python3.7下测试connection.send需要发送bytes的数据格式，而不能是str，否则报错
	message = "Hello Client!"
	new_message = message.encode()
	conn.send(new_message)
	conn.close