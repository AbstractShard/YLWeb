import random

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, FileField, TextAreaField, BooleanField
from wtforms.validators import DataRequired
from consts import send_email


class RegisterForm(FlaskForm):
    name = StringField("* Имя пользователя", validators=[DataRequired()])
    email = EmailField("* Электронная почта", validators=[DataRequired()])

    password = PasswordField("* Пароль", validators=[DataRequired()])
    password_again = PasswordField("* Повторите пароль", validators=[DataRequired()])

    verify_code_field = StringField("* Подтверждение почты", validators=[DataRequired()])
    send_verify_code = SubmitField("Отправить код")

    submit = SubmitField("Зарегистрироваться")

    verify_code = None

    def validate_send_verify_code(self, field):
        if self.email.data and field.data:
            self.verify_code = str(random.randint(1, 999999999999999999999999999999999 ** 99))
            with open('verify_code.txt', 'w') as f:
                f.write(self.verify_code)
            send_email(self.email.data, "verify_email", self.verify_code)

    def code_verified(self):
        with open('verify_code.txt', 'r') as f:
            return f.read() == self.verify_code_field.data


class LoginForm(FlaskForm):
    email = EmailField("* Электронная почта", validators=[DataRequired()])
    password = PasswordField("* Пароль", validators=[DataRequired()])
    remember_me = BooleanField("Запомнить меня")

    submit = SubmitField("Войти")


class ProfileForm(FlaskForm):
    name = StringField("* Имя пользователя", validators=[DataRequired()])
    about = TextAreaField("О себе")
    img = FileField("Изображение профиля")

    submit = SubmitField("Сохранить изменения")


class ChangePasswordForm(FlaskForm):
    new_password = PasswordField("* Новый пароль", validators=[DataRequired()])
    verify_code_field = StringField("* Код смены пароля", validators=[DataRequired()])
    send_verify_code = SubmitField("Отправить код")
    question1 = BooleanField("Ты не мошенник?", validators=[DataRequired()])
    question2 = BooleanField("Ты запомнил пароль?", validators=[DataRequired()])
    submit = SubmitField("Сохранить изменения")
    verify_code = None

    def validate_send_verify_code(self, field):
        if field.data:
            with open('current_user.txt', 'r') as f:
                email = f.read()
            self.verify_code = str(random.randint(1, 999999999999999999999999999999999 ** 99))
            with open('verify_code.txt', 'w') as f:
                f.write(self.verify_code)
            send_email(email, "change_password", self.verify_code)

    def code_verified(self):
        with open('verify_code.txt', 'r') as f:
            return f.read() == self.verify_code_field.data
