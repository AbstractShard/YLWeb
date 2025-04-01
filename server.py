import datetime
import json
import os
from flask import Flask, url_for, request, render_template, redirect
from flask_wtf import FlaskForm
from wtforms import FileField
from wtforms import SubmitField
from wtforms.validators import DataRequired
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField
from wtforms.validators import DataRequired
from wtforms import FileField


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
is_logined = False


class LoginForm(FlaskForm):
    username = StringField('имя тут:', validators=[DataRequired()])
    password = PasswordField('пароль тут:', validators=[DataRequired()])
    email = EmailField('email:', validators=[DataRequired()])
    passport_number = PasswordField('номер паспорта:', validators=[DataRequired()])
    image = FileField('Добавить картинку', validators=[DataRequired()])
    access = SubmitField('Логин')


@app.route('/', methods=['GET'])
def main_page():
    if not is_logined:
        return redirect('/login')

    params = {

    }
    return render_template('mane_page.html', **params)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        global is_logined
        is_logined = True

        username = form.username.data
        password = form.password.data
        email = form.email.data
        passport_number = form.passport_number.data
        image = form.image.data.read()  # в байтовых данных

        # бд тут

        # конец бд

        return redirect('/')
    return render_template('login.html', title='Авторизация', form=form)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
