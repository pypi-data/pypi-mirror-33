#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/5/10 9:48
# @Author  : chenjw
# @Site    : 
# @File    : tapd_story.py
# @Software: PyCharm Community Edition
# @Desc    :  do what

from urllib.parse import urlencode
from ccommon.httpSimple import HttpSimple
from tapdApi import tapd, tapd_param
import datetime


class TapdStorys(tapd.Tapd):
    def __init__(self, usr, pwd, delay=1000):
        tapd.Tapd.__init__(self, usr, pwd, delay)

    def storyChange(self, workspace_id, story_id, creator=None, created=None, order=None, limit=None, page=None,
                    fields=None):
        '''
        :param workspace_id:    N       int         所属 TAPD 项目 ID
        :param story_id:        N       int         Story ID(story_id=1,2,3 支持一次性读取最多50 个 story_id 的数据)
        :param creator:         O       str         变更人
        :param created:         O       datetime    变更时间
        :param order:           O       str         按照上面的字段进行排序
        :param limit:           O       int         设置返回数量限制，默认为 30
        :param page:            O       int         返回当前数量限制下第 N 页的数据，默认为 1(第一页）
        :param fields:          O       str         设置获取的字段，多个字段间以','逗号隔开
        :return:
        '''
        url = 'https://api.tapd.cn/story_changes?'
        param = tapd_param.TapdParam()
        param.setValue(workspace_id, int, 'workspace_id', True, {param.Int: {param.gt: 0}})
        param.setValue(story_id, int, 'story_id')
        param.setValue(creator, str, 'creator')
        # param.setValue(created, datetime.datetime, 'created')
        param.setValue(order, str, 'order')
        param.setValue(limit, int, 'limit')
        param.setValue(page, int, 'page')
        param.setValue(fields, str, 'fields')
        self.wait()
        url = '%s%s' % (url, urlencode(param.data))
        if isinstance(created, dict):
            btime = None
            etime = None
            if 'btime' in created.keys():
                btime = created['btime']
            if 'etime' in created.keys():
                etime = created['etime']
            if btime is not None and etime is not None:
                url += '&created=%s~%s' % (btime, etime)
            elif btime is not None:
                url += '&created=>%s' % (btime)
            elif etime is not None:
                url += '&created=<%s' % (etime)

        _json = HttpSimple(url).addMethod(HttpSimple.method_get).addAuth(self.retAuth()).run().retJson()

        self.checkApiStatus(_json)
        return [ain_json.Dict for ain_json in _json.AryJson('data')]

    def listStory(self, workspace_id, id=None, name=None, creator=None, status=None, description=None, owner=None,
                  cc=None, size=None, priority=None, created=None, begin=None, due=None, modified=None,
                  iteration_id=None, developer=None, test_focus=None, type=None, source=None, version=None,
                  category_id=None, business_value=None, limit=None, page=None, fields=None):
        '''
        :param workspace_id:        N       int         项目 ID
        :param id:                  O       int         需求的 ID
        :param name:                O       str         需求标题
        :param creator:             O       str         创建人
        :param status:              O       str         状态
        :param description:         O       str         需求描述
        :param owner:               O       str         当前处理人
        :param cc:                  O       str         抄送人
        :param size:                O       int         规模
        :param priority:            O       str         优先级
        :param created:             O       datetime    创建时间
        :param begin:               O       datetime    预计开始时间
        :param due:                 O       datetime    预计结束时间
        :param modified:            O       datetime    最后修改时间
        :param iteration_id:        O       str         迭代 id
        :param developer:           O       str         开发者
        :param test_focus:          O       str         测试点
        :param type:                O       str         类型
        :param source:              O       str         来源
        :param version:             O       str         版本
        :param category_id:         O       str         模块
        :param business_value:      O       str         分类 id
        :param limit:               O       int         设置返回数量限制，默认为 30
        :param page:                O       int         返回当前数量限制下第 N 页的数据，默认为 1（第一页）
        :param fields:              O       str         设置获取的字段，多个字段间以','逗号隔开
        :return:
        '''
        url = 'https://api.tapd.cn/stories?'
        param = tapd_param.TapdParam()
        param.setValue(workspace_id, int, 'workspace_id', True, {param.Int: {param.gt: 0}})
        param.setValue(id, int, 'id')
        param.setValue(name, str, 'name')
        param.setValue(creator, str, 'creator')
        param.setValue(status, str, 'status')
        param.setValue(description, str, 'description')
        param.setValue(owner, str, 'owner')
        param.setValue(cc, str, 'cc')
        param.setValue(size, int, 'size')
        param.setValue(priority, str, 'priority')
        param.setValue(created, datetime.datetime, 'created')
        param.setValue(begin, datetime.datetime, 'begin')
        param.setValue(due, datetime.datetime, 'due')
        param.setValue(modified, datetime.datetime, 'modified')
        param.setValue(iteration_id, str, 'iteration_id')
        param.setValue(developer, str, 'developer')
        param.setValue(test_focus, str, 'test_focus')
        param.setValue(type, str, 'type')
        param.setValue(source, str, 'source')
        param.setValue(version, str, 'version')
        param.setValue(category_id, str, 'category_id')
        param.setValue(business_value, str, 'business_value')
        param.setValue(limit, int, 'limit')
        param.setValue(page, int, 'page')
        param.setValue(fields, str, 'fields')
        self.wait()
        url = '%s%s' % (url, urlencode(param.data))
        _json = HttpSimple(url).addMethod(HttpSimple.method_get).addAuth(self.retAuth()).run().retJson()
        self.checkApiStatus(_json)
        if _json.ExistP('data/Story/id'):
            return _json.JsonP('data/Story').Dict
        elif _json.ExistP('data/0/Story/id'):
            return [ain_json.Dict for ain_json in _json.AryJson('data')]
        else:
            return None

    def statusMap(self, workspace_id):
        '''
        :param workspace_id:        N       int         项目 ID
        :return:
        '''
        system = 'story'
        param = tapd_param.TapdParam()
        param.setValue(workspace_id, int, 'workspace_id', True, {param.Int: {param.gt: 0}})
        param.setValue(system, str, 'system')
        url = 'https://api.tapd.cn/workflows/status_map?'
        self.wait()
        url = '%s%s' % (url, urlencode(param.data))

        _json = HttpSimple(url).addMethod(HttpSimple.method_get).addAuth(self.retAuth()).run().retJson()

        self.checkApiStatus(_json)
        return _json.Json('data').Dict


if __name__ == '__main__':
    pass
