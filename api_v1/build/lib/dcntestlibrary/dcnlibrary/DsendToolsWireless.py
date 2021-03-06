# -*- coding: UTF-8 -*-
# *********************************************************************
# DsendToolsWireless.py 
# 
# Author:  zhaohj@digitalchina.com
#
# Features: 
#           used by dcn auto generating packet wireless tool
# 
# *********************************************************************
# Change log:
#     - 2011.11.7  added by zhaohj
# *********************************************************************
import re
from dautolibrary.dautoconnections.connDsend.dsend import *
from dutils.dcnprint import printRes


##################################################################################
# 
# SetDsendStreamWireless:配置某一个端口的某一条流
#    
# args:
#	  
#     Port : 1
#     PortTypeConfig : 0 :发包端口的类型，0：wlan，1：mon，默认为0
#     StreamMode 0 : 0:contine   1:stop after send  2:more than one stream on one port  默认为0
#     StreamNum 1 ：ixia端口模拟多条流时，各流的编号
#     LastStreamFlag true ：ixia端口模拟多条流时，该流是否为最后一条流
#     ReturnToId 1 ：ixia端口模拟多条流时，最后一条流的下一条流的编号
#     StreamRateMode : pps/bps
#     StreamRate : 100/100/102400
#     NumFrames : 100
#
#     SouMac : 00-00-00-00-00-01
#     SouNum : 1
#     DesMac : 00-00-00-00-00-02
#     DesNum : 1
#
#     FrameSize : 128 报文长度，默认128
#	
#
#     VlanTagFlag : 0   0:no vlan tag  1:exist one vlan tag  2:exist two vlan tag
#     VlanId : 3
#     Tpid : 8100
#     UserPriority : 5
#     Tpid1 : 9100
#     VlanId1 : 2
#     Tpid2 : 9200
#     VlanId2 : 3
#     
#     Protocl none : none/ipv4/arp/ipv6/ipv6ipv4  默认为none
#     EthernetType ethernetII  默认为ethernetII
#     
#	
#         SouIp 1.1.1.1
#         SouIpMode
#         SouIpNum 1
#	  DesIp 2.2.2.2
#	  DesIpMode ipIncrHost
#	  DesIpNum 1
#	  Fragment 0   :是否分片
#	  LastFragment 0 :是否分片的最后一片
#	
#
#         ArpOperation  1 :  1 request 2 reply
#	  SenderMac  00-00-00-00-00-01
#	  SenderMacNum  1
#	  TargetMac  00-00-00-00-00-02
#	  TargetMacNum 1
#	  SenderIp  1.1.1.1
#	  SenderIpNum  1
#	  TargetIp  2.2.2.2
#	  TargetIpNum 1 
#
#         SouIpv6    2003:0001:0002:0003:0000:0000:0000:0003
#	  SouNumv6   1
#	  DesIpv6    2003:0001:0002:0003:0000:0000:0000:0004  
#	  DesNumv6   1
#	  PriorityFlag 1  ;#1:Dscp 0:Tos 2:Ipprecedence 3:Ipprecedence&Tos
#	  Dscp 41
#	  Tos 4
#	  Ipprecedence 7
#	  TrafficClass 3
#	  FlowLabel 0
#         NextHeader ipV6NoNextHeader
#
#
# return: 
#     编辑一个报文，DsendWireless()
# 
# 
# examples: 
################
# 1、持续发送一条流：(发包速率不大于100pps)
# 脚本中的调用格式：
#    SetDsendStreamWireless(Port='2',PortTypeConfig='0',StreamMode='0',StreamRateMode='pps',StreamRate='10', FrameSize='64', \
#                   SouMac='00-00-00-00-00-01',SouNum='10',DesMac='00-00-00-00-00-04',DesNum='10')
# 实际发出的报文格式：
#    DsendWireless('''--port 2 --port2config 0 --proc setStream --streamMode pps --rate 10 --streamSize 64 --stream Ether(dst=incrMac1[incrCount],src=incrMac2[incrCount],type=0xffff) --incrMac1 00:00:00:00:00:04,10 --incrMac2 00:00:00:00:00:01,10''')
#################
# 2、发完一条流之后就停：（这种发包方式的个数会非常精确，利用的是sendp(count=n)），(发包速率不大于100pps)
# 脚本中的调用格式：
# 1)默认发1个
# SetDsendStreamWireless(Port='2',PortTypeConfig='0',StreamMode='1',StreamRateMode='pps',StreamRate='10', FrameSize='64', \
#                       SouMac='00-00-00-00-00-01',SouNum='10',DesMac='00-00-00-00-00-04',DesNum='10')
# 实际发出的报文格式：
#    DsendWireless('''--port 2 --port2config 0 --proc setStream --streamMode pps --rate 10 --streamSize 64 --stream Ether(dst=incrMac1[incrCount],src=incrMac2[incrCount],type=0xffff) --incrMac1 00:00:00:00:00:04,10 --incrMac2 00:00:00:00:00:01,10 --count 1 --mode 2''')
# 脚本中的调用格式：
# 2)可以设置发送的个数
# SetDsendStreamWireless(Port='2',PortTypeConfig='0',StreamMode='1',StreamRateMode='pps',StreamRate='10', FrameSize='64', \
#                       SouMac='00-00-00-00-00-01',SouNum='10',DesMac='00-00-00-00-00-04',DesNum='10',NumFrames='20')
# 实际发出的报文格式：
#    DsendWireless('''--port 2 --port2config 0 --proc setStream --streamMode pps --rate 10 --streamSize 64 --stream Ether(dst=incrMac1[incrCount],src=incrMac2[incrCount],type=0xffff) --incrMac1 00:00:00:00:00:04,10 --incrMac2 00:00:00:00:00:01,10 --count 20 --mode 2''')
######################
# 3、持续循环发送几条流：(发包速率不大于100pps)
# 脚本中的调用格式：
#    SetDsendStreamWireless(Port='2',PortTypeConfig='0',StreamMode='2',StreamRate='10',StreamRateMode='pps',NumFrames='10',FrameSize='64',LastStreamFlag='false', \
#		   DesMac='00-00-00-02-00-02',SouMac='00-00-00-01-00-01',SouNum='10')
#    SetDsendStreamWireless(Port='2',PortTypeConfig='0',StreamMode='2',StreamRate='10',StreamRateMode='pps',NumFrames='1',FrameSize='64',LastStreamFlag='true', \
#		   DesMac='00-00-00-00-00-04',SouMac='00-00-00-00-00-03')
# 实际发出的报文格式：
#    DsendWireless('''--port 2 --port2config 0 --proc setStream --streamMode pps --rate 10 --streamSize 64 --stream Ether(dst="00:00:00:02:00:02",src=incrMac1[incrCount],type=0xffff) --incrMac1 00:00:00:01:00:01,10 --lastStreamFlag 0 --countContinue 10''')
#    DsendWireless('''--port 2 --port2config 0 --proc setStream --streamMode pps --rate 10 --streamSize 64 --stream Ether(dst="00:00:00:00:00:04",src="00:00:00:00:00:03",type=0xffff) --lastStreamFlag 1 --countContinue 1 ''')
###############################################################################################################
def SetDsendStreamWireless(**args):
    # 需要用到的全局变量
    # 最后需要发送的流数据
    global dcnstream
    # 需要发送的数据流的参数列表
    global dcnarrArgs
    # 用于存储需要递增的报文域 :包括递增的类型(mac,ip,num),初始值，范围和步长；每条流的突发报文数目--countContinue；需要发送的报文数量(发完就停)--count,用于标识发送一定数量报文的发包速率是通过参数--rate指定:--mode 2
    global dcnincrlist
    # 用于记录是第几个需要变化的mac域类型
    global dcnincrmac
    # 用于记录是第几个需要变化的ip域类型
    global dcnincrip
    # 用于记录是第几个需要变化的num域类型
    global dcnincrnum
    # 用于记录是第几个需要变化的ipv6域类型
    global dcnincripv6
    # 待发送数据的速率模式
    global streamMode
    # 待发送数据的大小
    global streamSize

    # 初始化各全局变量
    dcnincrmac = 0
    dcnincrip = 0
    dcnincrnum = 0
    dcnincripv6 = 0
    # 初始化dcnincrlist为空列表
    dcnincrlist = []

    # 获取发包的速率模式--streamMode: pps,bps.默认为pps
    streamMode = GetRateMode(args)
    # 获取发包的默认速率--rate:1pps,1024bps
    GetDefaultStreamRate(args)
    # 获取发包的大小 --streamSize:默认128
    streamSize = GetStreamSize(args)

    # 构造需要发送的报文--stream(适合python scapy发送的报文结构，字符串格式,存储在dcnstream中)
    # 构造以太网报文头
    BuildEthernetII(args)

    # 下面可以添加各种报文

    # 二层报文头
    # 构造802.1q tag(vlan tag)
    BuildDot1Q(args)

    # 构造后续三层协议报文
    if 'Protocl' in args:
        if args['Protocl'] == 'arp':
            print('build arp packet')
            BuildArp(args)
        if args['Protocl'] == 'ipv4':
            print('build ipv4 packet')
            BuildIPv4(args)
        if args['Protocl'] == 'ipv6':
            print('build ipv6 packet')
            BuildIPv6(args)
        if args['Protocl'] == 'ipv6ipv4':
            print('build ipv4 over ipv6 tunnel packet')
            BuildIPv4OverIPv6(args)
    BuildPAYLOAD(args)
    BuildPCAPVALUE(args)
    # 添加报文结束

    # 针对发完一定数目报文就停的发包模式，比如--count 10 :标识该条流发完10个报文后停止
    SetStreamModeForStop(args)

    # 打印以方便调试
    # print args['Port']
    # print streamMode
    # print args['StreamRate']
    # print streamSize
    # print dcnstream

    # 变量 dcnarrArgs(PortTypeConfig)为1表示发包端口选择mon，为0表示选择wlan。默认为0
    if 'PortTypeConfig' in args:
        porttypename = ' --port' + args['Port'] + 'config '
        command = ("--port " + args['Port'] + porttypename + args[
            'PortTypeConfig'] + " --proc setStream " + "--streamMode " + streamMode + " --rate " + args[
                       'StreamRate'] + " --streamSize " + streamSize + " --stream " + dcnstream)
    else:
        command = ("--port " + args['Port'] + " --proc setStream " + "--streamMode " + streamMode + " --rate " + args[
            'StreamRate'] + " --streamSize " + streamSize + " --stream " + dcnstream)

    # 添加标识报文流是否为最后一条流的命令参数(存在多条流的情况才需要该参数),
    # 例如--lastStreamFlag 1
    AddLastStreamFlag(args)

    # 添加标识某条报文流的突发报文数量
    # 例如--countContinue 6 :标识该条流突发6条报文
    if 'NumFrames' in args and 'LastStreamFlag' in args and int(args['StreamMode']) == 2:
        print(args['NumFrames'])
        strinfo = '--countContinue ' + args['NumFrames']
        dcnincrlist.append(strinfo)

    # 添加报文中域值变化的相关命令参数例如--incrMac1 00:00:01:00:00:01,100 ;是否为最后一条流的命令参数例如--lastStreamFlag 1   ;流的突发数目:--countContinue 2;需要发送的数量:--count 10
    if len(dcnincrlist) >= 1:
        length = len(dcnincrlist)
        for i in range(length):
            command = command + ' ' + dcnincrlist[i]

        # 打印出命令，主要用于调试
    print(command)

    # 执行发包操作
    res = DsendWireless(command)
    print('SetDsendStreamWireless Res: ' + str(res))
    return res


##################################################################################
#
# GetRateMode :获取发送数据流的模式:pps,bps
#
#
# return: 数据流的模式:pps,bps
#
# addition:
#
# examples:
#     GetRateMode(args)
#
###################################################################################
def GetRateMode(args):
    if 'StreamRateMode' not in args:
        return 'pps'
    else:
        return args['StreamRateMode']


    ###################################################################################


#
# GetDefaultStreamRate :获取发送数据流的默认速率:1 pps,1024 bps
#
# args:  streamMode:数据流的发送模式:pps,bps
#
# examples:
#     GetDefaultStreamRate(pps,args)
#
#################################################################################### 
def GetDefaultStreamRate(args):
    global streamMode
    if 'StreamRate' not in args:
        if streamMode == 'pps':
            args['StreamRate'] = '1'
        if streamMode == 'bps':
            args['StreamRate'] = '1024'

        ##################################################################################


#
# GetStreamSize :获取发送数据流的报文大小
#
# args: 
#    args：全局参数
#
# return: 数据流的报文大小:指定大小或默认大小128byte
#
# addition:
#
# examples:
#     GetStreamSize(args)
#
###################################################################################
def GetStreamSize(args):
    if 'FrameSize' in args:
        return args['FrameSize']
    else:
        return '128'


##################################################################################
#
#  BuildEthernetII :构建由python scapy发送的EthernetII报文头，如Ether(....)
#
# args:  无
#
# return: 无
#
# addition:
#
# examples:
#     BuildEthernetII(args)
#
###################################################################################
def BuildEthernetII(args):
    global dcnstream
    dcnstream = "Ether("
    # 构造以太网的目的mac
    if 'DesMac' not in args:
        args['DesMac'] = '00-00-00-00-00-01'
    if 'DesNum' not in args:
        args['DesNum'] = '1'
    # 将mac的格式由00-00-00-00-00-01转化为00:00:00:00:00:01
    args['DesMac'] = re.sub('-', ':', args['DesMac'])
    # 构建目的mac域:覆盖两种处理情况连续变化和稳定不变
    BuildIncrField('dst', 'mac', args['DesMac'], args['DesNum'])

    # 构造以太网的源mac
    if 'SouMac' not in args:
        args['SouMac'] = '00-00-00-00-00-02'
    if 'SouNum' not in args:
        args['SouNum'] = '1'
    # 将mac的格式由00-00-00-00-00-01转化为00:00:00:00:00:01
    args['SouMac'] = re.sub('-', ':', args['SouMac'])
    # 构建目的mac域:覆盖两种处理情况连续变化和稳定不变
    BuildIncrField('src', 'mac', args['SouMac'], args['SouNum'])

    # 构造以太网的type，默认为0xffff(为了与有线发包工具的函数兼容)
    dcnstream = dcnstream + "type=0xffff)"


##################################################################################
#
# BuildIncrField  :构建由python scapy发送的报文中变化的域
#
# args:  name:域名，type:变化的类型，目前有三种:mac,ip和num;initi:变化的初始值；num:变化的范围数量
#          step为变化步长，duan为需要变化的字段具体位置
# return: 无
#
# addition:
#
# examples:
#     BuildIncrField('mac','dst','00:00:00:00:00:01','2',step='1',duan='128')
#
###################################################################################    
def BuildIncrField(name, type, initi, num, step='1', duan='64'):
    global dcnstream
    global dcnincrlist
    global dcnincrmac
    global dcnincrip
    global dcnincrnum
    global dcnincripv6

    if num == '1':
        if type == 'mac' or type == 'ip' or type == 'ipv6':
            dcnstream = dcnstream + name + '=' + '"' + initi + '"' + ','
        else:
            dcnstream = dcnstream + name + '=' + initi + ','
    else:
        if type == 'mac':
            dcnincrmac = dcnincrmac + 1
            dcnstream = dcnstream + name + '=incrMac' + str(dcnincrmac) + '[incrCount],'
            macliststr = "--incrMac" + str(dcnincrmac) + ' ' + initi + ',' + str(num)
            dcnincrlist.append(macliststr)
        if type == 'ip':
            dcnincrip = dcnincrip + 1
            dcnstream = dcnstream + name + '=incrIp' + str(dcnincrip) + '[incrCount],'
            ipliststr = "--incrIp" + str(dcnincrip) + ' ' + initi + ',' + str(num) + ',' + str(duan) + ',' + str(step)
            dcnincrlist.append(ipliststr)
        if type == 'num':
            dcnincrnum = dcnincrnum + 1
            dcnstream = dcnstream + name + '=incrNum' + str(dcnincrnum) + '[incrCount],'
            numliststr = "--incrNum" + str(dcnincrnum) + ' ' + initi + ',' + str(num)
            dcnincrlist.append(numliststr)
        if type == 'ipv6':
            dcnincripv6 = dcnincripv6 + 1
            dcnstream = dcnstream + name + '=incrIpv6' + str(dcnincripv6) + '[incrCount],'
            ipv6liststr = "--incrIpv6" + str(dcnincripv6) + ' ' + initi + ',' + str(num) + ',' + str(duan) + ',' + str(
                step)
            dcnincrlist.append(ipv6liststr)

        ##################################################################################


#
# SetStreamModeForStop :设置由python scapy发送报文的一种模式:发送一定数量的报文后停止
#
# args:  无
#
# return: 无
#
# addition:
#
# examples:
#     SetStreamModeForStop(args)
#
###################################################################################	    
def SetStreamModeForStop(args):
    global dcnarrArgs
    global dcnincrlist
    if 'StreamMode' in args:
        if args['StreamMode'] == '1':
            if 'NumFrames' in args:
                numframestr = '--count ' + args['NumFrames']
                dcnincrlist.append(numframestr)
            else:
                dcnincrlist.append('--count 1')


###################################################################################
#
# AddLastStreamFlag :对于待发送的多条流，需要添加参数--lastStreamFlag 0/1:
#                   1表示为最后一条流，0表示还有其它流
#
# args:  无
#
# return: 无
#
# addition:
#
# examples:
#     AddLastStreamFlag(args)
#     LastStreamFlag true/false
###################################################################################
def AddLastStreamFlag(args):
    global dcnincrlist
    if 'LastStreamFlag' in args:
        print(args['LastStreamFlag'])
        if args['LastStreamFlag'] == 'true':
            strinfo = '--lastStreamFlag 1'
            dcnincrlist.append(strinfo)
        if args['LastStreamFlag'] == 'false':
            strinfo = '--lastStreamFlag 0'
            dcnincrlist.append(strinfo)


##################################################################################
#
# BuildDot1Q :构建由python scapy发送的802.1q报文头，如Dot1Q(....)
#
# args:  无
#
# return: 无
#
# addition:
#
# examples:
#     BuildDot1Q(args)
# 脚本调用格式：	
##1）只带一层vlan tag，Tpid='9200',VlanId='33',UserPriority='5'：
#     SetDsendStreamWireless(Port='2',StreamRateMode='pps',StreamRate='10', FrameSize='64', \
#                    VlanTagFlag='1',Tpid='8100',VlanId='33',UserPriority='5', \
#		     SouMac='00-00-00-00-00-03',DesMac='00-00-00-00-00-04')
##2）只带一层vlan tag，vlanid从33递增10个	(步长只能为1)    
#     SetDsendStreamWireless(Port='2',StreamRateMode='pps',StreamRate='10', FrameSize='64', \
#                    VlanTagFlag='1',VlanId='33',VlanIdRepeat='10', \
#		     SouMac='00-00-00-00-00-03',DesMac='00-00-00-00-00-04')
##3）带2层vlan tag，外层tag：Tpid2='9200',VlanId2='33',UserPriority2='5',内层tag:Tpid1='8100',VlanId1='44',UserPriority2='6'.    
#     SetDsendStreamWireless(Port='2',StreamRateMode='pps',StreamRate='10', FrameSize='64', \
#                    VlanTagFlag='2',Tpid2='9200',VlanId2='33',UserPriority2='5', \
#                    Tpid1='8100',VlanId1='44',UserPriority2='6',\
#		     SouMac='00-00-00-00-00-03',DesMac='00-00-00-00-00-04')
###################################################################################				
def BuildDot1Q(args):
    global dcnstream
    global dcnincrnum
    global dcnincrlist

    if 'VlanTagFlag' in args:
        # 判断是否带802.1q tag
        if args['VlanTagFlag'] == '1':
            # 如果是带802.1q tag则修改前面获取的Dot1Q()中的type字段为用户指定值
            if 'Tpid' in args:
                strinfo = '0x' + args['Tpid']
                dcnstream = re.sub('0xffff', strinfo, dcnstream)
            # 如果是带802.1q tag,没有指定Tpid，则修改前面获取的Dot1Q()中的type字段为0x8100
            else:
                dcnstream = re.sub('0xffff', '0x8100', dcnstream)
            dcnstream = dcnstream + '/Dot1Q('
            if 'VlanId' in args:
                if 'VlanIdRepeat' not in args:
                    args['VlanIdRepeat'] = '1'
                if args['VlanIdRepeat'] == '1':
                    dcnstream = dcnstream + 'vlan=' + args['VlanId'] + ','
                else:
                    dcnincrnum = dcnincrnum + 1
                    dcnstream = dcnstream + 'vlan=incrNum' + str(dcnincrnum) + '[incrCount],'
                    strinfo = '--incrNum' + str(dcnincrnum) + ' ' + str(args['VlanId']) + ',' + args['VlanIdRepeat']
                    dcnincrlist.append(strinfo)
            if 'UserPriority' in args:
                dcnstream = dcnstream + 'prio=' + args['UserPriority'] + ','
            dcnstream = dcnstream + 'type=0xffff)'
        # 添加对DoubleTag 的支持
        if args['VlanTagFlag'] == '2':
            if 'Tpid2' in args:
                strinfo = '0x' + args['Tpid2']
                dcnstream = re.sub('0xffff', strinfo, dcnstream)
            else:
                dcnstream = re.sub('0xffff', '0x8100', dcnstream)
            # 内层vlan tag
            dcnstream = dcnstream + '/Dot1Q('
            if 'VlanId2' in args:
                dcnstream = dcnstream + 'vlan=' + args['VlanId2'] + ','
            if 'UserPriority2' in args:
                dcnstream = dcnstream + 'prio=' + args['UserPriority2'] + ','
            if 'Tpid1' in args:
                dcnstream = dcnstream + 'type=0x' + args['Tpid1'] + ')'
            else:
                dcnstream = dcnstream + 'type=0x8100)'
            # 外层vlan tag
            dcnstream = dcnstream + '/Dot1Q('
            if 'VlanId1' in args:
                dcnstream = dcnstream + 'vlan=' + args['VlanId1'] + ','
            if 'UserPriority1' in args:
                dcnstream = dcnstream + 'prio=' + args['UserPriority1'] + ','
            dcnstream = dcnstream + 'type=0xffff)'


