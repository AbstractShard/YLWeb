import datetime
import requests

from flask import Flask, render_template, redirect, request, jsonify
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from flask_restful import Api

from db_related.data.message import Message
from forms import RegisterForm, LoginForm, ProfileForm, ChangePasswordForm, ForgotPasswordForm, EditProjectForm
from db_related.data.verify_cods import VerifyCode, send_email
from db_related.data import db_session
import random

from db_related.data import db_session, users_resources, verify_cods_resources
from db_related.data.users import User
from db_related.data.projects import Project
from dotenv import load_dotenv
import os

import consts
from consts import check_buffer, project_to_dict, check_zip


load_dotenv('static/.env')

HCAPTCHA_SITE_KEY = os.getenv('HCAPTCHA_SITE_KEY')
HCAPTCHA_SECRET_KEY = os.getenv('HCAPTCHA_SECRET_KEY')
RECAPTCHA_SITE_KEY = os.getenv('RECAPTCHA_SITE_KEY')
RECAPTCHA_SECRET_KEY = os.getenv('RECAPTCHA_SECRET_KEY')
PROJECT_TYPES = ['Continue', 'Most-liked', 'Recent']

app = Flask(__name__)
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)

app.config['SECRET_KEY'] = HCAPTCHA_SECRET_KEY

def verify_recaptcha(token, action):
    """Verify reCAPTCHA v3 token and return (success, message) tuple."""
    if not token:
        return False, "reCaptcha не пройдена."
        
    data = {
        'secret': RECAPTCHA_SECRET_KEY,
        'response': token
    }
    
    try:
        recaptcha_result = requests.post('https://www.google.com/recaptcha/api/siteverify', 
                                       data=data, 
                                       timeout=5).json()
        
        if not recaptcha_result.get('success'):
            return False, "reCaptcha не прошла."
            
        if recaptcha_result.get('action') != action:
            return False, "Неверное действие reCaptcha."
            
        if recaptcha_result.get('score', 0) < 0.5:
            return False, f"reCaptcha не прошла, {1 - recaptcha_result.get('score', 0)}% бота."
            
        return True, None
    except requests.RequestException as e:
        return False, f"Ошибка при проверке reCaptcha: {str(e)}"

def verify_hcaptcha(response):
    """Verify hCaptcha response and return (success, message) tuple."""
    if not response:
        return False, "Капча не пройдена."
        
    data = {
        'secret': HCAPTCHA_SECRET_KEY,
        'response': response
    }
    
    try:
        hcaptcha_result = requests.post('https://hcaptcha.com/siteverify', 
                                      data=data, 
                                      timeout=5).json()
        
        if not hcaptcha_result.get('success'):
            return False, "hCaptcha не прошла."
            
        return True, None
    except requests.RequestException as e:
        return False, f"Ошибка при проверке hCaptcha: {str(e)}"

@app.errorhandler(400)
def bad_request(error):
    template_params = {
        "template_name_or_list": "error.html",
        "title": "UltimateUnity",
        "error": "400",
        "error_img": "../static/img/errors/400.jpg"
    }
    return render_template(**template_params)


@app.errorhandler(401)
def unauthorized(error):
    template_params = {
        "template_name_or_list": "error.html",
        "title": "UltimateUnity",
        "error": "401",
        "error_img": "../static/img/errors/401.jpg"
    }
    return render_template(**template_params)


@app.errorhandler(403)
def forbidden(error):
    template_params = {
        "template_name_or_list": "error.html",
        "title": "UltimateUnity",
        "error": "403",
        "error_img": "../static/img/errors/403.jpg"
    }
    return render_template(**template_params)


@app.errorhandler(404)
def not_found(error):
    template_params = {
        "template_name_or_list": "error.html",
        "title": "UltimateUnity",
        "error": "404",
        "error_img": "../static/img/errors/404.jpg"
    }
    return render_template(**template_params)


@app.route("/")
@check_buffer
def index():
    projects = {
        "Continue": ['!add_project', ..., ...],
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
        "form": form,
        "HCAPTCHA_SITE_KEY": HCAPTCHA_SITE_KEY,
        "RECAPTCHA_SITE_KEY": RECAPTCHA_SITE_KEY
    }

    if form.validate_on_submit():
        # Проверка паролей
        if form.password.data != form.password_again.data:
            return render_template(message="Пароли не совпадают.", **template_params)
        
        # Проверка верификационного кода
        if not form.code_verified():
            return render_template(message=f"Код не тот.", **template_params)


        # Проверка reCaptcha
        recaptcha_success, recaptcha_message = verify_recaptcha(
            request.form.get('recaptcha-token'),
            'register'
        )
        if not recaptcha_success:
            return render_template(message=recaptcha_message, **template_params)
        
        # Проверка hCaptcha
        hcaptcha_success, hcaptcha_message = verify_hcaptcha(
            request.form.get('h-captcha-response')
        )
        if not hcaptcha_success:
            return render_template(message=hcaptcha_message, **template_params)
        

        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template(message="Такой пользователь уже есть.", **template_params)

        user = User(name=form.name.data,
                    email=form.email.data)

        user.set_default_img()
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
    form = ChangePasswordForm(current_user.email)

    template_params = {
        "template_name_or_list": "change_password.html",
        "title": "Изменить пароль",
        "form": form,
        "RECAPTCHA_SITE_KEY": RECAPTCHA_SITE_KEY
    }

    if form.validate_on_submit():
        # Проверка верификационного кода
        if not form.code_verified():
            return render_template(message=f"Код не тот.{form.verify_code}", **template_params)

        recaptcha_success, recaptcha_message = verify_recaptcha(
            request.form.get('recaptcha-token'),
            'change_password'
        )
        if not recaptcha_success:
            return render_template(message=recaptcha_message, **template_params)

        current_user.set_password(form.new_password.data)

        db_sess = db_session.create_session()
        db_sess.merge(current_user)
        db_sess.commit()

        return redirect("/")

    return render_template(**template_params)


