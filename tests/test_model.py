import unittest
import time
from datetime import datetime
from app import create_app, db
from app.models import User, Role, UserRole,Post


class ModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.drop_all()
        db.create_all()
        role1 = Role(id=1, role_name='admin')
        role2 = Role(id=2, role_name='normal')
        db.session.add_all([role1, role2])
        db.session.commit()
        u = User(username='origin', email='origin@test.com')
        u.set_password('123456')
        db.session.add(u)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        u = User(username='test',email='cat@test.com')
        u.set_password('123456')
        self.assertTrue(u.password_hash is not None)

    def test_password_verification(self):
        u = User(username='test',email='cat@test.com')
        u.set_password('smallcat')
        self.assertTrue(u.check_password('smallcat'))
        self.assertFalse(u.check_password('bigdog'))

    def test_password_salts_are_random(self):
        u = User(username='test',email='cat@test.com')
        u.set_password('smallcat')
        u2 = User(username='test2',email='dog@test.com')
        u2.set_password('smallcat')
        self.assertTrue(u.password_hash != u2.password_hash)

    def test_edit_data(self):
        """edit data"""
        user = User.query.filter_by(username='origin').first()
        user.username='aftertest2'
        db.session.add(user)
        db.session.commit()
        user = User.query.filter_by(username='aftertest2').first()
        self.assertIsNotNone(user)

    def test_06delete_data(self):
        duser = User.query.filter_by(username='origin').first()
        db.session.delete(duser)
        db.session.commit()
        user = User.query.filter_by(username='origin').first()
        self.assertIsNone(user)

    def test_cascade_reaction(self):
        usr = User(username='test2', email='test2@qq.com')
        usr.set_password('test2')
        db.session.add(usr)
        db.session.commit()
        userrole = UserRole(user_id=usr.id)
        userrole.role_id = 2
        db.session.add(userrole)
        db.session.commit()
        user = User.query.filter_by(username='test2').first()
        db.session.delete(user)
        db.session.commit()
        role = UserRole.query.filter_by(user_id=user.id).first()
        self.assertIsNone(role)

    def test_post(self):
        post = Post(title='test2')
        post.timestamp =datetime.now()
        post.body='test message'
        db.session.add(post)
        db.session.commit()
        post = Post.query.filter_by(title='test2').first()
        db.session.delete(post)
        db.session.commit()


