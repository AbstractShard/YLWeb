from flask import Flask, render_template, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
authorized = False


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


@app.route('/', methods=['GET'])
def main_page():
    if not authorized:
        return redirect('/login')

    return render_template('main_page.html', **{})

@app.route("/register", methods=["GET", "POST"])
def register():
    global authorized
    if authorized:
        return redirect("/")

    form = RegisterForm()

    if form.validate_on_submit():
        import sqlite3

        con = sqlite3.connect("db/user_db.sql")
        cur = con.cursor()

        cur.execute("INSERT INTO user_data(username, password, email, passport_number) VALUES(?, ?, ?, ?)",
                    (form.username.data, form.password.data, form.email.data, form.passport_number.data))

        con.commit()

        authorized = True
        return redirect('/')

    return render_template('register.html', title='Регистрация', form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    global authorized
    if authorized:
        return redirect("/")

    form = LoginForm()

    if form.validate_on_submit():
        import sqlite3

        con = sqlite3.connect("db/user_db.sql")
        cur = con.cursor()

        login_data = cur.execute("SELECT id FROM user_data "
                                 "WHERE username = ? AND password = ? AND email = ? AND passport_number = ?",
                                 (form.username.data, form.password.data, form.email.data, form.passport_number.data)
                                 ).fetchall()

        if login_data:
            authorized = True
            return redirect("/")

        return redirect("/login")

    return render_template('login.html', title='Авторизация', form=form)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
