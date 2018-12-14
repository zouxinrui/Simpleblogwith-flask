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
            'password2': '456'},follow_redirects=True)
        self.assertFalse(re.search(b'Welcome to join', response.data))

    def test_register(self):
        """Register Test with long password"""
        response = self.client.post(("/register"), data={
            'email': '879651072@qq.com',
            'username': 'Hyman',
            'password': '12345644444444445555555555555677887',
            'password2': '12345644444444445555555555555677887'},follow_redirects=True)
        self.assertFalse(re.search(b'Welcome to join', response.data))

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
            'password': '123456'},follow_redirects=True)
        self.assertTrue(re.search(b'Recent', response.data))

        # only login successful can logout
        response_logout = self.client.get("/logout",follow_redirects=True)
        self.assertTrue(re.search(b'Recent', response_logout.data))


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

    def test_anou_01_home(self):
        """Operation without login"""
        response = self.client.get("/", follow_redirects=True)
        self.assertTrue(b'Recent' in response.data)

    def test_anou_02_user(self):
        # enter user info page
        response = self.client.get("/user/user/1", follow_redirects=True)
        self.assertTrue(b'about me' in response.data)

    def test_anou_03_admin(self):
        # Try to access background system directly
        response = self.client.get(("/admin"), follow_redirects=True)
        self.assertTrue(b'You have no' in response.data)

    def test_anou_04_newpost(self):
       # Try to get the new post page
        response = self.client.get("/new_post", follow_redirects=True)
        self.assertTrue(b'Login' in response.data)

    def test_anou_05_edit(self):
        # edit profile
        response = self.client.get("/edit_profile", follow_redirects=True)
        self.assertTrue(b'Login' in response.data)

    def test_anou_06_search(self):
        # search
        response = self.client.get("/search_results/testpost", follow_redirects=True)
        self.assertTrue(b'testpost' in response.data)

    def test_user_authority(self):
        """Operate as a normal user"""

        #login with wrong password
        response = self.client.post(("/login"), data={
            'username': 'user',
            'password': '456'}, follow_redirects=True)
        self.assertFalse(re.search(b'Recent', response.data))

        # login with correct password
        response = self.client.post(("/login"), data={
            'username': 'user',
            'password': '123456'},follow_redirects=True)
        self.assertTrue(re.search(b'Recent', response.data))

        # edit profile
        response = self.client.post(("/edit_profile"), data={
            'username': 'user',
            'about_me': 'nothing'}, follow_redirects=True)
        self.assertTrue(re.search(b'Your profile has changed', response.data))

        # edit password
        response = self.client.post(("/user/password"), data={
            'password': '123456',
            'password1': '345678',
            'passwordnew': '345678'},follow_redirects=True)
        self.assertTrue(b'Login' in response.data)

        # Login with correct password
        response = self.client.post(("/login"), data={
            'username': 'user',
            'password': '345678'},follow_redirects=True)
        self.assertTrue(b'Popular Tags' in response.data)

        # Try to access background system directly
        response = self.client.get(("/admin"), follow_redirects=True)
        self.assertTrue(b'You have no' in response.data)

        # normal user new post
        response = self.client.post(("/new_post"), data={
            'title': 'testpost',
            'body': 'that was amazing'},follow_redirects=True)
        self.client.post(("/new_post"), data={
            'title': 'testpost2',
            'body': 'that was amazing'}, follow_redirects=True)

        # admin user new post
        self.assertTrue(b'Create' in response.data)
        with self.app_context:
            response = self.client.get("/post/1", follow_redirects=True)
            self.assertTrue(b'testpost' in response.data)

        # normal user.comment.post
        with self.app_context:
            response = self.client.post(("/post/1"),data={
                "text" : "simple code"
            },follow_redirects=True)
            self.assertTrue(b'simple code' in response.data)

        # edit post
        response = self.client.post("/edit/1",data={
            'title': 'testpost',
            'body': 'simple test'}, follow_redirects=True)
        self.assertTrue(b'simple test' in response.data)

        #delete one of the post
        response = self.client.get("/delete_post/2",follow_redirects=True)
        self.assertTrue(b'Delete succss' in response.data)

       # After logout, cannot access this page
        self.client.get("/logout")
        response = self.client.get("/edit/1",follow_redirects=True)
        self.assertTrue(b'You have no' in response.data)

       # Try to delete without authority
        response = self.client.get("/delete_post/1",follow_redirects=True)
        self.assertTrue(b'You have no' in response.data)

    def test_admin_authority(self):
        """operate as an admin"""
        response = self.client.post(("/login"), data={
            'username': 'admin',
            'password': '123456'},follow_redirects=True)
        self.assertTrue(b'Recent' in response.data)

        # access background system directly
        response = self.client.get(("/admin"), follow_redirects=True)
        self.assertTrue(b'Welcome' in response.data)

        # access background system directly
        response = self.client.get(("/admin/user"), follow_redirects=True)
        self.assertTrue(b'about' in response.data)

        # admin user new post
        response_logout = self.client.get("/logout",follow_redirects=True)
        self.assertTrue(b'Recent' in response_logout.data)






