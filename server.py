from flask import Flask, render_template, redirect, request
from flask_login import LoginManager, login_user, login_required, current_user, logout_user

from forms import RegisterForm, LoginForm, ProfileForm, ChangePasswordForm

from db_related.data import db_session
from db_related.data.users import User

import consts
from consts import check_buffer


PROJECT_TYPES = ['Home', 'Most-liked', 'Recent']

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)

app.config['SECRET_KEY'] = 'qwerty_secret_12345'


@app.errorhandler(404)
def not_found(error):
    return render_template("404.html", title="UltimateUnity")


@app.errorhandler(400)
def bad_request(error):
    return render_template("404.html", title="UltimateUnity")


@app.route("/")
@check_buffer
def index():
    projects = {
        "Home": ['!add_project', ..., ...],
        "Most-liked": [..., ..., ..., ...],
        "Recent": [..., ..., ..., ..., ...]
    }
    template_params = {
        "template_name_or_list": 'index.html',
        "title": 'UltimateUnity',
        "project_types": PROJECT_TYPES,
        "projects": projects
    }
    return render_template(**template_params)


@app.route("/register", methods=["GET", "POST"])
@check_buffer
def register():
    form = RegisterForm()
    template_params = {
        "template_name_or_list": "register.html",
        "title": "Регистрация",
        "form": form
    }

    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template(message="Пароли не совпадают.", **template_params)

        if not form.code_verified():
            return render_template(message=f"Код не тот.{form.verify_code}", **template_params)

        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template(message="Такой пользователь уже есть.", **template_params)

        user = User(name=form.name.data,
                    email=form.email.data)

        with open(consts.DEFAULT_PROFILE_PATH, mode="rb") as def_img:
            user.img = def_img.read()

            with open(consts.CURRENT_PROFILE_PATH, mode="wb") as curr_img:
                curr_img.write(user.img)

        user.set_password(form.password.data)

        db_sess.add(user)
        db_sess.commit()

        return redirect("/login")

    return render_template(**template_params)


@app.route("/login", methods=["GET", "POST"])
@check_buffer
def login():
    form = LoginForm()

    template_params = {
        "template_name_or_list": "login.html",
        "title": "Вход",
        "form": form
    }

    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)

            with open(consts.CURRENT_PROFILE_PATH, mode="wb") as curr_img:
                curr_img.write(current_user.img)

            with open('current_user.txt', 'w') as f:
                f.write(str(current_user.email))

            return redirect("/")

        return render_template(message="Неправильный логин или пароль.", **template_params)

    return render_template(**template_params)


@app.route("/logout")
@login_required
@check_buffer
def logout():
    logout_user()
    return redirect("/")


@app.route("/profile", methods=["GET", "POST"])
@login_required
@check_buffer
def profile():
    form = ProfileForm()

    template_params = {
        "template_name_or_list": "profile.html",
        "title": "Профиль",
        "form": form
    }

    if request.method == "GET":
        form.name.data = current_user.name
        form.about.data = current_user.about

    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.about = form.about.data

        if img_data := form.img.data.read():
            current_user.img = img_data

            with open(consts.CURRENT_PROFILE_PATH, mode="wb") as curr_img:
                curr_img.write(current_user.img)

        db_sess = db_session.create_session()
        db_sess.merge(current_user)
        db_sess.commit()

    return render_template(**template_params)


@app.route("/change_password", methods=["GET", "POST"])
@login_required
@check_buffer
def change_password():
    form = ChangePasswordForm()

    template_params = {
        "template_name_or_list": "change_password.html",
        "title": "Изменить пароль",
        "form": form
    }

    if form.validate_on_submit():
        if not form.code_verified():
            return render_template(message=f"Код не тот.{form.verify_code}", **template_params)

        current_user.set_password(form.new_password.data)

        db_sess = db_session.create_session()
        db_sess.merge(current_user)
        db_sess.commit()

        return redirect("/")

    return render_template(**template_params)


@app.route('/currency')
@check_buffer
def currency():
    balance = current_user.currency
    price = [
        {"Цена": '500₽', "Android/OIS": 250, "Windows/Linux": 255},
        {"Цена": '1000₽', "Android/OIS": 500, "Windows/Linux": 510},
        {"Цена": '2000₽', "Android/OIS": 1000, "Windows/Linux": 1100},
        {"Цена": '5000₽', "Android/OIS": 2500, "Windows/Linux": 2600},
        {"Цена": '10000₽', "Android/OIS": 5000, "Windows/Linux": 5100},
        {"Цена": '15000₽', "Android/OIS": 7500, "Windows/Linux": 7600},
        {"Цена": '20000₽', "Android/OIS": 10000, "Windows/Linux": 10200},
        {"Цена": '25000₽', "Android/OIS": 12500, "Windows/Linux": 13000},
        {"Цена": '30000₽', "Android/OIS": 15000, "Windows/Linux": 16000}
    ]
    template_params = {
        "template_name_or_list": "currency.html",
        "title": "Валюта",
        "balance": balance,
        "price": price,
        "transactions": []
    }
    return render_template(**template_params)


def main():
    db_session.global_init("db_related/db/db.db")
    app.run()


@login_manager.user_loader
def load_user(user_id: int) -> User:
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


if __name__ == "__main__":
    main()
