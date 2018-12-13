from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_principal import Principal, Permission, RoleNeed, identity_loaded,UserNeed
from config import config
from flask_login import current_user

import flask_whooshalchemyplus

from flask_admin import Admin

db = SQLAlchemy()
principals = Principal()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'main.login'
admin_permission = Permission(RoleNeed('admin'))
user_permission = Permission(UserNeed('id'))


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    Principal(app)
    db.init_app(app)
    db.app = app
    with app.app_context():
        db.create_all()
    login_manager.init_app(app)
    from .models import User, Post, UserRole, Comment, Tag, posts_tags, Role
    from .modelview import MyAdminIndexView, MyViewAll, MyView, MyViewpost
    flask_whooshalchemyplus.init_app(app)
    admin = Admin(app, template_mode='bootstrap3',
                  index_view=MyAdminIndexView())
    admin.add_view(MyView(User, db.session))
    admin.add_view(MyViewpost(Post, db.session))
    admin.add_view(MyViewAll(Comment, db.session))
    admin.add_view(MyViewAll(Tag, db.session))

    @app.errorhandler(404)
    def page_not_fond(error):
        return render_template('base/404.html'), 404

    # Add identity to current user
    @identity_loaded.connect_via(app)
    def on_identity_loaded(sender, identity):
        # Set the identity user object
        identity.user = current_user

        # Add the UserNeed to the identity
        if hasattr(current_user, 'id'):
            identity.provides.add(UserNeed(current_user.id))

        # Assuming the User model has a list of roles, update the
        # identity with the roles that the user provides
        if hasattr(current_user, 'roles'):
            for role in current_user.roles:
                identity.provides.add(RoleNeed(role.role_name))

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .momentjs import momentjs
    app.jinja_env.globals['momentjs'] = momentjs



    return app





