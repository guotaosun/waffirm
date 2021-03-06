#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# *********************************************************************
# BasicConfiguration.py - Proc of Basic Management
# 
# Author:caisy(caisy@digitalchina.com)
#
# Version 2.0.0
#
# Copyright (c) 2004-9999 Digital China Networks Co. Ltd 
#
# 
# *********************************************************************
# Change log:
#     - 2011.8.31  modified by caisy
#     - 2017.5.16 lupingc RDM49103
#     - 2017.3.14 modified by lupingc RDM48868
#     - lupingc RDM49074 2017.5.17
#     - 2017.10.12 modified by zhangjxp RDM50134
#                  (修改函数WpaConnectWirelessNetwork为WpaConnectWirelessNetworkold，
#                  新增函数RebootStaNetcard、WpaConnectWirelessNetwork。
#                  实现sta网卡关联不上wifi时，卸载再加载网卡驱动，重新关联wifi；
#                  修改函数avoiderror，增加对ap是否处于bootloader模式下的检测；
#                  新增函数GetApMac、GetAcType、ApLogin、GetStaMac、GetStaIp、GetSwitchTime、
#                  CheckSutCmd、SshLogin、ClearNetworkConfig、ClearProfileConfig）
#     - 2017.11.10 modified by zhangjxp
#                  RDM50304 增加函数ChangeAPMode
#                  RDM50321 优化函数TelnetLogin，ApLogin，RebootAp
#     -2017.12.4 modified by zhangjxp 
#                RDM50486 新增函数ChangeAPMode、ApSetcmd、Get_ap_cmdtype
#                RDM50487 新增函数Get_apversion_fromac
#     -2017.12.13 modified by zhangjxp
#                 新增函数Get_switch_version、Get_ap_version、Get_ap_hwtype
#     -2017.12.18 modified by yanwh
#                 修改函数setcmd apsetcmd getapcmdtype
#    - 2017.12.19 modified by zhangjxp
#                 优化函数TelnetLogin
#                 RDM50633 优化函数RebootAp
#    - 2017.12.28 modified by zhangjxp 新增函数Check_ap_dhcpstatus
#                 修改函数WirelessApplyProfileWithCheck，适配任意个数AP
#    - 2018.1.8 modified by zhangjxp 优化函数WirelessApplyProfileWithCheck,telnetlogin
#    - 2018.3.12 modified by zhangjxp 修复函数WpaConnectWirelessNetworkold存在的bug，
#               优化函数ReloadMultiSwitch，WirelessApplyProfileWithCheck，ApSetcmd，
#               Check_ap_dhcpstatus，新增函数Check_ap_ip,Check_ap_provision_switchip,Check_ap_static_switchip,
#                Check_ap_automatic_switchip,Check_ap_dnsserver_ip
# *********************************************************************

from .BasicCheck import *
from .dcn_pprint import DcnPrettyPrint as pp
from dutils.dcnprint import *
from .dreceiver import *



####################################
#
# EnterEnableMode:
#
# args:
#     sut:  被测设备
#
# return: NULL
#
# addition:  
# 
# examples:
#     EnterEnableMode('s1')
#           
####################################
def EnterEnableMode(sut, noMore=False):
    res = SetCmd(sut, "\x03", newLine=False, promoteStop=True)
    if res.find('>'):
        SetCmd(sut, "enable")
        if noMore:
            SetCmd(sut, 'terminal length 0')
            IdleAfter(0.5)


####################################
#
# EnterConfigMode:
#
# args:
#     sut:    ���
#
# return:  NULL
#
# addition:
# 
# examples:
#     EnterConfigMode('s1')
#           
####################################
def EnterConfigMode(sut):
    EnterEnableMode(sut)
    SetCmd(sut, "config")


####################################
#
# EnterInterfaceMode:
#
# args:
#     sut:    ���
#     interface:�ӿ�
#
# return:  NULL
#
# examples:
#     EnterInterfaceMode('s1','Ethernet1/1')
#     EnterInterfaceMode('s1','Vlan1')
#      
####################################
def EnterInterfaceMode(sut, interface):
    EnterConfigMode(sut)
    SetCmd(sut, "interface " + str(interface))


#####################################
# EnterVlanMode :
#
# args :
#    sut : ������
#    vid : vlan id ��
#
# return :NULL
#
# addition:
#
# examples:
#
#    EnterVlanMode('s1',10)
#####################################
def EnterVlanMode(sut, vid):
    EnterConfigMode(sut)
    SetCmd(sut, "vlan " + str(vid))


#####################################
# EnterModes :
#
# args :
#      sut : ������
#      *modes: 
#
# return :NULL
#
# addition:
#
# examples:
#
#    EnterModes('s1','mode1','mode2','mode3',...)
#    EnterModes('s1','config','interface vlan 1')
#####################################
def EnterModes(sut, *args):
    for i in args:
        SetCmd(sut, str(i))


#####################################
# Exit :
#
# args :
#      sut : ������
#      *modes: 
#
# return :NULL
#
# addition:
#
# examples:
#
#    Exit('s1',1)
#    Exit('s1',2)
#####################################
def Exit(sut, times=1):
    for i in range(int(times)):
        SetCmd(sut, 'exit')


#####################################
# SetTerminalLength :
#
# args :
#      sut : ������
#      *modes: 
#
# return :NULL
#
# addition:
#
# examples:
#
#    SetTerminalLength('s1')
#    SetTerminalLength('s1',20)
#####################################
def SetTerminalLength(sut, length=0):
    EnterEnableMode(sut)
    SetCmd(sut, 'terminal length ' + str(length))


############################
#
# Reload :设备重启
# args:
#     sut :被测设备
#
# return: no return 
#
# addition:
#
#
# examples:
#     Reload('s1')
#     Reload('s1',nowrite=True)
############################
def Reload(sut, **flag):
    printMore = False
    for j in list(flag.keys()):
        if j == 'PrintMore':
            printMore = flag[j]
    if 'nowrite' in flag:
        pass
    else:
        Receiver(sut, 'write')
        time.sleep(1)
        Receiver(sut, 'y')
        time.sleep(5)
    Receiver(sut, 'reload')
    time.sleep(1)
    Receiver(sut, 'y')
    time.sleep(180)
    Receiver(sut, '\n', 0.1)
    Receiver(sut, '\n', 0.1)
    Receiver(sut, '\n', 0.1)
    Receiver(sut, '\n', 0.1)
    EnterEnableMode(sut)
    if not printMore:
        Receiver(sut, 'terminal length 0')


#####################################
# SetDefault :
#
# args :
#      sut : ������
#
# return :string
#
# addition:
#
# examples:
#
#    SetDefault('s1')
#####################################
def SetDefault(sut, timeout=0.1):
    EnterEnableMode(sut)
    Receiver(sut, 'set default', 0.3)
    Receiver(sut, 'y', timeout)


#####################################
# SetCmd :
#
# args :
#      sut : 
#      *arg: 命令
#      **args: 可选参数
#              包括: timeout           等待时间
#                    promoteStop       是否进行特殊字符匹配
#                    promotePatten     特殊字符匹配内容
#                    promoteTimeout    特殊字符匹配超时时间
#                    newLine           输入命令后是否回车
#
# return :string
#
# addition:
#            默认promoteStop = True
#            timeout优先权大于promoteStop
#            promoteTimeout默认5分钟
# examples:
#
#      res = SetCmd('s1','show run')
#      SetCmd('s1', 'show run', timeout = 5)
#      SetCmd('s1', 'write', 'boot.rom /f',  promotePatten = 'write ok')
#      SetCmd('s1','sh ru', promotePatten = 'I')
#####################################
def SetCmd(sut, *arg, **args):
    cmd = JoinCmd(*arg)
    promoteFlag = True
    if 'promoteStop' in args:
        promoteFlag = args['promoteStop']
        del args['promoteStop']
    return Receiver(sut, cmd, promoteStop=promoteFlag, **args)


#####################################
# JoinCmd :
#
# args :
#      cmd : ������
#      *arg: 
#
# return :string
#
# addition:
#
# examples:
#
#    JoinCmd('port-group','1')
#    return :'port-group 1'
#####################################
def JoinCmd(*arg):
    joinstr = ' '
    reslist = []
    for i in arg:
        reslist.append(str(i))
    return joinstr.join(reslist)


#####################################
# GetPorts :
#
# args :  ������
#    *arg: 
#
# return :string
#
# addition:
#
# examples:
#
#    GetPorts('ethernet1/1','ethernet1/2','ethernet1/10','ethernet1/11')
#    return :'ethernet1/1;2;10;11'
#####################################
def GetPorts(*arg):
    flag = 0
    head = ''
    for i in arg:
        if flag == 0:
            head = i
            flag = 1
        else:
            strTail = re.search('/(.*)', i)
            if strTail is not None:
                head += ';' + strTail.group(1)
            else:
                print('Argument ' + i + ' format inlegal')
    return head


#####################################
# SetIpAddress :
#
# args : ����
#      sut: 
#      ip: 
#      mask: 
#
# addition:
#
# examples:
#
#    SetIpAddress('s1','100.1.1.2','255.255.255.0')
#####################################
def SetIpAddress(sut, ip, mask):
    SetCmd(sut, 'Ip address ' + str(ip) + ' ' + str(mask))


#####################################
# GetVlanMac :
#
# args : ���
#      sut: 
#
# addition:
#
# return :vlan mac
#
# examples:
#
#      GetVlanMac('s1')
#      return: '00-03-0f-00-11-22'
#####################################
def GetVlanMac(sut):
    data = SetCmd(sut, 'show mac-address-table')
    match = re.search('\d+\s+([a-f\d-]+)\s+STATIC\s+System\s+CPU', data)
    if match != None:
        match = match.group(1)
        # print str(sut), 'vlanmac is', match
    return match


#####################################
# GetCpuMac :
#
# args : ����
#    sut: 
#
# addition:
#
# return :cpu mac
#
# examples:
#
#    GetCpuMac('s1','Ethernet1/1')
#      return: '00-03-0f-00-11-23'
#####################################
def GetCpuMac(sut, port):
    data = SetCmd(sut, 'show interface ' + port)
    match = re.search('address\s+is\s+([a-f\d-]+)', data)
    if match != None:
        match = match.group(1)
    return match


#####################################
# SetExecTimeout :
#
# args : �����
#      sut: 
#      timeout: 
#
# addition:
#
#
# examples:
#
#    SetExecTimeout('s1')
#####################################
def SetExecTimeout(sut, timeout=0):
    EnterConfigMode(sut)
    SetCmd(sut, 'exec-timeout ' + str(timeout))


#####################################
# SetWatchdogDisable :
#
# args : �����
#      sut: 
#
# addition:
#
# examples:
#
#      SetWatchdogDisable('s1')
#####################################
def SetWatchdogDisable(sut):
    EnterConfigMode(sut)
    SetCmd(sut, 'watchdog disable')


#####################################
# ShowVersion :
#
# args : ����
#      sut: 
#
# addition:
#
# return :show version imformation
#
# examples:
#
#      ShowVersion('s1')
#
#      return:
#      Switch Device, Compiled on Apr 28 11:59:28 2011
#      SoftWare Version 6.2.111.0
#      BootRom Version 4.1.0
#      HardWare Version 1.0.1
#      CPLD Version N/A
#      Device serial number N000000004
#      Copyright (C) 2001-2009 by Vendor
#      All rights reserved
#      Last reboot is warm reset.
#      Uptime is 0 weeks, 5 days, 22 hours, 45 minutes
#####################################
def ShowVersion(sut):
    EnterEnableMode(sut)
    res = Receiver(sut, 'show version', promoteStop=True)
    return res


#####################################
# ShowRun :
#
# args : ���
#      sut: 
#
# addition:
#
# return :show run imformation
#
# examples:
#
#      ShowRun('s1')
#####################################
def ShowRun(sut):
    EnterEnableMode(sut)
    res = Receiver(sut, 'show running-config', promoteStop=True)
    return res


########################################
#
# EnterBootRomModeFromImg:
#
# args:
#     sut:  
#
# return:  string:  bootrom imformation
#          -1: fail
#
# addition:
# 
# examples:
#     EnterBootRomModeFromImg('s1')
#           
########################################

def EnterBootRomModeFromImg(sut):
    EnterEnableMode(sut)
    Receiver(sut, 'reload')
    time.sleep(1)
    res = Receiver(sut, 'y', 0, promoteStop=True, promotePatten='Testing RAM')
    if re.search('Testing RAM', res) is not None:
        res = Receiver(sut, '\x02', 0, promoteStop=True, promotePatten='Creation date')
        if re.search('Attaching', res) is not None:
            Receiver(sut, '\n')
            Receiver(sut, '\n')
            Receiver(sut, '\n')
            Receiver(sut, '\n')
            IdleAfter(1)
            return res
        else:
            return -1
    else:
        return -1


########################################
#
# EnterBootRomModeFromBoot:
#
# args:
#     sut:  
#
# return:  string:  bootrom imformation
#          -1: fail
#
# addition:
# 
# examples:
#     EnterBootRomModeFromBoot('s1')
#           
########################################

def EnterBootRomModeFromBoot(sut):
    res = Receiver(sut, 'reboot', 0, promoteStop=True, promotePatten='Testing RAM')
    if re.search('Testing RAM', res) is not None:
        res = Receiver(sut, '\x02', 0, promoteStop=True, promotePatten='Creation date')
        if re.search('Attaching', res) is not None:
            Receiver(sut, '\n')
            Receiver(sut, '\n')
            Receiver(sut, '\n')
            Receiver(sut, '\n')
            IdleAfter(1)
            return res
        else:
            return -1
    else:
        return -1


