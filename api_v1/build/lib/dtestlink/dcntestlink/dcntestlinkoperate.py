#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# *********************************************************************
# Software : PyCharm
#
# dcntestlink.py - 
#
# Author    :yanwh(yanwh@digitalchina.com)
#
# Version 1.0.0
#
# Copyright (c) 2004-9999 Digital China Networks Co. Ltd 
#
#
# *********************************************************************
# Change log:
#       - 2018/3/19 18:36  add by yanwh
#
# *********************************************************************

import json

from pyexpat import ExpatError

try:
    from wx import wx
except ImportError:
    import wx

from .dcntestlinkhelper import DcnTestlinkHelper, singleton


@singleton
class AffirmTestlinkOperate(object):
    """
    DCN所有测试脚本跟testlink服务器交互的入口类，脚本通过实例化该类来进行对服务器的操作
    单例设计模式，保证所有AffirmTestlinkOperate的实例对象均为同一实例
    affirm_tl_operate = AffirmTestlinkOperate(tl_args_flag=1, tl_overwrite_flag=1)
    """
    
    def __init__(self, tl_args_flag=1, tl_overwrite_flag=1):
        """
        :param tl_args_flag: 检查testlink参数是否正确的flag，0：不检查    1：检查
        :param tl_overwrite_flag: 重跑的测试例，结果是否覆盖前面的执行记录. 0:不覆盖，1:覆盖
        """
        self.tl = DcnTestlinkHelper().tl  # 连接到testlink服务器，并且获取到操作句柄
        self.tl_args_flag = tl_args_flag
        self.tl_overwrite_flag = tl_overwrite_flag
    
    def check_testlink_args(self):
        """
        设备型号是否被测试计划引用,如果testlink上没有Affirm/dtestlink/args.py文件中填写的产品线和测试计划，
        脚本不允许执行，参数修改后关掉Dauto平台，重新打开
        :return: None
        """
        if self.tl:
            try:
                
                if self.tl_args_flag == 1:
                    a = self.tl.isDeviceLinkedToTestplan(self.tl.__args__['productLine'], self.tl.__args__['testPlan'],
                                                         self.tl.__args__['testDevice'])
                    b = self.tl.doesUserExist(self.tl.__args__['user'])
                    if a != 0:
                        print(
                            '[告警]Testlink服务器上面不存在该产品线和产品计划，建议您通过Testlink服务器执行自动化测试用例')
                    if not b:
                        print('[告警]Testlink服务器上面不存在该用户，请检查如下配置文件: \n'
                              'AffirmWireless/dtestlink/args.py或者在Testlink服务器上面执行自动化测试用例')
                    if a != 0 or not b:
                        self.tl_args_flag = 0
                    else:
                        print('[通知]Testlink服务器校验成功')
            except Exception as ex:
                print('[错误]跟Testlink服务器交互出错，错误信息如下%s' % ex)
        else:
            print('[告警]与Testlink服务器的连接不成功，请检查网络环境')
    
    def set_waffirm_end(self):
        """
        更新testlink服务器上面执行状态，标记为完成
        :return: {'Status': 1 or 0, 'Message': 'XXX'}
        """
        try:
            job_type = self.tl.getJobInfo(self.tl.__args__['job_id'])['job_type']
            if self.tl.__args__['notes'] != 'end':
                # 如果只执行一个模块，直接将任务进度更新为完成状态
                if job_type == 'waffirm' or job_type == 'waffirm_X86':
                    self.tl.updateJobInfo(self.tl.__args__['job_id'], 2)
                    print('全部测试用例执行完毕，即将关闭确认测试用例平台')
                    main_window = wx.FindWindowById(10)
                    wx.CallAfter(main_window.OnAutoCloseWindow)
                    del self.tl.__args__['job_id']
                    return {'Status': 1, 'Message': 'Waffirm Test End'}
                else:
                    return {'Status': 0, 'Message': 'job type is not waffirm'}
            else:
                return {'Status': 0, 'Message': 'notes is end'}
        except Exception as ex:
            print('error %s' % ex)
    
    def set_testcase_name_by_title(self, title):
        """
        设置testlink服务器上面的testCase名称
        :param title: testCase名称
        :return: None
        """
        """
        通过case名称，更新testlink上面的tl.__args__参数
        :param title: testcase名称，通过printTimer函数中title参数传入
        :return: None, 更新tl.__args__
        """
        try:
            case = title.split()
            # 更新testCase名称
            self.tl.__args__['testCase'] = '_'.join(case[1:])
            if self.tl.getTestCaseByName(self.tl.__args__['productLine'], self.tl.__args__['testSuite'],
                                         self.tl.__args__['testCase'])[0].get('id') is None:
                self.tl.__args__['testCase'] = '_'.join(case[:])
        except Exception as ex:
            print('error %s' % ex)
    
    def set_test_build(self):
        """
        设置更新testlink上面的测试设备ap和ac的版本信息
        :return:
        """
        # 获得任务的testBuild，是否是Dynamic Create
        try:
            if 'job_id' in self.tl.__args__:
                job_test_build = self.tl.getJobInfo(self.tl.__args__['job_id'])['testBuild']
                if job_test_build == 'Dynamic Create' or not job_test_build:
                    # 如果AC的测试版本不存在，新增测试版本
                    # [{'status': False, 'operation': 'createBuild', 'message': '', 'id': 12868}]
                    build_ac_id = self.tl.createBuild(self.tl.__args__['productLine'], self.tl.__args__['testPlan'],
                                                      self.tl.__args__['testBuild'],
                                                      self.tl.__args__['notes'])
                    # 如果AP的测试版本不存在，新增AP的测试版本
                    # AP版本创建成功，服务器返回 [{'build_id':xxxx}, ...]
                    build_ap_id = self.tl.createApBuild(self.tl.__args__['job_id'], self.tl.__args__['productLine'],
                                                        self.tl.__args__['testPlan'],
                                                        self.tl.__args__['build_ap'],
                                                        self.tl.__args__['creation_ts'],
                                                        self.tl.__args__['release_date'],
                                                        self.tl.__args__['ap_notes']
                                                        )
                    if isinstance(build_ac_id, list) and isinstance(build_ap_id, list):
                        if 'id' in build_ac_id[0] and 'build_id' in build_ap_id[0]:
                            self.tl.updateJobBuild(self.tl.__args__['job_id'], build_ac_id[0].get('id', None))
                            self.tl.updateApBuild(self.tl.__args__['job_id'], build_ap_id[0].get('build_id', None),
                                                  self.tl.__args__['build_ap'],
                                                  self.tl.__args__['creation_ts'])
                            print('主测设备版本信息更新到Testlink服务器成功')
                        elif 'id' in build_ac_id[0] and 'build_id' not in build_ap_id[0]:
                            self.tl.updateJobBuild(self.tl.__args__['job_id'], build_ac_id[0].get('id', None))
                            print('在testlink服务器上面创建AP版本失败\n' +
                                  'AP版本在数据库里面ID为 {0}'.format(str(build_ap_id))
                                  )
                        elif 'id' not in build_ac_id[0] and 'build_id' in build_ap_id[0]:
                            self.tl.updateApBuild(self.tl.__args__self.tl.__args__['job_id'],
                                                  build_ap_id[0].get('build_id', None),
                                                  self.tl.__args__['build_ap'],
                                                  self.tl.__args__['creation_ts'])
                            print('在testlink服务器上面创建AC版本失败\n' +
                                  'AC版本在数据库里面ID为 {0}'.format(str(build_ap_id))
                                  )
                        else:
                            print('在testlink服务器上面创建AP和AC版本失败\n' +
                                  'AP和AC版本在数据库里面ID分别为 {0}'.format(str(build_ap_id), str(build_ap_id))
                                  )
                # 如果当前测试版本不在测试计划所关联的测试版本中，则在服务器上面创建该版本
                if self.tl.isBuildLinkedToTestplan(self.tl.__args__['productLine'], self.tl.__args__['testPlan'],
                                                   self.tl.__args__['testBuild']) != 0:
                    self.tl.createBuild(self.tl.__args__['productLine'], self.tl.__args__['testPlan'],
                                        self.tl.__args__['testBuild'], self.tl.__args__['notes'])
        except Exception as e:
            print('Set Test Build Error {}'.format(e))
    
    def update_testcase_result(self, result, notes):
        """
         在testlink服务器上更新测试结果，pass/fail/invalid更新测试结果
        :param notes: 对于执行Fail的测试用例上传对应错误的step
        :param result: 取值范围 p|f|b|w|x|s|c （对应pass、fail、block、warn、N/A、skip、accept）
        :return:None
        """
        self.tl.__args__['result'] = result
        self.tl.__args__['notes'] = notes
        self.tl.__args__['overwrite'] = self.tl_overwrite_flag
        if self.tl != '':
            try:
                if 'job_id' in self.tl.__args__:
                    # 报告测试结果
                    report_result = self.tl.reportTestResultByKeyWireless(**self.tl.__args__)
                    print('report res {report}'.format(report=report_result))
                    print(
                        'dtestlink arg {arg}'.format(arg=json.dumps(self.tl.__args__, ensure_ascii=False, indent=4)))
                    # 实时反馈脚本的执行进度到testlink
                    self.tl.updateJobInfo(self.tl.__args__['job_id'], 1, self.tl.__args__['testCase'])
                    self.tl.__args__['notes'] = ''
                    self.tl.__args__['ap_notes'] = ''
            # 捕获跟xmlrpc Server交互的时候服务器返回的XML解析错误异常
            except (ExpatError, Exception) as e:
                print('Update Testcase Result Error {}'.format(e))
    
    def update_waffirm_args(self, ac_version, ac_all_version, ap_version, ap_compile_time, ap_all_version,
                            run_time_date,
                            test_suite='waffirm', **kwargs):
        """"
        :param self:  连接testlink xmlrpc sever的句柄指针
        :param ac_version: ac1的版本信息 7.0.1.2（R001.0002）
        :param ac_all_version: ac的show version全部信息
        :param ap_version: ap1的版本信息 2.2.3.2
        :param ap_compile_time: ap的版本编译时间 2017-6-18 12:00:00（实际传入为cat /proc/version 全部信息，
                后面testlinkapi.py中createApBuild函数进行格式化）
        :param ap_all_version：ap的get system detail全部信息
        :param run_time_date: 脚本执行时间，默认为waffirm的加载时间 2017-12-12 12:00:00
        :param test_suite: 测试用例套的名称， 默认waffirm
        :param kwargs: 默认后面用于扩展参数
        :return: None
        """
        # 日后扩展预留
        if kwargs:
            pass
        if self.tl:
            try:
                if ac_version and ac_all_version and \
                        ap_version and ap_compile_time and ap_all_version \
                        and self.tl.__args__['testBuild'] == 'Dynamic Create':
                    # 更新testBuild,notes 交换机ac1的版本以及编译时间
                    self.tl.__args__['testBuild'] = str(ac_version)
                    self.tl.__args__['notes'] = str(ac_all_version)
                    # 更新build_ap,release_date,creation_ts ap1的版本，ap1的编译时间,脚本开始运行时间
                    self.tl.__args__['build_ap'] = str(ap_version)
                    self.tl.__args__['release_date'] = str(ap_compile_time)
                    self.tl.__args__['ap_notes'] = str(ap_all_version)
                    self.tl.__args__['creation_ts'] = run_time_date
                    # 更新testSuite
                    self.tl.__args__['testSuite'] = test_suite
            except (ValueError, Exception) as e:
                print('Update Waffirm Args  is Error {}'.format(e))


@singleton
class DautoTestlinkOperate(object):
    """
    Dauto平台跟testlink服务器交换机类
    """
    
    def __init__(self):
        self.tl = DcnTestlinkHelper().tl  # 连接到testlink服务器，并且获取到操作句柄
    
    def tl_on_close_window(self):
        """
        Dauto平台关闭的时候，将testlink服务器的notes状态标记为end
        :return:
        """
        try:
            if 'job_id' in self.tl.__args__:
                self.tl.__args__['notes'] = 'end'
        except Exception as e:
            print('Testlink On Close Window Error {}'.format(e))
    
    def tl_pause_test_manual(self):
        """
        testlink感知dauto平台暂停
        :return:
        """
        try:
            if 'job_id' in self.tl.__args__:
                self.tl.updateJobInfo(self.tl.__args__['job_id'], 0)
        except Exception as e:
            print('Testlink Pasue Test Manual Error {}'.format(e))
    
    def tl_ahead_test(self):
        """
        testlink平台感知dauto平台继续执行
        :return:
        """
        try:
            if 'job_id' in self.tl.__args__:
                self.tl.updateJobInfo(self.tl.__args__['job_id'], 1)
        except Exception as e:
            print('Testlink Ahead Test Error {}'.format(e))
