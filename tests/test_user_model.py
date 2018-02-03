import unittest
from app.models import User


class UserModelTestCase(unittest.TestCase):
    def test_password_setter(self):
        u = User(password='cat')
        # 这里写的是单元测试的预期结果
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password='cat')
        # 当直接调用的时候应该会提示相关错误
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password='cat')
        # 当输入不同密码时，应该会返回False
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    # 当测试相同密码时，返回的password_hash值应该不相同
    def test_password_salts_are_random(self):
        u = User(password='cat')
        u2 = User(password='cat')
        self.assertTrue(u.password_hash != u2.password_hash)