#coding:utf8
import re
class RegexUtils(object):
    @classmethod
    def checkEmail(cls,email):
        """
        regex: 表示匹配的邮件规则
        :param email: 传入需要被验证的邮件
        :return:
        """
        regex = "\\w+@\\w+\\.[a-z]+(\\.[a-z]+)?"
        return re.match(regex,email)

    @classmethod
    def checkIdCard(cls,idCard):
        """
        regex: 验证身份证号码
        :param idCard: 传入需要被验证的身份证号
        :return:
        """
        regex = "[1-9]\\d{13,16}[a-zA-Z0-9]{1}"
        return re.match(regex,idCard)


    @classmethod
    def checkMobile(cls,mobile):
        """
        regex: 验证手机号格式
        :param mobile: 传入需要被验证的手机号
        :return:
        """
        regex = "1[34578]\\d{9}"
        return re.match(regex,mobile)