##################################################################################
#
#  BuildPAYLOAD :构建由python scapy发送的用户自定义字段
#
# args:  无
#
# return: 无
#
# addition:
#
# examples:
#     BuildPAYLOAD(args)
# 脚本调用格式：
#     SetDsendStreamWireless(Port='2',StreamRateMode='pps',StreamRate='10', FrameSize='64', \
#                    SouMac='00-00-00-00-00-03',DesMac='00-00-00-00-00-04', \
#	             Payload='0102030405060708090a')
###################################################################################
def BuildPAYLOAD(args):
    global dcnstream
    if 'Payload' in args:
        dcnstream = dcnstream + '/"payloadflag' + args['Payload'].replace(' ', '') + 'payloadflag"'


##################################################################################
#
#  BuildPCAPVALUE :构建由python scapy发送的用户自定义字段,主要针对从.cap文件中读取的报文，经过修改后由该函数发送
#
# args:  无
#
# return: 无
#
# addition:
#
# examples:
#     BuildPCAPVALUE(args)
# 脚本调用格式：
#     SetDsendStreamWireless(Port='2',StreamRateMode='pps',StreamRate='10', FrameSize='64', \
#	                     Pcapvalue='0102030405060708090a')
# 典型应用：
#     1)从.cap文件中读取一个报文，并修改其中0~2个字段：pktstr=ReadPcapWireless(Filename='/root/bb.cap',Pktnum='2',Initnum1='3',Finalnum1='11',Replacevalue1='22 33 44')
#     2)编辑该报文流pktstr：SetDsendStreamWireless(Port='3',StreamMode='0',StreamRateMode='pps',FrameSize='64',StreamRate='1',Pcapvalue=pktstr)
###################################################################################
def BuildPCAPVALUE(args):
    global dcnstream
    if 'Pcapvalue' in args:
        dcnstream = 'Pcapnone()/"pcapvalueflag' + args['Pcapvalue'].replace(' ', '') + 'pcapvalueflag"'


##################################################################################
#
# BuildArp :构建由python scapy发送的arp报文，如ARP(....)
#
# args:  无
#
# return: 无
#
# addition:
#
# examples:
#     BuildArp(args)
# 脚本调用格式：
#    SetDsendStreamWireless(Port='2',StreamRateMode='pps',StreamRate='10', FrameSize='64', \
#		   SouMac='00-00-00-00-00-03',DesMac='00-00-00-00-00-04', \
#		   Protocl='arp',ArpOperation='2',\
#		   SenderMac='00-00-00-00-00-05',SenderMacNum='2',TargetMac='00-00-00-00-00-06',TargetMacNum='2', \
#		   SenderIp='5.5.5.5',SenderIpNum='2',TargetIp='6.6.6.6',TargetIpNum='2')		
###################################################################################	
def BuildArp(args):
    global dcnstream

    # 修改前面获取的Dot1Q()中的type字段为0x0806,如果前面是Dot3Tag,则需要增加len=0x0806
    if 'type=0xffff' in dcnstream:
        dcnstream = re.sub('0xffff', '0x0806', dcnstream)
    else:
        dcnstream = re.sub(',\)', ',len=0x0806)', dcnstream)
    dcnstream = dcnstream + '/ARP('

    # 构建arp operation字段
    if 'ArpOperation' in args:
        dcnstream = dcnstream + 'op=' + args['ArpOperation'] + ','

    # 构建arp SenderMac字段
    if 'SenderMac' not in args:
        args['SenderMac'] = '00-00-00-00-00-01'
    if 'SenderMacNum' not in args:
        args['SenderMacNum'] = '1'
    # 将mac的格式由00-00-00-00-00-01转化为00:00:00:00:00:01
    args['SenderMac'] = re.sub('-', ':', args['SenderMac'])
    BuildIncrField('hwsrc', 'mac', args['SenderMac'], args['SenderMacNum'])

    # 构建arp TargetMac字段
    if 'TargetMac' not in args:
        args['TargetMac'] = '00-00-00-00-00-02'
    if 'TargetMacNum' not in args:
        args['TargetMacNum'] = '1'
    # 将mac的格式由00-00-00-00-00-02转化为00:00:00:00:00:02
    args['TargetMac'] = re.sub('-', ':', args['TargetMac'])
    BuildIncrField('hwdst', 'mac', args['TargetMac'], args['TargetMacNum'])

    # 构建arp SenderIp字段
    if 'SenderIp' not in args:
        args['SenderIp'] = '1.1.1.1'
    if 'SenderIpNum' not in args:
        args['SenderIpNum'] = '1'
    if 'SenderIpMode' not in args:
        args['SenderIpMode'] = 'classD'
    if 'SenderIpStep' not in args:
        args['SenderIpStep'] = '1'
    BuildIncrField('psrc', 'ip', args['SenderIp'], args['SenderIpNum'], args['SenderIpStep'], args['SenderIpMode'])

    # 构建arp TargetIp字段
    if 'TargetIp' not in args:
        args['TargetIp'] = '2.2.2.2'
    if 'TargetIpNum' not in args:
        args['TargetIpNum'] = '1'
    if 'TargetIpMode' not in args:
        args['TargetIpMode'] = 'classD'
    if 'TargetIpStep' not in args:
        args['TargetIpStep'] = '1'
    BuildIncrField('pdst', 'ip', args['TargetIp'], args['TargetIpNum'], args['TargetIpStep'], args['TargetIpMode'])

    dcnstream = dcnstream + ')'


##################################################################################


#
# BuildIPv4 :构建由python scapy发送的ipv4报文，如IP(....)
#
# args:  无
#
# return: 无
#
# addition:
#
# examples:
#     BuildIPv4(args)
# 脚本调用格式：
#     SetDsendStreamWireless(Port='2',StreamRateMode='pps',StreamRate='10', FrameSize='64', \
#		     SouMac='00-00-00-00-00-03',DesMac='00-00-00-00-00-04', \
#		     Protocl='ipv4',Tos='12',Fragment='2',TTL='240', \
#		     SouIp='10.1.1.1',SouIpNum='10',DesIp='20.1.1.1',DesIpNum='10')     
###################################################################################  
def BuildIPv4(args):
    global dcnstream

    # 修改前面获取的Dot1Q()中的type字段为0x0800,如果前面是Dot3Tag,则需要增加len=0x0800
    if 'type=0xffff' in dcnstream:
        dcnstream = re.sub('0xffff', '0x0800', dcnstream)
    else:
        dcnstream = re.sub(',\)', ',len=0x0800)', dcnstream)
    dcnstream = dcnstream + '/IP('

    # 构建tos字段,tosh3存储tos的高三位的值即Ipprecedence的值
    if 'Ipprecedence' in args:
        tosh3 = int(args['Ipprecedence']) * 32
        if 'Tos' in args:
            tos = tosh3 + (int(args['Tos']) * 2)
        elif 'Dscp' in args:
            tos = int(args['Dscp']) * 4
        else:
            tos = tosh3
    elif 'Tos' in args:
        if 'Dscp' in args:
            tos = int(args['Dscp']) * 4
        else:
            tos = int(args['Tos'])
    elif 'Dscp' in args:
        tos = int(args['Dscp']) * 4
    else:
        tos = 0
    if tos > 0:
        dcnstream = dcnstream + 'tos=' + str(tos) + ','

    # 构建ip报头的长度值:TotalLength
    if 'LengthOverride' in args and 'TotalLength' in args:
        if 'true' in args['LengthOverride']:
            dcnstream = dcnstream + 'len=' + str(args['TotalLength']) + ','
    else:
        dcnstream = dcnstream + 'len=None' + ','

    # 构建ip报头的fragment标志位
    if 'Fragment' in args or 'LastFragment' in args:
        if 'Fragment' not in args:
            args['Fragment'] = '0'
        if 'LastFragment' not in args:
            args['LastFragment'] = '0'
        fragment = int(args['Fragment']) * 2 + int(args['LastFragment'])
        dcnstream = dcnstream + 'flags=' + str(fragment) + ','

    # 构建ip报头的偏移量FragmentOffset
    if 'FragmentOffset' in args:
        dcnstream = dcnstream + 'frag=' + str(args['FragmentOffset']) + ','

    # 构建ip报头的ttl
    if 'TTL' in args:
        dcnstream = dcnstream + 'ttl=' + str(args['TTL']) + ','

    # 构建ip报头的自定义checksum
    if 'ValidChecksum' in args:
        if args['ValidChecksum'] == 'false':
            dcnstream = dcnstream + 'chksum=0,'

    # 构建ip报头源地址
    if 'SouIp' not in args:
        args['SouIp'] = '1.1.1.1'
    if 'SouIpNum' not in args:
        args['SouIpNum'] = '1'
    if 'SouClassMode' not in args:
        args['SouClassMode'] = 'classD'
    if 'SouIpStep' not in args:
        args['SouIpStep'] = '1'
    BuildIncrField('src', 'ip', args['SouIp'], args['SouIpNum'], args['SouIpStep'], args['SouClassMode'])

    # 构建ip报头目的地址
    if 'DesIp' not in args:
        args['DesIp'] = '2.2.2.2'
    if 'DesIpNum' not in args:
        args['DesIpNum'] = '1'
    if 'DesClassMode' not in args:
        args['DesClassMode'] = 'classD'
    if 'DesIpStep' not in args:
        args['DesIpStep'] = '1'
    BuildIncrField('dst', 'ip', args['DesIp'], args['DesIpNum'], args['DesIpStep'], args['DesClassMode'])

    # 构建ProtoclEx字段
    if 'ProtoclEx' in args:
        # 此处可以添加多种子协议报文，比如udp,tcp,icmp,dhcp,igmp等等
        if args['ProtoclEx'] == 'udp':
            dcnstream = dcnstream + ')'
            BuildUDP(args)
        elif args['ProtoclEx'] == 'tcp':
            dcnstream = dcnstream + ')'
            BuildTCP(args)
        elif args['ProtoclEx'] == 'rip':
            dcnstream = dcnstream + ')'
            BuildRIP(args)
        elif args['ProtoclEx'] == 'msdp':
            dcnstream = dcnstream + ')'
            BuildMSDP(args)
        elif args['ProtoclEx'] == 'igmp':
            dcnstream = dcnstream + ')'
            BuildIGMP(args)
        #
        # 添加报文结束
        else:
            dcnstream = dcnstream + 'proto=' + args['ProtoclEx'] + ',)'
    else:
        dcnstream = dcnstream + ')'

    ##################################################################################


#
# BuildIPv6 :构建由于python scapy发送的ipv6报文，如IPv6(....)
#
# args:  无
#
# return: 无
#
# addition:
#
# examples:
#     BuildIPv6(args)
# 脚本调用格式：
#     SetDsendStreamWireless(Port='2',StreamRateMode='pps',StreamRate='10', FrameSize='64', \
#		     SouMac='00-00-00-00-00-03',DesMac='00-00-00-00-00-04', \
#		     Protocl='ipv6',TrafficClass='12',FlowLabel='10',HopLimit='20',NextHeader='58', \
#		     SouIpv6='2001::1',SouNumv6='10',DesIpv6='2002::1',DesNumv6='10')
# 注：以下参数中的值都是以十进制赋值，TrafficClass='12',FlowLabel='10',HopLimit='20',NextHeader='58',
###################################################################################
def BuildIPv6(args):
    global dcnstream
    global dcnincrlist
    global dcnincrnum

    # 修改前面获取的Dot1Q()中的type字段为0x0800,如果前面是Dot3Tag,则需要增加len=0x86dd
    if 'type=0xffff' in dcnstream:
        dcnstream = re.sub('0xffff', '0x86dd', dcnstream)
    else:
        dcnstream = re.sub(',\)', ',len=0x86dd)', dcnstream)
    dcnstream = dcnstream + '/IPv6('

    # 构建TrafficClass字段
    if 'TrafficClass' in args:
        dcnstream = dcnstream + 'tc=' + args['TrafficClass'] + ','

    # 构建FlowLabel字段
    if 'FlowLabel' in args:
        dcnstream = dcnstream + 'fl=' + args['FlowLabel'] + ','
    else:
        if 'Offset1' in args and args['Offset1'] == '20':
            if 'Value1' not in args:
                args['Value1'] = '0'
            value1 = '0x' + args['Value1']
            value1 = int(value1, 16)
            if 'Repeat1' not in args:
                args['Repeat1'] = '1'
            if 'Step1' not in args:
                args['Step1'] = '1'
            if args['Repeat1'] == '1':
                dcnstream = dcnstream + 'fl=' + str(value1) + ','
            else:
                dcnincrnum = dcnincrnum + 1
                dcnstream = dcnstream + 'fl=incrNum' + str(dcnincrnum) + '[incrCount],'
                strinfo = '--incrNum' + str(dcnincrnum) + ' ' + str(value1) + ',' + args['Repeat1']
                dcnincrlist.append(strinfo)

    # 构建HopLimit 字段
    if 'HopLimit' in args:
        dcnstream = dcnstream + 'hlim=' + args['HopLimit'] + ','

    # 构建NextHeader 字段
    if 'NextHeader' in args:
        dcnstream = dcnstream + 'nh=' + args['NextHeader'] + ','

    # 构建ipv6 源ipv6地址字段
    if 'SouIpv6' not in args:
        args['SouIpv6'] = '2003:0001:0002:0003:0000:0000:0000:0003'
    if 'SouNumv6' not in args:
        args['SouNumv6'] = '1'
    if 'SouStepv6' not in args:
        args['SouStepv6'] = '1'
    if 'SouAddrModev6' not in args:
        args['SouAddrModev6'] = '128'
    else:
        if args['SouAddrModev6'] == 'IncrHost':
            args['SouAddrModev6'] = '128'
    BuildIncrField('src', 'ipv6', args['SouIpv6'], args['SouNumv6'], args['SouStepv6'], args['SouAddrModev6'])

    # 构建ipv6 目的ipv6地址字段
    if 'DesIpv6' not in args:
        args['DesIpv6'] = '2003:0001:0002:0003:0000:0000:0000:0001'
    if 'DesNumv6' not in args:
        args['DesNumv6'] = '1'
    if 'DesStepv6' not in args:
        args['DesStepv6'] = '1'
    if 'DesAddrModev6' not in args:
        args['DesAddrModev6'] = '128'
    else:
        if args['DesAddrModev6'] == 'IncrHost':
            args['DesAddrModev6'] = '128'
    BuildIncrField('dst', 'ipv6', args['DesIpv6'], args['DesNumv6'], args['DesStepv6'], args['DesAddrModev6'])

    # 构建ProtoclEx字段
    if 'ProtoclEx' in args:
        # 此处可以添加多种子协议报文，比如udp,tcp,icmpv6,mld等等
        if args['ProtoclEx'] == 'udp':
            dcnstream = dcnstream + ')'
            BuildUDP(args)
        elif args['ProtoclEx'] == 'tcp':
            dcnstream = dcnstream + ')'
            BuildTCP(args)

        #
        # 添加报文结束
        else:
            dcnstream = dcnstream + 'nh=' + args['ProtoclEx'] + ')'
    else:
        if 'Offset1' in args and args['Offset1'] == '20':
            if 'Value1' in args:
                nh = '0x' + args['Value1']
                nh = int(nh, 16)
                dcnstream = dcnstream + 'nh=' + str(nh) + ','
            else:
                dcnstream = dcnstream + 'nh=0,'
        dcnstream = dcnstream + ')'

    ##################################################################################


#
# BuildIPv4OverIPv6 :构建由python scapy发送的ipv4 over ipv6 隧道报文，如IP(....)/IPv6()
#
# args:  无
#
# return: 无
#
# addition:
#
# examples:
#     BuildIPv4OverIPv6(args)
# 脚本调用格式：
#     SetDsendStreamWireless(Port='2',StreamRateMode='pps',StreamRate='10', FrameSize='128', \
#		   SouMac='00-00-00-00-00-03',DesMac='00-00-00-00-00-04', \
#		   Protocl='ipv6ipv4',Tos='12',Fragment='2', \
#		   SouIp='10.1.1.1',SouIpNum='10',DesIp='20.1.1.1',DesIpNum='10', \
#		   TrafficClass='12',FlowLabel='10', \
#		   SouIpv6='2001::1',SouNumv6='10',DesIpv6='2002::1',DesNumv6='10')
###################################################################################	   
def BuildIPv4OverIPv6(args):
    global dcnstream
    global dcnincrlist
    global dcnincrnum

    # 先构建外层ipv4报文头
    # 修改前面获取的Dot1Q()中的type字段为0x0800,如果前面是Dot3Tag,则需要增加len=0x0800
    if 'type=0xffff' in dcnstream:
        dcnstream = re.sub('0xffff', '0x0800', dcnstream)
    else:
        dcnstream = re.sub(',\)', ',len=0x0800)', dcnstream)
    dcnstream = dcnstream + '/IP('

    # 构建tos字段,tosh3存储tos的高三位的值即Ipprecedence的值
    if 'Ipprecedence' in args:
        tosh3 = int(args['Ipprecedence']) * 32
    else:
        tosh3 = 0
    if 'Tos' in args:
        tos = tosh3 + (int(args['Tos']) * 2)
    else:
        tos = tosh3
    if tos > 0:
        dcnstream = dcnstream + 'tos=' + str(tos) + ','

    # 构建ip报头的长度值:TotalLength
    if 'LengthOverride' in args and 'TotalLength' in args:
        if 'true' in args['LengthOverride']:
            dcnstream = dcnstream + 'len=' + str(args['TotalLength']) + ','

    # 构建ip报头的fragment标志位
    if 'Fragment' in args or 'LastFragment' in args:
        if 'Fragment' not in args:
            args['Fragment'] = '0'
        if 'LastFragment' not in args:
            args['LastFragment'] = '0'
        fragment = int(args['Fragment']) * 2 + int(args['LastFragment'])
        dcnstream = dcnstream + 'flags=' + str(fragment) + ','

    # 构建ip报头的偏移量FragmentOffset
    if 'FragmentOffset' in args:
        dcnstream = dcnstream + 'frag=' + str(args['FragmentOffset']) + ','

    # 构建ip报头的隧道报文协议类型
    dcnstream = dcnstream + 'proto=41,'

    # 构建ip报头的自定义checksum
    if 'ValidChecksum' in args:
        if args['ValidChecksum'] == 'false':
            dcnstream = dcnstream + 'chksum=0,'

    # 构建ip报头源地址
    if 'SouIp' not in args:
        args['SouIp'] = '1.1.1.1'
    if 'SouIpNum' not in args:
        args['SouIpNum'] = '1'
    if 'SouClassMode' not in args:
        args['SouClassMode'] = 'classD'
    if 'SouIpStep' not in args:
        args['SouIpStep'] = '1'
    BuildIncrField('src', 'ip', args['SouIp'], args['SouIpNum'], args['SouIpStep'], args['SouClassMode'])

    # 构建ip报头目的地址
    if 'DesIp' not in args:
        args['DesIp'] = '2.2.2.2'
    if 'DesIpNum' not in args:
        args['DesIpNum'] = '1'
    if 'DesClassMode' not in args:
        args['DesClassMode'] = 'classD'
    if 'DesIpStep' not in args:
        args['DesIpStep'] = '1'
    BuildIncrField('dst', 'ip', args['DesIp'], args['DesIpNum'], args['DesIpStep'], args['DesClassMode'])

    dcnstream = dcnstream + ')'

    # 构建内层ipv6报文头
    dcnstream = dcnstream + '/IPv6('

    # 构建TrafficClass字段
    if 'TrafficClass' in args:
        dcnstream = dcnstream + 'tc=' + args['TrafficClass'] + ','

    # 构建FlowLabel字段
    if 'FlowLabel' in args:
        dcnstream = dcnstream + 'fl=' + args['FlowLabel'] + ','
    else:
        if 'Offset1' in args and args['Offset1'] == '20':
            if 'Value1' not in args:
                args['Value1'] = '0'
            value1 = '0x' + args['Value1']
            value1 = int(value1, 16)
            if 'Repeat1' not in args:
                args['Repeat1'] = '1'
            if 'Step1' not in args:
                args['Step1'] = '1'
            if args['Repeat1'] == '1':
                dcnstream = dcnstream + 'fl=' + str(value1) + ','
            else:
                dcnincrnum = dcnincrnum + 1
                dcnstream = dcnstream + 'fl=incrNum' + str(dcnincrnum) + '[incrCount],'
                strinfo = '--incrNum' + str(dcnincrnum) + ' ' + str(value1) + ',' + args['Repeat1']
                dcnincrlist.append(strinfo)

    # 构建HopLimit 字段
    if 'HopLimit' in args:
        dcnstream = dcnstream + 'hlim=' + args['HopLimit'] + ','

    # 构建ipv6 源ipv6地址字段
    if 'SouIpv6' not in args:
        args['SouIpv6'] = '2003:0001:0002:0003:0000:0000:0000:0003'
    if 'SouNumv6' not in args:
        args['SouNumv6'] = '1'
    if 'SouStepv6' not in args:
        args['SouStepv6'] = '1'
    if 'SouAddrModev6' not in args:
        args['SouAddrModev6'] = '128'
    else:
        if args['SouAddrModev6'] == 'IncrHost':
            args['SouAddrModev6'] = '128'
    BuildIncrField('src', 'ipv6', args['SouIpv6'], args['SouNumv6'], args['SouStepv6'], args['SouAddrModev6'])

    # 构建ipv6 目的ipv6地址字段
    if 'DesIpv6' not in args:
        args['DesIpv6'] = '2003:0001:0002:0003:0000:0000:0000:0001'
    if 'DesNumv6' not in args:
        args['DesNumv6'] = '1'
    if 'DesStepv6' not in args:
        args['DesStepv6'] = '1'
    if 'DesAddrModev6' not in args:
        args['DesAddrModev6'] = '128'
    else:
        if args['DesAddrModev6'] == 'IncrHost':
            args['DesAddrModev6'] = '128'
    BuildIncrField('dst', 'ipv6', args['DesIpv6'], args['DesNumv6'], args['DesStepv6'], args['DesAddrModev6'])

    # 构建ProtoclEx字段
    if 'ProtoclEx' in args:
        # 此处可以添加多种子协议报文，比如udp,tcp,icmpv6,mld等等
        if args['ProtoclEx'] == 'udp':
            dcnstream = dcnstream + ')'
            BuildUDP(args)
        elif args['ProtoclEx'] == 'tcp':
            dcnstream = dcnstream + ')'
            BuildTCP(args)

        #
        # 添加报文结束
        else:
            dcnstream = dcnstream + 'nh=' + args['ProtoclEx'] + ')'
    else:
        if 'Offset1' in args and args['Offset1'] == '20':
            if 'Value1' in args:
                nh = '0x' + args['Value1']
                nh = int(nh, 16)
                dcnstream = dcnstream + 'nh=' + str(nh) + ','
            else:
                dcnstream = dcnstream + 'nh=0,'
        dcnstream = dcnstream + ')'


