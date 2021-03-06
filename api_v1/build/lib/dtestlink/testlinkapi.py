﻿#! /usr/bin/python
# -*- coding: UTF-8 -*-

import socket
#  Copyright 2011-2012 Olivier Renault, James Stock, TestLink-API-Python-client developers
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
# ------------------------------------------------------------------------
# *********************************************************************
# Change log:
#     - 2017.12.11 modified by yanwh
#       添加reportTestResultByKeyWireless(**arg)接口增加wireles_tp字段上传
#       添加createApBuild函数
#     - 2017.12.19 modified by yanwh
#       修改createApBuild函数，去除对时间的正则表达式处理
# *********************************************************************
import xmlrpc.client

from . import testlinkerrors
from .args import args
from .testlinkhelper import VERSION


class TestlinkAPIClient(object):
    __slots__ = ['server', 'devKey', 'stepsList', '_server_url']
    
    __VERSION__ = VERSION
    __args__ = args
    
    def __init__(self, server_url, devKey):
        self.server = xmlrpc.client.Server(server_url)
        self.devKey = devKey
        socket.setdefaulttimeout(10)
        self.stepsList = []
        self._server_url = server_url
    
    def _callServer(self, methodAPI, argsAPI=None):
        """ call server method METHODAPI with error handling and returns the 
        responds """
        
        response = None
        try:
            if argsAPI is None:
                response = getattr(self.server.tl, methodAPI)()
            else:
                response = getattr(self.server.tl, methodAPI)(argsAPI)
        except (IOError, xmlrpc.client.ProtocolError) as msg:
            new_msg = 'problems connecting the TestLink Server %s\n%s' % \
                      (self._server_url, msg)
            raise testlinkerrors.TLConnectionError(new_msg)
        except xmlrpc.client.Fault as msg:
            new_msg = 'problems calling the API method %s\n%s' % \
                      (methodAPI, msg)
            raise testlinkerrors.TLAPIError(new_msg)
        return response
    
    #  BUILT-IN API CALLS
    
    def about(self):
        """ about :
        Gives basic information about the API    
        """
        return self._callServer('about')
    
    def doesUserExist(self, user):
        """ doesUserExist :
        Checks if a user name exists 
        """
        argsAPI = {
            'devKey': self.devKey,
            'user': str(user)
        }
        return self._callServer('doesUserExist', argsAPI)
    
    def isProductLineExist(self, productlinename):
        productlinename = productlinename
        argsAPI = {'devKey': self.devKey, 'testprojectname': productlinename}
        temp = self._callServer('getTestProjectByName', argsAPI)
        if type(temp) == dict:  # getTestProjectByName will return dict if success，or a list if fail
            if 'name' in temp:
                return 0
        else:
            return -1
    
    def isTestplanExist(self, productlinename, testplanname):
        argsAPI = {
            'devKey': self.devKey,
            'testprojectname': productlinename,
            'testplanname': testplanname
        }
        temp = self._callServer('getTestPlanByName', argsAPI)
        if type(temp) == list:
            if 'is_open' in temp[0]:
                if temp['is_open'] == '1' and plan['active'] == '1':
                    return 0
        return -1
    
    def isBuildLinkedToTestplan(self, productlinename, testplanname, buildname):
        testplanid = self.getTestPlanByName(productlinename, testplanname)[0].get('id')
        argsAPI = {
            'devKey': self.devKey,
            'testplanid': str(testplanid)
        }
        builds = self._callServer('getBuildsForTestPlan', argsAPI)
        result = -1
        buildname = buildname
        if type(builds) == list:
            for i in range(len(builds)):
                build = builds[i].get('name')
                if build == buildname:
                    result = 0
            return result
    
    def isDeviceLinkedToTestplan(self, productlinename, testplanname, devicename):
        devices = self.getTestPlanDevicesByName(productlinename, testplanname)
        result = -1
        devicename = devicename
        if type(devices) == list:
            for i in range(len(devices)):
                device = devices[i].get('name')
                if device == devicename:
                    result = 0
            return result
    
    def createBuild(self, productlinename, testplanname, buildname, buildnotes=''):
        testplanid = self.getTestPlanByName(productlinename, testplanname)[0].get('id')
        argsAPI = {
            'devKey': self.devKey,
            'testplanid': testplanid,
            'buildname': buildname,
            'buildnotes': buildnotes
        }
        return self._callServer('createBuild', argsAPI)
    
    def createApBuild(self, job_id, productlinename, testplanname, build_ap, creation_ts, release_date,
                      build_ap_notes=''):
        testplan_id = self.getTestPlanByName(productlinename, testplanname)[0].get('id')
        # 处理release_date进行格式化处理
        if release_date:
            try:
                from enum import Enum
                month_list = Enum('month', ('Jan', 'Feb', 'Mar', 'Apr', 'May',
                                            'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'))
                # 传递过来的信息中通过正则表达式获取有效时间数据'Mon Oct 23 17:53:53 CST 2017'
                # 然后将获取的有效数据通过split转换成list，最后list下标取得对应的year month day time
                # this is hard code , it is bad
                # import re
                # reg = re.compile(r'#\d+\s+(.*)')
                # release_date = reg.search(release_date).group(1).split()
                release_date = str(release_date).split()
                year, time, day, month = release_date[-1], release_date[-3], release_date[-4], release_date[-5]
                # 列表解析，例如将获取到的Oct转换成数字10
                month = [member.value for name, member in list(month_list.__members__.items()) if name == month][0]
            except ImportError:
                release_date = str(release_date).split()
                year, time, day, month = release_date[-1], release_date[-3], release_date[-4], release_date[-5]
                month_dic = {
                    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9,
                    'Oct': 10, 'Nov': 11, 'Dec': 12
                }
                month = [value for name, value in list(month_dic.items()) if name == month][0]
            import datetime
            # 格式化时间
            release_date = datetime.datetime(int(year), int(month),
                                             int(day), int(time[:2]),
                                             int(time[3:5]), int(time[6:8])).strftime('%Y-%m-%d %H:%M:%S')
            del datetime
        argsAPI = {
            'devKey': self.devKey,
            'job_id': job_id,
            'testplan_id': testplan_id,
            'build_ap': build_ap,
            'notes': build_ap_notes,
            'release_date': release_date,
            'creation_ts': creation_ts,
        }
        return self._callServer('createApBuild', argsAPI)
    
    def updateApBuild(self, job_id, build_ap_id, build_ap, creation_ts):
        argsAPI = {
            'devKey': self.devKey,
            'job_id': job_id,
            'build_id': build_ap_id,
            'build_ap': build_ap,
            'creation_ts': creation_ts,
            'notes': ''
            # 'release_date': release_date
        }
        return self._callServer('updateApBuild', argsAPI)
    
    def sayHello(self):
        argsAPI = {}
        return self._callServer('sayHello', argsAPI)
    
    def reportTestResult(self, productlinename, testsuitename, testcasename, testplanname, buildname, devicetype,
                         result, user, overwrite=0, notes=''):
        testcase = self.getTestCaseByName(productlinename, testsuitename, testcasename)
        testcaseid = testcase[0].get('id')
        
        testplanid = self.getTestPlanByName(productlinename, testplanname)[0].get('id')
        argsAPI = {
            'devKey': self.devKey,
            'testcaseid': testcaseid,
            'testplanid': testplanid,
            'status': result,
            'buildname': buildname,
            'notes': notes,
            'platformname': devicetype,
            'user': user,
            'overwrite': overwrite
        }
        return self._callServer('reportTCResult', argsAPI)
    
    def reportTestResultByKey(self, **kwargs):
        for args in ["productLine", "testSuite", "testCase", "testPlan", "testDevice", "testBuild", "result", "user"]:
            if args not in kwargs:
                return "Your provided parameters are not completed,please check what is missing!!!"
        if kwargs['result'] not in ['p', 'f', 'b', 'w', 'x', 's',
                                    'c']:  # p-pass f-fail b-block w-warn x-NA s-skip c-accept
            return "Your Test result is not in 'p'-pass 'f'-fail 'b'-block 'w'-warn 'x'-NA 's'-skip 'c'-accept"
        
        productLine = kwargs['productLine']
        testSuite = kwargs['testSuite']
        testCase = kwargs['testCase']
        testcaseid = ''
        testBuild = kwargs['testBuild']
        testDevice = kwargs['testDevice']
        testcase = self.getTestCaseByName(productLine, testSuite, testCase)
        if type(testcase) == list:
            if 'id' in testcase[0]:
                testcaseid = testcase[0].get('id')
        else:
            return "error when get testCase"
        testplanid = self.getTestPlanByName(kwargs['productLine'], kwargs['testPlan'])[0].get('id')
        
        argsAPI = {
            'devKey': self.devKey,
            'testcaseid': testcaseid,
            'testplanid': testplanid,
            'status': kwargs['result'],
            'buildname': kwargs['testBuild'],
            'platformname': kwargs['testDevice'],
            'job_id': kwargs['job_id']
        }
        
        if 'notes' in kwargs:
            argsAPI['notes'] = kwargs['notes']
        if 'overwrite' in kwargs:
            argsAPI['overwrite'] = kwargs['overwrite']
        if 'user' in kwargs:
            argsAPI['user'] = kwargs['user']
        if 'job_id' in kwargs:
            argsAPI['job_id'] = kwargs['job_id']
        if 'stack' in kwargs:
            argsAPI['stack'] = kwargs['stack']
        return self._callServer('reportTCResult', argsAPI)
    
    def reportTestResultByKeyWireless(self, **kwargs):
        for args in ["productLine", "testSuite", "testCase", "testPlan", "testDevice", "testBuild", "result", "user",
                     'wireless_tp']:
            if args not in kwargs:
                return "Your provided parameters are not completed,please check what is missing!!!"
        if kwargs['result'] not in ['p', 'f', 'b', 'w', 'x', 's',
                                    'c']:  # p-pass f-fail b-block w-warn x-NA s-skip c-accept
            return "Your Test result is not in 'p'-pass 'f'-fail 'b'-block 'w'-warn 'x'-NA 's'-skip 'c'-accept"
        
        productLine = kwargs['productLine']
        testSuite = kwargs['testSuite']
        testCase = kwargs['testCase']
        testcaseid = ''
        testBuild = kwargs['testBuild']
        testDevice = kwargs['testDevice']
        testcase = self.getTestCaseByName(productLine, testSuite, testCase)
        if type(testcase) == list:
            if 'id' in testcase[0]:
                testcaseid = testcase[0].get('id')
        else:
            return "error when get testCase"
        testplanid = self.getTestPlanByName(kwargs['productLine'], kwargs['testPlan'])[0].get('id')
        
        argsAPI = {
            'devKey': self.devKey,
            'testcaseid': testcaseid,
            'testplanid': testplanid,
            'status': kwargs['result'],
            'buildname': kwargs['testBuild'],
            'platformname': kwargs['testDevice'],
            'wireless_tp': kwargs['wireless_tp'],
            'job_id': kwargs['job_id'],
        }
        
        if 'notes' in kwargs:
            argsAPI['notes'] = kwargs['notes']
        if 'overwrite' in kwargs:
            argsAPI['overwrite'] = kwargs['overwrite']
        if 'user' in kwargs:
            argsAPI['user'] = kwargs['user']
        if 'job_id' in kwargs:
            argsAPI['job_id'] = kwargs['job_id']
        if 'stack' in kwargs:
            argsAPI['stack'] = kwargs['stack']
        return self._callServer('reportTCResult_wireless', argsAPI)
    
    def createDailyBuildJob(self, **kwargs):
        for args in ['productLine', 'testPlan', 'testDevice', 'testBuild', 'user', 'vdi_ip']:
            if args not in kwargs:
                return [{'status': 'false', 'message': 'Your provided parameters are not completed'}]
        
        argsAPI = {
            'devKey': self.devKey,
            'productLine': kwargs['productLine'],
            'testPlan': kwargs['testPlan'],
            'testDevice': kwargs['testDevice'],
            'testBuild': kwargs['testBuild'],
            'user': kwargs['user'],
            'vdi_ip': kwargs['vdi_ip'],
            's1ip': 's1ip',
            's2ip': 's2ip',
            's1p1': 's1p1',
            's1p2': 's1p2',
            's1p3': 's1p3',
            's2p1': 's2p1',
            's2p2': 's2p2',
            's2p3': 's2p3',
            'ixia_ip': 'ixia_ip',
            'tp1': 'tp1',
            'tp2': 'tp2'
        }
        
        if 's1ip' in kwargs:
            argsAPI['s1ip'] = kwargs['s1ip']
        if 's2ip' in kwargs:
            argsAPI['s2ip'] = kwargs['s2ip']
        if 's1p1' in kwargs:
            argsAPI['s1p1'] = kwargs['s1p1']
        if 's1p2' in kwargs:
            argsAPI['s1p2'] = kwargs['s1p2']
        if 's1p3' in kwargs:
            argsAPI['s1p3'] = kwargs['s1p3']
        if 's2p1' in kwargs:
            argsAPI['s2p1'] = kwargs['s2p1']
        if 's2p2' in kwargs:
            argsAPI['s2p2'] = kwargs['s2p2']
        if 's2p3' in kwargs:
            argsAPI['s2p3'] = kwargs['s2p3']
        if 'ixia_ip' in kwargs:
            argsAPI['ixia_ip'] = kwargs['ixia_ip']
        if 'tp1' in kwargs:
            argsAPI['tp1'] = kwargs['tp1']
        if 'tp2' in kwargs:
            argsAPI['tp2'] = kwargs['tp2']
        
        return self._callServer('createJob', argsAPI)
    
    def getIssueInfo(self, productlinename, product, script, testcase, step):
        """ getIssueInfo :
        Gets issue info
        """
        productlinename = productlinename
        argsAPI = {'devKey': self.devKey, 'testprojectname': productlinename}
        temp = self._callServer('getTestProjectByName', argsAPI)
        testProjectID = temp['id']
        argsAPI = {
            'devKey': self.devKey,
            'testProjectID': testProjectID,
            'product': product,
            'script': script,
            'testcase': testcase,
            'step': step
        }
        return self._callServer('getIssueInfo', argsAPI)
    
    def reportJobResult(self, jobid, exeid):
        """ reportJobResult :
        report job result info
        """
        argsAPI = {
            'devKey': self.devKey,
            'jobid': jobid,
            'exeid': exeid
        }
        return self._callServer('reportJobResult_new', argsAPI)
    
    def getJobInfo(self, jobid):
        """ getJobInfo :
        Gets job general info
        """
        argsAPI = {
            'devKey': self.devKey,
            'jobid': str(jobid)
        }
        return self._callServer('getJobInfo', argsAPI)
    
    def getJobEnv(self, jobid):
        """ getJobEnv :
        Gets job environment info
        """
        argsAPI = {
            'devKey': self.devKey,
            'jobid': str(jobid)
        }
        return self._callServer('getJobEnv', argsAPI)
    
    def getJobCases(self, jobid):
        """ getJobCases :
        Gets test cases which job need to execute
        """
        argsAPI = {
            'devKey': self.devKey,
            'jobid': str(jobid)
        }
        return self._callServer('getJobCases', argsAPI)
    
    def updateJobInfo(self, jobid, status, testcase=''):
        """ updateJobInfo :
        Update job information
        """
        argsAPI = {
            'devKey': self.devKey,
            'jobid': str(jobid),
            'status': status,
            'case': str(testcase)
        }
        return self._callServer('updateJobInfo', argsAPI)
    
    def updateJobBuild(self, jobid, buildid):
        """ updateJobBuild :
        Update build id for a job
        """
        argsAPI = {
            'devKey': self.devKey,
            'jobid': str(jobid),
            'id': str(buildid)
        }
        return self._callServer('updateJobBuild', argsAPI)
    
    def uploadExecutionAttachment(self, filename, executionid):
        """
        Attach a file to a test execution
        attachmentfile: python file descriptor pointing to the file
        name : name of the file
        title : title of the attachment
        description : description of the attachment
        content type : mimetype of the file
        """
        import mimetypes
        import base64
        import os.path
        with open(filename) as attachmentfile:
            argsAPI = {
                'devKey': self.devKey,
                'executionid': executionid,
                # 'title':title,
                'filename': os.path.basename(attachmentfile.name),
                # 'description':description,
                'filetype': mimetypes.guess_type(attachmentfile.name)[0],
                'content': base64.encodestring(attachmentfile.read())
            }
        return self._callServer('uploadExecutionAttachment', argsAPI)
    
    def getProductLineByName(self, productlinename):
        """ getProductLineByName :
        Gets info about target product line    
        """
        productlinename = productlinename
        argsAPI = {'devKey': self.devKey, 'testprojectname': productlinename}
        return self._callServer('getTestProjectByName', argsAPI)
    
    def getTestPlanByName(self, productlinename, testplanname):
        """ getTestPlanByName :
        Gets info about target test project   
        """
        argsAPI = {
            'devKey': self.devKey,
            'testprojectname': productlinename,
            'testplanname': testplanname
        }
        return self._callServer('getTestPlanByName', argsAPI)
    
    def getTestPlanDevices(self, tplanid):
        """ getTestPlanDevices :
        Returns the list of device associated to a given test plan    
        """
        argsAPI = {
            'devKey': self.devKey,
            'testplanid': str(tplanid)
        }
        return self._callServer('getTestPlanPlatforms', argsAPI)
    
    def getTestCaseByName(self, testProjectName, testSuiteName, testCaseName):
        """ 
        Find a test case by its name
        testSuiteName and testProjectName are optionals arguments
        This function return a list of tests cases
        """
        
        testCaseName = testCaseName
        argsAPI = {'devKey': self.devKey, 'testcasename': testCaseName}
        
        if testSuiteName is not None:
            testSuiteName = testSuiteName
            argsAPI.update({'testsuitename': testSuiteName})
        
        if testProjectName is not None:
            testProjectName = testProjectName
            argsAPI.update({'testprojectname': testProjectName})
        
        ret_srv = self._callServer('getTestCaseIDByName', argsAPI)
        if type(ret_srv) == dict:
            retval = []
            for value in list(ret_srv.values()):
                retval.append(value)
            return retval
        else:
            return ret_srv
    
    def getTestPlanDevicesByName(self, productlinename, testplanname):
        """ getTestPlanDevices :
        Returns the list of device associated to a given test plan    
        """
        name = testplanname
        testplanid = self.getTestPlanByName(productlinename, name)[0].get('id')
        argsAPI = {'devKey': self.devKey, 'testplanid': str(testplanid)}
        return self._callServer('getTestPlanPlatforms', argsAPI)
