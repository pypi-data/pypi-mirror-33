#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/4/23 10:06
# @Author  : chenjw
# @Site    : 
# @File    : smtp.py
# @Software: PyCharm Community Edition
# @Desc    :  send mail by smtp

import logging

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import smtplib
import os


class SIMPLESMTP:
    def __init__(self, fromAddress, password, smtpServer, port):
        '''
        :param fromAddress: username of email eg:123@qq.com
        :param password: password of username
        :param smtpServer:  host of mail eg:smtp.qq.com
        :param port: port of mail send
        '''
        self.fromAddress = fromAddress
        self.password = password
        self.smtpServer = smtpServer
        self.port = port


    def combineContent(self, receivers, subject, context, context_type='plain', encode='utf-8', charset='base64',
                       attachs=[]):
        '''
        :param receivers: who is going to receive the mail , AryStr
        :param subject: title of mail
        :param context: context of mail
        :param context_type: context type of mail,common to be plain,html and so on
        :param encode: common to be utf-8
        :param charset: attachs charset
        :param attachs: files arystr
        :return:
        '''
        if attachs is None or (isinstance(attachs, list) and len(attachs) == 0):
            message = MIMEText(context, context_type, encode)
            message['From'] = Header(self.fromAddress, encode)
            message['To'] = Header(",".join(receivers), encode)
            message['Subject'] = Header(subject, encode)
        else:
            message = MIMEMultipart()
            message['From'] = Header(self.fromAddress, encode)
            message['To'] = Header(",".join(receivers), encode)
            message['Subject'] = Header(subject, encode)
            message.attach(MIMEText(context, context_type, encode))
            for fileName in attachs:
                attach = MIMEText(open(fileName, 'rb').read(), charset, encode)
                attach["Content-Type"] = 'application/octet-stream'
                attach["Content-Disposition"] = '''attachment; filename="%s"''' % fileName.split(os.pathsep)[-1]
                message.attach(attach)
        return message

    def send(self, message, receivers):
        '''
        :param message:
        :param receivers:
        :return:
        '''
        try:
            smtp = smtplib.SMTP()
            smtp.connect(self.smtpServer, self.port)
            smtp.login(self.fromAddress, self.password)
            smtp.sendmail(self.fromAddress, receivers, message.as_string())
        except smtplib.SMTPException as e:
            logging.error("call [smtp.sendmail] error:%s", e)

    def sendEmail(self, receivers, subject, context, context_type='plain', encode='utf-8', charset='base64',
                  attachs=[]):
        try:
            message = self.combineContent(receivers, subject, context, context_type, encode, charset, attachs)
            smtp = smtplib.SMTP()
            smtp.connect(self.smtpServer, self.port)
            smtp.login(self.fromAddress, self.password)
            smtp.sendmail(self.fromAddress, receivers, message.as_string())
        except smtplib.SMTPException as e:
            logging.error("call [smtp.sendmail] error:%s", e)


if __name__ == '__main__':
    username = 'username'
    pwd = 'pwd'
    mailServer = 'smtp.exmail.qq.com'
    port = 25
    receivers = ['781354598@qq.com']

    simple = SIMPLESMTP(username, pwd, mailServer, port)
    simple.sendEmail(receivers, '文本标题', '内容')
    simple.sendEmail(receivers, 'html标题', '''
    hello ff
    <html><body><h1>hello</h1></body></html>
    ''', context_type='html')
    simple.sendEmail(receivers, '附件', '附件哦哦', attachs=['__init__.py'])

    pass