########################################
#
# IdleAfter:
#
# args:
#     time:second 
#
# return:  None
#
# addition:
# 
# examples:
#     IdleAfter('1')
#           
########################################

def IdleAfter(strSecond, printflag=True, msg=''):
    """
    1 脚本等待strSecond 2 打印友好的提示信息
    ---[Message:Reboot Device]---
    Please Wait In Idle After 3 Seconds
    :param strSecond: 等待时间
    :param printflag: 是否打印提示信息
    :param msg: 格式头部的提示信息
    :return: None
    """
    if printflag:
        first_msg = '{decorate}[Message:{msg}]{decorate}\n'.format(decorate='-' * 3, msg=msg) if msg else ''
        last_msg = '{} Seconds'.format(strSecond) if strSecond > 1 else '{} Second'.format(strSecond)
        mid_msg = '请等待 '
        final_msg = first_msg + mid_msg + last_msg
        printRes(final_msg)
        # if strSecond > 1:
        #     printRes('[Message{msg}]Please Wait In Idle After ' + str(strSecond) + ' Seconds')
        # else:
        #     printRes('[Message{msg}]Please Wait In Idle After ' + str(strSecond) + ' Second')
    time.sleep(int(strSecond))


#####################################
# add by wangyinb 2012-02-09
# EnterWirelessMode :
#
# args :
#    sut : ������
#
# return :NULL
#
# addition:
#
# examples:
#
#    EnterVlanMode('s1')
#####################################
def EnterWirelessMode(sut):
    EnterConfigMode(sut)
    SetCmd(sut, "wireless")


#####################################
# add by wangyinb 2012-02-09
# EnterApProMode :
#
# args :
#    sut : ������
#    proid: the id of ap profile
# return :NULL
#
# addition:
#
# examples:
#
#    EnterApProMode('s1',1)
#####################################
def EnterApProMode(sut, proid):
    EnterWirelessMode(sut)
    SetCmd(sut, "ap profile " + str(proid))


#####################################
# add by wangyinb 2012-02-09
# EnterNetworkMode :
#
# args :
#    sut : ������
#    netid : the id of network
# return :NULL
#
# addition:
#
# examples:
#
#    EnterNetworkMode('s1',1)
#####################################
def EnterNetworkMode(sut, netid):
    EnterWirelessMode(sut)
    SetCmd(sut, "network " + str(netid))


#########################################
# CheckPing
#
#
# args: 
#     switch:要ping的设备标签名
#     ipadd:需要ping的目的ip地址
#     mode:交换机所处的模式，默认为img 模式（由于bootrom和img模式下交换机ping之后的返回结果不同，需采取不同的取值方式）     
#     time:ping操作的时间
#     returnPercent:返回ping的成功率0-100，默认False
#     pingPara:添加ping的其他参数  默认无
# return: 
#       1 :失败
#       0 :ping成功
#
# addition:
#
# examples:
#     CheckPing(switch5,'172.16.1.2')
#     CheckPing(switch5,'172.16.1.2',mode='img',time=10,returnPercent=False,pingPara='')
#
##########################################
def CheckPing(switch, ipadd, mode='img', time=10, returnPercent=False, pingPara='', srcip='', retry=2):
    if mode == 'img':
        EnterEnableMode(switch)
        StartDebug(switch)
        if srcip == '':
            SetCmd(switch, 'ping', ipadd, pingPara, timeout=time)
        else:
            SetCmd(switch, 'ping src ', srcip, ipadd, pingPara, timeout=time)
        SetCmd(switch, "\x03", promoteStop=False, timeout=1)
        data = StopDebug(switch)
        res1 = int(GetValueBetweenTwoValuesInData(data, "Success rate is ", " percent").strip())
        if not returnPercent:
            if res1 > 0:
                return 0
            else:
                return 1
        else:
            return res1
    elif mode == 'boot':
        data = SetCmd(switch, 'ping', ipadd, pingPara, timeout=time)
        if CheckLine(data, 'no answer from') == 0:
            return 1
        else:
            res1 = int(GetValueBetweenTwoValuesInData(data, "transmitted, ", " packets ").strip())
            if res1 > 0:
                return 0
            else:
                return 1
    elif mode == 'linux':
        # modified by lupingc 2017.5.16
        for i in range(retry):
            StartDebug(switch)
            if pingPara == '' and srcip == '':
                SetCmd(switch, 'ping', ipadd, ' -c 5', timeout=time)
            elif pingPara != '' and srcip == '':
                SetCmd(switch, 'ping', ipadd, pingPara, timeout=time)
            elif pingPara == '' and srcip != '':
                SetCmd(switch, 'ping -I', srcip, ipadd, timeout=time)
            else:
                SetCmd(switch, 'ping -I', srcip, ipadd, pingPara, timeout=time)
            SetCmd(switch, "\x03", promoteStop=False, timeout=1)
            data = StopDebug(switch)
            res1 = re.search("(\d+)% packet loss", data)
            if res1:
                res = res1.group(1)
                if not returnPercent:
                    if int(res) < 100:
                        res = 0
                    else:
                        res = 1
                else:
                    res = 100 - int(res)
                    return res
            else:
                res = 1
            if res == 0:
                break
        return res
    else:
        printRes("Parameter <mode> error!")
        return 1


#########################################
# TelnetLogin
#
#
# args: 
#     switch:要ping的设备标签名
#     username:用户名
#     password:密码
# return: 
#       1 :失败
#       0 :成功
#
# addition:
#
# examples:
#     TelnetLogin(switch1,'root','123456')
#
##########################################
def TelnetLogin(switch, username, password):
    # import wx
    # tn = wx.FindWindowByName(str(switch)).conn.telnet
    # # def read_some():
    # #     while 1:
    # #         r = tn.read_some()
    # #         if any(x in r for x in ['#', '>', 'login', 'password', 'Password']):
    # #             return r
    #
    # tn.sock.sendall(os.linesep)
    # while 1:
    #     r = read_some()
    #     if '#' in r:
    #         return 1
    #     elif 'login:' in r:
    #         tn.sock.sendall(username+os.linesep)
    #     elif 'Password:' in r:
    #         tn.sock.sendall(password)
    #         tn.sock.sendall(os.linesep)
    #     elif 'Last login|Enter \'help\' for' in r:
    #         return 1

    IdleAfter(2, printflag=False)
    for iTime in range(3):
        res = SetCmd(switch, username, promotePatten='Password|password|login|Login|#', promoteTimeout=30)
        if re.search('#', res):
            return 0
        elif re.search('login:\s+' + username, res) or re.search('Password|password', res):
            data = SetCmd(switch, password, promotePatten='Last login|Enter \'help\' for', promoteTimeout=15)
            if re.search('Last login|Enter \'help\' for', data, re.I):
                break
        elif re.search('login:\s+', res):
            pass
    for iTime in range(5):
        StartDebug(switch)
        SetCmd(switch, '\n', timeout=1)
        res = StopDebug(switch)
        if re.search('>|#|\$', res):
            return 0
        else:
            IdleAfter(10)


#########################################
# GetMibPortIndex
# 
# function:
#     SNMP查询mib时，交换机端口的索引值；
#     如盒式机 "ethernet1/20",索引值为 20
#       机架式 "ethernet5/1",索引值为 385
# args: 
#     Port: 要查询的交换机端口 如:s1p1='ethernet5/1'
#     switchtype: 交换机类型, 1 机架式, 0 盒式，默认为机架式
# return: 
#       失败 ：1
#       成功 ：端口的索引值
#
# addition:
#
# examples:
#     GetMibPortIndex(s1p1)
#     GetMibPortIndex(s1p2,0)
#
##########################################

def GetMibPortIndex(Port, switchtype=1):
    if 0 != CheckLine(Port, 'ethernet', IC=True):
        printRes('Parameter wrong: The first parameter should be a port')
        return 1
    if (0 != switchtype) and (1 != switchtype):
        printRes('Parameter wrong: The second parameter should be Integer 1 or 0')
        return 1

    PortNum = re.search('.*/(\d+)', Port)
    if PortNum:
        # 如果是盒式交换机
        if switchtype == 0:
            portIndex = PortNum.group(1)
            if int(portIndex) > 0:
                return portIndex
            else:
                printRes('Fail, Get portIndex not right: ' + portIndex)
                return 1

                # 如果是机架式设备,port的index值，对于机架交换机，为每个slot预留了64个端口号，
        # 因此，如果线卡在slot4，则该线卡的第一个端口index为4*64+1=193
        if switchtype == 1:
            SlotNum = re.search('Ethernet(\d+)/\d+', Port, re.I)
            if SlotNum:
                SlotIndex = SlotNum.group(1)
                if int(SlotIndex) > 4:
                    SlotIndex = str(int(SlotIndex) + 2)
                portIndex = str(int(PortNum.group(1)) + (int(SlotIndex) - 1) * 64)
                return portIndex
            else:
                printRes('Fail: slot ID match wrong')
                return 1
    else:
        printRes('Fail: port Num match wrong')
        return 1


#########################################
# StaScanSSID
# 
# function:
#     调用linux 下wpa_supplicat 扫描ssid，并处理异常
# args: 
#     sta：用于扫描的linux
#     NetcardName: sta 的无线网卡名称，如 "wlan0"

# return: 
#
# addition:
#
# examples:
#     StaScanSSID(sta2,'wlan0')
##########################################
def StaScanSSID(sta, netcardName):
    data = SetCmd(sta, 'wpa_cli -i ' + netcardName + ' scan')
    if 0 != CheckLine(data, 'OK'):
        SetCmd(sta, 'rmmod iwlwifi')
        IdleAfter(5)
        SetCmd(sta, 'modprobe iwlwifi')
        SetCmd(sta, 'pkill -9 wpa_supplicant')
        IdleAfter(3)
        SetCmd(sta,
               'wpa_supplicant -B -i ' + netcardName + ' -c /etc/wpa_supplicant/wpa_supplicant.conf -f /tmp/wpa_log/%s.log' % netcardName)
        IdleAfter(3)
        SetCmd(sta, 'wpa_cli -i ' + netcardName + ' scan')


#########################################
# RebootStaNetcard
# 
# function:
#     重启sta网卡
# args: 
#     sta：需要关联的device
#     NetcardName: sta 的无线网卡名称，如 "wlan0"
#
##########################################
def RebootStaNetcard(sta, netcardName, times=1, printflag=True):
    for i in range(times):
        for j in range(3):
            # SetCmd(sta,'ifconfig '+netcardName+' up')
            # IdleAfter(3)
            # data = SetCmd(sta,'iwconfig')
            SetCmd(sta, 'rmmod iwldvm')
            SetCmd(sta, 'rmmod iwlwifi')
            IdleAfter(5, printflag)
            SetCmd(sta, 'modprobe iwlwifi')
            # if CheckLine(data,'mon0')!=0:
            SetCmd(sta, 'ifconfig mon0')
            SetCmd(sta, 'ifconfig ' + netcardName + ' up')
            data = SetCmd(sta, 'ifconfig')
            if 0 == CheckLine(data, netcardName, PM=printflag):
                break
        for k in range(3):
            SetCmd(sta, 'pkill -9 wpa_supplicant')
            IdleAfter(2, printflag)
            SetCmd(sta, 'airmon-ng start ' + netcardName)
            IdleAfter(3, printflag)
            data = SetCmd(sta,
                          'wpa_supplicant -B -i ' + netcardName + ' -c /etc/wpa_supplicant/wpa_supplicant.conf -f /tmp/wpa_log/%s.log' % netcardName)
            if CheckLine(data, 'another wpa_supplicant process already running') == 0:
                pass
            else:
                break


