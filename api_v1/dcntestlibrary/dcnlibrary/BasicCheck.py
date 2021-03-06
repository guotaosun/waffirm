#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# *********************************************************************
# BasicCheck.py - Proc of Basic Check
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
#
# *********************************************************************
import re
import time

from dutils.dcnprint import printRes, printResWarn


def CheckLine(data, *args, **flag):
    """
##################################################################################
#
# CheckLine :检查表项中是否含有指定行
#
# args:
#     data: 要检查匹配的值
#     *args : 需要匹配的字符串，以逗号分隔
#     **flag: 可选的标志位[RS:列敏感]
#
# return:
#     成功：返回0
#     失败：返回-1
#
# addition:
#
# examples:
#    在某一行中按先后顺序存在1、2、5
#    CheckLine('1 2 3 4 5','1','2')
#    return 0
#
#    列敏感
#    CheckLine('1 2 3 4 5','1','2',RS = True)
#    return 0
#    CheckLine('1 2 3 4 5','1','5',RS = True)
#    return -1
#    CheckLine('1 2 3 4 5','1','','','','5',RS = True)
#    return 0
###################################################################################
    :param data: 要检查匹配的值
    :param args: 需要匹配的字符串，以逗号分隔
    :param flag: 可选的标志位[RS:列敏感]
    :return: 成功：返回0, 失败：返回-1
    """
    rowSensitive = False
    printMatch = True
    moreLine = False
    ignoreCase = False
    for j in list(flag.keys()):
        if j == 'RS':
            rowSensitive = flag[j]
        elif j == 'PM':
            printMatch = flag[j]
        elif j == 'ML':
            moreLine = flag[j]
        elif j == 'IC':
            ignoreCase = flag[j]
    
    if not rowSensitive:
        pat = '.*?'
        patstr = '.*?'
    else:
        pat = '\s*'
        patstr = '\s*'
    
    for i in args:
        if i == '':
            i = '[\S]+'
        patstr += str(i) + pat
    if moreLine:
        compilerule = re.compile(patstr, re.S)
    elif ignoreCase:
        compilerule = re.compile(patstr, re.I)
    else:
        compilerule = re.compile(patstr)
    match = compilerule.search(data)
    if match:
        try:
            if printMatch:
                printRes('[Match Line:]' + str(match.group()))
            res = 0
        except BaseException as e:
            print(e)
            res = -2
    else:
        if printMatch:
            printResWarn('[Match Line Fail:]' + patstr)
        res = -1
    return res


def CheckLineList(data, checklist, **flag):
    """
##################################################################################
#
# CheckLineList :检查表项中是否含有指定的多行
#
# args:
#     data: 要检查匹配的值
#     checklist : 需要匹配的字符串列表，类型为由元组组成的列表[(tuple),(tuple),(tuple)]
#     **flag: 可选的标志位[RS:列敏感]
#
# return:
#     成功：返回0
#     失败：返回-1
#
# addition:
#
# examples:
#    data:
#    1    00-00-01-00-00-02           DYNAMIC Hardware Ethernet1/0/1
#    1    00-00-01-00-00-03           DYNAMIC Hardware Ethernet1/0/1
#    1    00-00-01-00-00-04           DYNAMIC Hardware Ethernet1/0/1
#    1    00-00-01-00-00-05           DYNAMIC Hardware Ethernet1/0/1
#    1    00-00-01-00-00-06           DYNAMIC Hardware Ethernet1/0/1
#
#    checklist1 = []
#    checklist1.append(('00-00-01-00-00-02','DYNAMIC'))
#    checklist1.append(('00-00-01-00-00-03','DYNAMIC'))
#    checklist1.append(('00-00-01-00-00-06','DYNAMIC'))
#
#    CheckLineList(data,checklist1)
#    return 0
#    CheckLineList(data,checklist1,RS=True)
#    return -1
###################################################################################
    modified by yanwh 2017/12/28
    给rx赋予初始值，用isinstance的方式判断数据类型取代之前的type方式，兼容支持string和unicode类型
    :param data: 要检查匹配的值
    :param checklist: 需要匹配的字符串列表，类型为由元组组成的列表[(tuple),(tuple),(tuple)]
    :param flag: 可选的标志位[RS:列敏感]
    :return: 成功：返回0
             失败：返回-1
    """
    res, rx = 0, -1
    if not isinstance(checklist, list):
        printRes('Error:Require a list type!')
        return -3
    for checkline in checklist:
        if isinstance(checkline, tuple):
            rx = CheckLine(data, *checkline, **flag)
        elif isinstance(checkline, str):
            rx = CheckLine(data, checkline, **flag)
        if rx == -1:
            res = -1
    return res