##################################################################################
#
# BuildUDP :构建由于python scapy发送的 udp报文头，如UDP(....)
#
# args:  无
#
# return: 无
#
# addition:
#
# examples:
#     BuildUDP(args)
# 脚本调用格式：
##1.ipv4 UDP报文，source port和destination port分别为12和22
#     SetDsendStreamWireless(Port='2',StreamMode='0',StreamRateMode='pps',StreamRate='10', \
#		   SouMac='00-00-00-0F-00-05',DesMac='00-00-00-0F-00-06', \
#		   Protocl='ipv4',ProtoclEx='udp', \	   
#		   SPort='12',DPort='22')
##2.ipv4 UDP报文，源或目的端口递增的写法，推荐此种写法。source port和destination port为递增的几个端口，比如sport为12-20（12开始递增9个），dport为22-25（22开始递增4个）
#     SetDsendStreamWireless(Port='2',StreamMode='0',StreamRateMode='pps',StreamRate='10', \
#		   SouMac='00-00-00-0F-00-05',DesMac='00-00-00-0F-00-06', \
#		   Protocl='ipv4',ProtoclEx='udp', \	   
#		   SPort='12-20',DPort='22-25')
##3.ipv4 UDP报文，source port和destination port为递增的几个端口，采用偏移量的写法。不推荐。
#     SetDsendStreamWireless(Port='2',StreamMode='0',StreamRateMode='pps',StreamRate='10', \
#		   SouMac='00-00-00-0F-00-05',DesMac='00-00-00-0F-00-06', \
#		   Protocl='ipv4',ProtoclEx='udp', \	   
#		   Offset1='38',Value1='12',Repeat1='10', \
#		   Offset2='40',Value2='F',Repeat2='10')	
##4.ipv6 UDP报文，source port和destination port分别为12和22
#     SetDsendStreamWireless(Port='2',StreamMode='0',StreamRateMode='pps',StreamRate='10', \
#		   SouMac='00-00-00-0F-00-05',DesMac='00-00-00-0F-00-06', \
#		   Protocl='ipv6',ProtoclEx='udp', \	   
#		   SPort='12',DPort='22')
##5.ipv6 UDP报文，源或目的端口递增的写法，推荐此种写法。source port和destination port为递增的几个端口，比如sport为12-20（12开始递增9个），dport为22-25（22开始递增4个）
#     SetDsendStreamWireless(Port='2',StreamMode='0',StreamRateMode='pps',StreamRate='10', \
#		   SouMac='00-00-00-0F-00-05',DesMac='00-00-00-0F-00-06', \
#		   Protocl='ipv6',ProtoclEx='udp', \	   
#		   SPort='12-20',DPort='22-25')
##6.ipv4 UDP报文，source port和destination port为递增的几个端口，采用偏移量的写法。不推荐。
#     SetDsendStreamWireless(Port='2',StreamMode='0',StreamRateMode='pps',StreamRate='10', \
#		   SouMac='00-00-00-0F-00-05',DesMac='00-00-00-0F-00-06', \
#		   Protocl='ipv6',ProtoclEx='udp', \	   
#		   Offset1='58',Value1='12',Repeat1='10', \
#		   Offset2='60',Value2='F',Repeat2='10')
##7.IPv4OverIPv6 UDP报文，source port和destination port分别为12和22
#     SetDsendStreamWireless(Port='2',StreamMode='0',StreamRateMode='pps',StreamRate='10', \
#		   SouMac='00-00-00-0F-00-05',DesMac='00-00-00-0F-00-06', \
#		   Protocl='ipv6ipv4',ProtoclEx='udp', \	   
#		   SPort='12',DPort='22')
##8.IPv4OverIPv6 UDP报文，源或目的端口递增的写法.source port和destination port为递增的几个端口，比如sport为12-20（12开始递增9个），dport为22-25（22开始递增4个）
#     SetDsendStreamWireless(Port='2',StreamMode='0',StreamRateMode='pps',StreamRate='10', \
#		   SouMac='00-00-00-0F-00-05',DesMac='00-00-00-0F-00-06', \
#		   Protocl='ipv6ipv4',ProtoclEx='udp', \	   
#		   SPort='12-20',DPort='22-25')
###################################################################################
def BuildUDP(args):
    global dcnstream
    dportflag = '0'
    sportflag = '0'
    dcnstream = dcnstream + "/UDP("

    # 构造Dport字段
    if 'DPort' not in args:
        args['DPort'] = '0'

    if 'Offset2' in args or 'Offset1' in args:
        if 'Offset1' in args:
            # 如果dcnarrArgs(Offset1)为40则ipv4 udp Dport的值渐变
            if args['Offset1'] == '40':
                if 'Value1' not in args:
                    args['Value1'] == '0'
                value1 = '0x' + args['Value1']
                value1 = int(value1, 16)
                if 'Repeat1' not in args:
                    args['Repeat1'] == '1'
                BuildIncrField('dport', 'num', str(value1), args['Repeat1'])
                dportflag = '1'
            # 如果dcnarrArgs(Offset1)为60则ipv6 udp Dport的值渐变
            if args['Offset1'] == '60':
                if 'Value1' not in args:
                    args['Value1'] == '0'
                value1 = '0x' + args['Value1']
                value1 = int(value1, 16)
                if 'Repeat1' not in args:
                    args['Repeat1'] == '1'
                BuildIncrField('dport', 'num', str(value1), args['Repeat1'])
                dportflag = '1'
        if 'Offset2' in args:
            # 如果dcnarrArgs(Offset2)为40则ipv4 udp Dport的值渐变
            if args['Offset2'] == '40':
                if 'Value2' not in args:
                    args['Value2'] == '0'
                value2 = '0x' + args['Value2']
                value2 = int(value2, 16)
                if 'Repeat2' not in args:
                    args['Repeat2'] == '1'
                BuildIncrField('dport', 'num', str(value2), args['Repeat2'])
                dportflag = '1'
            # 如果dcnarrArgs(Offset2)为60则ipv6 udp Dport的值渐变
            if args['Offset2'] == '60':
                if 'Value2' not in args:
                    args['Value2'] == '0'
                value2 = '0x' + args['Value2']
                value2 = int(value2, 16)
                if 'Repeat2' not in args:
                    args['Repeat2'] == '1'
                BuildIncrField('dport', 'num', str(value2), args['Repeat2'])
                dportflag = '1'
    if dportflag == '0':
        if '-' in args['DPort']:
            Dinitvalue = (args['DPort'].split('-'))[0]
            Dfinalvalue = (args['DPort'].split('-'))[1]
            Dchangenum = int(Dfinalvalue) - int(Dinitvalue) + 1
            if Dchangenum <= 0:
                printRes('the Dport para is set to wrong value please check')
            BuildIncrField('dport', 'num', str(Dinitvalue), str(Dchangenum))
        else:
            dcnstream = dcnstream + 'dport=' + args['DPort'] + ','

    # 构造Sport字段
    if 'SPort' not in args:
        args['SPort'] = '0'
    if 'Offset2' in args or 'Offset1' in args:
        if 'Offset1' in args:
            # 如果dcnarrArgs(Offset1)为38则ipv4 udp Sport的值渐变
            if args['Offset1'] == '38':
                if 'Value1' not in args:
                    args['Value1'] == '0'
                value1 = '0x' + args['Value1']
                value1 = int(value1, 16)
                if 'Repeat1' not in args:
                    args['Repeat1'] == '1'
                BuildIncrField('sport', 'num', str(value1), args['Repeat1'])
                sportflag = '1'
            # 如果dcnarrArgs(Offset1)为58则ipv6 udp Dport的值渐变
            if args['Offset1'] == '58':
                if 'Value1' not in args:
                    args['Value1'] == '0'
                value1 = '0x' + args['Value1']
                value1 = int(value1, 16)
                if 'Repeat1' not in args:
                    args['Repeat1'] == '1'
                BuildIncrField('sport', 'num', str(value1), args['Repeat1'])
                sportflag = '1'
        if 'Offset2' in args:
            # 如果dcnarrArgs(Offset2)为38则ipv4 udp Dport的值渐变
            if args['Offset2'] == '38':
                if 'Value2' not in args:
                    args['Value2'] == '0'
                value2 = '0x' + args['Value2']
                value2 = int(value2, 16)
                if 'Repeat2' not in args:
                    args['Repeat2'] == '1'
                BuildIncrField('dport', 'num', str(value2), args['Repeat2'])
                sportflag = '1'
            # 如果dcnarrArgs(Offset2)为58则ipv6 udp Dport的值渐变
            if args['Offset2'] == '58':
                if 'Value2' not in args:
                    args['Value2'] == '0'
                value2 = '0x' + args['Value2']
                value2 = int(value2, 16)
                if 'Repeat2' not in args:
                    args['Repeat2'] == '1'
                BuildIncrField('dport', 'num', str(value2), args['Repeat2'])
                sportflag = '1'
    if sportflag == '0':
        if '-' in args['SPort']:
            Sinitvalue = (args['SPort'].split('-'))[0]
            Sfinalvalue = (args['SPort'].split('-'))[1]
            Schangenum = int(Sfinalvalue) - int(Sinitvalue) + 1
            if Schangenum <= 0:
                printRes('the SPort para is set to wrong value please check')
            BuildIncrField('sport', 'num', str(Sinitvalue), str(Schangenum))
        else:
            dcnstream = dcnstream + 'sport=' + args['SPort'] + ','

    dcnstream = dcnstream + ')'


##################################################################################
#
# BuildTCP :构建由于python scapy发送的 tcp报文头，如TCP(....)
#
# args:  无
#
# return: 无
#
# addition:
#
# examples:
#     BuildTCP(args)
# 脚本调用格式：
##1.ipv4 TCP报文，source port和destination port分别为12和22
#    SetDsendStreamWireless(Port='2',StreamMode='1',StreamRateMode='pps',StreamRate='10',NumFrames='50', \
#		   SouMac='00-00-00-0F-00-05',DesMac='00-00-00-0F-00-06', \
#		   Protocl='ipv4',ProtoclEx='tcp', \
#		   SPort='12',DPort='22', \
#		   SequenceNum='22',PSH='true',ACK='false',URG='true',RST='true',SYN='false',FIN='true')
##2.ipv4 TCP报文，端口号递增,推荐此种用法.source port和destination port分别为12-25和22-25,SequenceNum为'22-25'
#    SetDsendStreamWireless(Port='2',StreamMode='1',StreamRateMode='pps',StreamRate='10',NumFrames='50', \
#		   SouMac='00-00-00-0F-00-05',DesMac='00-00-00-0F-00-06', \
#		   Protocl='ipv4',ProtoclEx='tcp', \
#		   SequenceNum='22-25',SPort='12-25',DPort='22-25')
##3.ipv4 TCP报文，端口号递增,不推荐此种用法.source port和destination port分别为12-25和22-25
#    SetDsendStreamWireless(Port='2',StreamMode='1',StreamRateMode='pps',StreamRate='10',NumFrames='50', \
#		   SouMac='00-00-00-0F-00-05',DesMac='00-00-00-0F-00-06', \
#		   Protocl='ipv4',ProtoclEx='tcp', \
#		   Offset1='34',Value1='c',Repeat1='4', \
#		   Offset2='36',Value2='16',Repeat2='4')
##4.ipv6 TCP报文，source port和destination port分别为12和22
#    SetDsendStreamWireless(Port='2',StreamMode='1',StreamRateMode='pps',StreamRate='10',NumFrames='50', \
#		   SouMac='00-00-00-0F-00-05',DesMac='00-00-00-0F-00-06', \
#		   Protocl='ipv6',ProtoclEx='tcp', \
#		   SPort='12',DPort='22', \
#		   SequenceNum='22',PSH='true',ACK='false',URG='true',RST='true',SYN='false',FIN='true')
##5.ipv6 TCP报文，端口号递增,推荐此种用法.source port和destination port分别为12-25和22-25
#    SetDsendStreamWireless(Port='2',StreamMode='1',StreamRateMode='pps',StreamRate='10',NumFrames='50', \
#		   SouMac='00-00-00-0F-00-05',DesMac='00-00-00-0F-00-06', \
#		   Protocl='ipv6',ProtoclEx='tcp', \
#		   SPort='12-25',DPort='22-25')
##6.ipv6 TCP报文，端口号递增,不推荐此种用法.source port和destination port分别为12-25和22-25
#    SetDsendStreamWireless(Port='2',StreamMode='1',StreamRateMode='pps',StreamRate='10',NumFrames='50', \
#		   SouMac='00-00-00-0F-00-05',DesMac='00-00-00-0F-00-06', \
#		   Protocl='ipv6',ProtoclEx='tcp', \
#		   Offset1='58',Value1='c',Repeat1='4', \
#		   Offset2='60',Value2='16',Repeat2='4')    
##7.ipv4overipv6 TCP报文，source port和destination port分别为12和22
#    SetDsendStreamWireless(Port='2',StreamMode='1',StreamRateMode='pps',StreamRate='10',NumFrames='50', \
#		   SouMac='00-00-00-0F-00-05',DesMac='00-00-00-0F-00-06', \
#		   Protocl='ipv6ipv4',ProtoclEx='tcp', \
#		   SPort='12',DPort='22', \
#		   SequenceNum='22',PSH='true',ACK='false',URG='true',RST='true',SYN='false',FIN='true')
##8.ipv4overipv6 TCP报文，端口号递增,推荐此种用法.source port和destination port分别为12-25和22-25
#    SetDsendStreamWireless(Port='2',StreamMode='1',StreamRateMode='pps',StreamRate='10',NumFrames='50', \
#		   SouMac='00-00-00-0F-00-05',DesMac='00-00-00-0F-00-06', \
#		   Protocl='ipv6ipv4',ProtoclEx='tcp', \
#		   SPort='12-25',DPort='22-25')		   
###################################################################################
def BuildTCP(args):
    global dcnstream
    dportflag = '0'
    sportflag = '0'
    dcnstream = dcnstream + "/TCP("

    # 构造Dport字段
    if 'DPort' not in args:
        args['DPort'] = '0'

    if 'Offset2' in args or 'Offset1' in args:
        if 'Offset1' in args:
            # 如果dcnarrArgs(Offset1)为36则ipv4 udp Dport的值渐变
            if args['Offset1'] == '36':
                if 'Value1' not in args:
                    args['Value1'] == '0'
                value1 = '0x' + args['Value1']
                value1 = int(value1, 16)
                if 'Repeat1' not in args:
                    args['Repeat1'] == '1'
                BuildIncrField('dport', 'num', str(value1), args['Repeat1'])
                dportflag = '1'
            # 如果dcnarrArgs(Offset1)为60则ipv6 udp Dport的值渐变
            if args['Offset1'] == '60':
                if 'Value1' not in args:
                    args['Value1'] == '0'
                value1 = '0x' + args['Value1']
                value1 = int(value1, 16)
                if 'Repeat1' not in args:
                    args['Repeat1'] == '1'
                BuildIncrField('dport', 'num', str(value1), args['Repeat1'])
                dportflag = '1'
        if 'Offset2' in args:
            # 如果dcnarrArgs(Offset2)为36则ipv4 udp Dport的值渐变
            if args['Offset2'] == '36':
                if 'Value2' not in args:
                    args['Value2'] == '0'
                value2 = '0x' + args['Value2']
                value2 = int(value2, 16)
                if 'Repeat2' not in args:
                    args['Repeat2'] == '1'
                BuildIncrField('dport', 'num', str(value2), args['Repeat2'])
                dportflag = '1'
            # 如果dcnarrArgs(Offset2)为60则ipv6 udp Dport的值渐变
            if args['Offset2'] == '60':
                if 'Value2' not in args:
                    args['Value2'] == '0'
                value2 = '0x' + args['Value2']
                value2 = int(value2, 16)
                if 'Repeat2' not in args:
                    args['Repeat2'] == '1'
                BuildIncrField('dport', 'num', str(value2), args['Repeat2'])
                dportflag = '1'
    if dportflag == '0':
        if '-' in args['DPort']:
            Dinitvalue = (args['DPort'].split('-'))[0]
            Dfinalvalue = (args['DPort'].split('-'))[1]
            Dchangenum = int(Dfinalvalue) - int(Dinitvalue) + 1
            if Dchangenum <= 0:
                printRes('the Dport para is set to wrong value please check')
            BuildIncrField('dport', 'num', str(Dinitvalue), str(Dchangenum))
        else:
            dcnstream = dcnstream + 'dport=' + args['DPort'] + ','

    # 构造Sport字段
    if 'SPort' not in args:
        args['SPort'] = '0'
    if 'Offset2' in args or 'Offset1' in args:
        if 'Offset1' in args:
            # 如果dcnarrArgs(Offset1)为34则ipv4 udp Sport的值渐变
            if args['Offset1'] == '34':
                if 'Value1' not in args:
                    args['Value1'] == '0'
                value1 = '0x' + args['Value1']
                value1 = int(value1, 16)
                if 'Repeat1' not in args:
                    args['Repeat1'] == '1'
                BuildIncrField('sport', 'num', str(value1), args['Repeat1'])
                sportflag = '1'
            # 如果dcnarrArgs(Offset1)为58则ipv6 udp Dport的值渐变
            if args['Offset1'] == '58':
                if 'Value1' not in args:
                    args['Value1'] == '0'
                value1 = '0x' + args['Value1']
                value1 = int(value1, 16)
                if 'Repeat1' not in args:
                    args['Repeat1'] == '1'
                BuildIncrField('sport', 'num', str(value1), args['Repeat1'])
                sportflag = '1'
        if 'Offset2' in args:
            # 如果dcnarrArgs(Offset2)为34则ipv4 udp Dport的值渐变
            if args['Offset2'] == '34':
                if 'Value2' not in args:
                    args['Value2'] == '0'
                value2 = '0x' + args['Value2']
                value2 = int(value2, 16)
                if 'Repeat2' not in args:
                    args['Repeat2'] == '1'
                BuildIncrField('dport', 'num', str(value2), args['Repeat2'])
                sportflag = '1'
            # 如果dcnarrArgs(Offset2)为58则ipv6 udp Dport的值渐变
            if args['Offset2'] == '58':
                if 'Value2' not in args:
                    args['Value2'] == '0'
                value2 = '0x' + args['Value2']
                value2 = int(value2, 16)
                if 'Repeat2' not in args:
                    args['Repeat2'] == '1'
                BuildIncrField('dport', 'num', str(value2), args['Repeat2'])
                sportflag = '1'
    if sportflag == '0':
        if '-' in args['SPort']:
            Sinitvalue = (args['SPort'].split('-'))[0]
            Sfinalvalue = (args['SPort'].split('-'))[1]
            Schangenum = int(Sfinalvalue) - int(Sinitvalue) + 1
            if Schangenum <= 0:
                printRes('the SPort para is set to wrong value please check')
            BuildIncrField('sport', 'num', str(Sinitvalue), str(Schangenum))
        else:
            dcnstream = dcnstream + 'sport=' + args['SPort'] + ','

    # 构造SequenceNum字段
    if 'SequenceNum' in args:
        if '-' in args['SequenceNum']:
            Seinitvalue = (args['SequenceNum'].split('-'))[0]
            Sefinalvalue = (args['SequenceNum'].split('-'))[1]
            Sechangenum = int(Sefinalvalue) - int(Seinitvalue) + 1
            if Sechangenum <= 0:
                printRes('the SPort para is set to wrong value please check')
            BuildIncrField('seq', 'num', str(Seinitvalue), str(Sechangenum))
        else:
            dcnstream = dcnstream + 'seq=' + args['SequenceNum'] + ','

        # 构造FlagsField字段
        # 计算FIN
    if 'FIN' in args:
        if 'true' in args['FIN']:
            fin = '1'
        else:
            if args['FIN'] == 'false':
                fin = '0'
            else:
                printRes('the para FIN value is wrong.')
    else:
        fin = '0'

    # 计算SYN
    if 'SYN' in args:
        if 'true' in args['SYN']:
            syn = '2'
        else:
            if args['SYN'] == 'false':
                syn = '0'
            else:
                printRes('the para SYN value is wrong.')
    else:
        syn = '0'

    # 计算RST
    if 'RST' in args:
        if 'true' in args['RST']:
            rst = '4'
        else:
            if args['RST'] == 'false':
                rst = '0'
            else:
                printRes('the para RST value is wrong.')
    else:
        rst = '0'

    # 计算PSH
    if 'PSH' in args:
        if 'true' in args['PSH']:
            psh = '8'
        else:
            if args['PSH'] == 'false':
                psh = '0'
            else:
                printRes('the para PSH value is wrong.')
    else:
        psh = '0'

    # 计算ACK
    if 'ACK' in args:
        if 'true' in args['ACK']:
            ack = '16'
        else:
            if args['ACK'] == 'false':
                ack = '0'
            else:
                printRes('the para ACK value is wrong.')
    else:
        ack = '0'

    # 计算URG
    if 'URG' in args:
        if 'true' in args['URG']:
            urg = '32'
        else:
            if args['URG'] == 'false':
                urg = '0'
            else:
                printRes('the para URG value is wrong.')
    else:
        urg = '0'

    tcpflags = int(ack) + int(fin) + int(psh) + int(rst) + int(syn) + int(urg)
    tcpflags = hex(tcpflags)
    if tcpflags != '0x2':
        dcnstream = dcnstream + 'flags=' + tcpflags + ','
    dcnstream = dcnstream + ')'


