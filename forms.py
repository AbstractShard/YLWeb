import random

from flask import redirect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, FileField, TextAreaField, BooleanField
from wtforms.validators import DataRequired
from consts import send_email, user_exists
from db_related.data import db_session
from db_related.data.users import User, TempUser


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

    submit = SubmitField("Зарегистрироваться")

    verify_code = None

    def validate_send_verify_code(self, field):
        if self.email.data and field.data:
            db_sess = db_session.create_session()
            verify_code = str(random.randint(1000000000000000000000,
                                             9999999999999999999999 ** 99))
            if user_exists(self.email.data, True):
                user = db_sess.query(TempUser).filter(TempUser.email == self.email.data).first()
                user.set_verify_code(verify_code)
            else:
                user = TempUser(email=self.email.data)
                user.set_verify_code(verify_code)
                db_sess.add(user)

            db_sess.commit()
            send_email(self.email.data, "verify_email", verify_code)

    def code_verified(self):
        db_sess = db_session.create_session()
        user = db_sess.query(TempUser).filter(TempUser.email == self.email.data).first()
        if not user:
            return False
        return user.check_verify_code(self.verify_code_field.data)


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

    def __init__(self, email):
        super().__init__()
        self.email = email

    def validate_send_verify_code(self, field):
        if field.data:
            db_sess = db_session.create_session()
            verify_code = str(random.randint(1000000000000000000,
                                             9999999999999999999 ** 99))
            user = db_sess.query(User).filter(User.email == self.email).first()
            user.set_verify_code(verify_code)
            db_sess.commit()
            send_email(user.email, "change_password", verify_code)

    def code_verified(self):
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == self.email).first()
        if not user or not user.verify_code:
            return False
        return user.check_verify_code(self.verify_code_field.data)


class ForgotPasswordForm(FlaskForm):
    email = EmailField("* Электронная почта", validators=[DataRequired()])
    verify_code_field = StringField("* Код смены пароля", validators=[DataRequired()])
    new_password = PasswordField("* Новый пароль", validators=[DataRequired()])
    send_verify_code = SubmitField("Отправить код")
    question1 = BooleanField("Ты не мошенник?", validators=[DataRequired()])
    question2 = BooleanField("Ты запомнил пароль?", validators=[DataRequired()])

    submit = SubmitField("Восстановить пароль")

    verify_code = None

    def validate_send_verify_code(self, field):
        if field.data and self.email.data:
            db_sess = db_session.create_session()
            if not user_exists(self.email.data):
                return redirect("/forgot_password2/123")

            verify_code = str(random.randint(1000000000000000000,
                                             9999999999999999999 ** 99))
            user = db_sess.query(User).filter(User.email == self.email.data).first()
            user.set_verify_code(verify_code)
            db_sess.commit()
            send_email(self.email.data, "forgot_password", verify_code)

    def code_verified(self):
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == self.email.data).first()
        if not user:
            return False
        return user.check_verify_code(self.verify_code_field.data)
