from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, TextAreaField, FloatField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NumberRange, EqualTo, ValidationError
from models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    is_seller = BooleanField('Register as a Seller')
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already in use. Please choose a different one.')

class ProjectForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])
    language = SelectField('Language', choices=[
        ('python', 'Python'), ('javascript', 'JavaScript'), ('java', 'Java'),
        ('cpp', 'C++'), ('csharp', 'C#'), ('php', 'PHP'), ('other', 'Other')
    ], validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('web', 'Web Development'), ('mobile', 'Mobile Development'), ('ml', 'Machine Learning'),
        ('ai', 'AI'), ('data', 'Data Science'), ('game', 'Game Development'),
        ('api', 'API/Backend'), ('other', 'Other')
    ], validators=[DataRequired()])
    tags = StringField('Tags (comma-separated)')
    file = FileField('Project File (.zip, .rar)', validators=[
        FileRequired(),
        FileAllowed(['zip', 'rar'], 'Only .zip and .rar files are allowed!')
    ])
    submit = SubmitField('Upload Project')

class SearchForm(FlaskForm):
    query = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')

class ReviewForm(FlaskForm):
    rating = SelectField('Rating', choices=[
        ('5', '5 - Excellent'), ('4', '4 - Very Good'), ('3', '3 - Good'),
        ('2', '2 - Fair'), ('1', '1 - Poor')
    ], validators=[DataRequired()])
    comment = TextAreaField('Comment')
    submit = SubmitField('Submit Review')