##################################################################################
#
# BuildRIP :构建由于python scapy发送的 RIP报文，如RIP(....)
#
# args:  无
#
# return: 无
#
# addition:
#
# examples:
#     BuildRIP(args)
# 脚本调用格式：
#    SetDsendStreamWireless(Port='4',StreamMode='0',StreamRateMode='pps',StreamRate='10', \
#		   SouMac='00-00-00-0F-00-05',DesMac='00-00-00-0F-00-06', \
#		   Protocl='ipv4',SouIp = '120.1.1.1', DesIp = '122.1.1.1',ProtoclEx='rip',RipCommand='2',RipVersion='2', \
#		   RipRoute=[{'Ip':'10.1.1.1','Mask':'255.255.255.255','Nexthop':'10.1.1.1','Metric':'5','Num':'5'}, \
#			     {'Ip':'20.1.1.1','Mask':'255.255.255.0','Nexthop':'100.1.1.1','Metric':'6','Num':'20'}])
###################################################################################
def BuildRIP(args):
    global dcnstream
    dcnstream = dcnstream + "/UDP(sport=520)"
    dcnstream = dcnstream + "/RIP("
    # 构建rip command和version
    if "RipCommand" in args:
        dcnstream = dcnstream + "cmd=" + str(args["RipCommand"]) + ","
    if "RipVersion" in args:
        dcnstream = dcnstream + "version=" + str(args["RipVersion"]) + ","
    dcnstream = dcnstream + ")"
    if "RipRoute" in args:
        intRouteLength = len(args["RipRoute"])
        for i in range(intRouteLength):
            RIPEntryArgs = args["RipRoute"][i]
            dcnstream = dcnstream + "/RIPEntry("
            if "Ip" in RIPEntryArgs:
                if "Num" not in RIPEntryArgs:
                    strRIPEntryNum = "1"
                else:
                    strRIPEntryNum = RIPEntryArgs["Num"]
                if "RIPEntryMode" not in RIPEntryArgs:
                    strRIPEntryMode = "classC"
                else:
                    strRIPEntryMode = RIPEntryArgs["RIPEntryMode"]
                if "RIPEntryStep" not in RIPEntryArgs:
                    strRIPEntryStep = "1"
                else:
                    strRIPEntryStep = RIPEntryArgs["RIPEntryStep"]
                BuildIncrField("addr", "ip", RIPEntryArgs["Ip"], strRIPEntryNum, strRIPEntryStep, strRIPEntryMode)
            if "Mask" in RIPEntryArgs:
                dcnstream = dcnstream + "mask=\"" + RIPEntryArgs["Mask"] + "\","
            if "Nexthop" in RIPEntryArgs:
                dcnstream = dcnstream + "nextHop=\"" + RIPEntryArgs["Nexthop"] + "\","
            if "Metric" in RIPEntryArgs:
                dcnstream = dcnstream + "metric=" + str(RIPEntryArgs["Metric"])
            dcnstream = dcnstream + ")"

        ##################################################################################


#
# BuildMSDP :构建由于python scapy发送的 MSDP报文，如MSDP(....)
#
# args:  无
#
# return: 无
#
# addition:
#
# examples:
#     BuildMSDP(args)
# 脚本调用格式：
#    SetDsendStreamWireless(Port='4',StreamMode='0',StreamRateMode='pps',StreamRate='10', \
#		   SouMac='00-00-00-0F-00-05',DesMac='00-00-00-0F-00-06', \
#		   Protocl='ipv4',SouIp = '120.1.1.1', DesIp = '122.1.1.1',ProtoclEx='msdp',MsdpType='0x05')

###################################################################################
def BuildMSDP(args):
    global dcnstream
    dcnstream = dcnstream + "/TCP(dport=639,sport=3531,flags=0x18)"
    dcnstream = dcnstream + "/MSDP("
    # 构建rip command和version
    if "MsdpType" in args:
        dcnstream = dcnstream + "type=" + str(args["MsdpType"]) + ","
    dcnstream = dcnstream + ")"


##################################################################################
#
# BuildIGMP :构建由于python scapy发送的 IGMP报文，如IGMP(....)
#
# args:  无
#
# return: 无
#
# addition:
#
# examples:
#     BuildIGMP(args)
# 脚本调用格式：
##1.v3的report报文
# SetDsendStreamWireless(Port='4',StreamMode='0',StreamRateMode='pps',StreamRate='10', \
#		   SouMac='00-00-00-0F-00-05',DesMac='01-00-5e-00-00-02', \
#		   Protocl='ipv4',SouIp = '120.1.1.1', DesIp = '224.0.0.2',ProtoclEx='igmp', \
#		   Type='report',IgmpVersion='3',IgmpGroupRecord=[['239.1.1.1','include',['14.0.0.1' \
#		   ,'14.0.0.2']],['225.1.1.9','exclude',['18.0.0.1','19.0.0.1']]])
##2.v2的report报文
# SetDsendStreamWireless(Port='4',StreamMode='0',StreamRateMode='pps',StreamRate='10', \
#		   SouMac='00-00-00-0F-00-05',DesMac='01-00-5e-00-00-02', \
#		   Protocl='ipv4',SouIp = '120.1.1.1', DesIp = '224.0.0.2',ProtoclEx='igmp', \
#		   Type='report',IgmpVersion='2',IgmpGroupAddress = '225.10.10.1', IgmpRepeat='10')
##3.v2的leave报文
# SetDsendStreamWireless(Port='4',StreamMode='0',StreamRateMode='pps',StreamRate='10', \
#		   SouMac='00-00-00-0F-00-05',DesMac='01-00-5e-00-00-02', \
#		   Protocl='ipv4',SouIp = '120.1.1.1', DesIp = '224.0.0.2',ProtoclEx='igmp', \
#		   Type='leave',IgmpVersion='2',IgmpGroupAddress = '225.10.10.1', IgmpRepeat='10')
###################################################################################
def BuildIGMP(args):
    global dcnstream
    dcnstream = dcnstream + "/IGMP("
    if "Version" in args or "Type" in args:
        if "Type" in args:
            if "IgmpVersion" in args:
                if args["IgmpVersion"] == '1':
                    if args["Type"] == 'report' or args["Type"] == '2':
                        dcnstream = dcnstream + 'version=0x12,maxres=0x00,'
                    elif args["Type"] == 'query' or args["Type"] == '1':
                        dcnstream = dcnstream + 'version=0x11,maxres=0x00,'
                    else:
                        pass
                    dcnstream = re.sub('len=None', 'len=28', dcnstream)
                if args["IgmpVersion"] == '2':
                    if args["Type"] == 'report' or args["Type"] == '22':
                        dcnstream = dcnstream + 'version=0x16,'
                    elif args["Type"] == 'query' or args["Type"] == '17':
                        dcnstream = dcnstream + 'version=0x11,'
                    elif args["Type"] == 'leave' or args["Type"] == '23':
                        dcnstream = dcnstream + 'version=0x17,'
                    else:
                        pass
                    dcnstream = re.sub('len=None', 'len=28', dcnstream)
                if args["IgmpVersion"] == '3':
                    if args["Type"] == 'report' or args["Type"] == '22' or args["Type"] == '34':
                        dcnstream = re.sub('IGMP', 'IGMPv3Report', dcnstream)
                        dcnstream = dcnstream + 'version=0x22,'
                    elif args["Type"] == 'query' or args["Type"] == '17':
                        dcnstream = re.sub('IGMP', 'IGMPv3Query', dcnstream)
                        dcnstream = dcnstream + 'version=0x11,'
                    else:
                        pass
            else:
                dcnstream = dcnstream + 'version=' + args["Type"] + ','
        else:
            dcnstream = dcnstream + 'version=' + args["Version"] + ','
    else:
        if 'Offset1' in args:
            if args["Offset1"] == '38' or args["Offset1"] == '34':
                if "Value1" not in args:
                    tempValue = 0
                else:
                    tempValue = args["Value1"]
                value1 = '0x'
                value1 = value1 + tempValue
                value1 = int(value1, 16)
                if "Repeat1" not in args:
                    strRepeat = 1
                else:
                    strRepeat = args["Repeat1"]
                if "Step1" not in args:
                    strStep1 = 1
                else:
                    strStep1 = args["Step1"]
                BuildIncrField('version', 'num', value1, strRepeat)
    if 'Group' in args or 'IgmpGroupAddress' in args:
        if 'IgmpGroupAddress' in args:
            group = args['IgmpGroupAddress']
        else:
            group = args['Group']
        if 'IgmpRepeat' not in args:
            tmpIgmpRepeat = 1
        else:
            tmpIgmpRepeat = args["IgmpRepeat"]
        if 'IgmpStep' not in args:
            tmpIgmpStep = 1
        else:
            tmpIgmpStep = args["IgmpStep"]
        if 'DesClassMode' not in args:
            tmpIgmpClassMode = 'classD'
        else:
            tmpIgmpClassMode = args["DesClassMode"]
        BuildIncrField('group', 'ip', group, tmpIgmpRepeat, tmpIgmpStep, tmpIgmpClassMode)
    if 'IgmpVersion' in args and 'Type' in args:
        if args["IgmpVersion"] == '3' and args["Type"] == 'query':
            if 'IgmpSourceIpAddress' in args:
                dcnstream = dcnstream + 'sournum=1,/SrcList(source=\"' + args["IgmpSourceIpAddress"] + '\"'
    if 'IgmpGroupRecord' in args:
        if len(args["IgmpGroupRecord"]) >= 1:
            tmpLen = len(args["IgmpGroupRecord"])
            dcnstream = dcnstream + 'numrec=' + str(tmpLen) + ',)'
            for i in range(tmpLen):
                tmpList = args["IgmpGroupRecord"][i]
                strGroup = tmpList[0]
                listSourc = tmpList[2]
                intLenSourc = len(listSourc)
                if str.lower(tmpList[1]) == 'include':
                    dcnstream = dcnstream + '/IGMPv3Record(rectype=0x01,'
                elif str.lower(tmpList[1]) == 'exclude':
                    dcnstream = dcnstream + '/IGMPv3Record(rectype=0x02,'
                elif str.lower(tmpList[1]) == 'toinclude':
                    dcnstream = dcnstream + '/IGMPv3Record(rectype=0x03,'
                elif str.lower(tmpList[1]) == 'toexclude':
                    dcnstream = dcnstream + '/IGMPv3Record(rectype=0x04,'
                elif str.lower(tmpList[1]) == 'allow':
                    dcnstream = dcnstream + '/IGMPv3Record(rectype=0x05,'
                elif str.lower(tmpList[1]) == 'block':
                    dcnstream = dcnstream + '/IGMPv3Record(rectype=0x06,'
                dcnstream = dcnstream + 'numsour=' + str(intLenSourc) + ','
                dcnstream = dcnstream + 'group=\"' + strGroup + '\")'
                if intLenSourc == 0:
                    dcnstream = dcnstream + '/SrcList(source=\"\"'
                    if i != tmpLen - 1:
                        dcnstream = dcnstream + ')'
                else:
                    for j in range(intLenSourc):
                        tmpSourc = listSourc[j]
                        if (i == tmpLen - 1) and (j == intLenSourc - 1):
                            dcnstream = dcnstream + '/SrcList(source=\"' + tmpSourc + '\"'
                        else:
                            dcnstream = dcnstream + '/SrcList(source=\"' + tmpSourc + '\")'

    dcnstream = dcnstream + ")"


############### Dsend tools  ############################


##################################################################################
#
# ConnectDsendWireless :连接发包工具服务器
#
# args:  
#    host: 发包工具服务器ip地址
#    port: 连接服务器的端口号，默认为11918
#
# return: 连接成功返回0
#
# addition:
#
# examples:
#     ConnectDsendWireless('172.16.1.43')
#
###################################################################################
def ConnectDsendWireless(host, port=11918):
    res = Dconn(host, port)
    return res


##################################################################################
#
# DisconnectDsendWireless :断开连接发包工具服务器
#
# args:  
#
# return: 断开成功返回0
#
# addition:
#
# examples:
#     DisconnectDsendWireless()
#
###################################################################################
def DisconnectDsendWireless():
    res = Ddisconn()
    return res


##################################################################################
#
# StartTransmitWireless :开始发包
#
# args:  
#    Port: 发包的端口（必选）
#    PortType: 网卡类型，0为wlan，1为mon。默认为0.（可选）
# 
# return: 发包成功返回0
#
# addition:
#     
# examples:
#     StartTransmitWireless('1','1')
#     StartTransmitWireless(Port='1',PortType='1')
#     StartTransmitWireless('1')
###################################################################################
def StartTransmitWireless(Port, PortType='0'):
    res = 0
    if str(PortType) != '0':
        porttypestr = "--port" + str(Port) + "config 1"
        resx = DsendWireless(" --port " + str(Port) + " --proc startTransmit " + porttypestr)
        res = int(res) + int(resx)
    else:
        resx = DsendWireless(" --port " + str(Port) + " --proc startTransmit")
        res = int(res) + int(resx)
    return res


##################################################################################
#
# StartTransmitWireless :停止发包
#
# args:  
#    port: 停止发包的端口
#
# return: 停止成功返回0
#
# addition:
#     支持多个端口同时停止发包
# examples:
#     StopTransmitWireless('1','2')
#
###################################################################################
def StopTransmitWireless(*args):
    res = 0
    for port in args:
        resx = DsendWireless(" --port " + str(port) + " --proc stopTransmit")
        res = int(res) + int(resx)
    return res


##################################################################################
#
# GetIwconfigWireless :获得网卡iwconfig的关联信息
#
# args:  
#    Port: 网卡端口号
#
# return: 返回网卡iwconfig的关联信息
#
# addition:
#
# examples:
#     GetIwconfigWireless(Port='1')
#     GetIwconfigWireless('1')
###################################################################################
def GetIwconfigWireless(Port):
    res = DassociateWireless(" --port " + str(Port) + " --proc getIwconfig")
    return res


##################################################################################
#
# GetIfconfigWireless :获得网卡ifconfig的信息
#
# args:  
#    Port: 网卡端口号
#
# return: 返回网卡ifconfig的关联信息
#
# addition:
#
# examples:
#     GetIfconfigWireless(Port='1')
#     GetIfconfigWireless('1')
###################################################################################
def GetIfconfigWireless(Port):
    res = DassociateWireless(" --port " + str(Port) + " --proc getIfconfig")
    return res


##################################################################################
#
# DelAssociateWireless :释放网卡的ip并取消网卡关联，“dhclient -r 网卡号”
#
# args:  
#    Port: 网卡端口号
#
# return: 成功返回0
#
# addition:
#
# examples:
#     DelAssociateWireless(Port='1')
#     DelAssociateWireless('1')
###################################################################################
def DelAssociateWireless(Port):
    res = DassociateWireless(" --port " + str(Port) + " --proc delAssociate")
    return res


##################################################################################
#
# CreateAssociateWireless :无线网卡与AP之间建立关联，并获取IP
#
# args:  
#    Port: 网卡端口号
#    Essid: 要关联的essid
#
# return: 成功返回0
#
# addition:
#
# examples:
#     CreateAssociateWireless(Port='1'，Essid='dcntest')
#     CreateAssociateWireless('1','dcntest')
###################################################################################
def CreateAssociateWireless(Port, Essid):
    res = DassociateWireless(" --port " + str(Port) + " --proc createAssociateAndIp " + "--essid " + str(Essid))
    return res


##################################################################################
#
# RecreateAssociateWireless :无线网卡与AP之间重新建立关联，并获取IP。（即先解除关联、释放ip，再重新关联、获取ip。）
#
# args:  
#    Port: 网卡端口号
#    Essid: 要重新关联的essid
#
# return: 成功返回0
#
# addition:
#
# examples:
#     RecreateAssociateWireless(Port='1',Essid='dcntest')
#     RecreateAssociateWireless('1','dcntest')
###################################################################################
def RecreateAssociateWireless(Port, Essid):
    res = DassociateWireless(" --port " + str(Port) + " --proc recreateAssociateAndIp " + "--essid " + str(Essid))
    return res


##################################################################################
#
# CheckAssociateWireless :检查某无线网卡是否正常关联某个网络
#                         如果关联正确：返回0；如果没有关联或关联的网络不正确：重新关联到正确的网络，如果关联成功，返回0，否则返回关联失败的打印信息
#
# args:  
#    Port: 网卡端口号
#    Essid: 要重新关联的essid
#
# return: 
#         成功，返回0
#         失败，返回关联失败的打印信息
#
# addition:
#
# examples:
#     CheckAssociateWireless(Port='1',Essid='dcntest')
#     CheckAssociateWireless('1','dcntest')
###################################################################################
def CheckAssociateWireless(Port, Essid):
    res = DassociateWireless(" --port " + str(Port) + " --proc checkAssociate " + "--essid " + str(Essid))
    return res


##################################################################################
#
# CheckAssociateAndIpWireless :检查某无线网卡是否正常关联某个网络并获得ip
#                         如果关联正确：返回0；如果没有关联或关联的网络不正确：重新关联到正确的网络，如果关联成功，返回0，否则返回关联失败的打印信息
#
# args:  
#    Port: 网卡端口号
#    Essid: 要重新关联的essid
#
# return: 
#         成功，返回0
#         失败，返回关联失败的打印信息
#
# addition:
#
# examples:
#     CheckAssociateAndIpWireless(Port='1',Essid='dcntest')
#     CheckAssociateAndIpWireless('1','dcntest')
###################################################################################
def CheckAssociateAndIpWireless(Port, Essid):
    res = DassociateWireless(" --port " + str(Port) + " --proc checkAssociateAndIp " + "--essid " + str(Essid))
    return res


##################################################################################
#
# AddRouteWireless :在发包工具服务器添加一条路由，格式举例:route add -net 10.1.1.0/24 gw 20.1.1.254 dev wlan4
#
# args:  
#    Port: 网卡端口号
#    Net: 目的网段
#    Gateway: 网关
#
# return: 
#         成功，返回0
#         失败，返回失败打印信息
#
# addition:
#
# examples:
#     AddRouteWireless(Port='1',Net='10.0.0.0/8',Gateway='20.1.1.254')
#     AddRouteWireless('1','10.0.0.0/8','20.1.1.254')
###################################################################################
def AddRouteWireless(Port, Net, Gateway):
    res = DrouteWireless(
        " --port " + str(Port) + " --proc addRoute " + "--net " + str(Net) + " --gateway " + str(Gateway))
    return res


