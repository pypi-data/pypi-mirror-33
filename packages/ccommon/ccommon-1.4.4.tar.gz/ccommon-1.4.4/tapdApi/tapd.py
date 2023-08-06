#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/5/10 9:35
# @Author  : chenjw
# @Site    : 
# @File    : tapd.py
# @Software: PyCharm Community Edition
# @Desc    :  do what

from urllib.parse import urlencode
from requests import auth
import time
import threading
from tapdApi import tapd_param
from ccommon.httpSimple import HttpSimple


class Tapd:
    def __init__(self, usr, pwd,delay=1000):
        self.usr = usr
        self.pwd = pwd
        self.delay = delay
        self.lastRequestTime = 0
        self.lock = threading.Lock()

    def retAuth(self):
        return auth.HTTPBasicAuth(self.usr, self.pwd)

    def checkApiStatus(self,_json):
        if _json.Int('status') != 1:
            raise Exception('[Tapd] checkApiStatus eager %s but indeed %s' % (1,_json.Int('status')))

    # 时间戳 毫秒
    def now(self):
        return int(round(time.time()*1000))

    # 等待
    def wait(self):
        self.lock.acquire()
        try:
            if self.lastRequestTime == 0:
                self.lastRequestTime = self.now()
            else:
                sub_time = self.now() - self.lastRequestTime
                if sub_time < self.delay:
                    time.sleep(float(self.delay-sub_time) / float(1000))
                self.lastRequestTime = self.now()
        except:
            pass
        finally:
            self.lock.release()

    # 获取所有的项目
    def loadAllWorkspace(self,company_id):
        '''
        :param company_id:    N   int     公司 id
        :return:    list
            {
                "Workspace": {
                    "id": "20003271",
                    "name": "the_preoject_name",
                    "pretty_name": "20003271",
                    "status": "normal",
                    "secrecy": "0",
                    "created": "2015-05-08 16:20:01",
                    "creator_id": "2000005851",
                    "member_count": 14,
                    "creator": "username (mail@host.name)"
                }
            }
        '''
        url = 'https://api.tapd.cn/workspaces/projects?'
        param = tapd_param.TapdParam()
        param.setValue(company_id, int, 'company_id', True, {param.Int: {param.gt: 0}})
        self.wait()
        url = '%s%s' % (url, urlencode(param.data))
        _json = HttpSimple(url).addMethod(HttpSimple.method_get).addAuth(
            self.retAuth()).run().retJson()
        self.checkApiStatus(_json)
        return [ain_json.Dict for ain_json in _json.AryJson('data')]

    def loadWorkspaceUsers(self,workspace_id,fields=None):
        '''
        :param workspace_id:    N   int     项目 id
        :param fields:          O   str     需要查的字段值     user,role_id,email
        :return:    list
            {
                "UserWorkspace": {
                    "user": "wiki",
                    "role_id": [
                        "1000000000000000002"
                    ]
                }
            }
        '''
        url = 'https://api.tapd.cn/workspaces/users?'
        param = tapd_param.TapdParam()
        param.setValue(workspace_id, int, 'workspace_id', True, {param.Int: {param.gt: 0}})
        param.setValue(fields, str, 'fields')
        self.wait()
        url = '%s%s' % (url, urlencode(param.data))
        _json = HttpSimple(url).addMethod(HttpSimple.method_get).addAuth(
            self.retAuth()).run().retJson()
        self.checkApiStatus(_json)
        return [ain_json.Dict for ain_json in _json.AryJson('data')]

if __name__ == '__main__':
    pass