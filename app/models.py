from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db, login_manager
from hashlib import md5


class UserRole(db.Model):
    __tablename__ = 'userroles'

    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True, nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True, nullable=False)


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(30), unique=True, nullable=False)

    def __repr__(self):
        return self.role_name


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer,primary_key=True)
    about_me = db.Column(db.String(180))
    username = db.Column(db.String(64),index=True,unique=True)
    email = db.Column(db.String(100),index=True,unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post',backref='author',lazy='dynamic', cascade="all, delete-orphan"
                            )
    roles = db.relationship('Role', secondary="userroles",backref = db.backref('users', lazy='dynamic'))
    comments = db.relationship(
        'Comment',
        backref='user',
        lazy='dynamic', cascade="all, delete, delete-orphan")

    def __repr__(self):
        return 'User:{}'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)


posts_tags = db.Table('posts_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id', ondelete='CASCADE')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id')))


class Tag(db.Model):
    """Represents Proected tags."""
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

    def __repr__(self):
        return "Model Tag: `{}`".format(self.name)


class Post(db.Model):
    __tablename__ = 'post'
    __searchable__ = ['body','title']

    id = db.Column(db.Integer,primary_key=True)
    body = db.Column(db.String())
    title = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime,index=True,default=datetime.utcnow)
    user_id = db .Column(db.Integer,db.ForeignKey('user.id', ondelete='CASCADE'))
    comments = db.relationship(
        'Comment',
        backref='posts',
        lazy='dynamic', cascade="all, delete-orphan")
    tags = db.relationship(
        'Tag',
        secondary=posts_tags,
        backref=db.backref('posts', lazy='dynamic'))

    def __repr__(self):
        return 'Post:{}'.format(self.title)


class Comment(db.Model):
    """Represents Proected comments."""
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db .Column(db.Integer,db.ForeignKey('user.id', ondelete='CASCADE'))
    text = db.Column(db.Text())
    date = db.Column(db.DateTime())
    post_id = db.Column(db.Integer,db.ForeignKey('post.id', ondelete='CASCADE'))

    def __repr__(self):
        return 'Model Comment: `{}`'.format(self.id)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))