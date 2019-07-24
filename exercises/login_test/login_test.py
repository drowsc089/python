#!/usr/bin/env python
#-*- coding:utf-8 -*-
#simple login system execrise



import getpass

print "\n"
print "##################"
print "欢迎来到测试系统"
print "##################"
print "\n"


#(1,4)区间包含1,2,3不含4

for count in range(1,4):
    username = raw_input("请输入登录账号:")
    password = getpass.getpass("请输入密码:")
    if username == "testuser" and password == "testpassword":
       print "登陆成功!%s, 欢迎!" % username
       break
    else:
       if count == 3:
          print "登录失败重试超过3次，正在退出..."
       else:
	  num = 3 - count
	  print "登录失败，账号名或密码错误，剩余%d次重试机会，请重试" % num
          continue