#########################################
# WpaConnectWirelessNetworkold
# 
# function:
#     调用linux 下wpa_supplicat 关联AP 并DHCP 获取地址
# args: 
#     sta：需要关联的device
#     NetcardName: sta 的无线网卡名称，如 "wlan0"
#     ssid: 关联的ssid, 如 "affirm_auto_test1"
#     apmac: ap mac地址
#     Type： 关联的类型,如"open","wep","wpa"
#     **args: 可选参数，当关联的类型不为"open"时,用于传入用户名和密码
#             如 id ='admin', ps ='123456'
# return: 
#       失败 ：1
#       成功 ：0
#
# addition:
#
# examples:
#     WpaConnectWirelessNetwork(sta2,'wlan0','affirm_auto_test1')
#     WpaConnectWirelessNetwork(sta1,'wlan1','affirm_auto_test2',Type='open')
#    WpaConnectWirelessNetwork('s1','wlan0','affirm_auto_test1',connectType='open',checkDhcpAddress='192.168.91.0')
##########################################
def WpaConnectWirelessNetworkold(sta, netcardName, ssid, connectType='open', dhcpFlag=True, **args):
    if ('' == sta) or ('' == netcardName) or ('' == ssid):
        printRes('Error: parameter input error')
        return 1
    if 'printflag' in args:
        printflag = args['printflag']
    else:
        printflag = True
    res = 1
    CONFIGFLAG = 0
    bssid = ''
    SetCmd(sta, 'dhclient -r ' + netcardName)
    IdleAfter('2', printflag)
    SetCmd(sta, 'ifconfig ' + netcardName + ' up')
    IdleAfter('2', printflag)
    SetCmd(sta, 'dmesg -c -T| grep ' + netcardName)

    SetCmd(sta, 'wpa_cli -i ' + netcardName + ' remove_network 0')
    SetCmd(sta, 'wpa_cli -i ' + netcardName + ' add_network 0')
    SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 ssid ' + '\'"' + ssid + '"\'')

    if 'bssid' in args:
        bssid = args['bssid']
        SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 bssid ' + args['bssid'])
    if connectType.lower() == 'open':
        SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 key_mgmt NONE')
    elif connectType.lower() == 'wep_open':
        if 'wep_key0' in args:
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 key_mgmt NONE')
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 wep_key0 ' + '\'"' + args['wep_key0'] + '"\'')
        else:
            print('Parameter wep_key0 not found in args')
            CONFIGFLAG = 1
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' remove_network 0')
    elif connectType.lower() == 'wep_shared':
        if 'wep_key0' in args:
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 key_mgmt NONE')
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 auth_alg SHARED')
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 wep_key0 ' + '\'"' + args['wep_key0'] + '"\'')
        else:
            print('Parameter wep_key0 not found in args')
            CONFIGFLAG = 1
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' remove_network 0')
    elif connectType.lower() == 'wep_shared104':
        if 'wep_key0' in args:
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 key_mgmt NONE')
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 group WEP104')
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 auth_alg SHARED')
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 wep_key0 ' + '\'"' + args['wep_key0'] + '"\'')
        else:
            print('Parameter wep_key0 not found in args')
            CONFIGFLAG = 1
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' remove_network 0')
    elif connectType.lower() == 'wpa_psk':
        if 'psk' in args:
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 key_mgmt WPA-PSK')
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 proto WPA')
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 pairwise TKIP')
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 group TKIP')
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 psk ' + '\'"' + args['psk'] + '"\'')
        else:
            print('Parameter psk not found in args')
            CONFIGFLAG = 1
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' remove_network 0')
    elif connectType.lower() == 'wpa2_psk':
        if 'psk' in args:
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 key_mgmt WPA-PSK')
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 proto WPA2')
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 pairwise TKIP')
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 group TKIP')
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 psk ' + '\'"' + args['psk'] + '"\'')
        else:
            print('Parameter psk not found in args')
            CONFIGFLAG = 1
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' remove_network 0')
    elif connectType.lower() == 'wpa_eap':
        if 'identity' in args and 'password' in args:
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 key_mgmt WPA-EAP')
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 proto WPA')
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 pairwise TKIP')
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 group TKIP')
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 eap PEAP')
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 identity ' + '\'"' + args['identity'] + '"\'')
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 password ' + '\'"' + args['password'] + '"\'')
        else:
            print('Parameter identity or password not found in args')
            CONFIGFLAG = 1
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' remove_network 0')
    elif connectType.lower() == 'wpa2_eap':
        if 'identity' in args and 'password' in args:
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 key_mgmt WPA-EAP')
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 proto WPA2')
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 pairwise TKIP')
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 group TKIP')
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 eap PEAP')
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 identity ' + '\'"' + args['identity'] + '"\'')
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 password ' + '\'"' + args['password'] + '"\'')
        else:
            print('Parameter identity or password not found in args')
            CONFIGFLAG = 1
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' remove_network 0')
    elif connectType.lower() == 'custom':
        if 'key_mgmt' in args:
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 key_mgmt ' + args['key_mgmt'])
        if 'psk' in args:
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 psk ' + '\'"' + args['psk'] + '"\'')
        if 'priority' in args:
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 priority ' + args['priority'])
        if 'scan_ssid' in args:
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 scan_ssid ' + args['scan_ssid'])
        if 'proto' in args:
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 proto ' + args['proto'])
        if 'pairwise' in args:
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 pairwise ' + args['pairwise'])
        if 'group' in args:
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 group ' + args['group'])
        if 'wpa_ptk_rekey' in args:
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 wpa_ptk_rekey ' + args['wpa_ptk_rekey'])
        if 'eap' in args:
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 eap ' + args['eap'])
        if 'identity' in args:
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 identity ' + '\'"' + args['identity'] + '"\'')
        if 'ca_cert' in args:
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 ca_cert ' + args['ca_cert'])
        if 'client_cert' in args:
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 client_cert ' + args['client_cert'])
        if 'private_key' in args:
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 private_key ' + args['private_key'])
        if 'private_key_passwd' in args:
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 private_key_passwd ' + args['private_key_passwd'])
        if 'phase1' in args:
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 phase1 ' + args['phase1'])
        if 'phase2' in args:
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 phase2 ' + args['phase2'])
        if 'anmonymous_identity' in args:
            SetCmd(sta,
                   'wpa_cli -i' + netcardName + ' set_network 0 anmonymous_identity ' + args['anmonymous_identity'])
        if 'password' in args:
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 password ' + '\'"' + args['password'] + '"\'')
        if 'pin' in args:
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 pin ' + args['pin'])
        if 'pcsc' in args:
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 pcsc ' + args['pcsc'])
        if 'eapol_flags' in args:
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 eapol_flags ' + args['eapol_flags'])
        if 'pac_file' in args:
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 pac_file ' + args['pac_file'])
        if 'wep_key0' in args:
            wep_key0_str = args['wep_key0'] if 'wep_key_type' in args and args['wep_key_type'] == 'hex' else '\'"' + args['wep_key0'] + '"\''
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 wep_key0 ' + wep_key0_str)
        if 'wep_key1' in args:
            wep_key1_str = args['wep_key1'] if 'wep_key_type' in args and args['wep_key_type'] == 'hex' else '\'"' + args['wep_key1'] + '"\''
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 wep_key1 ' + wep_key1_str)
        if 'wep_key2' in args:
            wep_key2_str = args['wep_key2'] if 'wep_key_type' in args and args['wep_key_type'] == 'hex' else '\'"' + args[ 'wep_key2'] + '"\''
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 wep_key2 ' + wep_key2_str)
        if 'wep_key3' in args:
            wep_key3_str = args['wep_key3'] if 'wep_key_type' in args and args[ 'wep_key_type'] == 'hex' else '\'"' + args['wep_key3'] + '"\''
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 wep_key3 ' + wep_key3_str)
        if 'wep_tx_keyidx' in args:
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 wep_tx_keyidx ' + args['wep_tx_keyidx'])
        if 'auth_alg' in args:
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' set_network 0 auth_alg ' + args['auth_alg'])
    else:
        print('Parameter connectType input is unknown!')
        SetCmd(sta, 'wpa_cli -i ' + netcardName + ' remove_network 0')
        CONFIGFLAG = 1
    if CONFIGFLAG == 0:
        try:
            # 使能网络
            SetCmd(sta, 'wpa_cli -i ' + netcardName + ' enable_network 0')
            # sta 关联 ap
            i_time = 1
            interval = 3
            while i_time < 16:
                data = SetCmd(sta, 'wpa_cli -i ' + netcardName + ' status')
                if 0 == CheckLineList(data, [('ssid', ssid), ('wpa_state', 'COMPLETED')], IC=True, PM=printflag):
                    if printflag:
                        printRes('Connect to AP succeed in ' + str(interval * (i_time - 1)) + ' sec')
                    res = 0
                    break
                elif 0 == CheckLineList(data, [('wpa_state', 'DISCONNECTED')], IC=True, PM=False):
                    return 1
                elif 0 == CheckLineList(data, [('wpa_state', 'INACTIVE')], IC=True, PM=False):
                    return 1
                else:
                    i_time = i_time + 1
                if 15 == i_time:
                    if printflag:
                        printRes('Failed: connet to ' + ssid + ' failed in ' + str(interval * i_time) + ' sec')
                    try:
                        res = 2
                        # 优化时长，将sta和AC上进行检查的操作省略，实际运行时测试人员基本不会用到这些检查
                        # #连接失败，开启抓包功能
                        # # StaStartCapture(sta,netcardName,ssid,bssid)			
                        # for i in range(3):						
                        # SetCmd(sta,'wpa_cli -i ' + netcardName + ' scan ')
                        # IdleAfter(2)
                        # SetCmd(sta,'wpa_cli -i ' + netcardName + ' scan_results')
                        # IdleAfter(3)
                        # SetCmd(sta,'iwlist ' + netcardName + ' scan | grep ' + ssid)
                        # SetCmd(sta,'cat /tmp/wpa_log/%s.log' % netcardName )
                        # SetCmd(sta,'dmesg -c -T')
                        # SetCmd('ap1','admin')
                        # SetCmd('ap1','admin')
                        # SetCmd('ap1','iwconfig')
                        # SetCmd('ap1','brctl show')                        
                        # SetCmd('s1','show wireless ap status')
                        # SetCmd('s1','show wireless ap fail status')
                        # SetCmd('s1','show wireless client status')
                        # tempRe1 = SetCmd('ap1','iwconfig ath0') 
                        # if re.search('Bit Rate:0 kb',tempRe1) is not None:
                        # res = 3
                    except Exception:
                        print('DEBUG ERROR')
                    finally:
                        IdleAfter(1, printflag)
                        # StaStopCapture(sta,netcardName)
                    return res
                IdleAfter(interval, printflag)
        except Exception:
            print('Connetion Error')
        # sta 网卡 dhcp 获取地址
        if dhcpFlag:
            SetCmd(sta, 'dhclient ' + netcardName)
            IdleAfter(2, printflag)
            i_time = 1
            if 'checkDhcpAddress' in args:
                tempNetworkIpRe = re.search('\d+\.\d+\.\d+\.', args['checkDhcpAddress'])
                tempNetworkIp = tempNetworkIpRe.group(0)
            while i_time < 7:
                data = SetCmd(sta, 'ifconfig -v ' + netcardName)
                if re.search('inet.*?((2[0-4]\d|25[0-5]|[01]?\d\d?)\.){3}(2[0-4]\d|25[0-5]|[01]?\d\d?)', data,
                             re.I) is not None:
                    if 'checkDhcpAddress' in args:
                        if re.search('inet.*?' + tempNetworkIp, data, re.I) is None:
                            if printflag:
                                printRes('Obatin ip via dhcp succeed but not match')
                            return 4
                    res = 0
                    if printflag:
                        printRes('Obatin ip via dhcp succeed')
                    break
                i_time = i_time + 1
                IdleAfter(5, printflag)
                if 6 == i_time:
                    if printflag:
                        printRes('Failed: Obtain ip via dhcp failed')
                        # try:
                        # 优化时长，将sta和AC上进行检查的操作省略，实际运行时测试人员基本不会用到这些检查
                        # SetCmd(sta,'iwlist ' + netcardName + ' scan | grep ' + ssid)
                        # SetCmd('ap1','admin')
                        # SetCmd('ap1','admin')
                        # SetCmd('ap1','iwconfig')
                        # tempRe2 = SetCmd('ap1','brctl show')
                        # if re.search('ath0\.4091',tempRe2) is None:
                        # if res == 0:
                        # res = 5
                        # SetCmd('s1','show wireless ap status')
                        # SetCmd('s1','show wireless ap fail status')
                        # SetCmd('s1','show wireless client status')                       
                        # except Exception:
                        # print 'DEBUG ERROR'
                    return 1

    return res


#########################################
# WpaConnectWirelessNetwork
#
# function:
#     调用linux 下wpa_supplicat 关联AP 并DHCP 获取地址
# args:
#     sta：需要关联的device
#     NetcardName: sta 的无线网卡名称，如 "wlan0"
#     ssid: 关联的ssid, 如 "affirm_auto_test1"
#     apmac: ap mac地址
#     Type： 关联的类型,如"open","wep","wpa"
#     **args: 可选参数，当关联的类型不为"open"时,用于传入用户名和密码
#             如 id ='admin', ps ='123456'
# return:
#       失败 ：1
#       成功 ：0
#
# addition:
#
# examples:
#     WpaConnectWirelessNetwork(sta2,'wlan0','affirm_auto_test1')
#     WpaConnectWirelessNetwork(sta1,'wlan1','affirm_auto_test2',Type='open')
#    WpaConnectWirelessNetwork('s1','wlan0','affirm_auto_test1',connectType='open',checkDhcpAddress='192.168.91.0')
##########################################


def start_dhcp_server_debug(debug_device):
    """
    开启dhcp server上面的debug
    :param debug_device: 设备名称
    :return: None
    """
    with pp.context_debug_print('Open DHCP Server({}) Debug'.format(debug_device.upper())):
        EnterEnableMode(debug_device)
        SetCmd(debug_device, 'debug ip dhcp server packets')
        SetCmd(debug_device, 'debug ip dhcp client packet')


def find_dhcp_server_dev(debug_device):
    """
    :param debug_device: 传入参数为str类型或者tuple类型
    :return: 针对设备串口下面的设置show run查看设备是否开启dhcp server如果为dhcp server返回[dev,]
    """
    _dev = []
    if debug_device:
        if isinstance(debug_device, tuple):
            for dev in debug_device:
                EnterEnableMode(dev)
                _res = SetCmd(dev, 'show running-config | include dhcp', timeout=5)
                if not CheckLine(_res, 'dhcp'):
                    _dev.append(dev)
        elif isinstance(debug_device, str):
            _dev.append(debug_device)
    else:
        printRes('Argument Of Device is None')
    return _dev


