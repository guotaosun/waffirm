#-*- coding: UTF-8 -*-#
#
#*******************************************************************************
# clustermanagement_3.2.1.py - test case 3.2.1 of clustermanagement
#
# Author:  humj
#
# Version 1.0.0
#
# Date:2018-01-18 10:00:00
#
# Copyright (c) 2006-2011 Digital China Networks Co. Ltd
#
# Features:
#3.1.1 AC开启无线IP地址自动选择功能测试(IPV6)
# 测试目的：测试AC开启IP地址自动选择功能后，AC是否能自动选择IPV6地址提供无线服务
# 测试环境：同测试拓扑

#Package

#Global Definition

#Source files

#Procedure Definition 

#Functional Code

testname = 'TestCase clustermanagement_3.2.1'

avoiderror(testname)
printTimer(testname,'Start','Test AC automatically choose wireless IPV6 Address')

################################################################################
#Step 1
#
#操作
# AC1没有配置环回接口和三层接口
# 在AC1无线模式下开启无线功能和无线IP地址自动选择功能，无线功能不能开启成功
# 用show wireless查看结果
#
#预期
#AC1的无线功能不能开启成功,show wireless看到'WLAN Switch Disable Reason'项显示为'IP address not configured'
################################################################################

printStep(testname,'Step 1',
          'Delete all the interface and open auto ip assign',
          'Check the result')

# operate	
exec(compile(open('clustermanagement\\clustermanagement_initial(ipv6).py', "rb").read(), 'clustermanagement\\clustermanagement_initial(ipv6).py', 'exec'))
	  
EnterConfigMode(switch1)
SetCmd(switch1,'no interface vlan',Vlan70)
SetCmd(switch1,'no interface vlan',Vlan80)
SetCmd(switch1,'no interface loopback 100')

EnterWirelessMode(switch1)
SetCmd(switch1,'auto-ip-assign')

#check
EnterEnableMode(switch1)
res1 = CheckSutCmd(switch1,'show wireless',
				   check=[('WLAN Switch Disable Reason','IP address not configured')],
				   retry=5,interval=3,waitflag=False,IC=True)
#result
printCheckStep(testname, 'Step 1', res1)

################################################################################
#Step 2
#
#操作
#在AC1上配置一个三层接口
#
#预期
#AC1上show wireless看到'WS IPv6 Address'项已经显示为'If_vlan10_ipv6
################################################################################

printStep(testname,'Step 2',
          'Config a three layer interface on AC1',
          'Check the result')

# operate		  
EnterConfigMode(switch1)
SetCmd(switch1,'vlan',Vlan10)
EnterConfigMode(switch1)
SetCmd(switch1,'interface',s1p1)
SetCmd(switch1,'switchport trunk allowed vlan',Vlan70+';'+Vlan80+';'+Vlan10)

EnterConfigMode(switch1)
SetCmd(switch1,'interface vlan',Vlan10)
SetCmd(switch1,'ipv6 address',If_vlan10_ipv6)

#check
EnterEnableMode(switch1)
res1 = CheckSutCmd(switch1,'show wireless',
				   check=[('WS IPv6 Address',If_vlan10_ipv6_s)],
				   retry=5,interval=3,waitflag=False,IC=True)
#result
printCheckStep(testname, 'Step 2', res1)

################################################################################
#Step 3
#
#操作
#在AC1上另外配置两个三层接口，其中接口索引号interface vlan10> interface vlan9> interface vlan8
#
#预期
#AC1上show wireless看到'WS IPv6 Address'项已经显示为'If_vlan10_ipv6_s'
################################################################################

printStep(testname,'Step 3',
          'Config other two three layer interfaces on AC1',
          'Check the result')		  

# operate		  
#配置interface vlan9
EnterConfigMode(switch1)
SetCmd(switch1,'vlan',Vlan9)
EnterConfigMode(switch1)
SetCmd(switch1,'interface',s1p1)
SetCmd(switch1,'switchport trunk allowed vlan',Vlan70+';'+Vlan80+';'+Vlan10+';'+Vlan9)
EnterConfigMode(switch1)
SetCmd(switch1,'interface vlan',Vlan9)
SetCmd(switch1,'ipv6 address',If_vlan9_ipv6)

#配置interface vlan8
EnterConfigMode(switch1)
SetCmd(switch1,'vlan',Vlan8)
EnterConfigMode(switch1)
SetCmd(switch1,'interface',s1p1)
SetCmd(switch1,'switchport trunk allowed vlan',Vlan70+';'+Vlan80+';'+Vlan10+';'+Vlan9+';'+Vlan8)
EnterConfigMode(switch1)
SetCmd(switch1,'interface vlan',Vlan8)
SetCmd(switch1,'ipv6 address',If_vlan8_ipv6)