##################################################################################
#
# DelRouteWireless :在发包工具服务器删除一条路由，格式举例:route del -net 10.1.1.0/24 gw 20.1.1.254 dev wlan4
#
# args:  
#    Port: 网卡端口号
#    Net: 目的网段
#    Gateway: 网关
#
# return: 
#         成功，返回0
#         失败，返回失败打印信息
#
# addition:
#
# examples:
#     DelRouteWireless(Port='1',Net='10.0.0.0/8',Gateway='20.1.1.254')
#     DelRouteWireless('1','10.0.0.0/8','20.1.1.254')
###################################################################################
def DelRouteWireless(Port, Net, Gateway):
    res = DrouteWireless(
        " --port " + str(Port) + " --proc delRoute " + "--net " + str(Net) + " --gateway " + str(Gateway))
    return res


##---------------------------------读取.cap文件相关函数------------------------------------##
######################################################################
#
# ReadPcapWireless: 读取.cap文件中的某一个报文，并修改其中的一些字段
#
# args:  
#    Filename: 读取的.cap文件的名称，包括路径，比如/home/test.cap（必选）
#    Pktnum: .cap文件中的第几个报文，从0开始（必选）
#    args: 修改的字段参数，可选项。
#        Initnum1：修改的第一个字段的起始位置，比如对于报文的hex格式“01 02 03 04 05 00 00”，如果要将03修改为ff，那么
#        Finalnum1：修改的第一个字段的结束位置+1
#        Replacevalue1：第一个字段修改后的值
#        Initnum2：修改的第二个字段的起始位置，比如对于报文的hex格式“01 02 03 04 05 00 00”，如果要将03修改为ff，那么
#        Finalnum2：修改的第二个字段的结束位置+1
#        Replacevalue2：第二个字段修改后的值
#
# return: 
#        返回修改后的报文
# 
# examples:
# 比如对于/root/bb.cap文件中的第3个报文，hex格式为“01 02 03 04 05 06 07 08 09 0A 0B 00 00 00 00 00 00 00 00 00 00 00”
# 1.如果不修改任何字段，直接读取输出：
#           ReadPcapWireless(Filename='/root/bb.cap',Pktnum='2',)
# 2.如果只修改1个字段，将'02 03 04'修改为‘22 33 44’：
#           ReadPcapWireless(Filename='/root/bb.cap',Pktnum='2',Initnum1='3',Finalnum1='11',Replacevalue1='22 33 44')
# 3.如果要修改2个字段，将'02 03 04'修改为‘22 33 44’，将‘0B’修改为‘BB’：
#           ReadPcapWireless(Filename='/root/bb.cap',Pktnum='2',Initnum1='3',Finalnum1='11',Replacevalue1='22 33 44' \
#                            Initnum2='30',Finalnum2='32',Replacevalue2='BB')
#
######################################################################
def ReadPcapWireless(Filename, Pktnum, **args):
    cmdtmp = "--proc readPcap --filename " + Filename + " --pktnum " + Pktnum
    if 'Initnum1' in args:
        cmdtmp = cmdtmp + ' --initnum1 ' + str(args['Initnum1'])
    if 'Finalnum1' in args:
        cmdtmp = cmdtmp + ' --finalnum1 ' + str(args['Finalnum1'])
    if 'Replacevalue1' in args:
        cmdtmp = cmdtmp + ' --replacevalue1 ' + str(args['Replacevalue1']).replace(' ', '')
    if 'Initnum2' in args:
        cmdtmp = cmdtmp + ' --initnum2 ' + str(args['Initnum2'])
    if 'Finalnum2' in args:
        cmdtmp = cmdtmp + ' --finalnum2 ' + str(args['Finalnum2'])
    if 'Replacevalue2' in args:
        cmdtmp = cmdtmp + ' --replacevalue2 ' + str(args['Replacevalue2']).replace(' ', '')
    res = DrdpcapWireless(cmdtmp)
    return res


##---------------------------------抓包相关函数------------------------------------##

######################################################################
#
# StartDsendCaptureWireless: 开始抓包函数
#
# args:  
#    Port: 抓包的端口（必选）
#    PortType: 网卡类型，0为wlan，1为mon。默认为0.（可选）
#    Filter: 抓包过滤条件（可选）。如果有过滤条件，则按照过滤条件先过滤再抓包，如果无，则抓取所有报文。
#
# return: 开始抓包操作成功返回0
# 
# examples:
#           StartDsendCaptureWireless('2')
#           StartDsendCaptureWireless(Port='2')
#           StartDsendCaptureWireless(Port='2',PortType='1',Filter='arp')
######################################################################
def StartDsendCaptureWireless(Port, **args):
    res = 0
    if 'Filter' in args:
        if 'PortType' in args:
            if str(args['PortType']) != '0':
                porttypestr = "--port" + str(Port) + "config 1"
                resx = DcaptureWireless(
                    "--port " + str(Port) + " --proc startCapture " + porttypestr + " --filter " + str(args['Filter']))
                res = int(res) + int(resx)
            else:
                resx = DcaptureWireless("--port " + str(Port) + " --proc startCapture --filter " + str(args['Filter']))
                res = int(res) + int(resx)
        else:
            resx = DcaptureWireless("--port " + str(Port) + " --proc startCapture --filter " + str(args['Filter']))
            res = int(res) + int(resx)
    else:
        if 'PortType' in args:
            if str(args['PortType']) != '0':
                porttypestr = "--port" + str(Port) + "config 1"
                resx = DcaptureWireless("--port " + str(Port) + " --proc startCapture " + porttypestr)
                res = int(res) + int(resx)
            else:
                resx = DcaptureWireless("--port " + str(Port) + " --proc startCapture")
                res = int(res) + int(resx)
        else:
            resx = DcaptureWireless("--port " + str(Port) + " --proc startCapture")
            res = int(res) + int(resx)
    return res


######################################################################
#
# StopDsendCaptureWireless: 停止抓包函数（该函数会打印抓到的包的个数）
#
# return: 停止抓包操作成功返回0
# addition:
#     支持多个端口同时停止发包
# 
# examples:
#           StopDsendCaptureWireless('2','3')
######################################################################
def StopDsendCaptureWireless(*args):
    res = 0
    for port in args:
        resx = DcaptureWireless("--port " + str(port) + " --proc stopCapture")
        pktnum = DcaptureWireless("--port " + str(port) + " --proc getCaptureBuffer --fid count")
        print(pktnum)
        res = int(res) + int(resx)
    return res


######################################################################
#
# CheckDsendCaptureStreamWireless: 检查抓到的流是否满足要求
#
# args:
#           检查的端口和条件
#           port:   抓包端口
#           PortType:   抓包端口的类型，0：检查wlan抓包格式；1：mon抓包格式。默认为wlan抓包格式
#           Num: 检查的最大报文个数，默认为1000
##报文总长度
#           Length: 报文的字节长度
##Ethernet
#           SrcMac: 源mac
#           DstMac: 目的mac
##ip
#           SrcIp: source ip
#           DstIp: destination ip
##ipv6
#           SrcIpv6: source ipv6
#           DstIpv6: destination ipv6
##vlan(802.1q) 
#           Tpid
#           VlanTag: 取值 -1 不带tag,0 不关心带不带tag,>0 要求带的tag
#           Cos :   user priority
##arp
#           Arp: 1 是arp报文
#           ArpType: request,reply
#           ArpSenderHardwareAddress: 协议里的源mac
#           ArpSenderProtocolAddress: 协议里的源ip
#           ArpTargetHardwareAddress: 协议里的目的mac
#           ArpTargetProtocolAddress: 协议里的目的ip
##tcp（基于ipv4）
#           PSH: 'true',1；'false'，0
#           ACK: 'true',1；'false'，0
#           URG: 'true',1；'false'，0
#           RST: 'true',1；'false'，0
#           SYN: 'true',1；'false'，0
#           FIN: 'true',1；'false'，0
##扩展协议类型（基于ipv4）
#           ProtocolEx: 'tcp','udp','rip','icmp','igmp'
# return: 
#      成功：返回满足条件的报文个数
#      失败：返回0
#
# addition:
#     最大支持1000个报文的检查，但是也可以自定义最大值，通过Num设定检查报文个数的最大值。
# 
# examples:
#           CheckDsendCaptureStreamWireless('2',SrcMac='00-00-00-00-00-03')
#           CheckDsendCaptureStreamWireless('2',Num='10',SrcMac='00-00-00-00-00-03')
#           CheckDsendCaptureStreamWireless('2',PortType='1',SrcIp='10.1.1.2')
#########################################################################################################
def CheckDsendCaptureStreamWireless(port, **args):
    counter = 0
    # Get the number of frames captured
    numFrames = DcaptureWireless("--port " + port + " --proc getCaptureBuffer --fid count")

    if not numFrames:
        print('capture no packet,please check')
        return 0

    if 'Num' in args:
        checknum = int(args['Num'])
    else:
        checknum = 1000

    # Limit the number of checked packets to 1000
    if int(numFrames) > int(checknum):
        numFrames = str(checknum)

    checknum = int(numFrames)
    character = ''
    # pak是自定义的一个字符串，是为了与python后台交互。在numFrames后面跟一个pak字符串，后台就会识别为输出全部的抓包数据（最大1000个）
    numFrames = str(numFrames) + 'pak'
    capturebuffer = DcaptureWireless("--port " + port + " --proc getCaptureBuffer --fid " + numFrames)

    # mon网卡抓包格式检查，即802.11头的报文
    if 'PortType' in args and str(args['PortType']) == '1':
        for i in range(checknum):
            # Note that the frame number starts at 1
            # Get the actual frame data
            data = capturebuffer[i]
            if data == '':
                continue
            ret = 1

            ################# 添加各个需要检查的报文或字段 ###############

            # Address1
            if 'Address1' in args:
                ret = ret * CheckAddress1InDataWireless(args['Address1'], data)
                if i == 1:
                    character = character + ' Address1 ' + str(args['Address1'])

            # Address2
            if 'Address2' in args:
                ret = ret * CheckAddress2InDataWireless(args['Address2'], data)
                if i == 1:
                    character = character + ' Address2 ' + str(args['Address2'])

            # Address3
            if 'Address3' in args:
                ret = ret * CheckAddress3InDataWireless(args['Address3'], data)
                if i == 1:
                    character = character + ' Address3 ' + str(args['Address3'])

            # Address4
            if 'Address4' in args:
                ret = ret * CheckAddress4InDataWireless(args['Address4'], data)
                if i == 1:
                    character = character + ' Address4 ' + str(args['Address4'])

            # SrcIp
            if 'SrcIp' in args:
                ret = ret * CheckSrcIpInDataWireless(args['SrcIp'], data)
                if i == 1:
                    character = character + ' SrcIp ' + str(args['SrcIp'])

            # DstIp
            if 'DstIp' in args:
                ret = ret * CheckDstIpInDataWireless(args['DstIp'], data)
                if i == 1:
                    character = character + ' DstIp ' + str(args['DstIp'])

            # SrcIpv6
            if 'SrcIpv6' in args:
                ret = ret * CheckSrcIpv6InDataWireless(args['SrcIpv6'], data)
                if i == 1:
                    character = character + ' SrcIpv6 ' + str(args['SrcIpv6'])

            # DstIpv6
            if 'DstIpv6' in args:
                ret = ret * CheckDstIpv6InDataWireless(args['DstIpv6'], data)
                if i == 1:
                    character = character + ' DstIpv6 ' + str(args['DstIpv6'])

            # Tpid
            if 'Tpid' in args:
                ret = ret * CheckTpidInDataWireless(args['Tpid'], data)
                if i == 1:
                    character = character + ' Tpid ' + str(args['Tpid'])

            # VlanTag
            if 'VlanTag' in args:
                ret = ret * CheckVlanTagInDataWireless(args['VlanTag'], data)
                if i == 1:
                    character = character + ' VlanTag ' + str(args['VlanTag'])

            # Cos
            if 'Cos' in args:
                ret = ret * CheckCosInDataWireless(args['Cos'], data)
                if i == 1:
                    character = character + ' Cos ' + str(args['Cos'])

            # Length
            if 'Length' in args:
                ret = ret * CheckLengthOfData(args['Length'], data)
                if i == 1:
                    character = character + ' Length ' + str(args['Length'])

            # Arp
            if 'Arp' in args:
                ret = ret * CheckArpInDataWireless(args['Arp'], data)
                if i == 1:
                    character = character + ' Arp '

            # ArpType
            if 'ArpType' in args:
                ret = ret * CheckArpTypeInDataWireless(args['ArpType'], data)
                if i == 1:
                    character = character + ' ArpType ' + str(args['ArpType'])

            # ArpSenderHardwareAddress
            if 'ArpSenderHardwareAddress' in args:
                ret = ret * CheckArpSenderHardwareAddressInDataWireless(args['ArpSenderHardwareAddress'], data)
                if i == 1:
                    character = character + ' ArpSenderHardwareAddress ' + str(args['ArpSenderHardwareAddress'])

            # ArpSenderProtocolAddress
            if 'ArpSenderProtocolAddress' in args:
                ret = ret * CheckArpSenderProtocolAddressInDataWireless(args['ArpSenderProtocolAddress'], data)
                if i == 1:
                    character = character + ' ArpSenderProtocolAddress ' + str(args['ArpSenderProtocolAddress'])

            # ArpTargetHardwareAddress
            if 'ArpTargetHardwareAddress' in args:
                ret = ret * CheckArpTargetHardwareAddressInDataWireless(args['ArpTargetHardwareAddress'], data)
                if i == 1:
                    character = character + ' ArpTargetHardwareAddress ' + str(args['ArpTargetHardwareAddress'])

            # ArpTargetProtocolAddress
            if 'ArpTargetProtocolAddress' in args:
                ret = ret * CheckArpTargetProtocolAddressInDataWireless(args['ArpTargetProtocolAddress'], data)
                if i == 1:
                    character = character + ' ArpTargetProtocolAddress ' + str(args['ArpTargetProtocolAddress'])

                # ACK
            if 'ACK' in args:
                ret = ret * CheckACKInDataWireless(args['ACK'], data)
                if i == 1:
                    character = character + ' ACK ' + str(args['ACK'])

            # SYN
            if 'SYN' in args:
                ret = ret * CheckSYNInDataWireless(args['SYN'], data)
                if i == 1:
                    character = character + ' SYN ' + str(args['SYN'])

            # FIN
            if 'FIN' in args:
                ret = ret * CheckFINInDataWireless(args['FIN'], data)
                if i == 1:
                    character = character + ' FIN ' + str(args['FIN'])

            # RST
            if 'RST' in args:
                ret = ret * CheckRSTInDataWireless(args['RST'], data)
                if i == 1:
                    character = character + ' RST ' + str(args['RST'])

            # PSH
            if 'PSH' in args:
                ret = ret * CheckPSHInDataWireless(args['PSH'], data)
                if i == 1:
                    character = character + ' PSH ' + str(args['PSH'])

            # U
            if 'URG' in args:
                ret = ret * CheckURGInDataWireless(args['URG'], data)
                if i == 1:
                    character = character + ' URG ' + str(args['URG'])

            # protocolEx
            if 'ProtocolEx' in args:
                ret = ret * CheckProtocolExInDataWireless(args['ProtocolEx'], data)
                if i == 1:
                    character = character + ' ProtocolEx ' + str(args['ProtocolEx'])

            ##############    添加报文结束  #############

            if ret != 0:
                counter = counter + 1
            else:
                pass
            # wlan网卡抓包格式检查，即Ethernet头的报文
    else:
        for i in range(checknum):
            # Note that the frame number starts at 1
            # Get the actual frame data
            data = capturebuffer[i]
            if data == '':
                continue
            ret = 1

            ################# 添加各个需要检查的报文或字段 ###############

            # SrcMac
            if 'SrcMac' in args:
                ret = ret * CheckSrcMacInData(args['SrcMac'], data)
                if i == 1:
                    character = character + ' SrcMac ' + str(args['SrcMac'])

            # DstMac
            if 'DstMac' in args:
                ret = ret * CheckDstMacInData(args['DstMac'], data)
                if i == 1:
                    character = character + ' DstMac ' + str(args['DstMac'])

            # SrcIp
            if 'SrcIp' in args:
                ret = ret * CheckSrcIpInData(args['SrcIp'], data)
                if i == 1:
                    character = character + ' SrcIp ' + str(args['SrcIp'])

            # DstIp
            if 'DstIp' in args:
                ret = ret * CheckDstIpInData(args['DstIp'], data)
                if i == 1:
                    character = character + ' DstIp ' + str(args['DstIp'])

            # SrcIpv6
            if 'SrcIpv6' in args:
                ret = ret * CheckSrcIpv6InData(args['SrcIpv6'], data)
                if i == 1:
                    character = character + ' SrcIpv6 ' + str(args['SrcIpv6'])

            # DstIpv6
            if 'DstIpv6' in args:
                ret = ret * CheckDstIpv6InData(args['DstIpv6'], data)
                if i == 1:
                    character = character + ' DstIpv6 ' + str(args['DstIpv6'])

            # Tpid
            if 'Tpid' in args:
                ret = ret * CheckTpidInData(args['Tpid'], data)
                if i == 1:
                    character = character + ' Tpid ' + str(args['Tpid'])

            # VlanTag
            if 'VlanTag' in args:
                ret = ret * CheckVlanTagInData(args['VlanTag'], data)
                if i == 1:
                    character = character + ' VlanTag ' + str(args['VlanTag'])

            # Length
            if 'Length' in args:
                ret = ret * CheckLengthOfData(args['Length'], data)
                if i == 1:
                    character = character + ' Length ' + str(args['Length'])

            # Cos
            if 'Cos' in args:
                ret = ret * CheckCosInData(args['Cos'], data)
                if i == 1:
                    character = character + ' Cos ' + str(args['Cos'])

            # Arp
            if 'Arp' in args:
                ret = ret * CheckArpInData(args['Arp'], data)
                if i == 1:
                    character = character + ' Arp '

            # ArpType
            if 'ArpType' in args:
                ret = ret * CheckArpTypeInData(args['ArpType'], data)
                if i == 1:
                    character = character + ' ArpType ' + str(args['ArpType'])

            # ArpSenderHardwareAddress
            if 'ArpSenderHardwareAddress' in args:
                ret = ret * CheckArpSenderHardwareAddressInData(args['ArpSenderHardwareAddress'], data)
                if i == 1:
                    character = character + ' ArpSenderHardwareAddress ' + str(args['ArpSenderHardwareAddress'])

            # ArpSenderProtocolAddress
            if 'ArpSenderProtocolAddress' in args:
                ret = ret * CheckArpSenderProtocolAddressInData(args['ArpSenderProtocolAddress'], data)
                if i == 1:
                    character = character + ' ArpSenderProtocolAddress ' + str(args['ArpSenderProtocolAddress'])

            # ArpTargetHardwareAddress
            if 'ArpTargetHardwareAddress' in args:
                ret = ret * CheckArpTargetHardwareAddressInData(args['ArpTargetHardwareAddress'], data)
                if i == 1:
                    character = character + ' ArpTargetHardwareAddress ' + str(args['ArpTargetHardwareAddress'])

            # ArpTargetProtocolAddress
            if 'ArpTargetProtocolAddress' in args:
                ret = ret * CheckArpTargetProtocolAddressInData(args['ArpTargetProtocolAddress'], data)
                if i == 1:
                    character = character + ' ArpTargetProtocolAddress ' + str(args['ArpTargetProtocolAddress'])

                # ACK
            if 'ACK' in args:
                ret = ret * CheckACKInData(args['ACK'], data)
                if i == 1:
                    character = character + ' ACK ' + str(args['ACK'])

            # SYN
            if 'SYN' in args:
                ret = ret * CheckSYNInData(args['SYN'], data)
                if i == 1:
                    character = character + ' SYN ' + str(args['SYN'])

            # FIN
            if 'FIN' in args:
                ret = ret * CheckFINInData(args['FIN'], data)
                if i == 1:
                    character = character + ' FIN ' + str(args['FIN'])

            # RST
            if 'RST' in args:
                ret = ret * CheckRSTInData(args['RST'], data)
                if i == 1:
                    character = character + ' RST ' + str(args['RST'])

            # PSH
            if 'PSH' in args:
                ret = ret * CheckPSHInData(args['PSH'], data)
                if i == 1:
                    character = character + ' PSH ' + str(args['PSH'])

            # URG
            if 'URG' in args:
                ret = ret * CheckURGInData(args['URG'], data)
                if i == 1:
                    character = character + ' URG ' + str(args['URG'])

            # protocolEx
            if 'ProtocolEx' in args:
                ret = ret * CheckProtocolExInData(args['ProtocolEx'], data)
                if i == 1:
                    character = character + ' ProtocolEx ' + str(args['ProtocolEx'])

            # Dot1xType
            if 'Dot1xType' in args:
                ret = ret * CheckDot1xTypeInData(args['Dot1xType'], data)
                if i == 1:
                    character = character + ' Dot1xType ' + str(args['Dot1xType'])

            # Dot1xCode
            if 'Dot1xCode' in args:
                ret = ret * CheckDot1xCodeInData(args['Dot1xCode'], data)
                if i == 1:
                    character = character + ' Dot1xCode ' + str(args['Dot1xCode'])

            # Dot1xProType
            if 'Dot1xProType' in args:
                ret = ret * CheckDot1xProTypeInData(args['Dot1xProType'], data)
                if i == 1:
                    character = character + ' Dot1xProType ' + str(args['Dot1xProType'])

            # EthernetType
            if 'EthernetType' in args:
                ret = ret * CheckEthernetTypeInData(args['EthernetType'], data)
                if i == 1:
                    character = character + ' EthernetType ' + str(args['EthernetType'])

            # DSCP
            if 'DSCP' in args:
                ret = ret * CheckDSCPInData(args['DSCP'], data)
                if i == 1:
                    character = character + ' DSCP ' + str(args['DSCP'])

            # CUSTOM BYTE
            if 'HEX' in args:
                if 'StartByte' in args and 'EndByte' in args:
                    ret = ret * CheckHEXInData(args['HEX'], data, args['StartByte'], args['EndByte'])
                else:
                    ret = ret * CheckHEXInData(args['HEX'], data)
                if i == 0:
                    character = character + ' HEX ' + str(args['HEX'])

            # CUSTOM BIT
            if 'BIT' in args:
                if 'ByteOffset' in args and 'BitOffset' in args:
                    ret = ret * CheckBITInData(args['BIT'], data, args['ByteOffset'], args['BitOffset'])
                    if i == 0:
                        character = character + ' BIT ' + str(args['BIT']) + ' Byte offset ' + args[
                            'ByteOffset'] + ' Bit offset ' + args['BitOffset']

            ######  添加报文结束 #####

            if ret != 0:
                counter = counter + 1
            else:
                pass

    strinfo = 'Check capture packets on ' + str(port) + ' with ' + character + ' is ' + str(counter)
    print(strinfo)
    return counter