def WpaConnectWirelessNetwork(sta, netcardName, ssid, connectType='open', dhcpFlag=True, retry=2, reconnectflag=1,
                              debug_device='s3', **args):
    """
    :param sta:   设备名称
    :param netcardName: 网卡名称
    :param ssid: 要扫描的ssid
    :param connectType: 连接类型 默认open
    :param dhcpFlag: 是否需要进行dhcp检测
    :param retry: 重复执行测试
    :param reconnectflag: 是否需要重连
    :param debug_device: 无线确认测试环境默认开启dhcp debug的设备
    :param args: 其他参数
    :return: 成功0 失败-1
    """
    if 'printflag' in args:
        printflag = args['printflag']
    else:
        printflag = True
    res = WpaConnectWirelessNetworkold(sta, netcardName, ssid, connectType, dhcpFlag, **args)
    if reconnectflag == 1:
        for i in range(retry):
            if res != 0:
                if i == retry - 1:
                    """说明 目前show ru问n | include dhcp 方式判断设备是否开启dhcp服务器存在题，规避手段是不判断
                    重复执行的时候最后一次会开启dhcp server上面的debug
                    dev = find_dhcp_server_dev(debug_device)
                    if not dev:
                        for _dev in dev:
                    """
                    try:
                        start_dhcp_server_debug(debug_device)
                        RebootStaNetcard(sta, netcardName, printflag=printflag)
                        res = WpaConnectWirelessNetworkold(sta, netcardName, ssid, connectType, dhcpFlag, **args)
                    finally:
                        control_o(debug_device)
                RebootStaNetcard(sta, netcardName, printflag=printflag)
                res = WpaConnectWirelessNetworkold(sta, netcardName, ssid, connectType, dhcpFlag, **args)
    return res


#########################################
# WpaDisconnectWirelessNetwork
# 
# function:
#     调用linux 下wpa_supplicat 与AP接关联并释放ip地址
# args: 
#     sta：需要关联的device
#     NetcardName: sta 的无线网卡名称，如 "wlan0"
#
# return: 
#       失败 ：1
#       成功 ：0
#
# addition:
#
# examples:
#     WpaDisconnectWirelessNetwork(sta2,'wlan0')
#     WpaDisconnectWirelessNetwork(sta1,'wlan1')
#
# #########################################
def WpaDisconnectWirelessNetwork(sta, NetcardName, forceFlag=False):
    if ('' == sta) or ('' == NetcardName):
        printRes('Error: parameter input error')
        return 1
    SetCmd(sta, '\x03')
    IdleAfter(2)
    SetCmd(sta, 'dhclient -r ' + NetcardName)
    if forceFlag:
        SetCmd(sta, 'ifconfig ' + NetcardName + ' down')
    SetCmd(sta, 'wpa_cli -i ' + NetcardName + ' disable_network 0')
    SetCmd(sta, 'wpa_cli -i ' + NetcardName + ' remove_network 0')
    SetCmd(sta, 'dhclient -r ' + NetcardName)
    if not forceFlag:
        SetCmd(sta, 'ifconfig ' + NetcardName + ' up')
    IdleAfter(2)

    return 0


#########################################
# RebootAp
# 
# function:
#     重启AP
# args: 
#     Type: 重启方法，'AP'为控制AP 重启，'AC' 为通过 AC 控制 AP 重启
#     timeout: AP重启时间，默认为150s
#     connectTime: AP重启后被AC发现的时间，默认为70s
#     username:登录AP 用户名，默认为 "admin"
#     password:登录AP 密码，默认为 "admin"
#
#     **flag: 可选参数
#             如果Type='AP',flag需要包含 AP 设备标签名 (如 "ap1")
#             如果Type='AC',flag需要包含 AP 设备标签名、AC设备标签名、AP mac地址
# return: 
#       失败 ：1
#       成功 ：0
#
# addition:
#
# examples:
#     RebootAp(AP=ap1)
#     RebootAp(Type='AC',AP=ap1,AC=ac1,MAC=ap1mac)
#
# #########################################
def RebootAp(Type='AP', timeout=50, connectTime=60, username='admin', password='admin', setdefaut=False, **flag):
    if 'AP' in flag:
        ap = flag['AP']
    else:
        printRes('Error: no "AP" device given')
        return 1
    if 'apcmdtype' in flag:
        apcmdtype = flag['apcmdtype']
    else:
        apcmdtype = 'set'

    # AP 自主 reboot
    if 'AP' == str(Type).upper():
        SetCmd(ap, '\x03')
        if not setdefaut:
            SetCmd(ap, 'reboot', timeout=1)
        else:
            # SetCmd(ap,'factory-reset',timeout=1)
            ApSetcmd(ap, apcmdtype, 'factoryreset', timeout=1)
        SetCmd(ap, 'y', timeout=2)
        SetCmd(ap, 'y', timeout=2)
        IdleAfter(timeout)
        ApLogin(ap, retry=30)

    # AC 控制 AP reboot
    elif 'AC' == str(Type).upper():

        if 'AC' in flag:
            ac = flag['AC']
        else:
            printRes('Error: no "AC" device given')
            return 1

        if 'MAC' in flag:
            apmac = flag['MAC']
        else:
            printRes('Error: no "AP Mac" given')
            return 1

        EnterEnableMode(ac)
        data = SetCmd(ac, 'wireless ap reset', apmac, timeout=2)
        if 0 == CheckLine(data, 'Y/N'):
            SetCmd(ac, 'y', timeout=1)
            # IdleAfter(timeout)
            IdleAfter(50)
            ApLogin(ap, retry=20)
            # for i in range(13):
            # data = SetCmd(ap,'\n\n',timeout=1)
            # if CheckLine(data,'login') == 0:
            # break
            # else:
            # IdleAfter(10)

    # 异常情况
    else:
        printRes('Error: "Type" parameter input error')
        return 1

    # 登录 AP
    ApLogin(ap)
    IdleAfter(connectTime)

    printRes('****** Reboot succeed *****')
    return 0


#########################################
# RebootMulitAp
# 
# function:
#     重启AP
# args: 
#     Type: 多个ap同时重启方法，'AP'为控制AP 重启，'AC' 为通过 AC 控制 AP 重启
#     timeout: AP重启时间，默认为150s
#     connectTime: AP重启后被AC发现的时间，默认为70s
#     username:登录AP 用户名，默认为 "admin"
#     password:登录AP 密码，默认为 "admin"
#
#     **flag: 可选参数
#             如果Type='AP',flag需要包含 AP 设备标签名 (如 "ap1")
#             如果Type='AC',flag需要包含 AP 设备标签名、AC设备标签名、AP mac地址
# return: 
#       失败 ：1
#       成功 ：0
#
# addition:
#
# examples:
#     RebootMulitAp(AP=[ap1])
#     RebootMulitAp(Type='AC',AP=ap1,AC=ac1,MAC=ap1mac)
#
# #########################################
def RebootMulitAp(Type='AP', timeout=120, connectTime=60, username='admin', password='admin', **flag):
    if 'AP' in flag:
        ap = flag['AP']
        mult = len(ap)
    else:
        printRes('Error: no "AP" device given')
        return 1

    # AP 自主 reboot
    if 'AP' == str(Type).upper():
        res1 = [0, 0]
        for i in range(mult):
            SetCmd(ap[i], '\x03')
            SetCmd(ap[i], 'reboot', timeout=1)
            SetCmd(ap[i], 'y', timeout=1)
            IdleAfter(1)
        IdleAfter(50)
        for i in range(13):
            for j in range(mult):
                data = SetCmd(ap[j], '\n\n', timeout=1)
                if CheckLine(data, 'login') == 0:
                    if j == 0:
                        res1[0] = 1
                    else:
                        res1[j] = res1[j - 1]
            if res1[j] == 1:
                break
            else:
                IdleAfter(10)
    # AC 控制 AP reboot
    elif 'AC' == str(Type).upper():
        res1 = [0, 0]
        if 'AC' in flag:
            ac = flag['AC']
        else:
            printRes('Error: no "AC" device given')
            return 1

        if 'MAC' in flag:
            apmac = flag['MAC']
        else:
            printRes('Error: no "AP Mac" given')
            return 1

        EnterEnableMode(ac)
        for i in range(mult):
            data = SetCmd(ac, 'wireless ap reset', apmac[i], timeout=2)
            if 0 == CheckLine(data, 'Y/N'):
                SetCmd(ac, 'y', timeout=1)
        IdleAfter(50)
        for j in range(13):
            for i in range(mult):
                data = SetCmd(ap[i], '\n\n', timeout=1)
                if CheckLine(data, 'login') == 0:
                    if i == 0:
                        res1[0] = 1
                    else:
                        res1[i] = res1[i - 1]
            if res1[i] == 1:
                break
            else:
                IdleAfter(10)

    # 异常情况
    else:
        printRes('Error: "Type" parameter input error')
        return 1

    # 登录 AP
    for i in range(mult):
        data = SetCmd(ap[i], '\n\n', timeout=1)
        SetCmd(ap[i], username, timeout=2)
        data = SetCmd(ap[i], password, timeout=2)
        if CheckLine(data, '#') != 0 or CheckLine(data, 'Login incorrect') == 0:
            SetCmd(ap[i], username, timeout=2)
            SetCmd(ap[i], password, timeout=2)
    IdleAfter(connectTime)
    printRes('******All Aps Reboot succeed *****')
    return 0


#########################################
# CheckWirelessClientOnline
# 
# function:
#     检查某STA 在线状态(online & offline)
# args: 
#     sut: 交换机 (AC)
#     mac: STA mac address
#     checkType: 要检查的状态 (online & offline)
#     retry: 查询次数
#     interval: 查询时间间隔
#
# return: 
#       失败 ：1
#       成功 ：0
#
# addition:
#
# examples:
#     CheckWirelessClientOnline('s1','00-15-00-5c-b1-00','online')
#     CheckWirelessClientOnline('s2','00-15-00-5c-b1-00',retry=30)
#
# #########################################
def CheckWirelessClientOnline(sut, mac, checkType, retry=60, interval=10):
    for tmpCounter in range(0, retry):
        data = SetCmd(sut, 'show wireless client summary')
        res = CheckLine(data, mac, IC=True)
        if checkType == 'online':
            if res == 0:
                printRes('Client online in ' + str(tmpCounter * interval) + ' sec')
                return 0
            if tmpCounter == retry - 1:
                printRes('Client online FAILED in ' + str(tmpCounter * interval) + ' sec')
                return 1
            IdleAfter(interval)
        else:
            if res != 0:
                printRes('Client offline in ' + str(tmpCounter * interval) + ' sec')
                return 0
            if tmpCounter == retry - 1:
                printRes('Client offline FAILED in ' + str(tmpCounter * interval) + ' sec')
                return 1
            IdleAfter(interval)


#########################################
# ScanSsidPower
# 
# function:
#     扫描某 ssid 的功率值 （调用 wpa_supplicant,扫描到 "signal level"）
# args: 
#     sta: 执行扫描的 STA标签
#     netcardName: STA网卡名称
#     ssid: 扫描的SSID
#     bssid: SSID的bssid
#     scan_times: 扫描的次数，默认为15次
#
# return: 
#       失败 ：0
#       成功 ：扫描到的功率的平均值
#
# addition:
#
# examples:
#     ScanSsidPower('sta2','ra0','affirm_auto_test2','00:03:0f:11:99:00')
#     ScanSsidPower('sta2','ra0','affirm_auto_test2','00:03:0f:11:99:00',scan_times=10)
#
#########################################
def ScanSsidPower(sta, netcardName, ssid, bssid, scan_times=15):
    i_time = 0
    level_list = list()
    power_total = 0
    ssidPower = 0

    SetCmd(sta, '\x03')
    while i_time < scan_times:
        power = 0
        SetCmd(sta, 'wpa_cli -i ' + netcardName + ' scan')
        data = SetCmd(sta, 'wpa_cli -i ' + netcardName + ' scan_results')
        power = int(str(GetValueBetweenTwoValuesInData(data, bssid + '\s+\d+', '\[.*?' + ssid)).lstrip().rstrip())
        if power > 0:
            level_list.append(power)
        IdleAfter(10)
        i_time = i_time + 1

    if 0 < len(level_list):
        for index in range(len(level_list)):
            power_total = power_total + level_list[index]
        ssidPower = power_total / len(level_list)
    else:
        printRes('Failed: the network can not scan as ssid power too low')
        ssidPower = 0

    return ssidPower


#########################################
# CheckLineSsidScan
# 
# function:
#     扫描某 ssid 信息
# args: 
#     sta: 执行扫描的 STA标签
#     netcardName: STA网卡名称
#     ssid: 扫描的SSID
#     bssid: SSID的bssid
#     *args : 需要匹配的字符串，以逗号分隔 
#     **flag: 可选的标志位[RS:列敏感]
#
# return: 
#       失败 ：-1
#       成功 ：0
#
# addition:
#
# examples:
#     CheckLineSsidScan('sta2','ra0','affirm_auto_test2','00:03:0f:11:99:00','WEP',IC=True)
#     CheckLineSsidScan('sta2','ra0','affirm_auto_test2','00:03:0f:11:99:00','WPA2',scan_times=10,RS=True)
#
########################################## 
def CheckLineSsidScan(sta, netcardName, ssid, bssid, *args, **flag):
    rowSensitive = False
    printMatch = True
    res = -1
    moreLine = False
    ignoreCase = False
    scan_times = 150
    mult = len(sta)
    patstr = ['', '']
    compilerule = ['', '']
    scanResult = ''
    i_time = 0
    for j in list(flag.keys()):
        if j == 'RS':
            rowSensitive = flag[j]
        elif j == 'PM':
            printMatch = flag[j]
        elif j == 'ML':
            moreLine = flag[j]
        elif j == 'IC':
            ignoreCase = flag[j]
        elif j == 'scan_times':
            scan_times = flag[j]
    for i in range(mult):
        if not rowSensitive:
            pat = '.*?'
            patstr[i] = '.*?' + bssid[i] + '.*?'
        else:
            pat = '\s*'
            patstr[i] = '\s*' + bssid[i] + '\s*'
    for i in range(mult):
        for j in args:
            if j == '':
                j = '[\S]+'
            patstr[i] += str(j) + pat
        patstr[i] += ssid[i] + pat
        if moreLine:
            compilerule[i] = re.compile(patstr[i], re.S)
        elif ignoreCase:
            compilerule[i] = re.compile(patstr[i], re.I)
        else:
            compilerule[i] = re.compile(patstr[i])
    times = 0
    res1 = [0, 0]
    while i_time < scan_times:
        for i in range(mult):
            SetCmd(sta[i], 'wpa_cli -i ' + netcardName[i] + ' scan')
            scanResult = SetCmd(sta[i], 'wpa_cli -i ' + netcardName[i] + ' scan_results')
            match = compilerule[i].search(scanResult)
            if match:
                try:
                    if printMatch:
                        printRes('[Match Line:]' + str(match.group()))
                        if i == 0:
                            res1[i] = 1
                            print(patstr[i])
                        else:
                            res1[i] = res1[i - 1]
                    else:
                        res1[i] = 0
                except (IndexError, Exception) as e:
                    print(e)
            else:
                printRes('[Match Line Fail:]' + patstr[i])
        if res1[0] == 1:
            break
        else:
            IdleAfter(5)
            i_time = i_time + 1
            times = i_time
    if times == scan_times:
        printRes("sta scan ssid failed!")
        return -1

    else:
        printRes("sta scan ssid successed!")
        return 0


