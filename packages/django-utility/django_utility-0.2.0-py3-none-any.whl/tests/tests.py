import datetime
import uuid

from django.test import TestCase, TransactionTestCase
from utility.logger import get_log_msg
from utility.mixins import DictMixin
from utility.exceptions import (ValidationError,
                                ObjectNotFoundError,
                                ExtLibError)
from utility.functions import (get_current_datetime, get_uuid1, get_zero_uuid,
                                str_to_uuid1, is_email_valid, are_similar,
                                contains_char_classes, isclose)


class FunctionsTest(TransactionTestCase):
    def test_get_current_datetime(self):
        dt = get_current_datetime()
        self.assertEqual(datetime.datetime, type(dt))

    def test_get_uuid1(self):
        u = get_uuid1()
        self.assertEqual(uuid.UUID, type(u))

    def test_get_zero_uuid(self):
        u1 = get_zero_uuid()
        u2 = uuid.UUID('00000000000000000000000000000000')
        self.assertEqual(uuid.UUID, type(u1))
        self.assertEqual(u1, u2)

    def test_str_to_uuid1(self):
        u_str = '7d08fc78-6001-11e8-8489-f40f2434c1ce'
        u = str_to_uuid1(u_str)
        self.assertEqual(uuid.UUID, type(u))
        self.assertEqual(u_str, str(u))

    def test_is_email_valid(self):
        mail1 = 'johndoe@example.technology'
        mail2 = 'john.doe@mail.org'
        mail3 = 'johndoeexample.mail'
        mail4 = 'johndoe@example@mail'
        mail5 = 'johndoe.example.com'

        self.assertEqual(True, is_email_valid(mail1))
        self.assertEqual(True, is_email_valid(mail2))
        self.assertEqual(False, is_email_valid(mail3))
        self.assertEqual(False, is_email_valid(mail4))
        self.assertEqual(False, is_email_valid(mail5))

    def test_are_similar(self):
        a1 = 'String'
        b1 = 'gnirtS'
        a2 = 'Username'
        b2 = 'user_name'
        a3 = 'HelloWorld'
        b3 = 'HelloJohn'
        a4 = 'Morning'
        b4 = 'Evening'
        a5 = 'Foo'
        b5 = 'Bar'

        self.assertEqual(True, isclose(0.1666666666666666, are_similar(a1, b1)))
        self.assertEqual(True, isclose(0.9411764705882353, are_similar(a2, b2)))
        self.assertEqual(True, isclose(0.631578947368421, are_similar(a3, b3)))
        self.assertEqual(True, isclose(0.5714285714285714, are_similar(a4, b4)))
        self.assertEqual(True, isclose(0.0, are_similar(a5, b5)))

    def test_contains_char_classes(self):
        s1 = 'string'
        s2 = 'String'
        s3 = 'String123'
        s4 = 'S123'
        s5 = '#3'
        s6 = 'str1'
        s7 = 'S#'
        s8 = 's#'
        s9 = 'String#1'

        self.assertEqual(True, contains_char_classes(s1, 1))
        self.assertEqual(False, contains_char_classes(s1, 2))

        self.assertEqual(True, contains_char_classes(s2, 2))
        self.assertEqual(False, contains_char_classes(s2, 3))

        self.assertEqual(True, contains_char_classes(s3, 3))
        self.assertEqual(False, contains_char_classes(s3, 4))

        self.assertEqual(True, contains_char_classes(s4, 2))
        self.assertEqual(False, contains_char_classes(s4, 3))

        self.assertEqual(True, contains_char_classes(s5, 2))
        self.assertEqual(False, contains_char_classes(s5, 3))

        self.assertEqual(True, contains_char_classes(s6, 2))
        self.assertEqual(False, contains_char_classes(s6, 3))

        self.assertEqual(True, contains_char_classes(s7, 2))
        self.assertEqual(False, contains_char_classes(s7, 3))

        self.assertEqual(True, contains_char_classes(s8, 2))
        self.assertEqual(False, contains_char_classes(s8, 3))

        self.assertEqual(True, contains_char_classes(s9, 4))
        self.assertEqual(False, contains_char_classes(s9, 5))

    def test_isclose(self):
        self.assertEqual(True, isclose(0.5, 0.499999999999))
        self.assertEqual(False, isclose(0.5, 0.4999))

class ExceptionsTest(TransactionTestCase):
    def test_validation_error(self):
        msg = 'Message'
        f = 'field'

        try:
            raise ValidationError(msg, field=f)
        except ValidationError as e:
            self.assertEqual(msg, e.msg)
            self.assertEqual("{0} ({1})".format(msg, f), str(e))

    def test_object_not_found_error(self):
        msg = 'Message'
        mc = 'modelclass'

        try:
            raise ObjectNotFoundError(msg, modelclass=mc)
        except ObjectNotFoundError as e:
            self.assertEqual(msg, e.msg)
            self.assertEqual("{0}".format(msg), str(e))

    def test_ext_lib_error(self):
        msg = 'Message'
        l = 'lib'

        try:
            raise ExtLibError(msg, lib=l)
        except ExtLibError as e:
            self.assertEqual(msg, e.msg)
            self.assertEqual("{0}".format(msg), str(e))

class LoggerTest(TransactionTestCase):
    def test_get_log_msg(self):

        class R:
            data = None
            META = None

            def __init__(self, data, META):
                self.data = data
                self.META = META

        user = None
        data = {'password':'1SecurePassword'}
        meta = {'REMOTE_ADDR':'127.0.0.1'}
        req = R(data, meta)
        msg = get_log_msg(req, user)

        self.assertEqual(True, ('METHOD: N/A' in msg))
        self.assertEqual(True, ('PATH_INFO: N/A' in msg))
        self.assertEqual(True, ('REMOTE_ADDR: 127.0.0.1' in msg))
        self.assertEqual(True, ('HTTP_USER_AGENT: N/A' in msg))
        self.assertEqual(True, ('USER_ID: N/A' in msg))
        self.assertEqual(True, ("DATA: {'password': '************'}" in msg))

        user = None
        data = {'username':'john.doe'}
        meta = {'REMOTE_ADDR':'127.0.0.1'}
        req = R(data, meta)
        msg = get_log_msg(req, user)

        self.assertEqual(True, ('METHOD: N/A' in msg))
        self.assertEqual(True, ('PATH_INFO: N/A' in msg))
        self.assertEqual(True, ('REMOTE_ADDR: 127.0.0.1' in msg))
        self.assertEqual(True, ('HTTP_USER_AGENT: N/A' in msg))
        self.assertEqual(True, ('USER_ID: N/A' in msg))
        self.assertEqual(True, ("DATA: {'username': 'john.doe'}" in msg))
        

class MixinTest(TransactionTestCase):
    def test_dict_mxin(self):
        data = 'data'
        field = 'field'
        
        class C(DictMixin):
            data = None
            field = None

            def __init__(self, data, field):
                self.data = data
                self.field = field

        c = C(data, field)
        self.assertEqual(c[data], data)
        self.assertEqual(c[field], field)

        newData = 'newData'
        newField = 'newField'
        c[data] = newData
        c[field] = newField
        self.assertEqual(c[data], newData)
        self.assertEqual(c[field], newField)