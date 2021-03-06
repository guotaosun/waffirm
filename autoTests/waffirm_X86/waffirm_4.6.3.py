#-*- coding: UTF-8 -*-#
#
#*******************************************************************************
# waffirm_4.6.3.py - test case 4.6.3 of waffirm_new
#
# Author:  ()
#
# Version 1.0.0
#
# Copyright (c) 2004-2011 Digital China Networks Co. Ltd
# 
# Date 2012-12-7 14:37:33
#
# Features:
# 4.6.3	本地转发功能测试1（二层转发）
# 测试目的：测试二层报文的本地转发
# 测试环境：同测试拓扑
# 测试描述：测试二层报文的本地转发
#
#*******************************************************************************
# Change log:
#     - 
#*******************************************************************************

#Package

#Global Definition
staticIpv6_sta1 = '2001:92::100'
staticIpv6_sta2 = '2001:92::200'

#Source files

#Procedure Definition

#Functional Code

testname = 'TestCase 4.6.3'
printTimer(testname,'Start','test L2 switch in local switch mode')

################################################################################
#Step 1
#操作
# 在AC2上开启对AC1的三层发现
# S3上配置 vlan 4092
# 在AC1配置network1的SSID为test1，关联vlan4092，配置下发到AP1
#
#预期
#AP1能够被AC1管理，配置下发成功
################################################################################
printStep(testname,'Step 1',\
          'Set AP1 management vlan-id to vlan 20,and untagged',\
          'Switchport s3p3 to be trunk,native vlan 20')

res1=1

#operate
#在AC2上开启对AC1的三层发现
EnterWirelessMode(switch2)
SetCmd(switch2,'discovery ip-list',StaticIpv4_ac1)  

i_times = 0
while i_times < 30:
    data0 = SetCmd(switch1,'show wireless peer-switch')
    if 0 == CheckLine(data0,StaticIpv4_ac2,'IP Poll',IC=True):
        break   
    i_times += 1
    IdleAfter(5)

EnterNetworkMode(switch1,1)
SetCmd(switch1,'ssid ' + Network_name1)
SetCmd(switch1,'vlan '+ Vlan4092)


#S3 上配置 vlan 4092
EnterConfigMode(switch3)
SetCmd(switch3,'vlan',Vlan4092)

#配置下发到AP1
WirelessApplyProfileWithCheck(switch1,['1'],[ap1mac])
EnterEnableMode(switch1)
data1 = SetCmd(switch1,'show wireless ap status')

#check
res1 = CheckLine(data1,ap1mac,Ap1_ipv4,'Managed','Success',IC=True)
#RDM34910
if res1 != 0:
    for tmpCounter in xrange(0,6):
        IdleAfter('10')
        data1 = SetCmd(switch1,'show wireless ap status')
        res1 = CheckLine(data1,ap1mac,Ap1_ipv4,'Managed','Success',IC=True)
        if res1 == 0:
            break

#result
printCheckStep(testname, 'Step 1',res1)

################################################################################
#Step 2
#操作
#在AC1上面将vlan4092从l2-tunnel vlan-list中删除
#
#预期
#通过show wireless l2-tunnel vlan-list看不到vlan4092
################################################################################

printStep(testname,'Step 2',\
          'Delete vlan 4092 from l2tunnel vlan')

res1=0

#operate

#tunnel vlan中删除 4092
EnterWirelessMode(switch1)
SetCmd(switch1,'l2tunnel vlan-list remove',Vlan4092)

EnterEnableMode(switch1)
data1 = SetCmd(switch1,'show wireless l2tunnel vlan-list')

#check
res1 = CheckLine(data1,Vlan4092)
res1 = 0 if 0 != res1 else 1

#result
printCheckStep(testname, 'Step 2',res1)

################################################################################
#Step 3
#操作
#STA1和STA2连接到网络test1
#
#预期
#关联成功。客户端能够获取192.168.92.X网段的IP地址
################################################################################

printStep(testname,'Step 3',\
          'STA1 and STA2 connect to network test1',\
          'Check if STA1,STA2 can obtain "192.168.92.x" address via dhcp')