#check
EnterEnableMode(switch1)
res1 = CheckSutCmd(switch1,'show wireless',
				   check=[('WS IPv6 Address',If_vlan10_ipv6_s)],
				   retry=5,interval=3,waitflag=False,IC=True)
#result
printCheckStep(testname, 'Step 3', res1)

################################################################################
#Step 4
#
#操作
#在无线模式下重新启动无线功能
#
#预期
#AC1会自动选择索引号最小的三层接口IPv6为无线模块的IPv6地址
#AC1上show wireless看到'WS IPv6 Address'项已经显示为'If_vlan8_ipv6_s'
################################################################################

printStep(testname,'Step 4',
          'Reboot the AC1 wireless',
          'Check the result')

# operate		  
EnterWirelessMode(switch1)
SetCmd(switch1,'no enable')
IdleAfter(1)
SetCmd(switch1,'enable')
IdleAfter(10)

#check
EnterEnableMode(switch1)
res1 = CheckSutCmd(switch1,'show wireless',
				   check=[('WS IPv6 Address',If_vlan8_ipv6_s)],
				   retry=5,interval=3,waitflag=False,IC=True)
#result
printCheckStep(testname,'Step 4', res1)

################################################################################
#Step 5
#
#操作
#把选定为无线模块IPv6地址的三层接口down掉
#AC会重新自动选择剩余up的接口索引号最小的接口对应的IPv6地址为无线模块的IPv6地址
#
#预期
#AC1上show wireless看到'WS IPv6 Address'项已经显示为'If_vlan9_ipv6_s'
################################################################################

printStep(testname,'Step 5',
          'Shutdown the three layer interface',
          'Check the result')

# operate		  
EnterConfigMode(switch1)
SetCmd(switch1,'interface vlan',Vlan8)
SetCmd(switch1,'shutdown')

#check
EnterEnableMode(switch1)
res1 = CheckSutCmd(switch1,'show wireless',
				   check=[('WS IPv6 Address',If_vlan9_ipv6_s)],
				   retry=6,interval=5,waitflag=False,IC=True)
#result
printCheckStep(testname, 'Step 5', res1)

################################################################################
#Step 6
#
#操作
#在AC上另外配置一个环回接口,重新启动无线功能
#
#预期
#AC1上show wireless看到'WS IPv6 Address'项已经显示为'If_loopback3_ipv6_s'
################################################################################

printStep(testname,'Step 6',
          ' Config a loopback interface on AC1',
          'Check the result')

# operate		  
EnterConfigMode(switch1)
SetCmd(switch1,'interface loopback 3')
SetCmd(switch1,'ipv6 address',If_loopback3_ipv6)
IdleAfter(10)

EnterWirelessMode(switch1)
SetCmd(switch1,'no enable')
IdleAfter(1)
SetCmd(switch1,'enable')

#check
EnterEnableMode(switch1)
res1 = CheckSutCmd(switch1,'show wireless',
				   check=[('WS IPv6 Address',If_loopback3_ipv6_s)],
				   retry=6,interval=5,waitflag=False,IC=True)
#result
printCheckStep(testname, 'Step 6', res1)

################################################################################
#Step 7
#
#操作
#在AC上另外再配置二个环回接口,其中接口索引号loopback 3> loopback 2> loopback 1,重新启动无线功能
#
#预期
#AC1上show wireless看到'WS IPv6 Address'项已经显示为'If_loopback1_ipv6_s'
################################################################################

printStep(testname,'Step 7',
          'Config other two loopback interfaces on AC1',
          'Check the result')

# operate		  
#配置loopback2
EnterConfigMode(switch1)
SetCmd(switch1,'interface loopback 2')
SetCmd(switch1,'ipv6 address',If_loopback2_ipv6)
IdleAfter(3)

#配置loopback1
EnterConfigMode(switch1)
SetCmd(switch1,'interface loopback 1')
SetCmd(switch1,'ipv6 address',If_loopback1_ipv6)
IdleAfter(3)

EnterWirelessMode(switch1)
SetCmd(switch1,'no enable')
IdleAfter(1)
SetCmd(switch1,'enable')
IdleAfter(10)

#check
EnterEnableMode(switch1)
res1 = CheckSutCmd(switch1,'show wireless',
				   check=[('WS IPv6 Address',If_loopback1_ipv6_s)],
				   retry=5,interval=3,waitflag=False,IC=True)
#result
printCheckStep(testname, 'Step 7', res1)