##################################################################################
#
# CheckNoLineList :检查表项中是否不含有指定的多行
#
# args:  
#     data: 要检查匹配的值
#     checklist : 需要匹配的字符串列表，类型为由元组组成的列表[(tuple),(tuple),(tuple)]
#     **flag: 可选的标志位[RS:列敏感]
#
# return: 
#     成功：返回0
#     失败：返回-1
#
# addition:
#
# examples:
#    data:
#    1    00-00-01-00-00-02           DYNAMIC Hardware Ethernet1/0/1
#    1    00-00-01-00-00-03           DYNAMIC Hardware Ethernet1/0/1
#    1    00-00-01-00-00-04           DYNAMIC Hardware Ethernet1/0/1
#    1    00-00-01-00-00-05           DYNAMIC Hardware Ethernet1/0/1
#    1    00-00-01-00-00-06           DYNAMIC Hardware Ethernet1/0/1
#
#    checklist1 = []
#    checklist1.append(('00-00-01-00-00-02','DYNAMIC'))
#    checklist1.append(('00-00-01-00-00-03','DYNAMIC'))
#    checklist1.append(('00-00-01-00-00-06','DYNAMIC'))
#
#    CheckNoLineList(data,checklist1)
#    return -1
#    CheckNoLineList(data,checklist1,RS=True)
#    return 0
###################################################################################
def CheckNoLineList(data, checklist, **flag):
    res = 0
    # if type(checklist) != type([]):
    if not isinstance(checklist, list):
        printRes('Error:Require a list type!')
        return -3
    for checkline in checklist:
        rx = 0
        # rx = CheckNoLine(data,*checkline,**flag)
        # if type(checkline) == type(()):
        if isinstance(checkline, tuple):
            rx = CheckLine(data, *checkline, **flag)
        # elif type(checkline) == type(''):
        elif isinstance(checkline, str):
            rx = CheckLine(data, checkline, **flag)
        if rx == 0:
            res = -1
    return res


##################################################################################
#
# CheckLineInOrder :检查表项中是否含有指定的按顺序排列的多行
#
# args:  
#     data: 要检查匹配的值
#     checklist : 需要匹配的字符串列表，类型为由元组组成的列表[(tuple),(tuple),(tuple)]
#     **flag: 可选的标志位[RS:列敏感]
#
# return: 
#     成功：返回0
#     失败：返回-1
#
# addition:
#
# examples:
#    data:
#    1    00-00-01-00-00-02           DYNAMIC Hardware Ethernet1/0/1
#    1    00-00-01-00-00-03           DYNAMIC Hardware Ethernet1/0/1
#    1    00-00-01-00-00-04           DYNAMIC Hardware Ethernet1/0/1
#    1    00-00-01-00-00-05           DYNAMIC Hardware Ethernet1/0/1
#    1    00-00-01-00-00-06           DYNAMIC Hardware Ethernet1/0/1
#
#    checklist1 = []
#    checklist1.append(('00-00-01-00-00-02','DYNAMIC'))
#    checklist1.append(('00-00-01-00-00-03','DYNAMIC'))
#    checklist1.append(('00-00-01-00-00-06','DYNAMIC'))
#
#    CheckLineInOrder(data,checklist1)
#    return 0
#    CheckLineInOrder(data,checklist1,RS=True)
#    return -1
###################################################################################
def CheckLineInOrder(data, checklist, **flag):
    patten = []
    if not isinstance(checklist, list):
        # if type(checklist) != type([]):
        printRes('Error:Require a list type!')
        return -3
    
    for checkline in checklist:
        # if type(checkline) == type(()):
        if isinstance(checkline, tuple):
            for i in checkline:
                patten.append(i)
        elif isinstance(checkline, str):
            # elif type(checkline) == type(''):
            patten.append(checkline)
    
    patten = tuple(patten)
    res = CheckLine(data, ML=True, *patten, **flag)
    return res


