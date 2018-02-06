import unittest
import time
from app.models import User
from app import create_app,db
from app.models import Permission,Role,AnonymousUser

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

    def test_valid_confirmation_token(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token()
        self.assertTrue(u.confirm(token))

    def test_invalid_confirmation_token(self):
        u1 = User(password='cat')
        u2 = User(password='dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_confirmation_token()
        self.assertFalse(u2.confirm(token))

    def test_expired_confirmation_token(self):
        u = User(password ='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token(1)
        time.sleep(2)
        self.assertFalse(u.confirm(token))

    def test_valid_email_change(self):
        u = User(email='test1@example.com',password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_email_change_token('susan1@example.org')
        self.assertTrue(u.change_email(token))
        self.assertTrue(u.email == 'susan1@example.org')

    def test_invalid_email_change_token(self):
        u1 = User(email = 'test2@example.com',password='cat')
        u2 = User(email = 'susan2@example.org',password='dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_email_change_token('david2@example.net')
        self.assertFalse(u2.change_email(token))
        self.assertTrue(u2.email == 'susan2@example.org')

    def test_duplicate_email_change_token(self):
        u1 = User(email = 'john3@example.com',password='cat')
        u2 = User(email = 'susan3@example.org',password='dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u2.generate_email_change_token('john3@example.com')
        self.assertFalse(u2.change_email(token))
        self.assertTrue(u2.email == 'susan3@example.org')

    def test_roles_and_permissions(self):
        Role.insert_roles()
        u = User(email='john4@example.com',password='cat')
        self.assertTrue(u.can(Permission.WRITE_ARTICLES))
        self.assertFalse(u.can(Permission.MODERATE_COMMENTS))

    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.FOLLOW))