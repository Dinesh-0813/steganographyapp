# First install flask-wtf using pip:
# pip install flask-wtf

from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, DateField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    date_of_birth = DateField('Date of Birth', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Reset Password')

class EncodeForm(FlaskForm):
    image = FileField('Select Image', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')
    ])
    message = TextAreaField('Message to Hide', validators=[DataRequired()])
    encryption_key = PasswordField('Encryption Key', validators=[
        DataRequired(),
        Length(min=8, message='Key must be at least 8 characters long')
    ])
    submit = SubmitField('Encode Message')

class DecodeForm(FlaskForm):
    image = FileField('Select Encoded Image', validators=[
        FileRequired(),
        FileAllowed(['png'], 'PNG images only!')
    ])
    encryption_key = PasswordField('Enter Encryption Key', validators=[DataRequired()])
    submit = SubmitField('Decode Message')