##################################################################################
#
# CheckLineInOneRow :检查表项中是否含有指定的按顺序排列的多行
#
# args:  
#     data: 要检查匹配的值
#     checklist : 需要匹配的字符串列表，类型为由元组组成的列表[(tuple),(tuple),(tuple)]
#     **flag: 可选的标志位[RS:列敏感]
#
# return: 
#     成功：返回0
#     失败：返回-1
#
# addition:
#
# examples:
#    data:
#    1    00-00-01-00-00-02           DYNAMIC Hardware Ethernet1/0/1
#    1    00-00-01-00-00-03           DYNAMIC Hardware Ethernet1/0/1
#    1    00-00-01-00-00-04           DYNAMIC Hardware Ethernet1/0/1
#    1    00-00-01-00-00-05           DYNAMIC Hardware Ethernet1/0/1
#    1    00-00-01-00-00-06           DYNAMIC Hardware Ethernet1/0/1
#
#    checklist1 = []
#    checklist1.append(('00-00-01-00-00-02','DYNAMIC'))
#    checklist1.append(('00-00-01-00-00-03','DYNAMIC'))
#    checklist1.append(('00-00-01-00-00-06','DYNAMIC'))
#    checklist2 = []
#    checklist2.append(('00-00-01-00-00-02','DYNAMIC'))
#    checklist2.append(('00-00-01-00-00-03','DYNAMIC'))
#    checklist2.append(('00-00-01-00-00-04','DYNAMIC'))
#
#    CheckLineList(data,checklist1)
#    return -1
#    CheckLineList(data,checklist2)
#    return 0
###################################################################################
def CheckLineInOneRow(data, checklist, **flag):
    patten = []
    if not isinstance(checklist, list):
        printRes('Error:Require a list type!')
        return -3
    for checkline in checklist:
        if isinstance(checkline, tuple):
            for i in checkline:
                patten.append(i)
        elif isinstance(checkline, str):
            patten.append(checkline)
        
        patten.append('\n')
    patten = tuple(patten)
    res = CheckLine(data, PM=False, *patten, **flag)
    return res


##################################################################################
#
# CheckLineInBlock :在一段表项内匹配
#
# args:  
#     data: 要检查匹配的值
#     seg : 分段标志
#     feature : 该段的特征标志
#     *args : 需要匹配的字符串，以逗号分隔 
#     **flag: 可选的标志位[RS:列敏感]
#
# return: 
#     成功：返回0
#     失败：返回-1
#
# addition:
#
# examples:
#        Interface Ethernet1/0/22
#          port-group 1 mode active
#
#     CheckLineInBlock(ShowRun('s1'),'!','Interface Ethernet1/0/22','port-group 1 mode active')
#     return:0
#
###################################################################################
def CheckLineInBlock(data, seg, feature, *arg, **flag):
    res = -1
    buflist = re.split(seg, data)
    for i in buflist:
        rx = re.search(feature, i)
        if rx is not None:
            res = CheckLine(i, *arg, **flag)
    return res


##################################################################################
#
# GetLineInBlock :返回匹配的一段表项
#
# args:  
#     data: 要检查匹配的值
#     seg : 分段标志
#     feature : 该段的特征标志
#
# return: 
#     成功：返回匹配到的一段表项
#     失败：返回''
#
# addition:
#
# examples:
#     GetLineInBlock(ShowRun('s1'),'!','Interface Ethernet1/0/22')
#     return:
#        Interface Ethernet1/0/22
#          port-group 1 mode active
#
###################################################################################
def GetLineInBlock(data, seg, feature):
    buflist = re.split(seg, data)
    for i in buflist:
        rx = re.search(feature, i)
        if rx is not None:
            return i
    return ''