#######################################################
# CheckSrcMacInData :检查抓到的流source mac是否满足镜像的要求
#
#   args:
#                scrmac: source mac
#                data: actual frame data
#
#   return: 
#                1 :满足要求
#                0:不满足要求
# examples:
#           CheckDsendCaptureStream('2',SrcMac='00-00-00-00-00-03')
########################################################## 
def CheckSrcMacInData(srcmac, data):
    # Get source mac from data
    data = data[18:35]
    data = re.sub(' ', '-', data)
    srcmac = srcmac.upper()
    if srcmac == data:
        return 1
    else:
        return 0


#######################################################
# CheckDstMacInData :检查抓到的流destination mac是否满足镜像的要求
#
#   args:
#                dstmac: destination mac
#                data: actual frame data
#
#   return: 
#                1 :满足要求
#                0:不满足要求
#
# examples:
#           CheckDsendCaptureStream('2',DstMac='00-00-00-00-00-03')
########################################################## 
def CheckDstMacInData(dstmac, data):
    # Get destination mac from data
    data = data[0:17]
    data = re.sub(' ', '-', data)
    dstmac = dstmac.upper()
    if dstmac == data:
        return 1
    else:
        return 0


    #######################################################


#
# CheckSrcIpInData :检查抓到的流source ip是否满足镜像的要求
#
#   args:
#                srcip: source ip
#                data: actual frame data
#
#   return: 
#                1 :满足要求
#                0:不满足要求
#
# examples:
#           CheckDsendCaptureStream('2',SrcIp='1.1.1.1')
########################################################## 
def CheckSrcIpInData(srcip, data):
    vlanflag = data[36:41]
    if vlanflag == '81 00':
        data = data[90:101]
    else:
        data = data[78:89]
    n1 = data[0:2]
    n2 = data[3:5]
    n3 = data[6:8]
    n4 = data[9:11]
    num1 = '0x' + str(n1)
    num1 = int(num1, 16)
    num2 = '0x' + str(n2)
    num2 = int(num2, 16)
    num3 = '0x' + str(n3)
    num3 = int(num3, 16)
    num4 = '0x' + str(n4)
    num4 = int(num4, 16)
    ipstr = str(num1) + '.' + str(num2) + '.' + str(num3) + '.' + str(num4)
    if srcip == ipstr:
        return 1
    else:
        return 0


#######################################################
#
# CheckDstIpInData :检查抓到的流destination ip是否满足镜像的要求
#
#   args:
#                dstip: destination ip
#                data: actual frame data
#
#   return: 
#                1 :满足要求
#                0:不满足要求
#
# examples:
#           CheckDsendCaptureStream('2',DstIp='2.2.2.2')
##########################################################  
def CheckDstIpInData(dstip, data):
    vlanflag = data[36:41]
    if vlanflag == '81 00':
        data = data[102:113]
    else:
        data = data[90:101]
    n1 = data[0:2]
    n2 = data[3:5]
    n3 = data[6:8]
    n4 = data[9:11]
    num1 = '0x' + str(n1)
    num1 = int(num1, 16)
    num2 = '0x' + str(n2)
    num2 = int(num2, 16)
    num3 = '0x' + str(n3)
    num3 = int(num3, 16)
    num4 = '0x' + str(n4)
    num4 = int(num4, 16)
    ipstr = str(num1) + '.' + str(num2) + '.' + str(num3) + '.' + str(num4)
    if dstip == ipstr:
        return 1
    else:
        return 0



    #######################################################


#
# CheckSrcIpv6InData :检查抓到的流source ipv6是否满足镜像的要求
#
#   args:
#                srcipv6: source ipv6
#                data: actual frame data
#
#   return: 
#                1 :满足要求
#                0:不满足要求
# examples:
#           CheckDsendCaptureStream('2',SrcIpv6='2001::1')
##########################################################  
def CheckSrcIpv6InData(srcipv6, data):
    vlanflag = data[36:41]
    if vlanflag == '81 00':
        data = data[78:126]
    else:
        data = data[66:114]
    data = re.sub(' ', '', data)
    n1 = data[0:4]
    n2 = data[4:8]
    n3 = data[8:12]
    n4 = data[12:16]
    n5 = data[16:20]
    n6 = data[20:24]
    n7 = data[24:28]
    n8 = data[28:32]
    ipv6str = str(n1) + ':' + str(n2) + ':' + str(n3) + ':' + str(n4) + ':' + str(n5) + ':' + str(n6) + ':' + str(
        n7) + ':' + str(n8)
    srcipv6 = FormatIpv6(srcipv6)
    srcipv6 = srcipv6.upper()
    if srcipv6 == ipv6str:
        return 1
    else:
        return 0


#######################################################
#
# CheckDstIpv6InData :检查抓到的流destination ipv6是否满足镜像的要求
#
#   args:
#                dstipv6: destination ipv6
#                data: actual frame data
#
#   return: 
#                1 :满足要求
#                0:不满足要求
# examples:
#           CheckDsendCaptureStream('2',DstIpv6='2001::2')
##########################################################
def CheckDstIpv6InData(dstipv6, data):
    vlanflag = data[36:41]
    if vlanflag == '81 00':
        data = data[126:173]
    else:
        data = data[114:161]
    data = re.sub(' ', '', data)
    n1 = data[0:4]
    n2 = data[4:8]
    n3 = data[8:12]
    n4 = data[12:16]
    n5 = data[16:20]
    n6 = data[20:24]
    n7 = data[24:28]
    n8 = data[28:32]
    ipv6str = str(n1) + ':' + str(n2) + ':' + str(n3) + ':' + str(n4) + ':' + str(n5) + ':' + str(n6) + ':' + str(
        n7) + ':' + str(n8)
    dstipv6 = FormatIpv6(dstipv6)
    dstipv6 = dstipv6.upper()
    if dstipv6 == ipv6str:
        return 1
    else:
        return 0


# 调用格式：FormatIpv6('2000::1') ==>2000:0000:0000:0000:0000:0000:0000:0001
def FormatIpv6(ipv6):
    if ipv6[0:2] == '::':
        ipv6 = re.sub(ipv6[0:2], '0::', ipv6)
    if ipv6[(len(ipv6) - 2):len(ipv6)] == '::':
        ipv6 = str(ipv6) + '0'
    ipv6length = len(ipv6)
    count = 0
    for i in range(ipv6length):
        tempchar = ipv6[i]
        if tempchar == ':':
            count = count + 1

    flag = ipv6.find('::')
    if flag == -1:
        result = Format4bit(ipv6)
    else:
        bitnum = (7 - count) + 1
        ipv6temp = ipv6[0:flag]
        for j in range(bitnum):
            ipv6temp = ipv6temp + ':0'
        tempipv6 = ipv6[(flag + 1):len(ipv6)]
        ipv6temp = ipv6temp + tempipv6
        result = Format4bit(ipv6temp)
    return result


# 将ipv6地址的每一个字段变为4字符宽度
def Format4bit(ipv6):
    templist = ipv6.split(':')
    length = len(templist)
    result = ''
    for i in range(length):
        tempipv6 = templist[i]
        tempipv6 = '0x' + str(tempipv6)
        tempipv6 = int(tempipv6, 16)
        tempipv6 = '%04X' % tempipv6
        n = length - 1
        if i == n:
            result = result + tempipv6
        else:
            result = result + tempipv6 + ':'
    return result


#######################################################
#
# CheckTpidInData :检查抓到的流vlan tpid是否满足镜像的要求
#
#   args:
#                vlantag: vlan tpid
#                data: actual frame data
#
#   return: 
#                1 :满足要求
#                0:不满足要求
#   eg:
# CheckDsendCaptureStream('2',Tpid=['81','91'])
# CheckDsendCaptureStream('2',Tpid=['81'])
# Tpid取一个值，则仅判断报文第一层Tpid;Tpid取两个值，第一个值为外层Tpid值，第二个值为内层Tpid的值
# 当Tpid值为8100或9100时，判断时只取81或91，即对前两位判断
#
##########################################################
def CheckTpidInData(Tpid, data):
    if len(Tpid) == 1:
        data = data[36:38]
        if Tpid[0] == data:
            return 1
        else:
            return 0
    if len(Tpid) == 2:
        outtpid = Tpid[0]
        intpid = Tpid[1]
        outdata = data[36:38]
        indata = data[48:50]
        if outtpid == outdata and intpid == indata:
            return 1
        else:
            return 0


#######################################################
#
# CheckVlanTagInData :检查抓到的流vlan tag是否满足镜像的要求
#
#   args:
#                vlantag: vlan tag
#                data: actual frame data
#
#   return: 
#                1 :满足要求
#                0:不满足要求
#
# CheckDsendCaptureStream('2',VlanTag=['100','10'])
# CheckDsendCaptureStream('2',VlanTag=['100'])
# VlanTag取一个值，则仅判断报文第一层Tag;VlanTag取两个值，第一个值为外层Tag值，第二个值为内层Tag的值
# 取值为-1，表示没有VlanTag;取值为0，表示不关心是否有VlanTag;取值为>0，表示要求有VlanTag，该值为Vid
#
##########################################################
def CheckVlanTagInData(vlantag, data):
    if len(vlantag) == 1:
        if int(vlantag[0]) == 0:
            # VlanTag为0，不关心是否有Tag
            return 1
        if int(vlantag[0]) > 0:
            # VlanTag>0，对报文进行判断
            if data[36:41] == '81 00':
                temp = data[43:47]
                temp = re.sub(' ', '', temp)
                temp = '0x' + temp
                temp = int(temp, 16)
                if int(vlantag[0]) == temp:
                    return 1
        if vlantag[0] == '-1':
            # VlanTag为-1，报文不存在Tag
            if data[36:41] != '81 00':
                return 1
    elif len(vlantag) > 2:
        # 判断三层tag
        outtag = vlantag[0]
        intag = vlantag[1]
        intag1 = vlantag[2]
        # 最外层
        temp = data[43:47]
        temp = re.sub(' ', '', temp)
        temp = '0x' + temp
        temp = int(temp, 16)
        # 第二层
        tmp = data[55:59]
        tmp = re.sub(' ', '', tmp)
        tmp = '0x' + tmp
        tmp = int(tmp, 16)
        # 第三层
        tmp1 = data[67:71]
        tmp1 = re.sub(' ', '', tmp1)
        tmp1 = '0x' + tmp1
        tmp1 = int(tmp1, 16)
        if outtag == temp and intag == tmp and intag1 == tmp1:
            return 1
    else:
        # VlanTag有两个取值
        outtag = vlantag[0]
        intag = vlantag[1]
        # 外层VlanTag为0时
        if int(outtag) == 0:
            if int(intag) == 0:
                return 1
            if intag == '-1':
                if data[48:53] != '81 00':
                    return 1
            if int(intag) > 0:
                if data[36:41] == '81 00':
                    if data[48:53] == '81 00':
                        temp = data[55:59]
                        temp = re.sub(' ', '', temp)
                        temp = '0x' + temp
                        temp = int(temp, 16)
                        if int(intag) == temp:
                            return 1
        # 外层VlanTag为0时
        if int(outtag) > 0:
            if data[36:41] == '81 00':
                temp = data[43:47]
                temp = re.sub(' ', '', temp)
                temp = '0x' + temp
                temp = int(temp, 16)
                if int(outtag) == temp:
                    if int(intag) == 0:
                        return 1
                    if intag == '-1':
                        if data[48:53] != '81 00':
                            return 1
                    if int(intag) > 0:
                        if data[48:53] == '81 00' or data[48:53] == '91 00':
                            tmp = data[55:59]
                            tmp = re.sub(' ', '', tmp)
                            tmp = '0x' + tmp
                            tmp = int(tmp, 16)
                            if int(intag) == tmp:
                                return 1
    return 0


#######################################################
#
# CheckLengthOfData :检查抓到的数据包长度,单位字节
#
#   args:
#                length: the ip offset vlaue in fragmented packet  
#                data: actual frame data
#
#   return: 
#                1 :满足要求
#                0:不满足要求
#   CheckDsendCaptureStream('2',Length='180')
########################################################## 
def CheckLengthOfData(length, data):
    if int(length) == len(data) / 3:
        return 1
    else:
        return 0


#######################################################
#
# CheckCosInData :检查抓到的流cos是否满足镜像的要求
#
#   args:
#                cos: cos 
#                data: actual frame data
#
#   return: 
#                1 :满足要求
#                0:不满足要求
#
# CheckDsendCaptureStream('2',Cos=['3'])
# CheckDsendCaptureStream('2',Cos=['3','4','5'])
# Cos的值使用十进制
# Cos取一个值，则仅判断报文第一层Cos;Cos取两个值，第一个值为外层Cos值，第二个值为内层Cos的值
# Cos取三个值，判断三层Cos值，第一个值为外层Cos值，第二个值为次外层Cos的值，第三个值为内层Cos的值
########################################################## 
def CheckCosInData(cos, data):
    # cos 取一个值
    if len(cos) == 1:
        data = data[42]
        data = '0x' + data
        data = int(data, 16)
        data = data / 2
        if int(cos[0]) == data:
            return 1
        else:
            return 0
        # cos 取两个值
    if len(cos) == 2:
        outcos = cos[0]
        incos = cos[1]
        outdata = data[42]
        outdata = '0x' + outdata
        outdata = int(outdata, 16)
        outdata = outdata / 2
        indata = data[54]
        indata = '0x' + indata
        indata = int(indata, 16)
        indata = indata / 2
        if int(outcos) == outdata and int(incos) == indata:
            return 1
        else:
            return 0
        # cos 取三个值
    if len(cos) == 3:
        outcos = cos[0]
        incos = cos[1]
        incos1 = cos[2]
        outdata = data[42]
        outdata = '0x' + outdata
        outdata = int(outdata, 16)
        outdata = outdata / 2
        indata = data[54]
        indata = '0x' + indata
        indata = int(indata, 16)
        indata = indata / 2
        indata1 = data[66]
        indata1 = '0x' + indata1
        indata1 = int(indata1, 16)
        indata1 = indata1 / 2
        if int(outcos) == outdata and int(incos) == indata and int(incos1) == indata1:
            return 1
        else:
            return 0

        ##################################


# 判断是否是arp包
# CheckDsendCaptureStream('2',Arp='1')
##################################
def CheckArpInData(arp, data):
    flag = data[36:41]
    if flag == '81 00':
        arphardwaretype = data[54:59]
        arpprotocoltype = data[60:65]
    else:
        arphardwaretype = data[42:47]
        arpprotocoltype = data[48:53]
    if arphardwaretype == '00 01' and arpprotocoltype == '08 00':
        return 1
    else:
        return 0


###########################################
# CheckArpTypeInData,判断arp包的类型
# CheckDsendCaptureStream('2',ArpType='request')
# CheckDsendCaptureStream('2',ArpType='reply')
###########################################
def CheckArpTypeInData(arptype, data):
    flag = data[36:41]
    if flag == '81 00':
        arpoperation = data[72:77]
    elif flag == '08 06':
        arpoperation = data[60:65]
    else:
        return 0
    if arptype == 'request' and arpoperation == '00 01':
        return 1
    elif arptype == 'reply' and arpoperation == '00 02':
        return 1
    else:
        return 0


###########################################
# CheckArpSenderHardwareAddressInData,判断arp包的协议源mac
# CheckDsendCaptureStream('2',ArpSenderHardwareAddress='00-00-00-00-00-01')
###########################################    
def CheckArpSenderHardwareAddressInData(sendermac, data):
    flag = data[36:41]
    if flag == '81 00':
        data = data[78:95]
    if flag == '08 06':
        data = data[66:83]
    data = re.sub(' ', '-', data)
    sendermac = sendermac.upper()
    if sendermac == data:
        return 1
    else:
        return 0


###########################################
# CheckArpSenderProtocolAddressInData,判断arp包的协议源ip
# CheckDsendCaptureStream('2',ArpSenderProtocolAddress='1.1.1.1')
###########################################    
def CheckArpSenderProtocolAddressInData(senderip, data):
    flag = data[36:41]
    if flag == '81 00':
        data = data[96:107]
    if flag == '08 06':
        data = data[84:95]
    n1 = data[0:2]
    n2 = data[3:5]
    n3 = data[6:8]
    n4 = data[9:11]
    n1 = '0x' + n1
    num1 = int(n1, 16)
    n2 = '0x' + n2
    num2 = int(n2, 16)
    n3 = '0x' + n3
    num3 = int(n3, 16)
    n4 = '0x' + n4
    num4 = int(n4, 16)
    spring = str(num1) + '.' + str(num2) + '.' + str(num3) + '.' + str(num4)
    if senderip == spring:
        return 1
    else:
        return 0


###########################################
# CheckArpTargetHardwareAddressInData,判断arp包的协议源mac
# CheckDsendCaptureStream('2',ArpTargetHardwareAddress='00-00-00-00-00-01')
###########################################    
def CheckArpTargetHardwareAddressInData(targetmac, data):
    flag = data[36:41]
    if flag == '81 00':
        data = data[108:125]
    if flag == '08 06':
        data = data[96:113]
    data = re.sub(' ', '-', data)
    targetmac = targetmac.upper()
    if targetmac == data:
        return 1
    else:
        return 0


###########################################
# CheckArpTargetProtocolAddressInData,判断arp包的协议源ip
# CheckDsendCaptureStream('2',ArpTargetProtocolAddress='1.1.1.1')
###########################################    
def CheckArpTargetProtocolAddressInData(targetip, data):
    flag = data[36:41]
    if flag == '81 00':
        data = data[126:137]
    if flag == '08 06':
        data = data[114:125]
    n1 = data[0:2]
    n2 = data[3:5]
    n3 = data[6:8]
    n4 = data[9:11]
    n1 = '0x' + n1
    num1 = int(n1, 16)
    n2 = '0x' + n2
    num2 = int(n2, 16)
    n3 = '0x' + n3
    num3 = int(n3, 16)
    n4 = '0x' + n4
    num4 = int(n4, 16)
    spring = str(num1) + '.' + str(num2) + '.' + str(num3) + '.' + str(num4)
    if targetip == spring:
        return 1
    else:
        return 0



    #######################################################


# CheckACKInData :检查抓到的流ACK是否满足要求
#
#   args:
#                record: true or false
#                data: actual frame data
#
#   return: 
#                1 :满足要求
#                0:不满足要求
#
# examples:
#           CheckDsendCaptureStream('2',ACK='true')
########################################################## 
def CheckACKInData(record, data):
    # Get tcp ACK from data
    flag = data[36:41]
    if flag == '81 00':
        TcpFlag = data[153:155]
        TcpFlag = '0x0' + TcpFlag
        TcpFlag = int(TcpFlag, 16)
    else:
        TcpFlag = data[141:143]
        TcpFlag = '0x0' + TcpFlag
        TcpFlag = int(TcpFlag, 16)
    if ((TcpFlag & 16 == 16) and (record == 'true')) or ((TcpFlag & 16 != 16) and (record == 'false')):
        return 1
    else:
        return 0


#######################################################
# CheckSYNInData :检查抓到的流SYN是否满足要求
#
#   args:
#                record: true or false
#                data: actual frame data
#
#   return: 
#                1 :满足要求
#                0:不满足要求
#
# examples:
#           CheckDsendCaptureStream('2',SYN='true')
########################################################## 
def CheckSYNInData(record, data):
    # Get tcp SYN from data
    flag = data[36:41]
    if flag == '81 00':
        TcpFlag = data[153:155]
        TcpFlag = '0x0' + TcpFlag
        TcpFlag = int(TcpFlag, 16)
    else:
        TcpFlag = data[141:143]
        TcpFlag = '0x0' + TcpFlag
        TcpFlag = int(TcpFlag, 16)
    if ((TcpFlag & 2 == 2) and (record == 'true')) or ((TcpFlag & 2 != 2) and (record == 'false')):
        return 1
    else:
        return 0


