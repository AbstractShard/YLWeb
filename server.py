# TODO: class ProfileForm, func show_profile

from flask import Flask, render_template, redirect
from forms import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'qwerty_secret_12345'
authorized = False


@app.route('/', methods=['GET'])
def main_page():
    if not authorized:
        return redirect('/login/Сначала логин')

    params = {

    }

    return render_template('main_page.html', **params)


@app.route("/register", methods=["GET", "POST"])
def register():
    global authorized
    if authorized:
        return redirect("/")

    form = RegisterForm()

    if form.validate_on_submit():
        import sqlite3

        con = sqlite3.connect("db/user_db.db")
        cur = con.cursor()

        cur.execute("INSERT INTO user_data(username, password, email, passport_number) VALUES(?, ?, ?, ?)",
                    (form.username.data, form.password.data, form.email.data, form.passport_number.data))

        con.commit()

        authorized = True
        return redirect('/')

    return render_template('register.html', title='Регистрация', form=form)


@app.route("/login/<message>", methods=["GET", "POST"])
def login(message):
    global authorized
    if authorized:
        return redirect("/")

    form = LoginForm()

    if form.validate_on_submit():
        import sqlite3

        con = sqlite3.connect("db/user_db.db")
        cur = con.cursor()

        login_data = cur.execute("SELECT id FROM user_data "
                                 "WHERE username = ? AND password = ? AND email = ? AND passport_number = ?",
                                 (form.username.data, form.password.data, form.email.data, form.passport_number.data)
                                 ).fetchall()

        if login_data:
            authorized = True
            return redirect("/")

        return redirect("/login/Нет такого юзера")

    params = {
        "title": 'Авторизация',
        "form": form,
        "message": message
    }

    return render_template('login.html', **params)


@app.route("/profile", methods=["GET", "POST"])
def show_profile():
    if not authorized:
        return redirect('/login/Сначала логин')

    form = ProfileForm()
    ...

    return render_template('profile.html', title='Профиль', form=form)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