##################################################################################
#
# GetItemLineNum :检查表项中含有某个值的总行数(检查的值不区分大小写)
#
# args:  
#     value: 要检查匹配的值
#     data : 匹配的范围 
#
# return: 
#     成功：返回匹配到的总行数
#     失败：返回0
#
# addition:
#
# examples:
#     GetItemLineNum('bac\naaa\nasd','a')     ==》返回的结果是3
#     GetItemLineNum('bac\naaa\nasd','zzz')     ==》返回的结果是0
###################################################################################
def GetItemLineNum(data, value):
    # value转化为包含value的一行
    data = str(data) + '\n'
    value = str(value) + '.*\n'
    # 将data和value中的字母都转化为大写字母，以免误判
    data = data.upper()
    value = value.upper()
    # 在data中查找所有包含value的行
    item = re.findall(value, data)
    if item:
        return len(item)
    else:
        return 0


##################################################################################
#
# GetValueBetweenTwoValuesInData :获取一段指定字符串中的2个指定字符串之间的值
#                                 注：1、mode='line', 即在一行内进行匹配，2个指定字符串必须在同一行：  
#                                 如果两个指定字符串有很多个相同的，返回第一个之间的值;
#                                 如果要获取的值是一行的最后一部分字符串，可将behindvalue置为空，即'';
#                                 如果要获取的值是一行的最前一部分字符串，可将beforevalue置为空，即''
#                                 2、mode='moreline', 即在所有行进行匹配，2个指定字符串不必在同一行, 贪婪匹配模式 
#                                 
#
# args:  
#     data: 匹配的范围
#     beforevalue: 要获取的值前面的标志性字符 
#     behindvalue: 要获取的值后面的标志性字符 
#     mode：line,默认值，在同一行匹配;moreline,全部匹配
#
# return: 
#     成功：返回要获取的值
#     失败：返回0
#
# addition:
#
# examples:
#      GetValueBetweenTwoValuesInData('zbcd123asdf\n123456\naaa444bby','zbcd','3','line')
#       ===》返回的结果是两个指定字符之间的'12'
#      GetValueBetweenTwoValuesInData('zbcd123asdf\n123456\naaa444bby','','bcd')
#       ===》返回的结果是指定字符所在行的最前面的字符串'z'
#      GetValueBetweenTwoValuesInData('zbcd123asdf\n123456\naaa444bby','444bb','')
#       ===》返回的结果是指定字符所在行的最后面的字符串'y'
#      GetValueBetweenTwoValuesInData('zbcd123asdf\n123456\naaa444bby','zbcd','3','moreline')
#      ===》多行贪婪匹配返回的结果是'123asdf\n12'
###################################################################################
def GetValueBetweenTwoValuesInData(data, beforevalue, behindvalue, mode='line'):
    if mode == 'line':
        temp1 = str(beforevalue) + '(.*)' + str(behindvalue)
        temp2 = re.search(temp1, data)
        if temp2 is not None:
            temp3 = temp2.group(1)
            # strinfo = 'The value between ' + beforevalue + ' and ' + behindvalue + ' is: ' + temp3
            # printRes(strinfo)
            return temp3
        else:
            strinfo = 'There may be no value between ' + beforevalue + ' and ' + behindvalue
            printRes(strinfo)
            printRes('The data is:')
            printRes(data)
            printRes('The beforevalue is:')
            printRes(beforevalue)
            printRes('The behindvalue is:')
            printRes(behindvalue)
            return 0
    if mode == 'moreline':
        temp1 = str(beforevalue) + '([\s\S]+)' + str(behindvalue)
        temp2 = re.search(temp1, data)
        if temp2 is not None:
            temp3 = temp2.group(1)
            # strinfo = 'The value between ' + beforevalue + ' and ' + behindvalue + ' is: ' + temp3
            # printRes(strinfo)
            return temp3
        else:
            strinfo = 'There may be no value between ' + beforevalue + ' and ' + behindvalue
            printRes(strinfo)
            printRes('The data is:')
            printRes(data)
            printRes('The beforevalue is:')
            printRes(beforevalue)
            printRes('The behindvalue is:')
            printRes(behindvalue)
            return 0