#######################################################
# CheckFINInData :检查抓到的流FIN是否满足要求
#
#   args:
#                record: true or false
#                data: actual frame data
#
#   return: 
#                1 :满足要求
#                0:不满足要求
#
# examples:
#           CheckDsendCaptureStream('2',FIN='true')
########################################################## 
def CheckFINInData(record, data):
    # Get tcp FIN from data
    flag = data[36:41]
    if flag == '81 00':
        TcpFlag = data[153:155]
        TcpFlag = '0x0' + TcpFlag
        TcpFlag = int(TcpFlag, 16)
    else:
        TcpFlag = data[141:143]
        TcpFlag = '0x0' + TcpFlag
        TcpFlag = int(TcpFlag, 16)
    if ((TcpFlag & 1 == 1) and (record == 'true')) or ((TcpFlag & 1 != 1) and (record == 'false')):
        return 1
    else:
        return 0


#######################################################
# CheckRSTInData :检查抓到的流RST是否满足要求
#
#   args:
#                record: true or false
#                data: actual frame data
#
#   return: 
#                1 :满足要求
#                0:不满足要求
#
# examples:
#           CheckDsendCaptureStream('2',RST='true')
########################################################## 
def CheckRSTInData(record, data):
    # Get tcp RST from data
    flag = data[36:41]
    if flag == '81 00':
        TcpFlag = data[153:155]
        TcpFlag = '0x0' + TcpFlag
        TcpFlag = int(TcpFlag, 16)
    else:
        TcpFlag = data[141:143]
        TcpFlag = '0x0' + TcpFlag
        TcpFlag = int(TcpFlag, 16)
    if ((TcpFlag & 4 == 4) and (record == 'true')) or ((TcpFlag & 4 != 4) and (record == 'false')):
        return 1
    else:
        return 0


#######################################################
# CheckPSHInData :检查抓到的流PSH是否满足要求
#
#   args:
#                record: true or false
#                data: actual frame data
#
#   return: 
#                1 :满足要求
#                0:不满足要求
#
# examples:
#           CheckDsendCaptureStream('2',PSH='true')
########################################################## 
def CheckPSHInData(record, data):
    # Get tcp PSH from data
    flag = data[36:41]
    if flag == '81 00':
        TcpFlag = data[153:155]
        TcpFlag = '0x0' + TcpFlag
        TcpFlag = int(TcpFlag, 16)
    else:
        TcpFlag = data[141:143]
        TcpFlag = '0x0' + TcpFlag
        TcpFlag = int(TcpFlag, 16)
    if ((TcpFlag & 8 == 8) and (record == 'true')) or ((TcpFlag & 8 != 8) and (record == 'false')):
        return 1
    else:
        return 0


#######################################################
# CheckURGInData :检查抓到的流URG是否满足要求
#
#   args:
#                record: true or false
#                data: actual frame data
#
#   return: 
#                1 :满足要求
#                0:不满足要求
#
# examples:
#           CheckDsendCaptureStream('2',URG='true')
########################################################## 
def CheckURGInData(record, data):
    # Get tcp URG from data
    flag = data[36:41]
    if flag == '81 00':
        TcpFlag = data[153:155]
        TcpFlag = '0x0' + TcpFlag
        TcpFlag = int(TcpFlag, 16)
    else:
        TcpFlag = data[141:143]
        TcpFlag = '0x0' + TcpFlag
        TcpFlag = int(TcpFlag, 16)
    if ((TcpFlag & 32 == 32) and (record == 'true')) or ((TcpFlag & 32 != 32) and (record == 'false')):
        return 1
    else:
        return 0


#######################################################
# CheckProtocolExInData :检查抓到的流ProtocolEx是否满足要求
#
#   args:
#                record: tcp, udp, rip, icmp or igmp
#                data: actual frame data
#
#   return: 
#                1 :满足要求
#                0:不满足要求
#
# examples:
#           CheckDsendCaptureStream('2',ProtocolEx='tcp')
########################################################## 
def CheckProtocolExInData(record, data):
    # Get tcp URG from data
    flag = data[36:41]
    if flag == '81 00':
        protocolEx = data[81:83]
    else:
        protocolEx = data[69:71]
    if record == 'tcp':
        record = 6
    elif record == 'udp':
        record = 17
    elif record == 'rip':
        record = 17
    elif record == 'icmp':
        record = 1
    elif record == 'igmp':
        record = 2
    else:
        record = -1
    strTemp = '0x0' + protocolEx
    if int(strTemp, 16) == record:
        return 1
    else:
        return 0


#######################################################
# CheckEthernetTypeInData  :检查抓到的流Ethernet Type是否满足要求
#
#   args:
#                record: tcp, udp, rip, icmp or igmp
#                data: actual frame data
#
#   return: 
#                1 :满足要求
#                0 :不满足要求
#
# examples:
#           CheckDsendCaptureStream('2',EthernetType='dot1x')
#           CheckDsendCaptureStream('4',EthernetType='08 06')
########################################################## 
def CheckEthernetTypeInData(record, data):
    # Get dot1x type from data
    flag = data[36:41]
    if flag == '81 00':
        flag = data[48:53]
    if record == '802.1x' or record == 'dot1x':
        record = '88 8E'
    elif record == 'ipv4' or record == 'IPv4':
        record = '08 00'
    elif record == 'arp' or record == 'ARP':
        record = '08 06'
    elif record == 'ipv6' or record == 'IPv6':
        record = '86 DD'
    elif record == 'ipx' or record == 'IPX':
        record = '81 37'
    if flag == record:
        return 1
    else:
        return 0


#######################################################
# CheckDSCPInData  :检查抓到的流DSCP是否满足要求
#
#   args:
#                dscp: dscp value
#                data: actual frame data
#
#   return: 
#                1 :满足要求
#                0 :不满足要求
#
# examples:
#           CheckDsendCaptureStream('4',DSCP='20')
########################################################## 
def CheckDSCPInData(dscp, data):
    # Get DSCP from data
    flag = data[36:41]
    dscpData = -1
    if flag == '81 00':
        version = data[54]
        if version == 4:
            dscpData = data[57:59]
            dscpData = '0x0' + dscpData.replace(' ', '')
            dscpData = int(dscpData, 16)
        elif version == 6:
            dscpString = data[55:58]
            dscpString = dscpString[1:]
            dscpData = '0x0' + dscpString.replace(' ', '')
            dscpData = int(dscpData, 16)
        else:
            version1 = data[78]
            if version1 == 4:
                dscpData = '0x0' + data[81:83].replace(' ', '')
                dscpData = int(dscpData, 16)
            elif version1 == 6:
                dscpString = data[79:82]
                dscpString = dscpString[1:]
                dscpData = '0x0' + dscpString.replace(' ', '')
                dscpData = int(dscpData, 16)
    elif flag == '08 00':
        dscpData = data[45:47]
        dscpData = '0x0' + dscpData.replace(' ', '')
        dscpData = int(dscpData, 16)
        dscpData = dscpData >> 2
    elif flag == '86 DD':
        dscpString = data[43:46]
        dscpString = dscpString[1:]
        dscpData = '0x0' + dscpString.replace(' ', '')
        dscpData = int(dscpData, 16)
    if int(dscp) == dscpData:
        return 1
    else:
        return 0


#######################################################
# CheckHEXInData  :检查抓到的流的某个字段的二进制格式是否满足要求
#
#   args:
#                strHexCheck: Hex string to be checked
#                data: actual frame data
#
#   return: 
#                1 :满足要求
#                0 :不满足要求
#
# examples:
#           CheckDsendCaptureStream('4', HEX='86dd',StartByte='20',EndByte='21')
#           CheckDsendCaptureStream('4', HEX='86dd12345678')
#           CheckDsendCaptureStream('4', HEX='86dd.*?0000')
########################################################## 
def CheckHEXInData(strHexCheck, data, strStartByte='ff', strEndByte='ff'):
    # Get HEX from data

    strHexGot = data.replace(' ', '')
    strHexCheck = strHexCheck.replace(' ', '')
    strHexCheck = strHexCheck.upper()
    if strStartByte == 'ff' and strEndByte == 'ff':
        tmpHex = re.search(strHexCheck, strHexGot)
    else:
        strHexGot = strHexGot[int(strStartByte) * 2:int(strEndByte) * 2 + 2]
        tmpHex = re.search(strHexCheck, strHexGot)
    if tmpHex is not None:
        return 1
    else:
        return 0


#######################################################
# CheckBITInData  :检查抓到的报文的某一位是否满足要求
#
#   args:
#                strBITCheck: Bit to be checked '0' or '1'
#                data: actual frame data
#                strByteOffset:Byte offset which bit in ,start with '0'
#                strBitOffset:Bit offset in byte '1' to '8'(left to right)
#
#   return: 
#                1 :满足要求
#                0 :不满足要求
#
# examples:
#           CheckDsendCaptureStream('4',DstMac='FF-FF-FF-FF-FF-FF', BIT='0',ByteOffset='20',BitOffset='4')
########################################################## 
def CheckBITInData(strBITCheck, data, strByteOffset='0', strBitOffset='0'):
    # Get BIT from data

    strHexGot = data.replace(' ', '')
    strBITCheck = strBITCheck.replace(' ', '')
    tmpByte = strHexGot[int(strByteOffset) * 2:int(strByteOffset) * 2 + 2]
    tmpByte = int(tmpByte, 16)
    if strBitOffset == '8':
        if ((tmpByte & 1 == 1) and (strBITCheck == '1')) or ((tmpByte & 1 != 1) and (strBITCheck == '0')):
            return 1
        else:
            return 0
    elif strBitOffset == '7':
        if ((tmpByte & 2 == 2) and (strBITCheck == '1')) or ((tmpByte & 2 != 2) and (strBITCheck == '0')):
            return 1
        else:
            return 0
    elif strBitOffset == '6':
        if ((tmpByte & 4 == 4) and (strBITCheck == '1')) or ((tmpByte & 4 != 4) and (strBITCheck == '0')):
            return 1
        else:
            return 0
    elif strBitOffset == '5':
        if ((tmpByte & 8 == 8) and (strBITCheck == '1')) or ((tmpByte & 8 != 8) and (strBITCheck == '0')):
            return 1
        else:
            return 0
    elif strBitOffset == '4':
        if ((tmpByte & 16 == 16) and (strBITCheck == '1')) or ((tmpByte & 16 != 16) and (strBITCheck == '0')):
            return 1
        else:
            return 0
    elif strBitOffset == '3':
        if ((tmpByte & 32 == 32) and (strBITCheck == '1')) or ((tmpByte & 32 != 32) and (strBITCheck == '0')):
            return 1
        else:
            return 0
    elif strBitOffset == '2':
        if ((tmpByte & 64 == 64) and (strBITCheck == '1')) or ((tmpByte & 64 != 64) and (strBITCheck == '0')):
            return 1
        else:
            return 0
    elif strBitOffset == '1':
        if ((tmpByte & 128 == 128) and (strBITCheck == '1')) or ((tmpByte & 128 != 128) and (strBITCheck == '0')):
            return 1
        else:
            return 0
    else:
        return 0


################################----- 无线报文头的检查函数 -----#########################


#######################################################
# GetMacHeaderLenWireless :获取mac header之前的header总长度（单位“字节”）
#
#   args:
#                data: actual frame data
#
#   return: 
#                (mac header + radiotap)的总长度
#
# examples:
#           
########################################################## 
def GetMacHeaderLenWireless(data):
    # 取出并计算Radiotap header的长度
    radiolen1 = data[6:8]
    radiolen2 = data[9:11]
    radiolen = '0x' + str(radiolen2) + str(radiolen1)
    radiolen = int(radiolen, 16)

    wdsvalue1 = data[(radiolen + 1) * 3]
    wdsvalue2 = '0x' + str(wdsvalue1)
    wdsvalue = int(str(wdsvalue2), 16)
    # 如果存在Address4，那么mac header为32字节，否则为26字节
    if wdsvalue & 0xc == 12:
        return radiolen + 32
    else:
        return radiolen + 26


#######################################################
#
# CheckSrcIpInDataWireless :检查抓到的流source ip是否满足镜像的要求
#
#   args:
#                srcip: source ip
#                data: actual frame data
#
#   return: 
#                1 :满足要求
#                0:不满足要求
#
# examples:
#           CheckDsendCaptureStreamWireless('2',PortType='1',SrcIp='1.1.1.1')
########################################################## 
def CheckSrcIpInDataWireless(srcip, data):
    Layer2Header = GetMacHeaderLenWireless(data) + 8
    vlanflaginit = (Layer2Header - 2) * 3
    vlanflag = data[vlanflaginit:(vlanflaginit + 5)]
    if vlanflag == '81 00':
        srcipinit = (Layer2Header + 16) * 3
        data = data[srcipinit:(srcipinit + 11)]
    else:
        srcipinit = (Layer2Header + 12) * 3
        data = data[srcipinit:(srcipinit + 11)]
    n1 = data[0:2]
    n2 = data[3:5]
    n3 = data[6:8]
    n4 = data[9:11]
    num1 = '0x' + str(n1)
    num1 = int(num1, 16)
    num2 = '0x' + str(n2)
    num2 = int(num2, 16)
    num3 = '0x' + str(n3)
    num3 = int(num3, 16)
    num4 = '0x' + str(n4)
    num4 = int(num4, 16)
    ipstr = str(num1) + '.' + str(num2) + '.' + str(num3) + '.' + str(num4)
    if srcip == ipstr:
        return 1
    else:
        return 0


#######################################################
#
# CheckDstIpInDataWireless :检查抓到的流destination ip是否满足镜像的要求
#
#   args:
#                dstip: destination ip
#                data: actual frame data
#
#   return: 
#                1 :满足要求
#                0:不满足要求
#
# examples:
#           CheckDsendCaptureStreamWireless('2',PortType='1',DstIp='2.2.2.2')
##########################################################  
def CheckDstIpInDataWireless(dstip, data):
    Layer2Header = GetMacHeaderLenWireless(data) + 8
    vlanflaginit = (Layer2Header - 2) * 3
    vlanflag = data[vlanflaginit:(vlanflaginit + 5)]
    if vlanflag == '81 00':
        srcipinit = (Layer2Header + 20) * 3
        data = data[srcipinit:(srcipinit + 11)]
    else:
        srcipinit = (Layer2Header + 16) * 3
        data = data[srcipinit:(srcipinit + 11)]
    n1 = data[0:2]
    n2 = data[3:5]
    n3 = data[6:8]
    n4 = data[9:11]
    num1 = '0x' + str(n1)
    num1 = int(num1, 16)
    num2 = '0x' + str(n2)
    num2 = int(num2, 16)
    num3 = '0x' + str(n3)
    num3 = int(num3, 16)
    num4 = '0x' + str(n4)
    num4 = int(num4, 16)
    ipstr = str(num1) + '.' + str(num2) + '.' + str(num3) + '.' + str(num4)
    if dstip == ipstr:
        return 1
    else:
        return 0



    #######################################################


#
# CheckSrcIpv6InDataWireless :检查抓到的流source ipv6是否满足镜像的要求
#
#   args:
#                srcipv6: source ipv6
#                data: actual frame data
#
#   return: 
#                1 :满足要求
#                0:不满足要求
# examples:
#           CheckDsendCaptureStreamWireless('2',PortType='1',SrcIpv6='2001::1')
##########################################################  
def CheckSrcIpv6InDataWireless(srcipv6, data):
    Layer2Header = GetMacHeaderLenWireless(data) + 8
    vlanflaginit = (Layer2Header - 2) * 3
    vlanflag = data[vlanflaginit:(vlanflaginit + 5)]
    if vlanflag == '81 00':
        srcipinit = (Layer2Header + 12) * 3
        data = data[srcipinit:(srcipinit + 47)]
    else:
        srcipinit = (Layer2Header + 8) * 3
        data = data[srcipinit:(srcipinit + 47)]
    data = re.sub(' ', '', data)
    n1 = data[0:4]
    n2 = data[4:8]
    n3 = data[8:12]
    n4 = data[12:16]
    n5 = data[16:20]
    n6 = data[20:24]
    n7 = data[24:28]
    n8 = data[28:32]
    ipv6str = str(n1) + ':' + str(n2) + ':' + str(n3) + ':' + str(n4) + ':' + str(n5) + ':' + str(n6) + ':' + str(
        n7) + ':' + str(n8)
    srcipv6 = FormatIpv6(srcipv6)
    srcipv6 = srcipv6.upper()
    if srcipv6 == ipv6str:
        return 1
    else:
        return 0


#######################################################
#
# CheckDstIpv6InDataWireless :检查抓到的流destination ipv6是否满足镜像的要求
#
#   args:
#                dstipv6: destination ipv6
#                data: actual frame data
#
#   return: 
#                1 :满足要求
#                0:不满足要求
# examples:
#           CheckDsendCaptureStreamWireless('2',PortType='1',DstIpv6='2001::2')
##########################################################
def CheckDstIpv6InDataWireless(dstipv6, data):
    Layer2Header = GetMacHeaderLenWireless(data) + 8
    vlanflaginit = (Layer2Header - 2) * 3
    vlanflag = data[vlanflaginit:(vlanflaginit + 5)]
    if vlanflag == '81 00':
        srcipinit = (Layer2Header + 28) * 3
        data = data[srcipinit:(srcipinit + 47)]
    else:
        srcipinit = (Layer2Header + 24) * 3
        data = data[srcipinit:(srcipinit + 47)]
    data = re.sub(' ', '', data)
    n1 = data[0:4]
    n2 = data[4:8]
    n3 = data[8:12]
    n4 = data[12:16]
    n5 = data[16:20]
    n6 = data[20:24]
    n7 = data[24:28]
    n8 = data[28:32]
    ipv6str = str(n1) + ':' + str(n2) + ':' + str(n3) + ':' + str(n4) + ':' + str(n5) + ':' + str(n6) + ':' + str(
        n7) + ':' + str(n8)
    dstipv6 = FormatIpv6(dstipv6)
    dstipv6 = dstipv6.upper()
    if dstipv6 == ipv6str:
        return 1
    else:
        return 0


#######################################################
#
# CheckTpidInDataWireless :检查抓到的流vlan tpid是否满足镜像的要求
#
#   args:
#                vlantag: vlan tpid
#                data: actual frame data
#
#   return: 
#                1 :满足要求
#                0:不满足要求
#   eg:
# CheckDsendCaptureStreamWireless('2',Tpid=['81','91'])
# CheckDsendCaptureStreamWireless('2',Tpid=['81'])
# Tpid取一个值，则仅判断报文第一层Tpid;Tpid取两个值，第一个值为外层Tpid值，第二个值为内层Tpid的值
# 当Tpid值为8100或9100时，判断时只取81或91，即对前两位判断
#
##########################################################
def CheckTpidInDataWireless(Tpid, data):
    Layer2Header = GetMacHeaderLenWireless(data) + 8
    vlanflaginit = (Layer2Header - 2) * 3
    if len(Tpid) == 1:
        data = data[vlanflaginit:(vlanflaginit + 2)]
        if Tpid[0] == data:
            return 1
        else:
            return 0
    if len(Tpid) == 2:
        outtpid = Tpid[0]
        intpid = Tpid[1]
        outdata = data[vlanflaginit:(vlanflaginit + 2)]
        indata = data[(vlanflaginit + 12):(vlanflaginit + 14)]
        if outtpid == outdata and intpid == indata:
            return 1
        else:
            return 0