#########################################
# incrmac
#
# args: 
#     mac:mac地址 如'00-01-01-01-01-01'
#     step:增长数量  默认1
#     mask:掩码，从掩码位置增长，默认6
# return: 
#       增长后的mac地址
#
# addition:
#
# examples:
#     incrmac('00-01-01-01-01-01')      结果00-01-01-01-01-02
#     incrmac('00-01-01-01-01-01',step=2)      结果00-01-01-01-01-03            
#     incrmac('00-01-01-01-01-01',mask=3)      结果00-01-02-01-01-01
##########################################
def incrmac(mac, step=1, mask=6):
    flag1 = True
    if mask > 6:
        print('mask error')
        return
    if re.search('-', mac) is not None:
        flag1 = False
        maclist = mac.split('-')
    else:
        maclist = mac.split(':')
    if len(maclist) != 6:
        print('mac length error')
        return
    snum = ''
    for i in range(mask):
        snum = snum + maclist[i]
    d = int(snum, 16)
    dnum = d + step
    l = '%0' + str(mask * 2) + 'X'
    ss = l % dnum
    for i in range(mask):
        maclist[i] = ss[i * 2:i * 2 + 2]
    if not flag1:
        return '-'.join(maclist)
    else:
        return ':'.join(maclist)


#########################################
# incrip
#
# args: 
#     ip:ip地址 如'10.1.1.1'
#     step:增长数量  默认1
#     mask:掩码，从掩码位置增长，默认32,即默认从最后一位开始增长
# return: 
#       增长后的ip地址
#
# addition:
#
# examples:
#     incrip('10.1.1.1')      结果10.1.1.2
#     incrip('10.1.1.1',step=2)      结果10.1.1.3            
#     incrip('10.1.1.1',mask=24)      结果10.1.2.1
##########################################
def incrip(ip, step=1, mask=32):
    iplist = ip.split('.')
    if len(iplist) != 4:
        print('ip format error')
        return
    shex = ''
    for svalue in iplist:
        h = int(svalue)
        if h > 0xff:
            print('ip error')
            return
        shex += '%02X' % h
    mv = 32 - mask
    inc = int(shex, 16) >> mv
    gv = inc + step
    mod = int(shex, 16) & (2 ** mv - 1)
    resv = ((gv << mv) + mod) & (2 ** 32 - 1)
    reslist = []
    for i in range(4):
        reslist.insert(0, str(resv >> (i * 8) & (2 ** 8 - 1)))
    return '.'.join(reslist)


##########################################
# avoiderror add for bug 31368 ,login before each testcase
##########################################
def avoiderror(testname):
    print(testname + ' avoid errors configuration start!')
    for ap in ['ap1', 'ap2']:
        data = SetCmd(ap, '\n\n', timeout=5)
        if re.search('login', data):
            print('Critical error! ap1 maybe restart before ' + testname)
            SetCmd(ap, 'admin', timeout=1)
            SetCmd(ap, 'admin', timeout=1)
            SetCmd(ap, 'admin', timeout=1)
            SetCmd(ap, 'admin', timeout=1)
            data1 = SetCmd(ap, '\n\n', timeout=5)
            if re.search('#', data1):
                print('Login succeed')
            else:
                print('Login failed')
        if re.search('Bootloader', data) or re.search('ath>', data):
            SetCmd(ap, 'reset')
            IdleAfter(50)
            ApLogin(ap, retry=20)


#########################################
# StaStartCapture
#     在station上使用airodump-ng(aircrack-ng的组件)在指定无线网口抓包
# args: 
#     sta：需要进行抓包的station
#     NetcardName: sta 的无线网卡名称，如 "wlan0","wls224"
#     ssid: 关联的ssid, 如 "affirm_auto_test1"
#     bssid: 关联的ap mac, 如 00:03:0F:01:02:03
# return: 
#     -1: 失败
#     0 : 成功
#
# addition:
#
# examples:
#     
##########################################
def StaStartCapture(sta, netcardName, ssid, bssid):
    # 停止之前的抓包进程
    SetCmd(sta, 'pgrep airodump | xargs kill')

    # 通过网卡名获取monitor端口
    data = SetCmd(sta, 'airmon-ng')
    res = re.search(netcardName + r'.*?\[(phy\d+)\]', data, re.M)
    if not res:
        printRes(
            '[StaStartCapture] Can not find ' + netcardName + ' by airmon-ng, please make sure installed aircrack-ng and wireless card up!')
        return -1
    netcardPhy = res.group(1)
    res = re.search(r'(mon\d+).*?\[%s\]' % netcardPhy, data, re.M)
    if not res:
        printRes(
            '[StaStartCapture] Can not find ' + netcardName + '\'s monitor port monx, please make sure airmon-ng excute ok!')
        return -1
    monitorPort = res.group(1)

    # 根据bssid获取channel号
    channel = ''
    if bssid:
        radio1 = SetCmd('ap1', 'get radio')
        radio2 = SetCmd('ap2', 'get radio')
        regexp_channel = re.compile(bssid.upper() + r'.*?\nchannel\s+(\d+)', re.S)
        res1 = regexp_channel.search(radio1)
        res2 = regexp_channel.search(radio2)
        if res1 or res2:
            channel = res1.group(1) if res1 else res2.group(1)
        else:
            printRes("[StaStartCapture] Can not find ap[%s]'s channel! Capture witout channel!")

    this_time = time.strftime('[%Y-%m-%d][%H-%M-%S]', time.localtime(time.time()))
    filename = '/tmp/capture/pcap' + this_time

    # 抓包命令行
    if channel:
        capture_cmd = 'nohup airodump-ng --channel %s --bssid %s --essid %s -w %s --output-format pcap %s &' % (
            channel, bssid, ssid, filename, monitorPort)
    else:
        capture_cmd = 'nohup airodump-ng --bssid %s --essid %s -w %s --output-format pcap %s &' % (
            bssid, ssid, filename, monitorPort)

    SetCmd(sta, capture_cmd)
    print('The capture file is : ' + filename)
    return 0


#########################################
# StaStopCapture
#     停止在station上抓包，若有多个抓包进程，则停止所有
# args: 
#     sta：需要停止抓包的station
#     NetcardName: sta 的无线网卡名称，如 "wlan0","wls224"
# return: 
#     -1: 失败
#     0 : 成功
#
# addition:
#
# examples:
#     
##########################################
def StaStopCapture(sta, netcardName):
    # 停止抓包进程
    SetCmd(sta, 'pgrep airodump | xargs kill')
    return 0


#########################################
# FactoryResetMultiAp
#     多ap恢复出厂配置
# args: 
#     ap：ap串口号
#
# addition:
#
# examples:
#     
##########################################
def FactoryResetMultiAp(ap):
    mult = len(ap)
    res = [0, 0]
    for i in range(mult):
        SetCmd(ap[i], 'factory-reset', timeout=1)
        SetCmd(ap[i], 'y', timeout=1)
        IdleAfter(1)
    IdleAfter(50)
    for i in range(13):
        for j in range(mult):
            data = SetCmd(ap[j], '\n\n', timeout=1)
            if CheckLine(data, 'login') == 0:
                if j == 0:
                    res[j] = 1
                else:
                    res[j] = res[j - 1]
            else:
                res[j] = 0
        if res[j] == 1:
            break
        else:
            IdleAfter(10)


#########################################
# ReloadMultiSwitch
#     多switch重启
# args: 
#     switch：switch串口号
#
# addition:
#
# examples:
#     
##########################################
def ReloadMultiSwitch(switch):
    mult = len(switch)
    res = 0
    res1 = [0, 0]
    for j in range(mult):
        data = SetCmd(switch[j], 'show slot', timeout=2)
        if CheckLine(data, 'Invalid input detected at', PM=False) != 0:
            res = 1
            break
    if res == 1:  # 机架设备重启
        for i in range(mult):
            printRes('***Device {} Reload Start***'.format(switch[i]))
            SetCmd(switch[i], 'reload', timeout=1)
            SetCmd(switch[i], 'y', timeout=1)
            time.sleep(1)
        IdleAfter(240)
        for i in range(12):
            for j in range(mult):
                SetTerminalLength(switch[j])
                data = SetCmd(switch[j], 'show slot', timeout=10)
                if CheckLine(data, 'Invalid input detected at', PM=False) != 0:
                    if len(re.findall('Inserted[^\n]+YES', data)) == len(re.findall('Work state[^\n]+RUNNING', data)):
                        if j == 0:
                            res1[j] = 1
                        else:
                            res1[j] = res1[j - 1]
                    else:
                        res1[j] = 0
                else:
                    if CheckLine(data, '>') == 0:
                        if j == 0:
                            res1[j] = 1
                        else:
                            res1[j] = res1[j - 1]
            if res1[j] == 1:
                printRes('***Device Reload Sucessfully***')
                SetTerminalLength(switch[j])
                break
            else:
                IdleAfter(20)

    else:  # 盒式设备重启
        for i in range(mult):
            printRes('***Device {} Reload Start***'.format(switch[i]))
            SetCmd(switch[i], 'reload', timeout=1)
            SetCmd(switch[i], 'y', timeout=1)
            time.sleep(1)
        IdleAfter(60)
        for i in range(36):
            for j in range(mult):
                data = SetCmd(switch[j], '\n\n', timeout=1)
                if CheckLine(data, '>') == 0:  # 表示设备重启成功
                    if j == 0:  # 第一台设备如果重启成功
                        res1[j] = 1
                    else:
                        res1[j] = res1[j - 1]
                else:
                    res1[j] = 0
            if res1[j] == 1:
                printRes('***Device Reload Successfully***')
                SetTerminalLength(switch[j])
                break
            else:
                IdleAfter(10)


def get_device_type(device):
    """
    获取设备类型，机架设备，或者盒式设备
    :param device: 's1' ,'s2'
    :return: 0 盒式设备， 1 机架设备
    """
    data = SetCmd(device, 'show slot', timeout=2)
    return 0 if CheckLine(data, 'Invalid input detected at', PM=False) == 0 else 1


def check_reload_device_status(device, wait_counts=80, wait_time=10):
    """
    多线程检查设备重启状况
    :param device: 设备
    :param wait_counts:检查次数
    :param wait_time:每次检查间隔时间
    :return:
    """
    for count in range(wait_counts):
        device_enter_user_mode = SetCmd(device, '\n\n', timeout=1)
        data_vsf = SetCmd(device, 'show slot', timeout=10)
        if CheckLine(device_enter_user_mode, '>') == 0:
            if CheckLine(data_vsf, 'Invalid input detected at', PM=False) != 0:
                if len(re.findall('Inserted[^\n]+YES', data_vsf)) == len(re.findall('Work state[^\n]+RUNNING',
                                                                                    data_vsf)):
                    SetTerminalLength(device)
                    printRes(r'***VSF/Chassis Device {} Reload Successfully***'.format(device))
                    return 1
                else:
                    continue
            else:
                SetTerminalLength(device)
                printRes(r'***Standalone/Box Device {} Reload Successfully***'.format(device))
                return 1
        else:
            IdleAfter(wait_time)


def reload_multi_switch(device_list):
    """
    多设备同时重启
    usage:
        reload_multi_switch(['s1', 's2', 's3'...])
    :param device_list: ['s1', 's2', 's3'...]
    :return: None
    """

    def _reload_device(device):
        """
        重启设备
        :param device:
        :return:
        """
        printRes('***Device {} Reload Start***'.format(device))
        EnterEnableMode(device)
        Receiver(device, 'reload')
        time.sleep(1)
        Receiver(device, 'y')
        time.sleep(1)

    threads = []  # 多线程列表
    if isinstance(device_list, list):
        if len(device_list):
            for _dev in device_list:
                _reload_device(_dev)
                threads.append(threading.Thread(target=check_reload_device_status, args=(_dev,)))
            IdleAfter(60)
            for t in threads:
                if t:
                    t.setDaemon(True)  # 设置守护线程，也就是后台线程，当主线程结束之后子线程立马结束
                    t.start()
            for t in threads:
                t.join()  # 各个子线程调用join方法，作用是实现线程同步
            printRes('***All Device Reload Successfully*** ')