##################################################################################
#
# GetTimeStampEx :获取某段字符串附近的时间戳
#                                 注：mode='1' default   format:   hh:mm:ss
#                                     mode='2' format:             MMMM DD hh:mm:ss YYYY
#                                     mode='3' format:             hhh:mmm:sss
#
# args:  
#     data: 匹配的范围
#     mode: 需要匹配的时间格式
#
#
# return: 
#     成功：返回要获取的值
#     失败：返回0
#
# addition:
#
# examples:
#      GetTimeStampEx(data,'asd',mode='3')
#      
#      
###################################################################################
def GetTimeStampEx(data, *arg, **args):
    re_conn = '.*?'
    re_head = ''
    if 'mode' in args:
        mode = args['mode']
    else:
        mode = '1'
    if mode == '1':
        re_head = '(\d\d:\d\d:\d\d).*?\n*.*?'
    elif mode == '2':
        re_head = '([A-Z][a-z]{2}\s\d\d\s\d\d:\d\d:\d\d\s\d\d\d\d).*?\n*.*?'
    elif mode == '3':
        re_head = '(\d\dh:\d\dm:\d\ds).*?\n*.*?'
    re_list = []
    if arg is not None:
        if len(arg) == 1:
            print(re_head + arg[0])
            match = re.findall(re_head + arg[0], data)
            if match:
                return match
            else:
                return []
        elif len(arg) > 1:
            for i in arg:
                re_list.append(re_head + i)
            re_str = re_conn.join(re_list)
            # print re_str
            match = re.search(re_str, data, re.S)
            if match:
                return list(match.groups())
            else:
                return []


##################################################################################
#
# GetTimeDifference :计算两个时间差
#
# args:  
#     value: 要检查匹配的值
#     data : 匹配的范围 
#
# return: 
#     成功：返回匹配到的总行数
#     失败：返回0
#
# addition:
#
# examples:
#     GetItemLineNum('bac\naaa\nasd','a')     ==》返回的结果是3
#     GetItemLineNum('bac\naaa\nasd','zzz')     ==》返回的结果是0
###################################################################################
# GetTimeDifference('11:06:06','11:07:03')
# GetTimeDifference('11:06:06','11:07:03',Year1 = 2001,Year2 = 2001,Month1=10,Month2=10,Date1 = 23,Date2 = 23)
def GetTimeDifference(time1, time2, **args):
    year1 = year2 = 2000
    month1 = month2 = 1
    date1 = date2 = 1
    monthdict = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
                 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}
    
    # time1、time2格式判断:
    re_rule1 = re.compile('\d\d:\d\d:\d\d')
    re_rule2 = re.compile('([A-Z][a-z]{2})\s(\d\d)\s(\d\d:\d\d:\d\d)\s(\d\d\d\d)')
    
    try:
        
        # 处理time1
        if re_rule1.match(time1):
            pass
        elif re_rule2.match(time1):
            timegroups1 = re_rule2.match(time1).groups()
            time1 = timegroups1[2]
            year1 = int(timegroups1[3])
            month1 = int(monthdict[timegroups1[0]])
            date1 = int(timegroups1[1])
        else:
            return -10
        
        timelist1 = time1.split(':')
        hour1 = int(timelist1[0])
        minute1 = int(timelist1[1])
        second1 = int(timelist1[2])
        
        # 处理time2
        if re_rule1.match(time2):
            pass
        elif re_rule2.match(time2):
            timegroups2 = re_rule2.match(time2).groups()
            time2 = timegroups2[2]
            year2 = int(timegroups2[3])
            month2 = int(monthdict[timegroups2[0]])
            date2 = int(timegroups2[1])
        else:
            return -10
        
        timelist2 = time2.split(':')
        hour2 = int(timelist2[0])
        minute2 = int(timelist2[1])
        second2 = int(timelist2[2])
    
    except BaseException as ex:
        print(ex)
        # 异常是由传入参数格式错误导致的，返回错误码-10
        return -10
    
    tmlist1 = [year1, month1, date1, hour1, minute1, second1, 0, 0, 0]
    tmlist2 = [year2, month2, date2, hour2, minute2, second2, 0, 0, 0]
    return int(time.mktime(tmlist2) - time.mktime(tmlist1))
