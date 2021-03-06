#-*- coding: UTF-8 -*-#
#
#*******************************************************************************
# clustermanagement_3.2.4.py - test case 3.2.4 of clustermanagement
#
# Author:  humj
#
# Version 1.0.0
#
# Date:2018-01-18 13:14:00
#
# Copyright (c) 2004-2011 Digital China Networks Co. Ltd
#
# Features:
# 3.2.4 自动发现功能AC上discovery ip list列表测试(IPV6)
# 测试目的：测试AC上discovery ipv6 list列表 
# 测试环境：同测试拓扑

#Package

#Global Definition

#Source files

#Procedure Definition 

#Functional Code

testname = 'TestCase clustermanagement_3.2.4'

avoiderror(testname)
printTimer(testname,'Start','Test discovery ipv6 list on AC')

################################################################################
#Step 1
#
#操作
# 在没有任何配置情况下查看ip list列表
#
#预期
# 查看成功，检查Total Number of Configured Entries值为0
################################################################################

printStep(testname,'Step 1',
          'Check ip list with default config on AC1',
          'Check the result')

# operate	
exec(compile(open('clustermanagement\\clustermanagement_initial(ipv6).py', "rb").read(), 'clustermanagement\\clustermanagement_initial(ipv6).py', 'exec'))
	  
EnterEnableMode(switch1)
data1 = SetCmd(switch1,'show wireless discovery ip-list')

#check
res1 = CheckLine(data1,'Total Number of Configured Entries','0',IC=True)
	
#result
printCheckStep(testname, 'Step 1', res1)

################################################################################
#Step 2
#
#操作
# 在AC1 的ip list列表中添加一个地址
#
#预期
# 用show wireless discovery ip-list查看检查：
# Total Number of Configured Entries值为1;IP Address 显示为2002:10::1
################################################################################

printStep(testname,'Step 2',
          'Add a new ip into discovery ip list',
          'Check the result')

# operate		  
EnterWirelessMode(switch1)
SetCmd(switch1,'discovery ipv6-list 2002:10::1')

data1 = SetCmd(switch1,'show wireless discovery ip-list')
#check
res1 = CheckLineList(data1,[('Total Number of Configured Entries','1'),
					 ('2002:10::1')],IC=True)

#result
printCheckStep(testname, 'Step 2', res1)

################################################################################
#Step 3
#
#操作
# 在AC1上ip-list列表中添加一个已经存在的地址
#
#预期
# ip-list列表不会增加，用show wireless discovery ip-list查看检查：
#Total Number of Configured Entries值为1;IP Address 显示为2002:10::1
################################################################################

printStep(testname,'Step 3',
          'Add a exist ip into discovery ip list',
		  'Check the result')		  

# operate		  
EnterWirelessMode(switch1)
SetCmd(switch1,'discovery ipv6-list 2002:10::1')

EnterEnableMode(switch1)
data1 = SetCmd(switch1,'show wireless discovery ip-list')
#check
res1 = CheckLineList(data1,[('Total Number of Configured Entries','1'),
					 ('2002:10::1')],IC=True)

#result
printCheckStep(testname, 'Step 3', res1)

################################################################################
#Step 4
#
#操作
# 在AC1上删除一个ip-list列表中不存在的地址
#
#预期
# ip-list列表不会变化,用show wireless discovery ip-list查看检查：
# Total Number of Configured Entries值为1
#
################################################################################

printStep(testname,'Step 4',
          ' Delete a not exist ip from discovery ip list',
          'Check the result')

# operate
EnterWirelessMode(switch1)
SetCmd(switch1,'no discovery ipv6-list 2002:10::2')

EnterEnableMode(switch1)
data1 = SetCmd(switch1,'show wireless discovery ip-list')

#check
res1 = CheckLine(data1,'Total Number of Configured Entries','1',IC=True)

#result
printCheckStep(testname,'Step 4', res1)

################################################################################
#Step 5
#
#操作
#在AC1上删除一个ip-list列表中已存在的地址
#
#预期
#删除成功,ip-list列表会变化,用show wireless discovery ip-list查看检查：
#Total Number of Configured Entries值为0
################################################################################

printStep(testname,'Step 5',
          ' Delete a exist ip from discovery ip list',
          'Check the result')

# operate		
EnterWirelessMode(switch1)
SetCmd(switch1,'no discovery ipv6-list 2002:10::1')

EnterEnableMode(switch1)
data1 = SetCmd(switch1,'show wireless discovery ip-list')

#check
res1 = CheckLine(data1,'Total Number of Configured Entries','0',IC=True)

#result
printCheckStep(testname,'Step 5', res1)

################################################################################
#Step 6
#
#操作
#在AC1 ip list列表中添加两个地址
#
#预期
#添加成功,ip-list列表会变化,用show wireless discovery ip-list查看检查：
#Total Number of Configured Entries值为2
################################################################################

printStep(testname,'Step 6',
          'Add two none exist ip into discovery ip list',
          'Check the result')

# operate		  
EnterWirelessMode(switch1)
SetCmd(switch1,'discovery ipv6-list 2002:10::2')

EnterWirelessMode(switch1)
SetCmd(switch1,'discovery ipv6-list 2002:10::3')

EnterEnableMode(switch1)
data1 = SetCmd(switch1,'show wireless discovery ip-list')

#check
res1 = CheckLine(data1,'Total Number of Configured Entries','2',IC=True)

#result
printCheckStep(testname, 'Step 6', res1)

################################################################################
#Step 7
#
#操作
#在AC1上删除所有的ip list列表
#
#预期
#删除成功,ip-list列表会变化,用show wireless discovery ip-list查看检查：
#Total Number of Configured Entries值为0
################################################################################

printStep(testname,'Step 7',
          'Delete all the discovery ip list on AC1',
          'Check the result')

# operate		  
EnterWirelessMode(switch1)
SetCmd(switch1,'no discovery ipv6-list')

EnterEnableMode(switch1)
data1 = SetCmd(switch1,'show wireless discovery ip-list')

#check
res1 = CheckLine(data1,'Total Number of Configured Entries','0',IC=True)

#result
printCheckStep(testname, 'Step 7', res1)

################################################################################
#Step 8
#
#操作
#AC1的ip-list列表删空后,在ip-list列表中添加一个地址
#
#预期
#添加成功,用show wireless discovery ip-list查看检查：
#Total Number of Configured Entries值为1
################################################################################

printStep(testname,'Step 8',
          'Add a new ip into discovery ip list',
          'Check the result')

# operate		  
EnterWirelessMode(switch1)
SetCmd(switch1,'discovery ipv6-list 2002:10::1')

EnterEnableMode(switch1)
data1 = SetCmd(switch1,'show wireless discovery ip-list')

#check
res1 = CheckLine(data1,'Total Number of Configured Entries','1',IC=True)

#result
printCheckStep(testname, 'Step 8', res1)

################################################################################
#Step 9
#
#操作
#恢复默认配置
################################################################################

printStep(testname,'Step 9',
          'Recover initial config')

# operate		  
#恢复AC1的配置
EnterWirelessMode(switch1)
SetCmd(switch1,'no discovery ipv6-list')
exec(compile(open('clustermanagement\\clustermanagement_unitial(ipv6).py', "rb").read(), 'clustermanagement\\clustermanagement_unitial(ipv6).py', 'exec'))  
#end
printTimer(testname, 'End')