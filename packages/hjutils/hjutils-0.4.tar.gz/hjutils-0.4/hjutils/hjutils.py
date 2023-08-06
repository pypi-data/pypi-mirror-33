#coding:utf8
"""
    hjutils
    ~~~~~

    A Lightweight regular expressions  It's extensively documented
    and follows best practice patterns.

    :copyright: (c) 2017 by Jing He.
    :license: BSD, see LICENSE for more details.
    suppor:邮箱,身份证号,手机号,整数小数,日期格式,网址,ipv4地址
"""
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
        支持:国际格式，+86135xxxx...（中国内地），+00852137xxxx...（中国香港））
        支持:移动、联通、电信运营商的号码段
        :param mobile: 传入需要被验证的手机号
        :return:
        """
        regex = "(\\+\\d+)?1[3458]\\d{9}$"
        return re.match(regex,mobile)

    @classmethod
    def checkDigit(cls,digit):
        """
        regex: 验证整数和浮点数
        支持: 整数,精确到9位的浮点数
        :param digit:
        :return:
        """
        regex = "\\-?[1-9]\\d+"
        return re.match(regex, digit)

    @classmethod
    def checkBirthday(cls,birthday):
        """
        regex: 验证日期
        格式：1992-09-03，或1992.09.03
        :param birthday:
        :return:
        """
        regex = "[1-9]{4}([-./])\\d{1,2}\\1\\d{1,2}"
        return re.match(regex, birthday)

    @classmethod
    def checkURL(cls, chinese):
        """
        regex: 验证URL地址
        支持: 验证URL地址
        :param chinese:
        :return:
        """
        regex = "^[\u4E00-\u9FA5]+$"
        return re.match(regex, chinese)

    @classmethod
    def checkIpAddress(cls, ipAddress):
        """
        regex: IPv4标准地址
        支持: IPv4标准地址
        :param chinese:
        :return:
        """
        regex = "[1-9](\\d{1,2})?\\.(0|([1-9](\\d{1,2})?))\\.(0|([1-9](\\d{1,2})?))\\.(0|([1-9](\\d{1,2})?))"
        return re.match(regex, ipAddress)
