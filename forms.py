from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, FileField, TextAreaField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    name = StringField("* Имя пользователя", validators=[DataRequired()])
    email = EmailField("* Электронная почта", validators=[DataRequired()])

    password = PasswordField("* Пароль", validators=[DataRequired()])
    password_again = PasswordField("* Повторите пароль", validators=[DataRequired()])

    submit = SubmitField("Зарегистрироваться")


class LoginForm(FlaskForm):
    email = EmailField("* Электронная почта", validators=[DataRequired()])
    password = PasswordField("* Пароль", validators=[DataRequired()])

    submit = SubmitField("Войти")


class ProfileForm(FlaskForm):
    name = StringField("Имя пользователя")
    about = TextAreaField("О себе")
    img = FileField("Изображение профиля")

    submit = SubmitField("Изменить")