res1=res2=res3=res4=-1

sta1_ipv4 = ''
sta2_ipv4 = ''

#operate
#STA1,STA2关联 network1
res1 = WpaConnectWirelessNetwork(sta1,Netcard_sta1,Network_name1,bssid=ap1mac_lower)
res2 = WpaConnectWirelessNetwork(sta2,Netcard_sta2,Network_name1,bssid=ap1mac_lower)
IdleAfter(10)

#获取STA1,STA2的地址
data1 = SetCmd(sta1,'ifconfig -v',Netcard_sta1)
data2 = SetCmd(sta2,'ifconfig -v',Netcard_sta2)
SearchResult1 = re.search('inet.+?(\d+\.\d+\.\d+\.\d+)\s+',data1,re.I)
SearchResult2 = re.search('inet.+?(\d+\.\d+\.\d+\.\d+)\s+',data2,re.I)

#check
if None != SearchResult1:
    sta1_ipv4 = SearchResult1.group(1)
    if None != re.search(Dhcp_pool2,sta1_ipv4):
        printRes('STA1 ip address: ' + sta1_ipv4)
        res3 = 0  
else:
    res3 = 1
    printRes('Failed: Get ipv4 address of STA1 failed') 
    
if None != SearchResult2:
    sta2_ipv4 = SearchResult2.group(1)
    if None != re.search(Dhcp_pool2,sta2_ipv4):
        printRes('STA2 ip address: ' + sta2_ipv4)
        res4 = 0  
else:
    res4 = 1
    printRes('Failed: Get ipv4 address of STA2 failed')

#result
printCheckStep(testname, 'Step 3',res1,res2,res3,res4)

################################################################################
#Step 4
#操作
#STA1 ping STA2
#
#预期
#能够 ping 通
################################################################################
printStep(testname,'Step 4',\
          'STA1 ping STA2')

res1=1

#operate
res1 = CheckPing(sta1,sta2_ipv4,mode='linux')

#check

#result
printCheckStep(testname,'Step 4',res1)

################################################################################
#Step 5
#操作
# AC2上在ap profile 2模式下配置,
# management vlan 30
# ethernet native-vlan 30
# AP2上配置：
#set management vlan-id 30
#set untagged-vlan vlan-id 30
#AC1删除对AP2自动发现
#配置AC2管理AP2，重启AP2
#AC2 从tunnel vlan中删除 4092
#配置s3p4,s3p1为Trunk 口, native vlan 30
#配置s2p1为Trunk 口, native vlan 30
#配置下发到AP2
#
#预期
#AP2能够被AC2管理，配置下发成功
################################################################################
printStep(testname,'Step 5',\
          'Set AP2 management vlan-id to vlan 30,and untagged',\
          'Switchport s3p4 to be trunk,native vlan 30')

res1=res2=1
# !!!!!!!!!!!!!!!!!如果要是AC2能够管理AP2那么 有两种方法，AC1上自动部署，或者在
#!!!!!!!!!!!!!!!!!!AP2上直接配置，采用后者

#operate
EnterWirelessMode(switch2)
EnterApProMode(switch2,'2')
SetCmd(switch2,'management vlan',Vlan30)
SetCmd(switch2,'ethernet native-vlan 30')
SetCmd(ap2,'set management vlan-id',Vlan30)
SetCmd(ap2,'set untagged-vlan vlan-id',Vlan30)

#AC1删除对AP2自动发现
EnterWirelessMode(switch1)
SetCmd(switch1,'no','discovery ip-list',Ap2_ipv4)
SetCmd(switch1,'no','discovery ipv6-list',Ap2_ipv6)

#配置AC2管理AP2，重启AP2
SetCmd(ap2,'set managed-ap switch-address-1',StaticIpv4_ac2)
SetCmd(ap2,'save-running')
RebootAp('AP',AP=ap2)

#AC2 从tunnel vlan中删除 4092
EnterWirelessMode(switch2)
SetCmd(switch2,'l2tunnel vlan-list remove',Vlan4092)

