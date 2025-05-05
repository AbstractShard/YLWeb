import random

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, FileField, TextAreaField, BooleanField, IntegerField
from wtforms.validators import DataRequired
from db_related.data.verify_cods import send_email
from db_related.data import db_session
from db_related.data.verify_cods import VerifyCode


class RegisterForm(FlaskForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auto_complete_off = StringField(render_kw={"autocomplete": "off", "style": "display:none"})
        self.fake_username = StringField(render_kw={"autocomplete": "off", "style": "display:none"})

    name = StringField("* Имя пользователя", validators=[DataRequired()])
    email = EmailField("* Электронная почта", validators=[DataRequired()], render_kw={"autocomplete": "username"})

    password = PasswordField("* Пароль", validators=[DataRequired()], render_kw={"autocomplete": "new-password"})
    password_again = PasswordField("* Повторите пароль", validators=[DataRequired()], render_kw={"autocomplete": "new-password"})

    verify_code_field = StringField("* Подтверждение почты", validators=[DataRequired()], render_kw={"autocomplete": "off"})
    send_verify_code = SubmitField("Отправить код")

    submit_btn = SubmitField("Зарегистрироваться")

    verify_code = None

    def code_verified(self):
        db_sess = db_session.create_session()
        verify_code = db_sess.query(VerifyCode).filter(VerifyCode.email == self.email.data).first()
        if not verify_code:
            return False
        return verify_code.check_verify_code(self.verify_code_field.data)


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
    submit_btn = SubmitField("Сохранить изменения")
    verify_code = None

    def __init__(self, email):
        super().__init__()
        self.email = email

    def code_verified(self):
        db_sess = db_session.create_session()
        verify_code = db_sess.query(VerifyCode).filter(VerifyCode.email == self.email).first()
        if not verify_code:
            return False
        return verify_code.check_verify_code(self.verify_code_field.data)


class ForgotPasswordForm(FlaskForm):
    email = EmailField("* Электронная почта", validators=[DataRequired()])
    verify_code_field = StringField("* Код смены пароля", validators=[DataRequired()])
    new_password = PasswordField("* Новый пароль", validators=[DataRequired()])
    send_verify_code = SubmitField("Отправить код")
    question1 = BooleanField("Ты не мошенник?", validators=[DataRequired()])
    question2 = BooleanField("Ты запомнил пароль?", validators=[DataRequired()])

    submit_btn = SubmitField("Восстановить пароль")

    def code_verified(self):
        db_sess = db_session.create_session()
        verify_code = db_sess.query(VerifyCode).filter(VerifyCode.email == self.email.data).first()
        if not verify_code:
            return False
        return verify_code.check_verify_code(self.verify_code_field.data)


class EditProjectForm(FlaskForm):
    name = StringField("* Имя проекта", validators=[DataRequired()])
    description = TextAreaField("Описание")

    price = IntegerField("Цена")

    imgs = FileField("* Изображения")
    files = FileField("* ZIP-Файл с проектом")

    submit = SubmitField("Сохранить изменения")
