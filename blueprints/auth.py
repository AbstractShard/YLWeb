from flask import Blueprint, render_template, redirect, request, jsonify
from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash
from consts import verify_captcha

from db_related.data import db_session
from db_related.data.users import User
from db_related.data.verify_cods import VerifyCode, send_email
from forms import RegisterForm, LoginForm, ProfileForm, ChangePasswordForm, ForgotPasswordForm
from consts import check_buffer, verify_captcha
import consts
import random

# Initialize blueprint
auth_bp = Blueprint('auth', __name__)

RECAPTCHA_SITE_KEY = consts.RECAPTCHA_SITE_KEY
HCAPTCHA_SITE_KEY = consts.HCAPTCHA_SITE_KEY

# Routes
@auth_bp.route("/register", methods=["GET", "POST"])
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
        
        # Проверка hCaptcha
        hcaptcha_success, hcaptcha_message = verify_captcha(
            request.form.get('h-captcha-response'),
            'hcaptcha',
            'register'
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

@auth_bp.route("/login", methods=["GET", "POST"])
@check_buffer
def login():
    form = LoginForm()
    template_params = {
        "template_name_or_list": "login.html",
        "title": "Вход",
        "form": form,
        "HCAPTCHA_SITE_KEY": consts.HCAPTCHA_SITE_KEY,
        "RECAPTCHA_SITE_KEY": consts.RECAPTCHA_SITE_KEY
    }

    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        
        return render_template(message="Неверный логин или пароль", **template_params)
    
    return render_template(**template_params)

@auth_bp.route("/logout")
@login_required
@check_buffer
def logout():
    logout_user()
    return redirect("/")

@auth_bp.route("/profile", methods=["GET", "POST"])
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
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        
        if user:
            user.name = form.name.data
            img_data = form.img.data.read()
            if img_data:
                current_user.img = img_data

                with open(consts.CURRENT_PROFILE_PATH, mode="wb") as curr_img:
                    curr_img.write(current_user.img)

            db_sess.merge(current_user)
            db_sess.commit()
            return redirect('/profile')
    
    return render_template(**template_params)


@auth_bp.route("/change_password", methods=["GET", "POST"])
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

        recaptcha_success, recaptcha_message = verify_captcha(
            request.form.get('recaptcha-token'),
            'recaptcha',
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

@auth_bp.route("/forgot_password", methods=["GET", "POST"])
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
        recaptcha_success, recaptcha_message = verify_captcha(
            request.form.get('recaptcha-token'),
            'recaptcha',
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


@auth_bp.route("/send_verify_code", methods=["POST"])
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