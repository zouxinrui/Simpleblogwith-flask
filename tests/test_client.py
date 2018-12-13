import re
import unittest
from flask import url_for
from app import create_app, db
from app.models import User, Role,UserRole, Post

class FlaskClientTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app('testing')
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.drop_all()
        db.create_all()
        # insert role
        role1 = Role(id=1,role_name='admin')
        role2 = Role(id=2,role_name='normal')
        db.session.add_all([role1,role2])
        db.session.commit()
        # insert an user
        user = User(username='user', email='user@test.com')
        user.set_password('123456')
        db.session.add(user)
        db.session.commit()
        userroles = UserRole(user_id=user.id, role_id = 2)
        db.session.add(userroles)
        db.session.commit()
        cls.client = cls.app.test_client(use_cookies=True)

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    def test_register(self):
        """Register Test with short password"""
        response = self.client.post(("/register"), data={
            'email': '879651072@qq.com',
            'username': 'Hyman',
            'password': '456',
            'password2': '456'})
        self.assertFalse(response.status_code == 302)

    def test_register(self):
        """Register Test with long password"""
        response = self.client.post(("/register"), data={
            'email': '879651072@qq.com',
            'username': 'Hyman',
            'password': '12345644444444445555555555555677887',
            'password2': '12345644444444445555555555555677887'})
        self.assertFalse(response.status_code == 302)

    def test_register(self):
        """Register Test with correct information"""
        response = self.client.post(("/register"), data={
            'email': '879651072@qq.com',
            'username': 'Hyman',
            'password': '123456',
            'password2': '123456'},follow_redirects=True)
        self.assertTrue(re.search(b'Welcome to join', response.data))

    def test_login_and_logout(self):
        """Login Test with correct password"""
        response = self.client.post(("/login"), data={
            'username': 'user',
            'password': '123456'})
        self.assertTrue(response.status_code == 302)
        # only login successful can logout
        response_logout = self.client.get("/logout")
        self.assertTrue(response_logout.status_code == 302)

class FlaskClientAuthorityTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app('testing')
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.drop_all()
        db.create_all()
        # insert role
        role1 = Role(id=1,role_name='admin')
        role2 = Role(id=2,role_name='normal')
        db.session.add_all([role1,role2])
        db.session.commit()
        # insert an admin
        u = User(username='admin', email='admin@test.com')
        u.set_password('123456')
        db.session.add(u)
        db.session.commit()
        userroles = UserRole(user_id=u.id, role_id = 1)
        db.session.add(userroles)
        db.session.commit()
        # insert an user
        user = User(username='user', email='user@test.com')
        user.set_password('123456')
        db.session.add(user)
        db.session.commit()
        userroles = UserRole(user_id=user.id, role_id = 2)
        db.session.add(userroles)
        db.session.commit()
        cls.client = cls.app.test_client(use_cookies=True)

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    def test_anou_authority(self):
        response = self.client.get(("/admin"))
        self.assertFalse(response.status_code == 200)

        response = self.client.get("/new_post")
        self.assertFalse(response.status_code == 200)

    def test_user_authority(self):
        """Login Test with correct password"""
        response = self.client.post(("/login"), data={
            'username': 'user',
            'password': '123456'})
        self.assertTrue(response.status_code == 302)
        # normal user access admin
        response = self.client.get(("/admin"))
        self.assertFalse(response.status_code == 200)
        # normal user new post
        response = self.client.get("/new_post")
        self.assertTrue(response.status_code == 200)
        # normal user new post
        response = self.client.post(("/new_post"), data={
            'title': 'testpost',
            'body': 'that was amazing'},follow_redirects=True)
        # admin user new post
        self.assertTrue(b'Create' in response.data)
        with self.app_context:
            response = self.client.get("/post/1")
        self.assertTrue(response.status_code == 200)
        # normal user.comment.post
        with self.app_context:
            response = self.client.post(("/post/1"),data={
                "text" : "simple code"
            },follow_redirects=True)
            self.assertTrue(b'simple code' in response.data)
        response_logout = self.client.get("/logout")
        self.assertTrue(response_logout.status_code == 302)

    def test_admin_authority(self):
        """Login Test with correct password"""
        response = self.client.post(("/login"), data={
            'username': 'admin',
            'password': '123456'})
        self.assertTrue(response.status_code == 302)
        # admin user new post
        response = self.client.get("/new_post",follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        response_logout = self.client.get("/logout")
        self.assertTrue(response_logout.status_code == 302)