#########################################
# WirelessApplyProfileWithCheck
#     profile 下发到ap
# args: 
#     switch：ac串口号
#     profile_id: profile number
#
# addition:
#
# examples:
#     WirelessApplyProfileWithCheck(ac,[1],[ap1mac])
##########################################
def WirelessApplyProfileWithCheck(switch, profile_id, apmac, eth_parameter=False):
    mult = len(profile_id)
    times = 0
    for i in range(mult):
        for j in range(10):
            EnterEnableMode(switch)
            if not eth_parameter:
                data = SetCmd(switch, 'wireless ap profile apply ' + profile_id[i],
                              promotePatten='Y/N', promoteTimeout=5)
                if CheckLine(data, 'Y/N') == 0:
                    SetCmd(switch, 'y', timeout=1)
                    break
                else:
                    IdleAfter(2)
            else:
                data = SetCmd(switch, 'wireless ap eth-parameter apply profile ' + profile_id[i], promoteTimeout=5)
                if CheckLine(data, 'wait a moment') == 0:
                    IdleAfter(2)
                else:
                    break
    IdleAfter(15)
    reslist = []
    for i in range(mult):
        reslist.append(0)
    for i in range(35):
        for j in range(mult):
            data = SetCmd(switch, 'show wireless ap status | include ' + apmac[j], timeout=1, includeCmd=False)
            flag = CheckLine(data, apmac[j] + '\\s+(\\d+\.){3}\\d+\\s+' + profile_id[j] + '\\s+Managed\\s+Success')
            if flag == 0:
                reslist[j] = 1
            else:
                reslist[j] = 0
        if 0 not in reslist:
            break
        else:
            IdleAfter(5)
            times = times + 1
    if times == 35:
        printRes("Ac manage ap failed!")
        return -1
    else:
        printRes("Ac manage ap successed!")
        return 0


#########################################
# WpaConnectWirelessNetworkCheck
#     profile 下发到ap
# args: 
#     switch：ac串口号
#     profile_id: profile number
#
# addition:
#
# examples:
#     WpaConnectWirelessNetworkCheck(sta1,15)
##########################################
def WpaConnectWirelessNetworkCheck(sta, Netcard_sta, Network_name, apmac, times=15):
    n = 0
    i_times = 0
    while i_times < times:
        CheckLineSsidScan(sta, Netcard_sta, Network_name, apmac, IC=True, scan_times=10)
        WpaDisconnectWirelessNetwork(sta[0], Netcard_sta[0])
        print(sta[0])
        print(Netcard_sta[0])
        res1 = WpaConnectWirelessNetwork(sta[0], Netcard_sta[0], Network_name[0], dhcpFlag=False, bssid=apmac[0])
        if res1 == 0:
            break
        else:
            i_times += 1
            n = i_times
    if n == times:
        printRes("sta connect to ssid failed!")
        return -1
    else:
        printRes("sta connect to ssid successed!")
        return 0


#########################################
# WpaConnectWirelessNetworkCheck
#     profile 下发到ap
# args: 
#     switch：ac串口号
#     profile_id: profile number
#
# addition:
#
# examples:
#     WpaConnectWirelessNetworkCheck(sta1,15)
##########################################
def WpaConnectWirelessNetworkMultiCheck(sta, Netcard_sta, Network_name, apmac, times=15):
    n = 0
    i_times = 0
    while i_times < times:
        CheckLineSsidScan(sta, Netcard_sta, Network_name, apmac, IC=True, scan_times=10)
        WpaDisconnectWirelessNetwork(sta[0], Netcard_sta[0])
        WpaDisconnectWirelessNetwork(sta[1], Netcard_sta[1])
        res1 = WpaConnectWirelessNetwork(sta[0], Netcard_sta[0], Network_name[0], dhcpFlag=False, bssid=apmac[0])
        res2 = WpaConnectWirelessNetwork(sta[1], Netcard_sta[1], Network_name[1], dhcpFlag=False, bssid=apmac[1])
        if res1 != 0 and res2 == 0:
            res3 = WpaConnectWirelessNetworkCheck([sta[0]], [Netcard_sta[0]], [Network_name[0]], [apmac[0]],
                                                  times=15 - i_times)
            if res3 == 0:
                break
            else:
                i_times = times
                n = times
        elif res1 == 0 and res2 != 0:
            res4 = WpaConnectWirelessNetworkCheck([sta[1]], [Netcard_sta[1]], [Network_name[1]], [apmac[1]],
                                                  times=15 - i_times)
            if res4 == 0:
                break
            else:
                i_times = times
                n = times
        elif res1 != 0 and res2 != 0:
            WpaDisconnectWirelessNetwork(sta[0], Netcard_sta[0])
            WpaDisconnectWirelessNetwork(sta[1], Netcard_sta[1])
            res5 = WpaConnectWirelessNetwork(sta[0], Netcard_sta[0], Network_name[0], dhcpFlag=False, bssid=apmac[0])
            res6 = WpaConnectWirelessNetwork(sta[1], Netcard_sta[1], Network_name[1], dhcpFlag=False, bssid=apmac[1])
            if res5 == 0 and res6 == 0:
                break
            else:
                i_times = i_times + 1
                n = n + 1
        else:
            break
    if n == times:
        printRes("sta connect to ssid failed!")
        return -1
    else:
        printRes("sta connect to ssid successed!")
        return 0


#########################################
# GetStaIpAddress
#     获取sta的ip地址
# args: 
#     sta：sta串口号
#     Netcard_sta:网卡名
#
# addition:
#
# examples:
#     GetStaIpAddress(sta1,wlan0)
##########################################	
def GetStaIpAddress(sta, Netcard_sta):
    data = SetCmd(sta, 'ifconfig ' + Netcard_sta)
    flag = re.search('inet.*?((\\d+\.){3}\\d+)\s+netmask', data, re.S)
    if flag != None:
        sta_ipv4 = flag.group(1)
        print('sta ipv4 address is ' + sta_ipv4 + '!')
        return sta_ipv4
    else:
        print('sta has no ipv4 address!')
        return ''


#########################################
# CheckStaScanSSID
#     检查sta是否能成功扫描出ssid
# args: 
#     sta：sta串口号
#     Netcard_sta:网卡名
#
# addition:
#
# examples:
#     CheckStaScanSSID(sta1,wlan0)
##########################################	
def CheckStaScanSSID(sta, Netcard_sta):
    mult = len(sta)
    times = 0
    res = [0, 0]
    for j in range(5):
        for i in range(mult):
            if j == 0:
                for k in range(3):
                    StaScanSSID(sta[i], Netcard_sta[i])
                    IdleAfter(3)
                    SetCmd(sta[i], 'wpa_cli -i ' + Netcard_sta[i] + ' scan_results')
            else:
                StaScanSSID(sta[i], Netcard_sta[i])
                IdleAfter(3)
                data = SetCmd(sta[i], 'wpa_cli -i ' + Netcard_sta[i] + ' scan_results')
                flag = re.search('(..:){5}..', data)
                if flag == None:
                    SetCmd(sta[i], 'rmmod iwldvm')
                    SetCmd(sta[i], 'rmmod iwlwifi')
                    IdleAfter(5)
                    SetCmd(sta[i], 'modprobe iwlwifi')
                    SetCmd(sta[i], 'airmon-ng start ' + Netcard_sta[i])
                    SetCmd(sta[i], 'pkill -9 wpa_supplicant')
                    IdleAfter(3)
                    SetCmd(sta[i], 'wpa_supplicant -B -i ' + Netcard_sta[
                        i] + ' -c /etc/wpa_supplicant/wpa_supplicant.conf -f /tmp/wpa_log/%s.log' % Netcard_sta[i])
                    if i == 0:
                        res[i] = 0
                    else:
                        res[i] = res[i - 1]
                else:
                    res[i] = 1
        if res[i] == 1:
            break
        else:
            IdleAfter(5)
            times = times + 1
    if times == 5:
        printRes("sta can not scan ssid successfully!")
        return -1
    else:
        printRes("Ac manage ap successed!")
        return 0


#########################################
# StaCaptureTcpDump
#     在station上使用tcpdump在指定无线网口抓包
# args: 
#     sta：需要进行抓包的station
#     NetcardName: sta 的无线网卡名称，如 "wlan0","wls224"
#     
# return: 
#     '': 失败
#     文件名: 成功
#
# addition:
#
# examples:
#     
##########################################
def StaCaptureTcpDump(sta, netcardName, **args):
    # 停止之前的抓包进程
    SetCmd(sta, 'pkill tcpdump')
    this_time = time.strftime('[%Y-%m-%d][%H-%M-%S]', time.localtime(time.time()))
    filename = '/tmp/capture/packetpcap' + this_time
    # 抓包命令行
    capture_cmd = 'nohup tcpdump -i ' + netcardName
    if 'protocol' in args:
        capture_cmd = capture_cmd + ' ' + args['protocol']
    if 'srcip' in args:
        capture_cmd = capture_cmd + ' src host ' + args['srcip']
    if 'dstip' in args:
        capture_cmd = capture_cmd + ' dst host ' + args['dstip']
    if 'srcport' in args:
        capture_cmd = capture_cmd + ' src port ' + args['srcport']
    if 'dstport' in args:
        capture_cmd = capture_cmd + ' dst port ' + args['dstport']
    if 'count' in args:
        capture_cmd = capture_cmd + ' -c ' + args['count']
    if 'filesize' in args:
        capture_cmd = capture_cmd + ' -C ' + args['filesize']
    if 'second' in args:
        capture_cmd = capture_cmd + ' -G ' + args['second']
    capture_cmd = capture_cmd + ' -w ' + filename + '.pcap &'
    SetCmd(sta, capture_cmd)
    data = SetCmd(sta, 'ps -aux | grep tcpdump')
    if CheckLine(data, capture_cmd) == 0:
        SetCmd(sta, 'pkill tcpdump')
        return filename + '.pcap'
    else:
        return ''


#########################################
# CMDKillFirefox
#     使用命令行关闭firefox浏览器页面
# args: 
#     sta：需要关闭firefox浏览器的客户端
#
# addition:
#
# examples:
#     CMDKillFirefox(sta1)
##########################################	
def CMDKillFirefox(sta):
    SetCmd(sta, '\n')
    data = SetCmd(sta, 'ps aux | grep firefox')
    firefox = re.findall('[a-zA-Z]+\s+(\d+)\s+', data, re.MULTILINE)
    print('firefox=', firefox)
    if None != firefox:
        for everyID in firefox:
            SetCmd(sta, 'kill ' + everyID)


#########################################
# GetApMac
# 
# function:
#     获取AP的MAC地址
# args: 
#     sut: AP
#     
#
# return: AP的MAC地址
#
# examples:
#     GetApMac(ap1)
##########################################       
def GetApMac(sut, apcmdtype):
    SetCmd(sut, '\n')
    data = ApSetcmd(sut, apcmdtype, 'getsystem', 'detail')
    apmac_type1 = str(GetValueBetweenTwoValuesInData(data, 'mac\s+', '\n')).lstrip().rstrip()
    apmac_list = str(apmac_type1).split(':')
    apmac = '-'.join(apmac_list).lower()
    apmac_type1 = apmac_type1.lower()
    return {'-': apmac, ':': apmac_type1}


#########################################
# GetAcType
# 
# function:
#     获取AC的Type值
# args: 
#     sut: AC   
# return: AP的Type值,字符串类型
# examples:
#     GetAcType(switch1)
########################################## 
def GetAcType(sut):
    EnterEnableMode(sut)
    data = SetCmd(sut, 'show vendor | include DevType', includeCmd=False)
    actypetemp = re.search('DevType\(ID\)\s+\d+\s+(\d+)\s', data, re.I)
    actype = actypetemp.group(1).strip()
    print(str(sut), 'type is', actype)
    return actype


#########################################
# ApLogin
# 
# function:
#     输入用户名和密码登陆Ap
# args: 
#     sut: ap1  
#     retry:登陆失败后的重试次数 
# examples:
#     ApLogin(ap1)
########################################## 
def ApLogin(sut, Ap_login_name='admin', Ap_login_password='admin', retry=3):
    res = 1
    for i in range(retry):
        data = SetCmd(sut, '\n', promoteStop=True, promotePatten=r'#|login',
                      promoteTimeout=5)
        if re.search(r'.*?#\s+', data) and not re.search(r'login', data):
            return 0
        elif re.search(r'login', data):
            SetCmd(sut, Ap_login_name, promoteStop=True, promotePatten='Password', promoteTimeout=10, IC=True)
            data = SetCmd(sut, Ap_login_password, promoteStop=True, promotePatten=r'#')
            if re.search(r'.*?#\s+', data):
                return 0
        else:
            IdleAfter(3)
    return res


#########################################
# GetStaMac
# 
# function:
#     获取sta的MAC地址
# args: 
#     sut: sta  
#     Netcard_sta:网卡名称
#     connectflag:MAC地址的连接符，':'或者'-'
# examples:
#     GetStaMac(sta1,connectflag=':')
########################################## 
def GetStaMac(sut, Netcard_sta='wls224', connectflag='-'):
    SetCmd(sut, '\n')
    # data = SetCmd(sut, 'ifconfig -v', Netcard_sta, promotePatten='#', timeout=20)
    data = SetCmd(sut, 'ifconfig -v', Netcard_sta, promoteStop=True, promotePatten='txqueuelen')
    stamac_memory = re.search('\w\w:\w\w:\w\w:\w\w:\w\w:\w\w', data)
    stamac_type1 = stamac_memory.group(0)
    stamac_list = str(stamac_type1).split(':')
    stamac = '-'.join(stamac_list).lower()
    if connectflag == '-':
        return stamac
    if connectflag == ':':
        return stamac_type1


# #########################################
#  control_c
#
# function:
#     输入Control+C
# args:
#     dev: 客户端，如linux switch ap等设备
# examples:
# #########################################


def control_c(dev):
    SetCmd(dev, '\n')
    time.sleep(0.2)
    SetCmd(dev, '\x03')
    time.sleep(0.2)
    SetCmd(dev, '\n')


# #########################################
#  control_o
#
# function:
#     输入Control+O
# args:
#     dev: 客户端，如linux switch ap等设备
# examples:
# #########################################


