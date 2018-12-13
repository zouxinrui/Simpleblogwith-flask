from flask_admin import Admin,AdminIndexView,expose
from flask_admin.contrib.sqla import ModelView
from . import admin_permission
from flask import render_template, flash, redirect, url_for, request,current_app
from app.models import User, Role, Post, Comment, UserRole, Tag, posts_tags
from flask_login import current_user



class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return admin_permission

    def inaccessible_callback(self, name, **kwargs):
        flash("You have no authority to access this page!")
        if current_user.is_authenticated:
             current_app.logger.warning('"%s"is try to access the admin page',current_user.username)
             return redirect(url_for('main.index', next=request.url))
        else:
            current_app.logger.warning('Anonymous usr tried to access the background')
            return redirect(url_for('main.index', next=request.url))

    @expose('/')
    def index(self):
        # Get URL for the test view method
        user = User.query.count()
        posts = Post.query.count()
        tags = Tag.query.count()
        comments = Comment.query.count()
        return self.render('admin/welcom.html',
                           users=user,
                           posts=posts,
                           tags=tags,
                           comments=comments,
                           url='/admin')


class MyViewAll(ModelView):
    def after_model_delete(self, model):
        current_app.logger.info('Admin "%s" deleted the "%s"',current_user.username, model)

    def after_model_change(self, form, model, is_create):
        current_app.logger.info('Admin "%s" updated the "%s"', current_user.username, model)

from wtforms.validators import DataRequired
class MyView(MyViewAll):
    column_exclude_list = ('password_hash')
    form_excluded_columns = ('posts', 'comments')
    form_args = {
        'password_hash': {
            'label':u'Password',
            'validators': [DataRequired()]
        },
        'username':{
            'validators': [DataRequired()]
        },
        'email': {
            'validators': [DataRequired()]
        },
        'roles': {
            'validators': [DataRequired()]
        }
    }


class MyViewpost(MyViewAll):
    form_excluded_columns = ('comments')
    page_size = 6
