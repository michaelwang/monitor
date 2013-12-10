#!/usr/bin/python
#-*- coding:utf8 -*-
'''
Created on 2013-7-14
#判断文件中的ip是否能ping通，并且将通与不通的ip分别写到两个文件中
'''
import time,os
import subprocess 
start_Time=int(time.time()) #
def ping_Test():
    ips=open('host.txt','r')
    ip_True = open('ip_True.txt','w')
    ip_False = open('ip_False.txt','w')
    count_True,count_False=0,0
    for ip in ips.readlines():
        ip = ip.replace('\n','')  #替换掉换行符
        #return1=os.system('ping -c 2 -w 1 %s'%ip) #每个ip ping2次
        return1=subprocess.call("ping -c 1 %s" % ip, shell=True, stdout=open(r'ping.temp','w'), stderr=subprocess.STDOUT) 
        print '-----the result is %s'%return1
        if return1:
            print 'ping %s is fail'%ip
            ip_False.write(ip)  #把ping不
            count_False += 1
        else:
            print 'ping %s is ok'%ip
            ip_True.write(ip)  #把ping通的ip写到
            count_True += 1
    ip_True.close()
    ip_False.close()
    ips.close()
    end_Time = int(time.time())  #记录结束时间
    print "time(秒):",end_Time - start_Time,"s"  #打印并计算用的
    print "ping通数:",count_True,"   ping不通的ip数：",count_False
    
ping_Test()