@app.route("/forgot_password", methods=["GET", "POST"])
@check_buffer
def forgot_password():
    form = ForgotPasswordForm()

    template_params = {
        "template_name_or_list": "forgot_password.html",
        "title": "Забыл пароль",
        "form": form,
        "RECAPTCHA_SITE_KEY": RECAPTCHA_SITE_KEY
    }

    if form.validate_on_submit():
        # Проверка верификационного кода
        if not form.code_verified():
            return render_template(message=f"Код не тот.", **template_params)

        # Проверка reCaptcha
        recaptcha_success, recaptcha_message = verify_recaptcha(
            request.form.get('recaptcha-token'),
            'forgot_password'
        )
        if not recaptcha_success:
            return render_template(message=recaptcha_message, **template_params)

        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if not user:
            return render_template(message="Такого пользователя нет.", **template_params)

        user.set_password(form.new_password.data)   
        db_sess.merge(user)
        db_sess.commit()

        return redirect("/login")

    return render_template(**template_params)


@app.route('/currency', methods=['GET', 'POST'])
@check_buffer
def currency():
    balance = current_user.balance

    price = [
        {"Цена": '500₽', "GEFs": 250},
        {"Цена": '1000₽', "GEFs": 500},
        {"Цена": '2000₽', "GEFs": 1000},
        {"Цена": '5000₽', "GEFs": 2500},
        {"Цена": '10000₽', "GEFs": 5000},
        {"Цена": '15000₽', "GEFs": 7500},
        {"Цена": '20000₽', "GEFs": 10000},
        {"Цена": '25000₽', "GEFs": 12500},
        {"Цена": '30000₽', "GEFs": 15000}
    ]

    if request.method == 'POST':
        button_name = request.form['button']

        db_sess = db_session.create_session()
        balance += [i["GEFs"] for i in price if i["Цена"] == button_name][0]
        current_user.balance = balance
        db_sess.merge(current_user)
        operation = Message(user=current_user.id, name='Покупка', data=datetime.datetime.now().strftime("%d.%m.%Y %H:%M"), readability=False,
                            sender='UltimateUnity', recipient=current_user.name, suma=button_name,
                            about=f'Вам начислено {[i["GEFs"] for i in price if i["Цена"] == button_name][0]} GEF')
        db_sess.add(operation)
        db_sess.commit()

        template_params = {
            "template_name_or_list": "buy.html",
            "title": "Оплата",
            "price": button_name[:-1]
        }

        return render_template(**template_params)

    transactions = []
    db_sess = db_session.create_session()
    messages_db = db_sess.query(Message).filter(Message.user == current_user.id).all()
    for i in messages_db:
        if i.suma:
            transactions.append({"Время": i.data,
                                 "Сумма": i.suma,
                                 "Отправитель": i.sender,
                                 "Получатель": i.recipient})

    template_params = {
        "template_name_or_list": "currency.html",
        "title": "Валюта",
        "balance": balance,
        "price": price,
        "transactions": transactions
    }
    return render_template(**template_params)


@app.route('/message')
@check_buffer
def message():
    messages = []
    db_sess = db_session.create_session()
    messages_db = db_sess.query(Message).filter(Message.user == current_user.id).all()
    news = 0
    for i in messages_db:
        messages.append({"Дата": i.data,
                         "Заголовок": i.name,
                         "Описание": i.about,
                         "Прочитанность": i.readability, })
        if not i.readability:
            news += 1

    template_params = {
        "template_name_or_list": "message.html",
        "title": "Уведомления",
        "messages": reversed(messages),
        "news": news
    }

    for i in messages_db:
        i.readability = True
    db_sess.commit()
    return render_template(**template_params)


