#-*- coding: UTF-8 -*-#
#
#*******************************************************************************
# 802.11I_2.1.7.py
#
# Author:  zhangjxp@digitalchina.com
#
# Version 1.0.0
#
# Copyright (c) 2004-2020 Digital China Networks Co. Ltd
#
# Features:
# 2.1.7 需要radius配合的认证，AP认证消息封装
# 测试描述：当客户端进行需要radius配合的认证时，AP会将认证消息封装到radius-proxy-command消息中发送给UWS
#*******************************************************************************
# Change log:
#     - created by zhangjxp 2018.2.1
#*******************************************************************************

#Package

#Global Definition

#Source files

#Procedure Definition 

#Functional Code

testname = 'TestCase 802.11I_2.1.7'
avoiderror(testname)
printTimer(testname,'Start','Test client-auth packet')

################################################################################
#Step 1
#操作
#配置AC1的network1的安全接入方式为WPA-Enterprise，WPA version为WPA，认证服务器使用wlan：
#Wireless
#Network 1
#security mode wpa-enterprise
#wpa versions wpa
#radius server-name acct wlan
#radius server-name auth wlan
#
#配置成功。在AC1上面show wireless network 1可以看到相关的配置。
################################################################################
printStep(testname,'Step 1',\
          'set security mde of network 1 wpa-enterprise,',\
          'set wpa versions wpa,',\
          'set radius server-name acct wlan,',\
          'set radius setver-name auth wlan,',\
          'and u should config others and so on,',\
          'check config success.')
#operate
#配置network模式下的radius配置参数
EnterNetworkMode(switch1,1)
SetCmd(switch1,'security mode wpa-enterprise')
SetCmd(switch1,'wpa ciphers TKIP')
SetCmd(switch1,'wpa versions wpa')
SetCmd(switch1,'radius server-name auth wlan')
SetCmd(switch1,'radius server-name acct wlan')
SetCmd(switch1,'radius accounting')
WirelessApplyProfileWithCheck(switch1,['1'],[ap1mac])
#check
data1 = SetCmd(switch1,'show wireless network 1',timeout=10)
res1 = CheckLine(data1,'Security Mode','WPA Enterprise')
res2 = CheckLine(data1,'RADIUS Authentication Server Name','wlan')
res3 = CheckLine(data1,'RADIUS Accounting Server Name','wlan')
res4 = CheckLine(data1,'WPA Versions','WPA2')
res5 = CheckLine(data1,'WPA Versions','WPA')
res4 = 0 if res4 != 0 else -1
#result
printCheckStep(testname, 'Step 1',res1,res2,res3,res4,res5)

################################################################################
#Step 2
#操作
# AC开启debug wireless client-auth packet receive ap1mac
#设置STA1无线网卡的属性为WPA-Enterprise认证，关联网络test1，使用在Radius服务器配置的用户名和密码。
# 预期
#成功关联，并获取192.168.91.X网段的IP地址。Show wireless client summery
#可以看到STA1（“MAC Address”显示“STA1MAC”），IP地址的网段正确。
# AC上可以看到sta1认证成功的报文
################################################################################
printStep(testname,'Step 2',\
          'debug wireless client-auth packet receive ap1mac on AC1',\
          'STA1 connect to network 1,',\
          'connect success.'
          'client auth packet can be seen on AC1')
res1=res2=res3=1
EnterEnableMode(switch1)
SetCmd(switch1,'debug wireless client-auth packet receive',ap1mac)
StartDebug(switch1)
res1 = WpaConnectWirelessNetwork(sta1,Netcard_sta1,Network_name1,connectType='custom',
                                key_mgmt='WPA-EAP',proto='WPA',pairwise='TKIP',group='TKIP',
                                eap='PEAP',identity=Dot1x_identity,password=Dot1x_password,
                                checkDhcpAddress=Netcard_ipaddress_check,bssid=ap1mac_type1)
IdleAfter(10)
EnterEnableMode(switch1)
SetCmd(switch1,'no debug all')
data=StopDebug(switch1)
if CheckLine(data,'WIRELESS_AUTH_RADIUS_PROXY_COMMAND_MSG_PKT',IC=True) == 0:
    res2 = 0
if res1 == 0:
    res3 = CheckWirelessClientOnline(switch1,sta1mac,'online')

# results
printCheckStep(testname, 'Step 2',res1,res2,res3)

################################################################################
#Step 3
#操作
#恢复默认配置
################################################################################
printStep(testname,'Step 3',\
          'Recover initial config for switches.')

#operate
# sta1解关联
WpaDisconnectWirelessNetwork(sta1,Netcard_sta1)
CheckWirelessClientOnline(switch1,sta1mac,'offline',retry=20)

# 恢复network1配置
ClearNetworkConfig(switch1,1)
EnterNetworkMode(switch1,1)
SetCmd(switch1,'ssid ' + Network_name1)
SetCmd(switch1,'vlan ' + Vlan4091)
WirelessApplyProfileWithCheck(switch1,['1'],[ap1mac])

#end
printTimer(testname, 'End')