#######################################################
#
# CheckVlanTagInDataWireless :检查抓到的流vlan tag是否满足镜像的要求
#
#   args:
#                vlantag: vlan tag
#                data: actual frame data
#
#   return: 
#                1 :满足要求
#                0:不满足要求
#
# CheckDsendCaptureStreamWireless('2',VlanTag=['100','10'])
# CheckDsendCaptureStreamWireless('2',VlanTag=['100'])
# VlanTag取一个值，则仅判断报文第一层Tag;VlanTag取两个值，第一个值为外层Tag值，第二个值为内层Tag的值
# 取值为-1，表示没有VlanTag;取值为0，表示不关心是否有VlanTag;取值为>0，表示要求有VlanTag，该值为Vid
#
##########################################################
def CheckVlanTagInDataWireless(vlantag, data):
    Layer2Header = GetMacHeaderLenWireless(data) + 8
    vlanflaginit = (Layer2Header - 2) * 3
    if len(vlantag) == 1:
        if int(vlantag[0]) == 0:
            # VlanTag为0，不关心是否有Tag
            return 1
        if int(vlantag[0]) > 0:
            # VlanTag>0，对报文进行判断
            if data[vlanflaginit:(vlanflaginit + 5)] == '81 00':
                temp = data[(vlanflaginit + 7):(vlanflaginit + 11)]
                temp = re.sub(' ', '', temp)
                temp = '0x' + temp
                temp = int(temp, 16)
                if int(vlantag[0]) == temp:
                    return 1
        if vlantag[0] == '-1':
            # VlanTag为-1，报文不存在Tag
            if data[135:140] != '81 00':
                return 1
    elif len(vlantag) > 2:
        # 判断三层tag
        outtag = vlantag[0]
        intag = vlantag[1]
        intag1 = vlantag[2]
        # 最外层
        temp = data[(vlanflaginit + 7):(vlanflaginit + 11)]
        temp = re.sub(' ', '', temp)
        temp = '0x' + temp
        temp = int(temp, 16)
        # 第二层
        tmp = data[(vlanflaginit + 19):(vlanflaginit + 23)]
        tmp = re.sub(' ', '', tmp)
        tmp = '0x' + tmp
        tmp = int(tmp, 16)
        # 第三层
        tmp1 = data[(vlanflaginit + 31):(vlanflaginit + 35)]
        tmp1 = re.sub(' ', '', tmp1)
        tmp1 = '0x' + tmp1
        tmp1 = int(tmp1, 16)
        if outtag == temp and intag == tmp and intag1 == tmp1:
            return 1
    else:
        # VlanTag有两个取值
        outtag = vlantag[0]
        intag = vlantag[1]
        # 外层VlanTag为0时
        if int(outtag) == 0:
            if int(intag) == 0:
                return 1
            if intag == '-1':
                if data[(vlanflaginit + 12):(vlanflaginit + 17)] != '81 00':
                    return 1
            if int(intag) > 0:
                if data[vlanflaginit:(vlanflaginit + 5)] == '81 00':
                    if data[(vlanflaginit + 12):(vlanflaginit + 17)] == '81 00':
                        temp = data[(vlanflaginit + 19):(vlanflaginit + 23)]
                        temp = re.sub(' ', '', temp)
                        temp = '0x' + temp
                        temp = int(temp, 16)
                        if int(intag) == temp:
                            return 1
        # 外层VlanTag为0时
        if int(outtag) > 0:
            if data[vlanflaginit:(vlanflaginit + 5)] == '81 00':
                temp = data[(vlanflaginit + 7):(vlanflaginit + 11)]
                temp = re.sub(' ', '', temp)
                temp = '0x' + temp
                temp = int(temp, 16)
                if int(outtag) == temp:
                    if int(intag) == 0:
                        return 1
                    if intag == '-1':
                        if data[(vlanflaginit + 12):(vlanflaginit + 17)] != '81 00':
                            return 1
                    if int(intag) > 0:
                        if data[(vlanflaginit + 12):(vlanflaginit + 17)] == '81 00' or data[(vlanflaginit + 12):(
                                    vlanflaginit + 17)] == '91 00':
                            tmp = data[(vlanflaginit + 19):(vlanflaginit + 23)]
                            tmp = re.sub(' ', '', tmp)
                            tmp = '0x' + tmp
                            tmp = int(tmp, 16)
                            if int(intag) == tmp:
                                return 1
    return 0


#######################################################
#
# CheckCosInDataWireless :检查抓到的流cos(vlan头中的UserPriority)是否满足镜像的要求
#
#   args:
#                cos: cos 
#                data: actual frame data
#
#   return: 
#                1 :满足要求
#                0:不满足要求
#
# CheckDsendCaptureStreamWireless('2',Cos=['3'])
# CheckDsendCaptureStreamWireless('2',Cos=['3','4','5'])
# Cos的值使用十进制
# Cos取一个值，则仅判断报文第一层Cos;Cos取两个值，第一个值为外层Cos值，第二个值为内层Cos的值
# Cos取三个值，判断三层Cos值，第一个值为外层Cos值，第二个值为次外层Cos的值，第三个值为内层Cos的值
########################################################## 
def CheckCosInDataWireless(cos, data):
    Layer2Header = GetMacHeaderLenWireless(data) + 8
    vlanflaginit = (Layer2Header - 2) * 3
    # cos 取一个值
    if len(cos) == 1:
        data = data[(vlanflaginit + 6)]
        data = '0x' + data
        data = int(data, 16)
        data = data / 2
        if int(cos[0]) == data:
            return 1
        else:
            return 0
        # cos 取两个值
    if len(cos) == 2:
        outcos = cos[0]
        incos = cos[1]
        outdata = data[(vlanflaginit + 6)]
        outdata = '0x' + outdata
        outdata = int(outdata, 16)
        outdata = outdata / 2
        indata = data[153]
        indata = '0x' + indata
        indata = int(indata, 16)
        indata = indata / 2
        if int(outcos) == outdata and int(incos) == indata:
            return 1
        else:
            return 0
        # cos 取三个值
    if len(cos) == 3:
        outcos = cos[0]
        incos = cos[1]
        incos1 = cos[2]
        outdata = data[(vlanflaginit + 6)]
        outdata = '0x' + outdata
        outdata = int(outdata, 16)
        outdata = outdata / 2
        indata = data[(vlanflaginit + 18)]
        indata = '0x' + indata
        indata = int(indata, 16)
        indata = indata / 2
        indata1 = data[(vlanflaginit + 30)]
        indata1 = '0x' + indata1
        indata1 = int(indata1, 16)
        indata1 = indata1 / 2
        if int(outcos) == outdata and int(incos) == indata and int(incos1) == indata1:
            return 1
        else:
            return 0



        ###########################################


# 判断arp包的类型
# CheckDsendCaptureStreamWireless('2',ArpType='request')
# CheckDsendCaptureStreamWireless('2',ArpType='reply')
###########################################
def CheckArpTypeInDataWireless(arptype, data):
    Layer2Header = GetMacHeaderLenWireless(data) + 8
    vlanflaginit = (Layer2Header - 2) * 3
    flag = data[vlanflaginit:(vlanflaginit + 5)]
    if flag == '81 00':
        arpoperation = data[(vlanflaginit + 36):(vlanflaginit + 41)]
    elif flag == '08 06':
        arpoperation = data[(vlanflaginit + 24):(vlanflaginit + 29)]
    else:
        return 0
    if arptype == 'request' and arpoperation == '00 01':
        return 1
    elif arptype == 'reply' and arpoperation == '00 02':
        return 1
    else:
        return 0


###########################################
# 判断arp包的协议源mac
# CheckDsendCaptureStreamWireless('2',ArpSenderHardwareAddress='00-00-00-00-00-01')
###########################################    
def CheckArpSenderHardwareAddressInDataWireless(sendermac, data):
    Layer2Header = GetMacHeaderLenWireless(data) + 8
    vlanflaginit = (Layer2Header - 2) * 3
    flag = data[vlanflaginit:(vlanflaginit + 5)]
    if flag == '81 00':
        data = data[(vlanflaginit + 42):(vlanflaginit + 59)]
    if flag == '08 06':
        data = data[(vlanflaginit + 30):(vlanflaginit + 47)]
    data = re.sub(' ', '-', data)
    sendermac = sendermac.upper()
    if sendermac == data:
        return 1
    else:
        return 0


###########################################
# 判断arp包的协议源ip
# CheckDsendCaptureStreamWireless('2',ArpSenderProtocolAddress='1.1.1.1')
###########################################    
def CheckArpSenderProtocolAddressInDataWireless(senderip, data):
    Layer2Header = GetMacHeaderLenWireless(data) + 8
    vlanflaginit = (Layer2Header - 2) * 3
    flag = data[vlanflaginit:(vlanflaginit + 5)]
    if flag == '81 00':
        data = data[(vlanflaginit + 60):(vlanflaginit + 71)]
    if flag == '08 06':
        data = data[(vlanflaginit + 48):(vlanflaginit + 59)]
    n1 = data[0:2]
    n2 = data[3:5]
    n3 = data[6:8]
    n4 = data[9:11]
    n1 = '0x' + n1
    num1 = int(n1, 16)
    n2 = '0x' + n2
    num2 = int(n2, 16)
    n3 = '0x' + n3
    num3 = int(n3, 16)
    n4 = '0x' + n4
    num4 = int(n4, 16)
    spring = str(num1) + '.' + str(num2) + '.' + str(num3) + '.' + str(num4)
    if senderip == spring:
        return 1
    else:
        return 0


###########################################
# 判断arp包的协议目的mac
# CheckDsendCaptureStreamWireless('2',ArpTargetHardwareAddress='00-00-00-00-00-01')
###########################################    
def CheckArpTargetHardwareAddressInDataWireless(targetmac, data):
    Layer2Header = GetMacHeaderLenWireless(data) + 8
    vlanflaginit = (Layer2Header - 2) * 3
    flag = data[vlanflaginit:(vlanflaginit + 5)]
    if flag == '81 00':
        data = data[(vlanflaginit + 72):(vlanflaginit + 89)]
    if flag == '08 06':
        data = data[(vlanflaginit + 60):(vlanflaginit + 77)]
    data = re.sub(' ', '-', data)
    targetmac = targetmac.upper()
    if targetmac == data:
        return 1
    else:
        return 0


###########################################
# 判断arp包的协议目的ip
# CheckDsendCaptureStreamWireless('2',ArpTargetProtocolAddress='1.1.1.1')
###########################################    
def CheckArpTargetProtocolAddressInDataWireless(targetip, data):
    Layer2Header = GetMacHeaderLenWireless(data) + 8
    vlanflaginit = (Layer2Header - 2) * 3
    flag = data[vlanflaginit:(vlanflaginit + 5)]
    if flag == '81 00':
        data = data[(vlanflaginit + 90):(vlanflaginit + 101)]
    if flag == '08 06':
        data = data[(vlanflaginit + 78):(vlanflaginit + 89)]
    n1 = data[0:2]
    n2 = data[3:5]
    n3 = data[6:8]
    n4 = data[9:11]
    n1 = '0x' + n1
    num1 = int(n1, 16)
    n2 = '0x' + n2
    num2 = int(n2, 16)
    n3 = '0x' + n3
    num3 = int(n3, 16)
    n4 = '0x' + n4
    num4 = int(n4, 16)
    spring = str(num1) + '.' + str(num2) + '.' + str(num3) + '.' + str(num4)
    if targetip == spring:
        return 1
    else:
        return 0


#######################################################
# CheckACKInDataWireless :检查抓到的流ACK是否满足要求
#
#   args:
#                record: true or false
#                data: actual frame data
#
#   return: 
#                1 :满足要求
#                0:不满足要求
#
# examples:
#           CheckDsendCaptureStreamWireless('2',ACK='true')
########################################################## 
def CheckACKInDataWireless(record, data):
    # Get tcp ACK from data
    Layer2Header = GetMacHeaderLenWireless(data) + 8
    vlanflaginit = (Layer2Header - 2) * 3
    flag = data[vlanflaginit:(vlanflaginit + 5)]
    if flag == '81 00':
        TcpFlag = data[(vlanflaginit + 117):(vlanflaginit + 119)]
        TcpFlag = '0x0' + TcpFlag
        TcpFlag = int(TcpFlag, 16)
    else:
        TcpFlag = data[(vlanflaginit + 105):(vlanflaginit + 107)]
        TcpFlag = '0x0' + TcpFlag
        TcpFlag = int(TcpFlag, 16)
    if ((TcpFlag & 16 == 16) and (record == 'true')) or ((TcpFlag & 16 != 16) and (record == 'false')):
        return 1
    else:
        return 0


#######################################################
# CheckSYNInDataWireless :检查抓到的流SYN是否满足要求
#
#   args:
#                record: true or false
#                data: actual frame data
#
#   return: 
#                1 :满足要求
#                0:不满足要求
#
# examples:
#           CheckDsendCaptureStreamWireless('2',SYN='true')
########################################################## 
def CheckSYNInDataWireless(record, data):
    # Get tcp SYN from data
    Layer2Header = GetMacHeaderLenWireless(data) + 8
    vlanflaginit = (Layer2Header - 2) * 3
    flag = data[vlanflaginit:(vlanflaginit + 5)]
    if flag == '81 00':
        TcpFlag = data[(vlanflaginit + 117):(vlanflaginit + 119)]
        TcpFlag = '0x0' + TcpFlag
        TcpFlag = int(TcpFlag, 16)
    else:
        TcpFlag = data[(vlanflaginit + 105):(vlanflaginit + 107)]
        TcpFlag = '0x0' + TcpFlag
        TcpFlag = int(TcpFlag, 16)
    if ((TcpFlag & 2 == 2) and (record == 'true')) or ((TcpFlag & 2 != 2) and (record == 'false')):
        return 1
    else:
        return 0


#######################################################
# CheckFINInDataWireless :检查抓到的流FIN是否满足要求
#
#   args:
#                record: true or false
#                data: actual frame data
#
#   return: 
#                1 :满足要求
#                0:不满足要求
#
# examples:
#           CheckDsendCaptureStreamWireless('2',FIN='true')
########################################################## 
def CheckFINInDataWireless(record, data):
    # Get tcp FIN from data
    Layer2Header = GetMacHeaderLenWireless(data) + 8
    vlanflaginit = (Layer2Header - 2) * 3
    flag = data[vlanflaginit:(vlanflaginit + 5)]
    if flag == '81 00':
        TcpFlag = data[(vlanflaginit + 117):(vlanflaginit + 119)]
        TcpFlag = '0x0' + TcpFlag
        TcpFlag = int(TcpFlag, 16)
    else:
        TcpFlag = data[(vlanflaginit + 105):(vlanflaginit + 107)]
        TcpFlag = '0x0' + TcpFlag
        TcpFlag = int(TcpFlag, 16)
    if ((TcpFlag & 1 == 1) and (record == 'true')) or ((TcpFlag & 1 != 1) and (record == 'false')):
        return 1
    else:
        return 0


#######################################################
# CheckRSTInDataWireless :检查抓到的流RST是否满足要求
#
#   args:
#                record: true or false
#                data: actual frame data
#
#   return: 
#                1 :满足要求
#                0:不满足要求
#
# examples:
#           CheckDsendCaptureStreamWireless('2',RST='true')
########################################################## 
def CheckRSTInDataWireless(record, data):
    # Get tcp RST from data
    Layer2Header = GetMacHeaderLenWireless(data) + 8
    vlanflaginit = (Layer2Header - 2) * 3
    flag = data[vlanflaginit:(vlanflaginit + 5)]
    if flag == '81 00':
        TcpFlag = data[(vlanflaginit + 117):(vlanflaginit + 119)]
        TcpFlag = '0x0' + TcpFlag
        TcpFlag = int(TcpFlag, 16)
    else:
        TcpFlag = data[(vlanflaginit + 105):(vlanflaginit + 107)]
        TcpFlag = '0x0' + TcpFlag
        TcpFlag = int(TcpFlag, 16)
    if ((TcpFlag & 4 == 4) and (record == 'true')) or ((TcpFlag & 4 != 4) and (record == 'false')):
        return 1
    else:
        return 0


#######################################################
# CheckPSHInDataWireless :检查抓到的流PSH是否满足要求
#
#   args:
#                record: true or false
#                data: actual frame data
#
#   return: 
#                1 :满足要求
#                0:不满足要求
#
# examples:
#           CheckDsendCaptureStreamWireless('2',PSH='true')
########################################################## 
def CheckPSHInDataWireless(record, data):
    # Get tcp PSH from data
    Layer2Header = GetMacHeaderLenWireless(data) + 8
    vlanflaginit = (Layer2Header - 2) * 3
    flag = data[vlanflaginit:(vlanflaginit + 5)]
    if flag == '81 00':
        TcpFlag = data[(vlanflaginit + 117):(vlanflaginit + 119)]
        TcpFlag = '0x0' + TcpFlag
        TcpFlag = int(TcpFlag, 16)
    else:
        TcpFlag = data[(vlanflaginit + 105):(vlanflaginit + 107)]
        TcpFlag = '0x0' + TcpFlag
        TcpFlag = int(TcpFlag, 16)
    if ((TcpFlag & 8 == 8) and (record == 'true')) or ((TcpFlag & 8 != 8) and (record == 'false')):
        return 1
    else:
        return 0


#######################################################
# CheckURGInDataWireless :检查抓到的流URG是否满足要求
#
#   args:
#                record: true or false
#                data: actual frame data
#
#   return: 
#                1 :满足要求
#                0:不满足要求
#
# examples:
#           CheckDsendCaptureStreamWireless('2',URG='true')
########################################################## 
def CheckURGInDataWireless(record, data):
    # Get tcp URG from data
    Layer2Header = GetMacHeaderLenWireless(data) + 8
    vlanflaginit = (Layer2Header - 2) * 3
    flag = data[vlanflaginit:(vlanflaginit + 5)]
    if flag == '81 00':
        TcpFlag = data[(vlanflaginit + 117):(vlanflaginit + 119)]
        TcpFlag = '0x0' + TcpFlag
        TcpFlag = int(TcpFlag, 16)
    else:
        TcpFlag = data[(vlanflaginit + 105):(vlanflaginit + 107)]
        TcpFlag = '0x0' + TcpFlag
        TcpFlag = int(TcpFlag, 16)
    if ((TcpFlag & 32 == 32) and (record == 'true')) or ((TcpFlag & 32 != 32) and (record == 'false')):
        return 1
    else:
        return 0


#######################################################
# CheckProtocolExInDataWireless :检查抓到的流ProtocolEx是否满足要求
#
#   args:
#                record: tcp, udp, rip, icmp or igmp
#                data: actual frame data
#
#   return: 
#                1 :满足要求
#                0:不满足要求
#
# examples:
#           CheckDsendCaptureStreamWireless('2',ProtocolEx='tcp')
########################################################## 
def CheckProtocolExInDataWireless(record, data):
    # Get tcp URG from data
    Layer2Header = GetMacHeaderLenWireless(data) + 8
    vlanflaginit = (Layer2Header - 2) * 3
    flag = data[vlanflaginit:(vlanflaginit + 5)]
    if flag == '81 00':
        protocolEx = data[(vlanflaginit + 45):(vlanflaginit + 47)]
    else:
        protocolEx = data[(vlanflaginit + 33):(vlanflaginit + 35)]
    if record == 'tcp':
        record = 6
    elif record == 'udp':
        record = 17
    elif record == 'rip':
        record = 17
    elif record == 'icmp':
        record = 1
    elif record == 'igmp':
        record = 2
    else:
        record = -1
    strTemp = '0x0' + protocolEx
    if int(strTemp, 16) == record:
        return 1
    else:
        return 0


#######################################################
# CheckAddress1InDataWireless :检查抓到的报文中的802.11 header中的Address1是否满足要求
#
#   args:
#                address1: 802.11 header中的Address1
#                data: actual frame data
#
#   return: 
#                1 :满足要求
#                0:不满足要求
#
# examples:
#           CheckDsendCaptureStreamWireless('2',PortType='1',Address1='00-03-0f-18-cf-81')
########################################################## 
def CheckAddress1InDataWireless(address1, data):
    # 取出并计算Radiotap header的长度
    radiolen1 = data[6:8]
    radiolen2 = data[9:11]
    radiolen = '0x' + str(radiolen2) + str(radiolen1)
    radiolen = int(radiolen, 16)

    valueinit = (radiolen + 4) * 3
    valuefina = valueinit + 17

    data = data[valueinit:valuefina]
    data = re.sub(' ', '-', data)
    address1 = address1.upper()
    if address1 == data:
        return 1
    else:
        return 0


#######################################################
# CheckAddress2InDataWireless :检查抓到的报文中的802.11 header中的Address2是否满足要求
#
#   args:
#                address2: 802.11 header中的Address2
#                data: actual frame data
#
#   return: 
#                1 :满足要求
#                0:不满足要求
#
# examples:
#           CheckDsendCaptureStreamWireless('2',Address2='00-03-0f-18-cf-81')
########################################################## 
def CheckAddress2InDataWireless(address2, data):
    # 取出并计算Radiotap header的长度
    radiolen1 = data[6:8]
    radiolen2 = data[9:11]
    radiolen = '0x' + str(radiolen2) + str(radiolen1)
    radiolen = int(radiolen, 16)

    valueinit = (radiolen + 10) * 3
    valuefina = valueinit + 17

    data = data[valueinit:valuefina]
    data = re.sub(' ', '-', data)
    address2 = address2.upper()
    if address2 == data:
        return 1
    else:
        return 0


#######################################################
# CheckAddress3InDataWireless :检查抓到的报文中的802.11 header中的Address3是否满足要求
#
#   args:
#                address3: 802.11 header中的Address3
#                data: actual frame data
#
#   return: 
#                1 :满足要求
#                0:不满足要求
#
# examples:
#           CheckDsendCaptureStreamWireless('2',Address3='00-03-0f-18-cf-81')
########################################################## 
def CheckAddress3InDataWireless(address3, data):
    # 取出并计算Radiotap header的长度
    radiolen1 = data[6:8]
    radiolen2 = data[9:11]
    radiolen = '0x' + str(radiolen2) + str(radiolen1)
    radiolen = int(radiolen, 16)

    valueinit = (radiolen + 16) * 3
    valuefina = valueinit + 17

    data = data[valueinit:valuefina]
    data = re.sub(' ', '-', data)
    address3 = address3.upper()
    if address3 == data:
        return 1
    else:
        return 0


#######################################################
# CheckAddress4InDataWireless :检查抓到的报文中的802.11 header中的Address4是否满足要求
#
#   args:
#                address4: 802.11 header中的Address4
#                data: actual frame data
#
#   return: 
#                1 :满足要求
#                0:不满足要求
#
# examples:
#           CheckDsendCaptureStreamWireless('2',Address4='00-03-0f-18-cf-81')
########################################################## 
def CheckAddress4InDataWireless(address4, data):
    # 取出并计算Radiotap header的长度
    radiolen1 = data[6:8]
    radiolen2 = data[9:11]
    radiolen = '0x' + str(radiolen2) + str(radiolen1)
    radiolen = int(radiolen, 16)

    valueinit = (radiolen + 24) * 3
    valuefina = valueinit + 17

    data = data[valueinit:valuefina]
    data = re.sub(' ', '-', data)
    address4 = address4.upper()
    if address4 == data:
        return 1
    else:
        return 0