def control_o(dev):
    SetCmd(dev, '\x0F')
    time.sleep(0.2)


#########################################
# GetStaIp
# 
# function:
#     获取sta的IP地址
# args: 
#     sta: 客户端，如sta1
#     Netcard_sta:网卡名称
#     checkippool:ip地址所属的地址范围，默认为None，即不需判断客户端ip所属的范围
#     v4v6flag:判断需要获取ipv4地址还是ipv6地址
# examples:
#     res = GetStaIp(sta1)[res]
#     sta1ip = GetStaIp(sta1)[ip]
##########################################

def GetStaIp(sta, Netcard_sta='wls224', checkippool=None, v4v6flag='ipv4'):
    # type: (object, object, object, object) -> object
    """

    :rtype: dict
    """

    def _get_sta_ip():
        SetCmd(sta, '\n')
        data, search_result = '', ''
        # 针对此处容易出错的地方增加循环获取ip地址的操作
        for x in range(3):
            # data = SetCmd(sta, 'ifconfig -v', Netcard_sta)
            data = Receiver(sta, 'ifconfig -v ' + Netcard_sta,
                            promotePatten='inet.*?((2[0-4]\d|25[0-5]|[01]?\d\d?)\.){3}(2[0-4]\d|25[0-5]|[01]?\d\d?)',
                            promoteStop=True)
            if data:
                break
            time.sleep(0.1)
        if not data:
            pp.common_print(sta, 'ifconfig -v {}'.format(Netcard_sta), 'fail', 'can not get buffer from the command of '
                                                                               'setcmd ')
            assert data, 'data is none'
        if v4v6flag == 'ipv4':
            search_result = re.search('inet.+?(\d+\.\d+\.\d+\.\d+)\s+', data, re.I)
        elif v4v6flag == 'ipv6':
            search_result = re.search('inet6\s+(.*)\s+', data, re.I)
        if search_result:
            return search_result.group(1)
        else:
            return 0

    def _check_ip_in_pool(ip, pool):
        if ip:
            if re.search(pool, ip):
                return 1
            else:
                return 0

    res, sta_ip = 1, '7.7.7.7'
    _ip_address = _get_sta_ip()
    if _ip_address:
        sta_ip = _ip_address
        if checkippool:
            if _check_ip_in_pool(_ip_address, checkippool):
                res = 0
                printRes(str(sta) + ' ip address: ' + _ip_address)
            else:
                res = 2
                printRes('get address success but not match checkippool')
        else:
            return {'res': 0, 'ip': _ip_address}
    else:
        res = 1
        printRes('Failed: Get ip of ' + str(sta) + ' failed')
    return {'res': res, 'ip': sta_ip}


#########################################
# GetSwitchTime
# 
# function:
#     获取设备的当前时间
# args: 
#     sut: 设备，如AC1
#     retrytime:获取失败后的重试次数
# examples:
#     Ac1time = GetSwitchTime(ac1)
########################################## 
def GetSwitchTime(sut, retrytime=3):
    for i in range(retrytime):
        data = SetCmd(sut, 'show clock')
        actime = re.search('\w\w\w\s\w\w\w\s\d\d\s\d\d:\d\d:\d\d\s\d\d\d\d', data)
        if actime:
            return actime.group(0)


#########################################
# CheckSutCmd
# 
# function:
#     向设备输入命令，并检查打印是否符合预期
# args: 
#     sut: 设备，如AC1
#     cmd:需要向设备输入的命令，字符串格式
#     *args:需要检查的打印信息，格式为由元祖组成的列表，如[('1','Managed','Success'),('2','Managed','Success')]
#     waittime:向设备输入命令后等待打印回显的时间
#     retry：检查打印信息失败后重试次数
#     interval:每次重试之间的等待时间
#     **flag:可选的标志位[RS:列敏感]
# examples:
#     res = CheckSutCmd(ac1,'show wireless ap status',[('1','Managed','Success'),('2','Managed','Success')],IC=True)
##########################################
def CheckSutCmd(sut, cmd, check=[], waittime=5, retry=10, interval=5, **flag):
    waitflag = True
    if 'waitflag' in list(flag.keys()):
        waitflag = flag['waitflag']
    for i in range(retry):
        if waitflag:
            data = SetCmd(sut, cmd, timeout=waittime)
        else:
            data = SetCmd(sut, cmd)
        res = CheckLineList(data, check, **flag)
        if res == 0:
            break
        IdleAfter(interval)
    return res


#########################################
# CheckSutCmdWithNoExpect
# 
# function:
#     向设备输入命令，并检查打印是否符合预期(用于检查特定字符串没有出现在打印中）
# args: 
#     sut: 设备，如AC1
#     cmd:需要向设备输入的命令，字符串格式
#     *args:需要检查的打印信息，格式为由元祖组成的列表，如[('1','Managed','Success'),('2','Managed','Success')]
#     waittime:向设备输入命令后等待打印回显的时间
#     retry：检查打印信息失败后重试次数
#     interval:每次重试之间的等待时间
#     **flag:可选的标志位[RS:列敏感]
# examples:
#     res = CheckSutCmd(ac1,'show wireless ap status',[('1','Managed','Success'),('2','Managed','Success')],IC=True)
##########################################
def CheckSutCmdWithNoExpect(sut, cmd, check=[], waittime=5, retry=10, interval=5, **flag):
    waitflag = True
    if 'waitflag' in list(flag.keys()):
        waitflag = flag['waitflag']
    for i in range(retry):
        if waitflag:
            data = SetCmd(sut, cmd, timeout=waittime)
        else:
            data = SetCmd(sut, cmd)
        res = CheckLineList(data, check, **flag)
        if res != 0:
            break
        IdleAfter(interval)
    res = 0 if res != 0 else 1
    return res


#########################################
# SshLogin
# 
# function:
#     ssh登陆到其他设备
# args: 
#     sut: 设备，如sta1
#     ip:ssh服务器ip地址
#     loginname:ssh服务器登陆用户名
#     login_password:ssh服务器登陆密码
#     check:输入ssh命令后的返回值，默认为'yes/no'
#     retry：重试次数，默认次数为1，即不重试
#     interval:每次重试之间的等待时间
#     **flag:可选的标志位[RS:列敏感]
# examples:
#     res = 
##########################################
def SshLogin(sut, ip, loginname, loginpassword, options='', check='yes/no', retry=1, timeout1=5, timeout2=5, timeout3=5,
             failflag=False):
    res = 1
    for i in range(retry):
        data = SetCmd(sut, 'ssh', options, loginname + '@' + ip, timeout=timeout1)
        if 0 == CheckLine(data, check):
            res = 2
            if failflag:
                SetCmd(sut, '\x03')
                return res
            SetCmd(sut, 'yes', timeout=timeout2)
            for j in range(3):
                data = SetCmd(sut, loginpassword, timeout=timeout3)
                if CheckLine(data, 'Permission denied', IC=True) != 0:
                    res = 0
                    break
        if res == 0:
            break
    return res


#########################################
# ClearNetworkConfig
# 
# function:
#     清除AC上network中的配置
# args: 
#     sut: 设备，如switch1
#     network:network名称，如'1'
# examples:
#     ClearNetworkConfig(switch1,'1')
##########################################
def ClearNetworkConfig(sut, network):
    EnterNetworkMode(sut, network)
    SetCmd(sut, 'clear', promotePatten='Y/N', promoteTimeout=10)
    SetCmd(sut, 'y', timeout=3)


#########################################
# ClearProfileConfig
# 
# function:
#     清除AC上ap profile中的配置
# args: 
#     sut: 设备，如switch1
#     profile:profile名称，如'1'
# examples:
#     ClearProfileConfig(switch1,'1')
##########################################
def ClearProfileConfig(sut, profile):
    EnterApProMode(sut, profile)
    SetCmd(sut, 'clear', promotePatten='Y/N', promoteTimeout=10)
    SetCmd(sut, 'y', timeout=3)


#########################################
# ChangeAPMode(sut,switch)
# 
# function:
#     通过在AP上配置set managed-ap mode down/up命令使AP重新向AC发起认证
# args: 
#     ap: AP
#     apmac:ap的mac
#     switch:配置set managed-ap mode down命令前AP的管理AC，配置命令后AC上查询AP状态变为Failed
#     apcmdtype:ap的命令格式'set' or 'uci set'
# examples:
#     ChangeAPMode(ap,switch1)
##########################################
def ChangeAPMode(ap, apmac, switch, apcmdtype='set'):
    if apcmdtype == 'set':
        SetCmd(ap, 'set managed-ap mode down')
        res = CheckSutCmd(switch, 'show wireless ap status',
                          check=[(apmac, 'Failed', 'Not\s+Config')],
                          retry=5, interval=1, IC=True, waitflag=False)
        SetCmd(ap, 'set managed-ap mode up')
        return res
    if apcmdtype == 'uci':
        RebootAp(connectTime=5, AP=ap)


#########################################
# ApSetcmd(ap,cmdtype,*args,**kargs)
# 
# function:
#     在AP上下发命令，根据cmdtype参数的不同取值下发不同的命令，此函数主要目的是兼容
#     自I3R2后出现的支持uci形式命令的AP，或者将来出现其他命令形式的AP也可扩展兼容
# args: 
#     ap: 需要下发命令的AP设备
#     cmdtype:AP支持的命令形式，目前有两类，一类是'set'形式的，大部分AP支持
#          另一类是'uci'形式的，I3R2支持
#     *args:需要下发的命令
#     **kargs:下发命令时附带的参数，同SetCmd函数和Receiver函数的**args
# examples:
#     ApSetcmd(ap1,'uci','set_static_ip','1.1.1.1',timeout=5)
##########################################
def ApSetcmd(ap, cmdtype, *args, **kargs):
    cmddic = {}
    if args[0] == 'getsystem':
        cmddic = {'set': 'get system ', 'uci': 'get system '}
    if args[0] == 'set_dhcp_down':
        cmddic = {'set': 'set management dhcp-status down', 'uci': 'uci set mapd.@switch[0].dhcp_switch=\'0\''}
    if args[0] == 'set_dhcp_up':
        cmddic = {'set': 'set management dhcp-status up', 'uci': 'uci set mapd.@switch[0].dhcp_switch=\'1\''}
    if args[0] == 'set_dhcpv6_down':
        cmddic = {'set': 'set management dhcpv6-status down', 'uci': '\n'}
    if args[0] == 'set_dhcpv6_up':
        cmddic = {'set': 'set management dhcpv6-status up', 'uci': '\n'}
    if args[0] == 'set_static_ip':
        cmddic = {'set': 'set management static-ip ', 'uci': 'uci set mapd.@staticApIp[0].ap_ip='}
    if args[0] == 'set_static_ipv6':
        cmddic = {'set': 'set management static-ipv6 ', 'uci': '\n'}
    if args[0] == 'set_static_mask':
        cmddic = {'set': 'set management static-mask ', 'uci': 'uci set mapd.@staticApIp[0].ip_mask='}
    if args[0] == 'set_ip_route':
        cmddic = {'set': 'set static-ip-route gateway ', 'uci': 'uci set mapd.@staticApIp[0].ip_router='}
    if args[0] == 'set_ipv6_route':
        cmddic = {'set': 'set static-ipv6-route gateway ', 'uci': '\n'}
    if args[0] == 'set_static_ipv6_prefix_len':
        cmddic = {'set': 'set management static-ipv6-prefix-length ', 'uci': '\n'}
    if args[0] == 'saverunning':
        cmddic = {'set': 'save-running', 'uci': 'uci commit mapd\n\nubus call mapd load'}
    if args[0] == 'factoryreset':
        cmddic = {'set': 'factory-reset', 'uci': 'factory-reset'}
    if args[0] == 'set_management_vlanid':
        cmddic = {'set': 'set management vlan-id ', 'uci': 'uci set network.lan.manage_vlan='}
    if args[0] == 'set_untagged_vlanid':
        cmddic = {'set': 'set untagged-vlan vlan-id ', 'uci': 'uci set network.lan.untag_vlan='}
    if args[0] == 'set_switch_address1':
        cmddic = {'set': 'set managed-ap switch-address-1 ', 'uci': 'uci set mapd.@staticAcIp[0].static_acip_1='}
    if args[0] == 'set_switch_address':
        if 'addressnum' in kargs:
            num = str(kargs['addressnum'])
            del kargs['addressnum']
        else:
            num = '1'
        cmddic = {'set': 'set managed-ap switch-address-' + num + ' ',
                  'uci': 'uci set mapd.@staticAcIp[0].static_acip_' + num + '='}
    if args[0] == 'set_switch_address_ipv6':
        if 'addressnum' in kargs:
            num = str(kargs['addressnum'])
            del kargs['addressnum']
        else:
            num = '1'
        cmddic = {'set': 'set managed-ap switch-ipv6-address-' + num + ' ', 'uci': '\n'}
    if args[0] == 'cp_debug vap_config':
        cmddic = {'set': 'cp_debug vap_config', 'uci': 'ubus call portal debug \'{\"display_config\":\"\"}\''}
    if args[0] == 'cp_debug whitelist_hostname':
        cmddic = {'set': 'cp_debug whitelist_hostname', 'uci': 'ubus call portal debug \'{\"display_config\":\"\"}\''}
    if args[0] == 'cp_debug whitelist_ip':
        cmddic = {'set': 'cp_debug whitelist_ip', 'uci': 'ubus call portal debug \'{\"display_config\":\"\"}\''}
    if args[0] == 'cp_debug blacklist_hostname':
        cmddic = {'set': 'cp_debug blacklist_hostname', 'uci': 'ubus call portal debug \'{\"display_config\":\"\"}\''}
    if args[0] == 'cp_debug blacklist_ip':
        cmddic = {'set': 'cp_debug blacklist_ip', 'uci': 'ubus call portal debug \'{\"display_config\":\"\"}\''}
    if args[0] == 'firmware_upgrade':
        cmddic = {'set': 'firmware-upgrade tftp://', 'uci': 'firmware-upgrade tftp://'}
    cmd = cmddic[cmdtype]
    if len(args) > 1:
        if cmd != '\n':
            for i in args[1:]:
                cmd = cmd + i
    if 'commitflag' in list(kargs.keys()):
        commitflag = kargs['commitflag']
        del kargs['commitflag']
    else:
        commitflag = False
    data = SetCmd(ap, cmd, **kargs)
    if cmdtype == 'uci' and commitflag:
        if 'mapd' in cmd:
            module = 'mapd'
            SetCmd(ap, 'uci commit ' + module)
            SetCmd(ap, 'ubus call ' + module + ' load')
        elif 'portal' in cmd:
            module = 'portal'
            SetCmd(ap, 'uci commit ' + module)
            SetCmd(ap, 'ubus call ' + module + ' load')
        elif r'network.lan.' in cmd:
            SetCmd(ap, 'ubus call wifi eth_vlan')
        else:
            pass
    return data


