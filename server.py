from flask import Flask, render_template, redirect, request
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from forms import RegisterForm, LoginForm, ProfileForm
from db_related.data import db_session
from db_related.data.users import User


PROJECT_TYPES = ['Home', 'Most-liked', 'Recent']

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)

app.config['SECRET_KEY'] = 'qwerty_secret_12345'


@app.route("/")
def index():

    template_params = {
        "template_name_or_list": 'index.html',
        "title": 'UltimateUnity',
        "home": ...,
        "most-liked": ...,
        "recent": ...,
        "project_types": PROJECT_TYPES
    }
    return render_template(**template_params)


@app.route("/register", methods=["GET", "POST"])
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

        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template(message="Такой пользователь уже есть.", **template_params)

        user = User(name=form.name.data,
                    email=form.email.data)

        user.set_password(form.password.data)

        db_sess.add(user)
        db_sess.commit()

        with open('static/img/profile.png', 'wb') as curr_f:
            curr_f.write(user.avatar)

        return redirect("/login")

    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
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

            return redirect("/")

        return render_template(message="Неправильный логин или пароль.", **template_params)

    return render_template(**template_params)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/profile", methods=["GET", "POST"])
@login_required
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
        avatar_data = form.img.data.read()

        with open('static/img/profile.png', 'wb') as f:
            f.write(avatar_data)

        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == current_user.email).first()
        user.avatar = avatar_data
        db_sess.merge(current_user)
        db_sess.commit()

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
