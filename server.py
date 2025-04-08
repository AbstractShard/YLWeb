# TODO: class ProfileForm, func show_profile

from flask import Flask, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import form

from templates.forms import ProfileForm, LoginForm, RegisterForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'qwerty_secret_12345'
authorized = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///member.db'
db = SQLAlchemy(app)


class User(db.Model):
    username = db.Column(db.String(300), primary_key=True)
    password = db.Column(db.String(300), nullable=False)
    email = db.Column(db.String(300), primary_key=True)
    passport_number = db.Column(db.Integer, nullable=False)
    image = db.Column(db.LargeBinary, nullable=True)


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
        if bool(User.query.filter_by(username=form.username.data).all()) * bool(User.query.filter_by(
                password=form.password.data).all()) == 0:
            user = User(username=form.username.data, password=form.password.data, email=form.email.data,
                        passport_number=int(form.passport_number.data))
            db.session.add(user)
            db.session.commit()
            authorized = True
            print('123')
            return redirect('/')
        else:
            # TODO почта и логин существуют
            pass

    return render_template('register.html', title='Регистрация', form=form)


@app.route("/login/<message>", methods=["GET", "POST"])
def login(message):
    global authorized
    if authorized:
        return redirect("/")

    form = LoginForm()

    if form.validate_on_submit():
        login_data = User.query.filter_by(username=form.username.data, password=form.password.data).all()

        if bool(login_data):
            print('yes')
            authorized = True
            return redirect("/")

        return redirect("/login")

    try:
        username = form.username.data()
    except:
        username = 'GUEST'

    params = {
        "title": 'Авторизация',
        "form": form,
        "message": message,
        "username": username
    }

    return render_template('login.html', **params)


@app.route("/profile", methods=["GET", "POST"])
def show_profile():
    if not authorized:
        return redirect('/login/Сначала логин')

    form = ProfileForm()
    params = {
        "title": 'Профиль',
        "form": form,
    }

    return render_template('profile.html', **params)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
