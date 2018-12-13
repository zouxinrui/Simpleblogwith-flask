from wtforms import StringField, BooleanField,  TextAreaField, SelectMultipleField, SelectField
from wtforms.validators import ValidationError,Email,EqualTo
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,TextAreaField, SubmitField, TextField
from wtforms.validators import DataRequired, Length

from ..models import User,Tag

class LoginForm(FlaskForm):
    #DataRequired，当你在当前表格没有输入而直接到下一个表格时会提示你输入
    username = StringField('Username',validators=[DataRequired(message='Please input username')])
    password = PasswordField('Password',validators=[DataRequired(message='Please input password')])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(),Length(min=6, max=15)])
    password2 = PasswordField(
        'Repeat password', validators=[DataRequired(), EqualTo('password'),Length(min=6, max=15)])
    submit = SubmitField('Register')
    # Cheack whether the username is repeated
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('The username has already been used!')
    # Cheack whether the email is repeated
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('The email has already been used!')

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(message='Please input username')])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=100)])
    submit = SubmitField('Submit')


class PasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(message='Please input password')])
    password1 = PasswordField('Password', validators=[DataRequired(),Length(min=6, max=15)])
    passwordnew = PasswordField(
        'Password Repetition', validators=[DataRequired(), EqualTo('password1')])
    submit = SubmitField('Submit')

class PostForm(FlaskForm):
    """Post Form."""
    title = StringField('Title', [DataRequired(), Length(max=255)])
    tag = [(t.id, t.name) for t in Tag.query.order_by('name')]
    tags = SelectMultipleField('Tags', coerce=int ,choices = tag)
    body = TextAreaField('Blog Content', [DataRequired()])

class CommentForm(FlaskForm):
    """Form vaildator for comment."""
    text = TextAreaField(u'Comment', validators=[DataRequired()])