#配置s3p4,s3p2为Trunk 口,native vlan
EnterInterfaceMode(switch3,s3p4)
SetCmd(switch3,'switchport mode trunk')
SetCmd(switch3,'switchport trunk native vlan',Vlan30)
EnterInterfaceMode(switch3,s3p2)
SetCmd(switch3,'switchport mode trunk')
SetCmd(switch3,'switchport trunk native vlan',Vlan30)

#配置s2p1为Trunk 口,native vlan
EnterInterfaceMode(switch2,s2p1)
SetCmd(switch2,'switchport mode trunk')
SetCmd(switch2,'switchport trunk native vlan',Vlan30)
WirelessApplyProfileWithCheck(switch2,['2'],[ap2mac])
# WirelessApProfileApply(switch2,'2')

# IdleAfter(Ac_ap_syn_time)
# IdleAfter(100)
EnterEnableMode(switch2)
data1 = SetCmd(switch2,'show wireless ap status')

#check
res1 = CheckLine(data1,ap2mac,Ap2_ipv4,'Managed','Success',IC=True)
res2 = CheckNoLineList(data1,[('\*'+ap2mac,Ap2_ipv4,'Managed','Success')],IC=True)
#RDM34910
if res1 != 0:
    for tmpCounter in xrange(0,6):
        IdleAfter('10')
        data1 = SetCmd(switch2,'show wireless ap status')
        res1 = CheckLine(data1,ap2mac,Ap2_ipv4,'Managed','Success',IC=True)
        if res1 == 0:
            break
    res2 = CheckNoLineList(data1,[('\*'+ap2mac,Ap2_ipv4,'Managed','Success')],IC=True)

#result
printCheckStep(testname, 'Step 5',res1,res2)

################################################################################
#Step 6
#操作
#客户端STA2连接到网络test2
#
#预期
#关联成功，STA2能够获取192.168.92.X网段的IP地址
################################################################################
printStep(testname,'Step 6',\
          'STA2 connect to network test2',\
          'Check if STA2 can obtain "192.168.92.x" address via dhcp')

res1=res2=-1

sta2_ipv4 = ''

#operate
#STA2关联 network1
res1 = WpaConnectWirelessNetwork(sta2,Netcard_sta2,Network_name2,bssid=ap2mac_type1_network2)
IdleAfter(10)

#获取STA1,STA2的地址
data1 = SetCmd(sta2,'ifconfig -v',Netcard_sta2)
SearchResult = re.search('inet.+?(\d+\.\d+\.\d+\.\d+)\s+',data1,re.I)

#check
if None != SearchResult:
    sta2_ipv4 = SearchResult.group(1)
    if None != re.search(Dhcp_pool2,sta2_ipv4):
        printRes('STA2 ip address: ' + sta2_ipv4)
        res2 = 0  
else:
    res2 = 1
    printRes('Failed: Get ipv4 address of STA2 failed') 

#result
printCheckStep(testname, 'Step 6',res1,res2)

################################################################################
#Step 7
#操作
#用STA1的ipv4地址ping STA2的ipv4地址
#
#预期
#能够ping通
################################################################################

printStep(testname,'Step 7',\
          'STA1 ping STA2 via ipv4 and ipv6')

res1=res2=res3=res4=-1

#operate

#手动配置STA1，STA2 ipv6 地址
SetCmd(sta1,'\x03')
SetCmd(sta1,'ifconfig '+ Netcard_sta1 + ' inet6 add',staticIpv6_sta1 + '/64')
SetCmd(sta2,'\x03')
SetCmd(sta2,'ifconfig '+ Netcard_sta2 + ' inet6 add',staticIpv6_sta2 + '/64')

#ping,ping6
res1 = CheckPing(sta1,sta2_ipv4,mode='linux')
CheckPing(sta2,sta1_ipv4,mode='linux')
SetCmd(sta1,'ping6',staticIpv6_sta2,promotePatten = 'PING',promoteTimeout=10)
IdleAfter(15)
data0 = SetCmd(sta1,'\x03',timeout = 1)

#查看表项
IdleAfter(10)
EnterEnableMode(switch1)
data3 = SetCmd(switch1,'show mac-address-table')
data4 = SetCmd(switch1,'show arp')

