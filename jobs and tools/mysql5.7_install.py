#!/usr/bin/env python
# -*- coding:utf-8 -*-
#功能：Linux系统下自动源码下载并编译安装mysql 5.7 带boost社区版本（community server）
#作者：dc
#创建时间：2019/7/9 17:48
#文件名：mysql5.7_install.py
#IDE：PyCharm
#使用注意事项：运行环境为Centos6 64位，代码解释器为python3，由于在windows7系统下编辑，于unix相关系统运行时请先更改文件格式（列如vim下:set ff=unix），最后注意代码声明头python解释器问题，请配置成当前系统环境下适用的python3解释器

import re
import sys
import os
import shutil
import subprocess
from urllib import request

store_path = "/data/usr/src"
#判断存放软件包下载存放目录是否存在
path_check = os.path.exists(store_path)
if path_check:
    print("存放下载文件目录已存在")
    pass
else:
    print("存放下载文件目录不存在，自动创建")
    os.makedirs(store_path)

def download_pkg():
    download_url1 = "https://dev.mysql.com/get/Downloads/MySQL-5.7/mysql-boost-5.7.26.tar.gz"
    download_url2 = "https://dl.bintray.com/boostorg/release/1.70.0/source/boost_1_70_0.tar.gz"
    # 下载mysql源码包
    file_check1 = os.path.exists("%s/mysql-boost-5.7.26.tar.gz" % store_path)
    if file_check1:
        print("mysql源码包已存在，跳过下载")
        pass
    else:
        print("开始下载mysql源码包...")
        request.urlretrieve(download_url1,"%s/mysql-boost-5.7.26.tar.gz" % store_path)
    #下载boost源码包
    file_check2 = os.path.exists("%s/boost_1_70_0.tar.gz" % store_path)
    if file_check2:
        print("boost源码包已存在，跳过下载")
        pass
    else:
        print("开始下载boost源码包...")
        request.urlretrieve(download_url2,"%s/boost_1_70_0.tar.gz" % store_path)


def set_pre_install():
    #新建mysql根目录
    mysql_home_path = "/data/usr/mysql-boost-5.7"
    path_check2 = os.path.exists(mysql_home_path)
    if path_check2:
        pass
    else:
        os.makedirs(mysql_home_path)
    #给mysql安装目录建立软链接
    slink_file = "/data/usr/mysql57"
    path_check3 = os.path.exists(slink_file)
    if path_check3:
        pass
    else:
        os.system('/bin/ln -s %s /data/usr/mysql57' % mysql_home_path)
    #替换当前系统yum下载源为163下载源
    #备份系统默认yum源配置文件
    os.system('/bin/cp -a /etc/yum.repos.d/CentOS-Base.repo /etc/yum.repos.d/CentOS-Base.repo.bak')
    #删除系统默认yum源配置文件
    os.system('/bin/rm -f /etc/yum.repos.d/CentOS-Base.repo')
    yum_repo_url = "http://mirrors.163.com/.help/CentOS6-Base-163.repo"
    #下载新的yum源配置文件并替换
    request.urlretrieve(yum_repo_url, '/etc/yum.repos.d/CentOS-Base.repo')
    os.system('/usr/bin/yum clean all')
    os.system('/usr/bin/yum makecache')
    #安装编译所需要用到的依赖库
    os.system('yum install -y make bzip2 bzip2-devel bzip2-libs python-devel bison-devel perl perl-devel gcc gcc-c++ openssl openssl-devel ncurses ncurses-devel cmake bison lrzsz')
    #新建用户组mysql和用户mysql
    os.system('/usr/sbin/groupadd mysql && /usr/sbin/useradd -g mysql mysql')
    #新建mysql的实例存放目录
    os.makedirs('/data/usr/mysql_instances')

def build_install():
    #安装boost运行库
    os.system('/bin/tar -zxf %s/boost_1_70_0.tar.gz -C %s' % (store_path,store_path))
    # 切换到解压后的boost源码目录
    os.chdir('%s/boost_1_70_0' % store_path)
    os.system('%s/boost_1_70_0/bootstrap.sh' % store_path)
    os.system('%s/boost_1_70_0/b2 install' % store_path)
    #安装mysql
    #解压mysql源码
    os.system('/bin/tar -zxf %s/mysql-boost-5.7.26.tar.gz -C %s' % (store_path,store_path))
    #切换到解压后的mysql源码目录
    os.chdir('%s/mysql-5.7.26' % store_path)
    #使用cmake编译安装
    os.system('/usr/bin/cmake -DCMAKE_INSTALL_PREFIX=/data/usr/mysql-boost-5.7 -DSYSCONFDIR=/data/usr/mysql-boost-5.7 -DWITH_MYISAM_STORAGE_ENGINE=1 -DWITH_INNOBASE_STORAGE_ENGINE=1 -DWITH_PARTITION_STORAGE_ENGINE=1 -DWITH_ARCHIVE_STORAGE_ENGINE=1  -DWITH_BLACKHOLE_STORAGE_ENGINE=1 -DWITH_FEDERATED_STORAGE_ENGINE=1  -DWITH_PERFSCHEMA_STORAGE_ENGINE=1 -DENABLED_LOCAL_INFILE=1 -DMYSQL_TCP_PORT=3306 -DWITH_EXTRA_CHARSETS=all -DWITH_DEBUG=0 -DENABLE_DEBUG_SYNC=0 -DWITH_SSL=system -DWITH_ZLIB=system -DWITH_READLINE=1 -DZLIB_INCLUDE_DIR=/usr -DWITH_READLINE=1 -DDEFAULT_CHARSET=utf8 -DDEFAULT_COLLATION=utf8_general_ci -DWITH_BOOST=boost')
    os.system('/usr/bin/make && /usr/bin/make install')
    #安装完毕，删除安装文件
    shutil.rmtree(path='%s/boost_1_70_0' % store_path)
    shutil.rmtree(path='%s/mysql-5.7.26' % store_path)
    #由于删除了mysql源码目录，出于shell终端的机制，需要切换到任意目录才不影响后续操作
    os.chdir(store_path)