################################################################################
#Step 8
#
#操作
# 把选定为无线模块IP地址的环回接口down掉
# AC会重新自动选择剩余up的接口索引号最小的接口对应的IPv6地址为无线模块的IPv6地址
#
#预期
#AC1上show wireless看到'WS IPv6 Address'项已经显示为'If_loopback2_ipv6_s'
################################################################################

printStep(testname,'Step 8',
          'Shutdown the loopback interface',
          'Check the result')

# operate		  
EnterConfigMode(switch1)
SetCmd(switch1,'interface loopback 1')
SetCmd(switch1,'shutdown')

#check
EnterEnableMode(switch1)
res1 = CheckSutCmd(switch1,'show wireless',
				   check=[('WS IPv6 Address',If_loopback2_ipv6_s)],
				   retry=6,interval=5,waitflag=False,IC=True)
#result
printCheckStep(testname, 'Step 8', res1)

################################################################################
#Step 9
#
#操作
# 删除以上所有三层接口和环回接口上的IPv6地址
#
#预期
#AC1上show wireless看到'WS IPv6 Address'项已经显示为'-----',
# 'WLAN Switch Disable Reason'显示为'IP address not configured'
################################################################################

printStep(testname,'Step 9',
          'Delete all the ipv6 address on interface',
          'Check the result')

# operate		  
EnterConfigMode(switch1)
SetCmd(switch1,'interface vlan',Vlan10)
SetCmd(switch1,'no ipv6 address',If_vlan10_ipv6)

EnterConfigMode(switch1)
SetCmd(switch1,'interface vlan',Vlan9)
SetCmd(switch1,'no ipv6 address',If_vlan9_ipv6)

EnterConfigMode(switch1)
SetCmd(switch1,'interface vlan',Vlan8)
SetCmd(switch1,'no ipv6 address',If_vlan8_ipv6)

EnterConfigMode(switch1)
SetCmd(switch1,'interface loopback 1')
SetCmd(switch1,'no ipv6 address',If_loopback1_ipv6)

EnterConfigMode(switch1)
SetCmd(switch1,'interface loopback 2')
SetCmd(switch1,'no ipv6 address',If_loopback2_ipv6)

EnterConfigMode(switch1)
SetCmd(switch1,'interface loopback 3')
SetCmd(switch1,'no ipv6 address',If_loopback3_ipv6)
IdleAfter(10)

#check
EnterEnableMode(switch1)
res1 = CheckSutCmd(switch1,'show wireless',
                   check=[('WS IPv6 Address','-----'),
                          ('WLAN Switch Disable Reason','IP address not configured')],
                   retry=5,interval=5,waitflag=False,IC=True)
#result
printCheckStep(testname, 'Step 9', res1)

################################################################################
#Step 10
#
#操作
#恢复默认配置
################################################################################

printStep(testname,'Step 10',
          'Recover initial config')

# operate
#删除以上三层接口、环回接口和Vlan
EnterConfigMode(switch1)
SetCmd(switch1,'no interface vlan',Vlan10)
SetCmd(switch1,'no interface vlan',Vlan9)
SetCmd(switch1,'no interface vlan',Vlan8)
SetCmd(switch1,'no interface loopback 1')
SetCmd(switch1,'no interface loopback 2')
SetCmd(switch1,'no interface loopback 3')
SetCmd(switch1,'no vlan',Vlan10)
SetCmd(switch1,'no vlan',Vlan9)
SetCmd(switch1,'no vlan',Vlan8)

#添加vlan
EnterConfigMode(switch1)
SetCmd(switch1,'interface',s1p1)
SetCmd(switch1,'switchport trunk allowed vlan',Vlan70+';'+Vlan80)

#配置IP
exec(compile(open('clustermanagement\\clustermanagement_unitial(ipv6).py', "rb").read(), 'clustermanagement\\clustermanagement_unitial(ipv6).py', 'exec'))
# EnterConfigMode(switch1)
# SetCmd(switch1,'interface vlan',Vlan70)
# SetCmd(switch1,'ip address',If_vlan70_s1_ipv4)
# SetCmd(switch1,'ipv6 address',If_vlan70_s1_ipv6)
# IdleAfter(3)
# EnterConfigMode(switch1)
# SetCmd(switch1,'interface vlan',Vlan80)
# SetCmd(switch1,'ip address',If_vlan80_s1_ipv4)
# SetCmd(switch1,'ipv6 address',If_vlan80_s1_ipv6)
# IdleAfter(3)
# SetCmd(switch1,'interface loopback 100')
# SetCmd(switch1,'ip address',StaticIpv4_ac1,'255.255.255.255')
# IdleAfter(3)

#关闭无线ip地址自动选择功能
EnterWirelessMode(switch1)
SetCmd(switch1,'no auto-ip-assign')
#end
printTimer(testname, 'End')
