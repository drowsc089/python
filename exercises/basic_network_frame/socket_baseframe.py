#!/usr/bin/env python
#-*- coding: utf-8 -*-
#socket服务端网络通讯基本框架之一
#单一服务器响应模式，非客户端交互模式，浏览器或模拟访问即返回结果
#python3.7下测试通过

import socket

def handle_request(client):
	buf = client.recv(1024)
	client.send("HTTP/1.1 200 OK\r\n\r\n")
	client.send("Hello, World")
	
	
def main():
	# 创建socket对象
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# 监听端口
	sock.bind(('127.0.0.1',8001))
	# 开始监听
	sock.listen(5)
	
	
	while True:
		#阻塞, deng . . . .
		#直到有请求连接
		print ('....')
		connection, address = sock.accept()
		# connection, 代表客户端socket对象,
		# address, 客户端IP地址
		#handle_request(connection)
		buf = connection.recv(1024)
		print (buf)
		# 经python3.7下测试connection.send需要发送bytes的数据格式，而不能是str，否则报错
		message1 = "HTTP/1.1 200 OK\r\n\r\n"
		new_message1 = message1.encode()
		message2 = "Hello, World"
		new_message2 = message2.encode()
		connection.send(new_message1)
		connection.send(new_message2)
		connection.close()
		
		
if __name__ == '__main__':
	main()