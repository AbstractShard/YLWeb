from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    username = StringField("*Никнейм:", validators=[DataRequired()])
    password = PasswordField("*Пароль:", validators=[DataRequired()])
    email = EmailField("*Электронная почта:", validators=[DataRequired()])
    passport_number = PasswordField("*Номер паспорта:", validators=[DataRequired()])

    access = SubmitField("Регистрация")


class LoginForm(FlaskForm):
    username = StringField("*Никнейм:", validators=[DataRequired()])
    password = PasswordField("*Пароль:", validators=[DataRequired()])
    email = EmailField("*Электронная почта:", validators=[DataRequired()])
    passport_number = PasswordField("*Номер паспорта:", validators=[DataRequired()])

    access = SubmitField("Войти")


class ProfileForm(FlaskForm):
    ...
