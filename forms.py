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

    submit = SubmitField("Зарегистрироваться")

    verify_code = None

    def validate_send_verify_code(self, field):
        if self.email.data and field.data:
            db_sess = db_session.create_session()
            verify_code_generated = str(random.randint(10000000000000000000000,
                                                       99999999999999999999999))

            verify_code = db_sess.query(VerifyCode).filter(VerifyCode.email == self.email.data).first()
            if not verify_code:
                verify_code = VerifyCode(
                    email=self.email.data,
                    subject="register"
                )
                verify_code.set_verify_code(verify_code_generated)
                db_sess.add(verify_code)
            else:
                verify_code.set_verify_code(verify_code_generated)
                verify_code.update('register')

            db_sess.commit()
            send_email(self.email.data, "verify_email", verify_code_generated)

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
    submit = SubmitField("Сохранить изменения")
    verify_code = None

    def __init__(self, email):
        super().__init__()
        self.email = email

    def validate_send_verify_code(self, field):
        if field.data:
            db_sess = db_session.create_session()
            verify_code_generated = str(random.randint(10000000000000000000000,
                                                       99999999999999999999999))

            verify_code = db_sess.query(VerifyCode).filter(user_email == self.email).first()
            if not verify_code:
                verify_code = VerifyCode(
                    email=self.email,
                    subject="change_password"
                )
                db_sess.add(verify_code)
                verify_code.set_verify_code(verify_code_generated)
            else:
                verify_code.set_verify_code(verify_code_generated)
                verify_code.update('change_password')

            db_sess.commit()
            send_email(self.email, "change_password", verify_code_generated)

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

    submit = SubmitField("Восстановить пароль")

    def validate_send_verify_code(self, field):
        if field.data and self.email.data:
            db_sess = db_session.create_session()
            verify_code_generated = str(random.randint(10000000000000000000000,
                                                       99999999999999999999999))

            verify_code = db_sess.query(VerifyCode).filter(VerifyCode.email == self.email.data).first()
            if not verify_code:
                verify_code = VerifyCode(
                    email=self.email.data,
                    subject="forgot_password"
                )
            else:
                verify_code.set_verify_code(verify_code_generated)
                verify_code.update('forgot_password')

            db_sess.commit()
            send_email(self.email.data, "forgot_password", verify_code_generated)

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
