#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/5/10 9:35
# @Author  : chenjw
# @Site    : 
# @File    : tapd_param.py
# @Software: PyCharm Community Edition
# @Desc    :  do what


from ccommon import jsonParse
import logging
import datetime

class TapdParam:
    def __init__(self):
        self.notEmpty = 'notEmpty'
        self.lt = 'lt'
        self.lte = 'lte'
        self.gt = 'gt'
        self.gte = 'gte'
        self.Int = 'int'
        self.Str = 'str'
        self.data = {}

    def isParamValid(self, v, eager_type):
        '''
        :param v: any type
        :param eager_type: int,str,dict so os on
        :return:
        '''
        if type(v) == eager_type:
            return True
        else:
            return False

    def setValue(self, v, eager_type, key, isNeed=False, rangeOfValue=None):
        '''
        :param v: any type,value of dict
        :param eager_type: int,str,dict so os on
        :param key: key of dict
        :param data: dict to set key and value
        :return:
        '''
        # 校验参数类型
        if self.isParamValid(v, eager_type):
            # 当没有取值限制的时候直接赋值
            if rangeOfValue is None:
                self.data[key] = v
            elif self.isParamValid(rangeOfValue, dict):
                _json = jsonParse.JsonParse(rangeOfValue)
                # 当 期望类型为 str 时候
                if eager_type == str:
                    if _json.ExistP('%s/%s' % (self.Str, self.notEmpty)) and v == '':
                        logging.warning('call [setValue] key(%s)  v(%s) is notEmpty' % (key, v))
                    else:
                        self.data[key] = v
                # 当 期望类型为 int 时候
                if eager_type == int:
                    int_json = _json.Json(self.Int)
                    normal = True
                    if normal and int_json.Exist(self.lt) and v >= int_json.Int(self.lt):
                        normal = False
                        logging.warning(
                            'call [setValue] eager key(%s) value(%s) to lt(%s)' % (key, v, int_json.Int(self.lt)))
                    if normal and int_json.Exist(self.lte) and v > int_json.Int(self.lte):
                        normal = False
                        logging.warning(
                            'call [setValue] eager key(%s) value(%s) to lte(%s)' % (key, v, int_json.Int(self.lte)))
                    if normal and int_json.Exist(self.gt) and v <= int_json.Int(self.gt):
                        normal = False
                        logging.warning(
                            'call [setValue] eager key(%s) value(%s) to gt(%s)' % (key, v, int_json.Int(self.gt)))
                    if normal and int_json.Exist(self.gte) and v < int_json.Int(self.gte):
                        normal = False
                        logging.warning(
                            'call [setValue] eager key(%s) value(%s) to gte(%s)' % (key, v, int_json.Int(self.gte)))
                    if normal:
                        self.data[key] = v
                if eager_type == datetime.datetime or eager_type == datetime.date:
                    self.data[key] = v

            else:
                logging.warning('call [setValue] rangeOfValue should be dict but not (%s)' % type(rangeOfValue))

        # 当参数为空值时候，且是必传参数时候抛出异常
        elif v is None and isNeed is True:
            logging.warning('call [setValue] key(%s) is Needed but None' % key)
        else:
            logging.debug('call [setValue] key(%s) value(%s) type(%s) will be filter for the eager type is (%s)' % (
                key, v, type(v), eager_type))

if __name__ == '__main__':
    pass