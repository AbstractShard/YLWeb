# TODO: class ProfileForm, func show_profile

from flask import Flask, render_template, redirect

from forms import RegisterForm, ProfileForm

from db_related.data import db_session
from db_related.data.users import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'qwerty_secret_12345'


@app.route("/")
def index():
    return render_template("index.html")


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

        user = User(name=form.name.data, email=form.email.data)
        user.set_password(form.password.data)

        db_sess.add(user)
        db_sess.commit()

        return redirect("/")

    return render_template("register.html", form=form)


@app.route("/profile", methods=["GET", "POST"])
def profile():
    form = ProfileForm()

    template_params = {
        "template_name_or_list": "profile.html",
        "title": "Профиль",
        "form": form
    }

    return render_template(**template_params)


def main():
    db_session.global_init("db_related/db/db.db")
    app.run()


if __name__ == "__main__":
    main()