#check
res2 = int(str(GetValueBetweenTwoValuesInData(data0,'transmitted,','received')).strip()) 
res2 = 0 if res2 > 0 else 1
res3 = CheckLineList(data3,[(sta1mac),(sta2mac)],IC=True)             
res4 = CheckLineList(data4,[(sta1_ipv4,sta1mac),(sta2_ipv4,sta2mac)],IC=True)                   
#check

#result
printCheckStep(testname,'Step 7',res1)

################################################################################
#Step 8
#操作
#恢复默认配置
################################################################################
printStep(testname,'Step 8',\
          'Recover initial config')
#operate

#AC2关闭对AC1 的发现
EnterWirelessMode(switch2)
SetCmd(switch2,'no','discovery ip-list',StaticIpv4_ac1)

#解关联
WpaDisconnectWirelessNetwork(sta1,Netcard_sta1)
WpaDisconnectWirelessNetwork(sta2,Netcard_sta2)
    
#删除手工配置ipv6 地址
SetCmd(sta1,'\x03')                                                                                                    
SetCmd(sta1,'ifconfig '+ Netcard_sta1 + ' inet6 del',staticIpv6_sta1 + '/64')
SetCmd(sta2,'\x03')
SetCmd(sta2,'ifconfig '+ Netcard_sta2 + ' inet6 del',staticIpv6_sta2 + '/64')

#删除dhcp binding,arp,mac-address-table,ipv6 neighbors信息
EnterEnableMode(switch1)
SetCmd(switch1,'clear ip dhcp binding all')
SetCmd(switch1,'clear arp traffic')
SetCmd(switch1,'clear mac-address-table dynamic')
SetCmd(switch1,'clear ipv6 neighbors')

#清除management vlan 配置
EnterWirelessMode(switch1)
EnterApProMode(switch1,'1')
SetCmd(switch1,'no','management vlan')
SetCmd(switch1,'ethernet native-vlan 1')
SetCmd(ap1,'set management vlan-id',1)
SetCmd(ap1,'set untagged-vlan vlan-id',1)
EnterWirelessMode(switch2)
EnterApProMode(switch2,'2')
SetCmd(switch2,'no','management vlan')
SetCmd(switch2,'ethernet native-vlan 1')
SetCmd(ap2,'set management vlan-id',1)
SetCmd(ap2,'set untagged-vlan vlan-id',1)

#tunnel vlan中添加 4092
EnterWirelessMode(switch1)
SetCmd(switch1,'l2tunnel vlan-list add',Vlan4092)
#tunnel vlan中添加 4092
EnterWirelessMode(switch2)
SetCmd(switch2,'l2tunnel vlan-list add',Vlan4092)

#恢复拓扑配置
#AC1
EnterNetworkMode(switch1,'1')
SetCmd(switch1,'ssid ' + Network_name1)
SetCmd(switch1,'vlan ' + Vlan4091)
EnterInterfaceMode(switch1,s1p1)
SetCmd(switch1,'no switchport mode')
SetCmd(switch1,'switchport access vlan',Vlan40)

#AC2
EnterInterfaceMode(switch2,s2p1)
SetCmd(switch2,'no switchport mode')
SetCmd(switch2,'switchport access vlan',Vlan30)

#S3
#S3 上删除 vlan 4092
EnterConfigMode(switch3)
SetCmd(switch3,'no','vlan',Vlan4092)

#配置下发到AP1
WirelessApProfileApply(switch1,'1')
    
#AC1添加对AP2的三层发现
EnterWirelessMode(switch1)
SetCmd(switch1,'discovery ip-list',Ap2_ipv4)
SetCmd(switch1,'discovery ipv6-list',Ap2_ipv6)

#配置AC2管理AP2，重启AP2
SetCmd(ap2,'set managed-ap switch-address-1')
SetCmd(ap2,'save-running')
RebootAp('AP',AP=ap2)

SetCmd(switch1,'end')
SetCmd(switch2,'end')
SetCmd(switch3,'end')
    
#end
printTimer(testname, 'End')