def set_after_install(instance_port):
    #新建mysql实例根目录，单独存放配置文件my.cnf和数据，日志等
    instance_path = "/data/usr/mysql_instances/%s" % instance_port
    instance_log_path = "%s/logs" % instance_path
    instance_data_path = "%s/data" % instance_path
    instance_binlog_path = "%s/binlogs" % instance_log_path
    instance_slowlog_path = "%s/slowlogs" % instance_log_path
    # 创建目录
    os.makedirs(instance_path)
    os.makedirs(instance_log_path)
    os.makedirs(instance_data_path)
    # 创建mysql日志二级目录binlogs和slowlogs
    os.makedirs(instance_binlog_path)
    os.makedirs(instance_slowlog_path)
    os.system('/bin/touch %s/mysqld.log' % instance_log_path)
    #写入mysql的配置文件my.cnf，涉及目录位置的配置项变量化
    #配置文件第一部分
    content_conf_part1 = ['[mysqld]\n']
    #配置文件变量项第一部分
    content_conf_ele1 = "basedir = /data/usr/mysql-boost-5.7\n"
    content_conf_ele2 = "datadir = %s\n" % instance_data_path
    content_conf_ele3 = "socket = %s/mysqld.sock\n" % instance_path
    content_conf_ele4 = "slow_query_log_file = %s/slowquery.log\n" % instance_slowlog_path
    content_conf_ele5 = "log-bin = %s/bin-log-mysqld\n" % instance_binlog_path
    content_conf_ele6 = "log-bin-index = %s/bin-log-mysqld.index\n" % instance_binlog_path
    content_conf_ele7 = "port = %s\n" % instance_port
    #获取系统内网网卡eth0的地址的最后一位作为配置文件server_id项的值
    server_eth0_ip = subprocess.getoutput('/sbin/ip addr | /bin/grep eth0 | /bin/grep inet | /bin/awk \'{print $2}\' | /bin/cut -d . -f 4 | /bin/cut -d / -f 1')
    content_conf_ele8 = "server_id = %s\n" % server_eth0_ip
    #合并配置文件第一部分和变量项第一部分
    content_conf_part1.append(content_conf_ele1)
    content_conf_part1.append(content_conf_ele2)
    content_conf_part1.append(content_conf_ele3)
    content_conf_part1.append(content_conf_ele4)
    content_conf_part1.append(content_conf_ele5)
    content_conf_part1.append(content_conf_ele6)
    content_conf_part1.append(content_conf_ele7)
    content_conf_part1.append(content_conf_ele8)
    #合并后的配置文件作为第二部分
    content_conf_part2 = content_conf_part1
    #把配置文件非变量项作为单独的列表等待合并
    content_conf = ['max_binlog_size = 1024M\n','local-infile = 0','skip_symbolic_links = yes','transaction-isolation = READ-COMMITTED\n','log_timestamps = SYSTEM\n','character_set_server = utf8\n','skip-name-resolve\n','skip-grant-tables\n','expire_logs_days = 7\n','slow_query_log = on\n','long_query_time = 6\n','max_connections = 500\n','max_allowed_packet = 32M\n','binlog-format = ROW\n','binlog-checksum = CRC32\n','binlog-rows-query-log_events = 1\n','query_cache_type = 1\n','query_cache_size = 128M\n','query_cache_limit = 2M\n','max_heap_table_size = 256M\n','binlog_cache_size = 2M\n','sort_buffer_size = 8M\n','join_buffer_size = 1024M\n','tmp_table_size = 512M\n','thread_cache_size = 64\n','read_buffer_size = 2M\n','read_rnd_buffer_size = 8M\n','key_buffer_size = 1024M\n','bulk_insert_buffer_size = 64M\n'	,'innodb_file_per_table = 1\n','innodb_open_files = 500\n','innodb_buffer_pool_size = 6G\n','innodb_thread_concurrency = 0\n'  ,'innodb_purge_threads = 1\n','innodb_flush_log_at_trx_commit = 1\n','innodb_log_buffer_size = 8M\n','innodb_log_files_in_group = 3\n','innodb_log_file_size = 512M\n','innodb_max_dirty_pages_pct = 90\n','innodb_lock_wait_timeout = 120\n','# Disabling symbolic-links is recommended to prevent assorted security risks\n','symbolic-links = 0\n','# Recommended in standard MySQL setup\n','sql_mode = NO_ENGINE_SUBSTITUTION,STRICT_TRANS_TABLES\n' ,'[mysqld_safe]\n']
    #把上面列表每一项合并到配置文件第二部分
    for ele in content_conf:
        content_conf_part2.append(ele)
    #合并后的配置文件作为第三部分
    content_conf_part3 = content_conf_part2
    #合并最后的变量项ele7和ele8，最后一项不需要换行符\n
    content_conf_ele7 = "log-error=%s/mysqld.log\n" % instance_log_path
    content_conf_ele8 = "pid-file=%s/mysqld.pid" % instance_path
    content_conf_part3.append(content_conf_ele7)
    content_conf_part3.append(content_conf_ele8)
    #得到最终需要写入配置文件的列表第四部分
    content_conf_part4 = content_conf_part3
    #写入到配置文件my.cnf
    with open('%s/my.cnf' % instance_path,'w+') as f:
        f.writelines(content_conf_part4)
    #更改编译后的得到mysql根目录及其里面所有文件从属为mysql
    os.system('/bin/chown -R mysql:mysql /data/usr/mysql-boost-5.7')
    #执行mysqld脚本初始化
    os.system('/data/usr/mysql-boost-5.7/bin/mysqld --initialize-insecure --user=mysql --basedir=/data/usr/mysql-boost-5.7 --datadir=%s' % instance_data_path)
    #拷贝mysql启动脚本mysql.server到系统目录下并重命名为mysqld
    shutil.copy('/data/usr/mysql-boost-5.7/support-files/mysql.server','/etc/init.d/mysqld')
    # 更改新建实例的目录及其里面所有文件从属为mysql
    os.system('/bin/chown -R mysql:mysql %s' % instance_path)
    #修改启动脚本mysqld内容适配新实例
    os.system('sed -i "s#conf=#\#conf=#" /etc/init.d/mysqld')
    os.system('sed -i "s#^basedir=#basedir=/data/usr/mysql-boost-5.7#" /etc/init.d/mysqld')
    os.system('sed -i "s#^datadir=#datadir=%s#" /etc/init.d/mysqld' % instance_data_path)
    os.system("sed -i '/^datadir=/a\conf=%s/my.cnf' /etc/init.d/mysqld" % instance_path)
    os.system('sed -i "s#lockdir=.*#lockdir=\'%s\'#" /etc/init.d/mysqld' % instance_path)
    os.system('sed -i "s#^mysqld_pid_file_path=#mysqld_pid_file_path=%s/mysqld.pid#" /etc/init.d/mysqld' % instance_path)
    os.system('sed -i "s#mysqld_safe\ --datadir#mysqld_safe\ --defaults-file=\"\$conf\"\ --datadir#" /etc/init.d/mysqld')
    #给mysqld脚本授予执行权限
    os.system('/bin/chmod u+x /etc/init.d/mysqld')
    #把mysql服务端添加为系统服务
    os.system('/sbin/chkconfig --add mysqld')
    os.system('/sbin/chkconfig mysqld off')
    os.system('/sbin/chkconfig --level 235 mysqld on')
    #启动mysql服务端
    os.system('/sbin/service mysqld start')
    #设置mysql可执行文件目录到系统环境变量
    os.system('/bin/echo "export PATH=\$PATH:/data/usr/mysql-boost-5.7/bin" >> /etc/profile')
    #添加临时目录项tmpdir到mysql配置文件中
    temp_dir = "%s/temp" % instance_data_path
    os.system('sed -i "/\[mysqld\]/a\\tmpdir = %s" %s/my.cnf' % (temp_dir,instance_path))
    #创建mysql临时文件目录
    os.makedirs(temp_dir)
    #更改临时文件目录权限为mysql:mysql使其可以正常读写
    os.system('/bin/chown -R mysql:mysql %s' % temp_dir)
    #修改mysql配置文件后需要重启服务端
    os.system('/sbin/service mysqld restart')
    #添加系统防火墙规则，放行服务端端口
    os.system('/sbin/iptables-save')
    os.system('sed -i "/-A INPUT -j REJECT --reject-with icmp-host-prohibited/i\-A INPUT -p tcp -m tcp --dport %s -m comment --comment \"mysqld%s\" -j ACCEPT" /etc/sysconfig/iptables' % (instance_port,instance_port))
    os.system('/sbin/service iptables reload')
    os.system('/sbin/iptables-save')

if __name__ == "__main__":
        mysql_port = input("请输入要使用的mysql服务端端口：")
        download_pkg()
        set_pre_install()
        build_install()
        set_after_install(mysql_port)
        print("mysql5.7已安装完毕，请使用socket方式登录实例并设置用户密码")
