#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/5/10 9:36
# @Author  : chenjw
# @Site    : 
# @File    : tapd_bug.py
# @Software: PyCharm Community Edition
# @Desc    :  do what


from urllib.parse import urlencode
from ccommon.httpSimple import HttpSimple
from tapdApi import tapd, tapd_param


class TapdBugs(tapd.Tapd):
    def __init__(self, usr, pwd):
        tapd.Tapd.__init__(self, usr, pwd)

    def createBug(self, workspace_id, title, reporter, description=None, de=None, te=None, current_owner=None,
                  status=None, resolution=None, priority=None, severity=None, module=None, version_report=None,
                  version_test=None, test_type=None, originphase=None, source=None, sourcephase=None, cc=None):
        '''
        :param workspace_id:    N   int     所属 TAPD 项目 ID
        :param title:           N   str     标题
        :param description:     O   str     详细描述
        :param reporter:        N   str     提交人
        :param de:              O   str     开发人员
        :param te:              O   str     测试人员
        :param current_owner:   O   str     当前处理人
        :param status:          O   str     状态
        :param resolution:      O   str     解决方法
        :param priority:        O   str     优先级
        :param severity:        O   str     严重程度
        :param module:          O   str     模块
        :param version_report:  O   str     发现版本
        :param version_test:    O   str     验证版本
        :param test_type:       O   str     测试类型
        :param originphase:     O   str     发现阶段
        :param source:          O   str     缺陷根源
        :param sourcephase:     O   str     引入阶段
        :param cc:              O   str     抄送人
        :return:
        '''
        url = 'https://api.tapd.cn/bugs?'
        param = tapd_param.TapdParam()
        param.setValue(workspace_id, int, 'workspace_id', True, {param.Int: {param.gt: 0}})
        param.setValue(title, str, 'title', True, {param.Str: {param.notEmpty: {}}})
        param.setValue(description, str, 'description')
        param.setValue(reporter, str, 'reporter', True, {param.Str: {param.notEmpty: {}}})
        param.setValue(de, str, 'de')
        param.setValue(te, str, 'te')
        param.setValue(current_owner, str, 'current_owner')
        param.setValue(status, str, 'status')
        param.setValue(resolution, str, 'resolution')
        param.setValue(priority, str, 'priority')
        param.setValue(severity, str, 'severity')
        param.setValue(module, str, 'module')
        param.setValue(version_report, str, 'version_report')
        param.setValue(version_test, str, 'version_test')
        param.setValue(test_type, str, 'test_type')
        param.setValue(originphase, str, 'originphase')
        param.setValue(source, str, 'source')
        param.setValue(sourcephase, str, 'sourcephase')
        param.setValue(cc, str, 'cc')
        self.wait()
        _json = HttpSimple(url).addData(param.data).addMethod(HttpSimple.method_post).addAuth(
            self.retAuth()).run().retJson()
        self.checkApiStatus(_json)
        return _json.StrP('data/Bug/id')

    def listBug(self, workspace_id, id=None, reporter=None, title=None, de=None, te=None, current_owner=None,
                status=None, resolution=None, priority=None, severity=None, module=None, version_report=None,
                version_test=None, test_type=None, originphase=None, source=None, sourcephase=None, iteration_id=None,
                closed=None, resolved=None, created=None, modified=None, page=1, limit=30, fields=None):
        '''
        :param workspace_id:    N   int     所属 TAPD 项目 ID
        :param id:              O   int     Bug ID id=1,2,3 支持一次性读取最多 50 个 id 的数据
        :param reporter:        O   str     提交人
        :param title:           O   str     标题 支持模糊匹配
        :param de:              O   str     开发人员 支持模糊匹配
        :param te:              O   str     测试人员 支持模糊匹配
        :param current_owner:   O   str     当前处理人 支持模糊匹配
        :param status:          O   str     状态 支持枚举查询
        :param resolution:      O   str     解决方法 支持枚举查询
        :param priority:        O   str     优先级 支持枚举查询
        :param severity:        O   str     严重程度 支持枚举查询
        :param module:          O   str     模块
        :param version_report:  O   str     发现版本 支持枚举查询
        :param version_test:    O   str     验证版本
        :param test_type:       O   str     测试类型
        :param originphase:     O   str     发现阶段
        :param source:          O   str     缺陷根源
        :param sourcephase:     O   str     引入阶段
        :param iteration_id:    O   str     关联的迭代 id
        :param closed:          O   str     缺陷关闭时间 支持时间字段调用
        :param resolved:        O   str     缺陷解决时间 支持时间字段调用
        :param created:         O   str     创建时间 支持时间字段调用
        :param modified:        O   str     最后修改时间 支持时间字段调用
        :param page:            O   int     设置返回数量限制，默认为 30
        :param limit:           O   int     返回当前数量限制下第 N 页的数据，默认为1（第一页）
        :param fields:          O   str     设置获取的字段，多个字段间以','逗号隔开
        :return:
        '''
        url = 'https://api.tapd.cn/bugs?'
        param = tapd_param.TapdParam()
        param.setValue(workspace_id, int, 'workspace_id', True, {param.Int: {param.gt: 0}})
        param.setValue(id, int, 'id')
        param.setValue(reporter, str, 'reporter')
        param.setValue(title, str, 'title')
        param.setValue(de, str, 'de')
        param.setValue(te, str, 'te')
        param.setValue(current_owner, str, 'current_owner')
        param.setValue(status, str, 'status')
        param.setValue(resolution, str, 'resolution')
        param.setValue(priority, str, 'priority')
        param.setValue(severity, str, 'severity')
        param.setValue(module, str, 'module')
        param.setValue(version_report, str, 'version_report')
        param.setValue(version_test, str, 'version_test')
        param.setValue(test_type, str, 'test_type')
        param.setValue(originphase, str, 'originphase')
        param.setValue(source, str, 'source')
        param.setValue(sourcephase, str, 'sourcephase')
        param.setValue(iteration_id, str, 'iteration_id')
        param.setValue(closed, str, 'closed')
        param.setValue(resolved, str, 'resolved')
        param.setValue(created, str, 'created')
        param.setValue(modified, str, 'modified')
        param.setValue(limit, int, 'limit', False, {param.Int: {param.gt: 0}})
        param.setValue(page, int, 'page', False, {param.Int: {param.gt: 0, param.lte: 30}})
        param.setValue(fields, str, 'fields')
        self.wait()
        url = '%s%s' % (url, urlencode(param.data))

        _json = HttpSimple(url).addMethod(HttpSimple.method_get).addAuth(self.retAuth()).run().retJson()
        self.checkApiStatus(_json)
        if _json.ExistP('data/Bug/id'):
            return _json.JsonP('data/Bug').Dict
        elif _json.ExistP('data/0/Bug/id'):
            return [ain_json.Dict for ain_json in _json.AryJson('data')]
        else:
            return None

    def updateBug(self, workspace_id, id, current_user, title=None, description=None, reporter=None, de=None, te=None,
                  status=None, resolution=None, priority=None, severity=None, module=None, version_report=None,
                  version_test=None, test_type=None, originphase=None, source=None, sourcephase=None):
        '''
        :param workspace_id:    N   int     所属 TAPD 项目 ID
        :param id:Bug ID:       N   int     Bug ID
        :param current_user:    N   str     当前处理人
        :param title:           O   str     标题
        :param description:     O   str     详细描述
        :param reporter:        O   str     提交人
        :param de:              O   str     开发人员
        :param te:              O   str     测试人员
        :param status:          O   str     状态
        :param resolution:      O   str     解决方法
        :param priority:        O   str     优先级
        :param severity:        O   str     严重程度
        :param module:          O   str     模块
        :param version_report:  O   str     发现版本
        :param version_test:    O   str     验证版本
        :param test_type:       O   str     测试类型
        :param originphase:     O   str     发现阶段
        :param source:          O   str     缺陷根源
        :param sourcephase:     O   str     引入阶段
        :return:
        '''
        url = 'https://api.tapd.cn/bugs'
        param = tapd_param.TapdParam()
        param.setValue(workspace_id, int, 'workspace_id', True, {param.Int: {param.gt: 0}})
        param.setValue(id, int, 'id', True, {param.Int: {param.gt: 0}})
        param.setValue(current_user, str, 'current_user', True, {param.Str: {param.notEmpty: {}}})
        param.setValue(title, str, 'title')
        param.setValue(description, str, 'description')
        param.setValue(reporter, str, 'reporter')
        param.setValue(de, str, 'de')
        param.setValue(te, str, 'te')
        param.setValue(status, str, 'status')
        param.setValue(resolution, str, 'resolution')
        param.setValue(priority, str, 'priority')
        param.setValue(severity, str, 'severity')
        param.setValue(module, str, 'module')
        param.setValue(version_report, str, 'version_report')
        param.setValue(version_test, str, 'version_test')
        param.setValue(test_type, str, 'test_type')
        param.setValue(originphase, str, 'originphase')
        param.setValue(source, str, 'source')
        param.setValue(sourcephase, str, 'sourcephase')
        self.wait()
        _json = HttpSimple(url).addData(param.data).addMethod(HttpSimple.method_post).addAuth(
            self.retAuth()).run().retJson()
        self.checkApiStatus(_json)
        return _json.JsonP('ary_data/Bug')


if __name__ == '__main__':
    pass