@app.route("/add_project", methods=["GET", "POST"])
@login_required
@check_buffer
def add_project():
    form = EditProjectForm()

    template_params = {
        "template_name_or_list": "edit_project.html",
        "title": "Добавление проекта",
        "action": "Добавление",
        "form": form
    }

    if form.validate_on_submit():
        db_sess = db_session.create_session()
        project = Project(name=form.name.data, description=form.description.data, price=form.price.data)

        if not (imgs := form.imgs.data.read()):
            return render_template(message="У проекта нет изображений", **template_params)
        elif not check_zip(imgs):
            return render_template(message="Изображения - не ZIP-файл", **template_params)

        if not (files := form.files.data.read()):
            return render_template(message="А где собственно, сами файлы проекта?", **template_params)
        elif not check_zip(files):
            return render_template(message="Файлы проекта - не ZIP-файл", **template_params)

        project.imgs = imgs
        project.files = files

        current_user.created_projects.append(project)

        db_sess.merge(current_user)
        db_sess.commit()

        return redirect("/current_projects")

    return render_template(**template_params)


@app.route("/current_projects")
@login_required
@check_buffer
def current_projects():
    db_sess = db_session.create_session()
    projects = db_sess.query(Project).filter(Project.created_by_user == current_user)

    user_projects = []
    for proj in projects:
        user_projects.append(project_to_dict(proj))

    template_params = {
        "template_name_or_list": "user_projects.html",
        "title": "Проекты",
        "projects": user_projects
    }

    return render_template(**template_params)


@app.route("/edit_project/<int:id>", methods=["GET", "POST"])
@login_required
@check_buffer
def edit_project(id: int):
    form = EditProjectForm()

    db_sess = db_session.create_session()
    project = db_sess.query(Project).filter(Project.id == id, Project.created_by_user == current_user).first()

    template_params = {
        "template_name_or_list": "edit_project.html",
        "title": "Редактирование проекта",
        "action": "Редактирование",
        "project": project,
        "form": form
    }

    if request.method == "GET":
        form.name.data = project.name
        form.description.data = project.description
        form.price.data = project.price

    if form.validate_on_submit():
        project.name = form.name.data
        project.description = form.description.data
        project.price = form.price.data

        if (imgs := form.imgs.data.read()) != project.imgs:
            if check_zip(imgs):
                project.imgs = imgs
            else:
                return render_template(message="Изображения - не ZIP-файл", **template_params)

        if (files := form.files.data.read()) != project.files:
            if check_zip(files):
                project.files = files
            else:
                return render_template(message="Файлы проекта - не ZIP-файл", **template_params)

        db_sess.commit()

        return redirect("/current_projects")

    return render_template(**template_params)


@app.route("/project_info/<int:id>", methods=["GET", "POST"])
@check_buffer
def project_info(id: int):
    db_sess = db_session.create_session()
    project = db_sess.query(Project).filter(Project.id == id).first()

    template_params = {
        "template_name_or_list": "project_info.html",
        "title": project.name,
        "project": project_to_dict(project)
    }
    return render_template(**template_params)


@app.route("/delete_project/<int:id>")
@login_required
@check_buffer
def delete_project(id: int):
    db_sess = db_session.create_session()
    project = db_sess.query(Project).filter(Project.id == id, Project.created_by_user == current_user).first()

    db_sess.delete(project)
    db_sess.commit()

    return redirect("/current_projects")


@login_manager.user_loader
def load_user(user_id: int) -> User:
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/send_verify_code", methods=["POST"])
def send_verify_code():
    data = request.get_json()
    email = data.get("email")
    subject = data.get("subject")
    if not subject:
        return jsonify({"success": False, "message": "Subject is required."}), 400

    # For change_password, require login and use current_user.email
    if subject == "change_password":
        if not current_user.is_authenticated:
            return jsonify({"success": False, "message": "Authentication required."}), 401
        email = current_user.email
    if not email:
        return jsonify({"success": False, "message": "Email is required."}), 400


    db_sess = db_session.create_session()
    verify_code_generated = str(random.randint(10000000000000000000000, 99999999999999999999999))

    verify_code = db_sess.query(VerifyCode).filter(VerifyCode.email == email).first()
    if not verify_code:
        verify_code = VerifyCode(
            email=email,
            subject=subject
        )
        db_sess.add(verify_code)
        verify_code.set_verify_code(verify_code_generated)
    else:
        verify_code.set_verify_code(verify_code_generated)
        verify_code.update(subject)

    db_sess.commit()
    try:
        send_email(email, subject, verify_code_generated)
    except ValueError as e:
        return jsonify({"success": False, "message": f"Error sending email: {str(e)}"}), 500
    return jsonify({"success": True, "message": "Verification code sent."})


def main():
    db_session.global_init("db_related/db/db.db")
    # restful api
    # для списка объектов
    api.add_resource(users_resources.UsersListResource, '/api/users')
    # для одного объекта
    api.add_resource(users_resources.UsersResource, '/api/user/<user_email>')
    # rest api
    # для получения верификационных кодов
    api.add_resource(verify_cods_resources.VerifyCodeResource, '/api/verify_code')

    app.run()


if __name__ == "__main__":
    main()