#########################################
# Get_ap_cmdtype(ap)
# 
# function:
#     判断Ap的命令格式是属于'set management static-ip'类型还是'uci set mapd.@staticApIp[0].ap_ip='类型
# args: 
#     ap: 需要下发命令的AP设备
# examples:
#     Get_ap_cmdtype(ap1)
##########################################		
def Get_ap_cmdtype(ap):
    cmdtype = ''
    data = SetCmd(ap, 'uci show mapd') or SetCmd(ap, 'uci show mapd', timeout=3)
    if CheckLine(data, 'mapd\.', PM=False) == 0:
        cmdtype = 'uci'
    elif CheckLine(data, 'Invalid command', PM=False) == 0 or CheckLine(data, 'not found', PM=False) == 0:
        data1 = SetCmd(ap, 'get system') or SetCmd(ap, 'get system', timeout=3)
        if CheckLine(data1, 'version', PM=False) == 0:
            cmdtype = 'set'
    else:
        pass
    # 增加判断如果获取不到cmdtype出发异常，脚本终止
    if not cmdtype:
        print('Warning:can not get ap cmdtype!!!!!!\nPlease check or rerun')
        raise ValueError
    # print str(ap) + 'cmdtype=', cmdtype
    return cmdtype


#########################################
# Get_apversion_fromac(ac,apmac)
# 
# function:
#     通过AC上的show wireless ap version status命令获取AP的版本信息
# args: 
#     ac: 需要下发show wireless ap version status命令的AC设备
#     apmac: 需要获取版本信息的AP的mac
# examples:
#     Get_apversion_fromac(switch1,00-03-0f-20-d9-40)
##########################################		
def Get_apversion_fromac(ac, apmac):
    data = SetCmd(ac, 'show wireless ap version status')
    temp = re.search(apmac + '\s+(.*?)\s+', data)
    if temp:
        apversion = temp.group(1)
        print('apversion is', apversion)
        return apversion
    else:
        print('Can not get ap version,please check!!!!!!')
        return 1


#########################################
# Get_switch_version(sut)
# 
# function:
#     获取交换机版本信息
# args: 
#     sut: 设备名称
# examples:
#     Get_switch_version(switch1)
##########################################	
def Get_switch_version(sut):
    EnterEnableMode(sut)
    data = SetCmd(sut, 'show version')
    temp = re.search('Version ([^\n ]+)', data)
    if temp:
        sutversion = temp.group(1)
        print(str(sut), 'version is', sutversion)
        return sutversion
    else:
        print('Can not get', str(sut), 'version,please check!!!!!!')


#########################################
# Get_ap_version(sut,apcmdtype)
# 
# function:
#     获取AP版本信息
# args: 
#     sut: 设备名称
#     apcmdtype:ap的命令格式'set' or 'uci set'
# examples:
#     Get_ap_version(ap1,Ap1cmdtype)
##########################################	
def Get_ap_version(sut, apcmdtype='set'):
    data = ApSetcmd(sut, apcmdtype, 'getsystem', 'detail')
    temp = re.search('version\s+([^\n ]+)', data)
    if temp:
        sutversion = temp.group(1)
        print(str(sut), 'version is', sutversion)
        return sutversion
    else:
        print('Can not get', str(sut), 'version,please check!!!!!!')


#########################################
# Get_ap_hwtype(sut,apcmdtype)
# 
# function:
#     获取APtype信息
# args: 
#     sut: 设备名称
#     apcmdtype:ap的命令格式'set' or 'uci set'
# examples:
#     Get_ap_hwtype(ap1,Ap1cmdtype)
##########################################	
def Get_ap_hwtype(sut, apcmdtype='set'):
    data = ApSetcmd(sut, apcmdtype, 'getsystem', 'device-type')
    temp = re.search('(\d+)', data)
    if temp:
        suttype = temp.group(1)
        print(str(sut), 'type is', suttype)
        return suttype
    else:
        print('Can not get', str(sut), 'type,please check!!!!!!')


##################################################################################
## Check_ap_dhcpstatus(ap,cmdtype,type,version)
##
## function:
##     检查AP的dhcp状态
## args:
##     ap: 需要下发命令的AP设备
##     cmdtype:AP支持的命令形式，目前有两类，一类是'set'形式的，大部分AP支持
##          另一类是'uci'形式的，I3R2支持
##     type:预期AP的dhcp状态，up 或者down
## examples:
##     Check_ap_dhcpstatus(ap1,'uci',type='up')
###################################################################################
def Check_ap_dhcpstatus(ap, cmdtype, type, version='ipv4'):
    _res = 1
    if cmdtype == 'set':
        if version == 'ipv4':
            data = SetCmd(ap, 'get management dhcp-status')
            _res = CheckLine(data, type)
        else:
            data = SetCmd(ap, 'get management dhcpv6-status')
            _res = CheckLine(data, type)
    elif cmdtype == 'uci':
        type = '1' if type == 'up' else '0'
        data = SetCmd(ap, 'uci show mapd')
        _res = CheckLine(data, 'dhcp_switch=\'' + type + '\'')
    return _res


##################################################################################
## Check_ap_ip(ap,cmdtype,ip,mode='ip',ipversion='ipv4')
##
## function:
##     检查AP的ip
## args:
##     ap: 需要下发命令的AP设备
##     cmdtype:AP支持的命令形式，目前有两类，一类是'set'形式的，大部分AP支持
##          另一类是'uci'形式的，I3R2支持
##     ip:预期AP的ip地址
##     mode:ip的类型，有三种,static：静态配置IP；ip:Ap当前的IP地址；dhcp:AP通过dhcp获取到的ip地址
##     ipversion:ipv4 or ipv6
## examples:
##     Check_ap_ip(ap1,'uci','192.168.10.1')
###################################################################################
def Check_ap_ip(ap, cmdtype, ip, mode='ip', ipversion='ipv4'):
    _res = 1
    if cmdtype == 'set':
        ipversion_str = 'ip' if ipversion == 'ipv4' else 'ipv6'
        data = SetCmd(ap, 'get management')
        if mode == 'ip' or mode == 'dhcp':
            result = re.search(ipversion_str + '\s+' + ip, data, re.M)
        elif mode == 'staticip':
            result = re.search('static-' + ipversion_str + '\s+' + ip, data, re.M)
        if result:
            _res = 0
    elif cmdtype == 'uci':
        data = SetCmd(ap, 'uci show mapd')
        _res = CheckLine(data, 'staticApIp[0].ap_ip=\'' + ip)
    return _res


##################################################################################
## Check_ap_provision_switchip(ap,cmdtype,ip,mode='primary',ipversion='ipv4')
##
## function:
##     检查AP上通过AC下发获得的switchip
## args:
##     ap: 需要下发命令的AP设备
##     cmdtype:AP支持的命令形式，目前有两类，一类是'set'形式的，大部分AP支持
##          另一类是'uci'形式的，I3R2支持
##     ip:预期的switchip地址
##     mode:primary 或者backup(I3R2目前不支持backup)
##     ipversion:ipv4 or ipv6
## examples:
##     Check_ap_provision_switchip(ap1,'uci','192.168.10.1',mode='primary',ipversion='ipv4')
###################################################################################
def Check_ap_provision_switchip(ap, cmdtype, ip, mode='primary', ipversion='ipv4'):
    _res = 1
    if cmdtype == 'set':
        ipversionstr = 'ip' if ipversion == 'ipv4' else 'ipv6'
        data = SetCmd(ap, 'get map-ap-provisioning')
        if mode == 'primary':
            _res = CheckLine(data, 'primary-switch-' + ipversionstr + '-address\s+' + ip)
        elif mode == 'backup':
            _res = CheckLine(data, 'backup-switch-' + ipversionstr + '-address\s+' + ip)
    elif cmdtype == 'uci':
        if mode == 'primary':
            data = SetCmd(ap, 'uci show mapd')
            _res = CheckLine(data, 'provisionAcIp[0].primary_acip=\'' + ip)
        elif mode == 'backup':
            _res = 0
    return _res


##################################################################################
## Check_ap_static_switchip(ap,cmdtype,ip_list,address_num_list)
##
## function:
##     检查AP上手工配置的静态switchip
## args:
##     ap: 需要下发命令的AP设备
##     cmdtype:AP支持的命令形式，目前有两类，一类是'set'形式的，大部分AP支持
##          另一类是'uci'形式的，I3R2支持
##     ip_list:预期的静态switchip地址列表
##     address_num_list:静态switchip的序号列表，必须和ip_list一一对应
## examples:
##     Check_ap_static_switchip(ap1,'uci',['192.168.10.1'],address_num_list=['1'])
###################################################################################
def Check_ap_static_switchip(ap, cmdtype, ip_list, address_num_list, ipversion='ipv4'):
    _res = 0
    num = len(ip_list)
    if cmdtype == 'set':
        data = SetCmd(ap, 'get managed-ap')
        for k in range(num):
            if ipversion == 'ipv4':
                tempres = CheckLine(data, 'switch-address-' + str(address_num_list[k]), ip_list[k])
            else:
                tempres = CheckLine(data, 'switch-ipv6-address-' + str(address_num_list[k]), ip_list[k])
            _res += tempres
    elif cmdtype == 'uci':
        data = SetCmd(ap, 'uci show mapd')
        for k in range(num):
            tempres = CheckLine(data, 'staticAcIp[0].static_acip_' + str(address_num_list[k]), ip_list[k])
            _res += tempres
    return _res


##################################################################################
## Check_ap_automatic_switchip(ap,cmdtype,mode,ip_list,address_num_list,ipversion)
##
## function:
##     检查AP上通过dhcp server或者dns server自动获得的switchip
## args:
##     ap: 需要下发命令的AP设备
##     cmdtype:AP支持的命令形式，目前有两类，一类是'set'形式的，大部分AP支持
##          另一类是'uci'形式的，I3R2支持
##     ip_list:预期的静态switchip地址列表,I3R2的Ip的显示为十六进制
##     address_num_list:静态switchip的序号列表，必须和ip_list一一对应
##     mode:dhcp或者dns，分别代表AP通过dhcp server或者dns server获取switchip
## examples:
##     Check_ap_automatic_switchip(ap1,'uci','192.168.10.1',mode='dhcp')
###################################################################################
def Check_ap_automatic_switchip(ap, cmdtype, mode, ip_list, address_num_list, ipversion='ipv4'):
    _res = 0
    num = len(ip_list)
    if cmdtype == 'set':
        data = SetCmd(ap, 'get managed-ap')
        for k in range(num):
            if ipversion == 'ipv6' and mode == 'dhcp':
                tempres = CheckLine(data, 'dhcpv6-switch-ipv6-address-' + address_num_list[k], ip_list[k])
            else:
                tempres = CheckLine(data, mode + '-switch-address-' + address_num_list[k], ip_list[k])
            _res += tempres
    elif cmdtype == 'uci':
        data = SetCmd(ap, 'ubus call mapd show_disc_info')
        for k in range(num):
            # 将IP转换为十六进制
            for j in range(4):
                temp_list[j] = int(temp_list[j])
                if j != 0:
                    temp_list[j] = '%02x' % temp_list[j]
                else:
                    temp_list[j] = '%x' % temp_list[j]
            hex_ip = ''.join(temp_list)
            tempres = CheckLine(data, mode, 'sw ip[' + str(address_num_list[k] - 1) + ']', hex_ip, IC=True)
            _res += tempres
    else:
        _res = 1
    return _res


##################################################################################
## Check_ap_dnsserver_ip(ap,cmdtype,dns_ip)
##
## function:
##     检查AP上的dns server的ip地址
## args:
##     ap: 需要下发命令的AP设备
##     cmdtype:AP支持的命令形式，目前有两类，一类是'set'形式的，大部分AP支持
##          另一类是'uci'形式的，I3R2支持
##     dns_ip:预期的静态dns server的ip地址
## examples:
##     Check_ap_dnsserver_ip(ap1,'uci','192.168.10.1')
###################################################################################
def Check_ap_dnsserver_ip(ap, cmdtype, dns_ip):
    _res = 1
    if cmdtype == 'set':
        data = SetCmd(ap, 'get host')
        _res = CheckLine(data, 'dns-1 ', dns_ip)
    elif cmdtype == 'uci':
        data = SetCmd(ap, 'cat /etc/resolv.conf')
        _res = CheckLine(data, 'nameserver', dns_ip)
    return _res
