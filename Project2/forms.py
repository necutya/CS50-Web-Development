from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=30)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=60)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=3)])
    confirm_password = PasswordField('Confirm password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign up')


    def validate_password(self, password):
        for char in password.data:
            if(char.isupper()):
                break
        else:
            raise ValidationError("Password must have at least one uppercase letter")




class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=3)])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign in')


class NewChatForm(FlaskForm):
    name = StringField('Chat name', validators=[DataRequired(), Length(min=3)])
    submit = SubmitField('Create')


class ConnectToChatForm(FlaskForm):
    submit = SubmitField('Connect')

