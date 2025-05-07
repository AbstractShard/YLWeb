from flask import Blueprint, render_template, redirect, request, jsonify
from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash

from db_related.data import db_session
from db_related.data.users import User
from db_related.data.verify_cods import VerifyCode, send_email
from forms import RegisterForm, LoginForm, ProfileForm, ChangePasswordForm, ForgotPasswordForm
from consts import check_buffer, verify_captcha
import consts
import random

# Initialize blueprint
auth_bp = Blueprint('auth', __name__)

# Routes
@auth_bp.route("/register", methods=["GET", "POST"])
@check_buffer
def register():
    form = RegisterForm()
    template_params = {
        "template_name_or_list": "register.html",
        "title": "Регистрация",
        "form": form,
        "HCAPTCHA_SITE_KEY": consts.HCAPTCHA_SITE_KEY,
        "RECAPTCHA_SITE_KEY": consts.RECAPTCHA_SITE_KEY
    }

    if form.validate_on_submit():
        # Password check
        if form.password.data != form.password_again.data:
            return render_template(message="Пароли не совпадают.", **template_params)
        
        # Verification code check
        if not form.code_verified():
            return render_template(message=f"Код не тот.", **template_params)

        # reCaptcha check
        recaptcha_success, recaptcha_message = verify_captcha(
            request.form.get('recaptcha-token'),
            action='register',
            captcha_type='recaptcha'
        )
        if not recaptcha_success:
            return render_template(message=recaptcha_message, **template_params)
        
        # hCaptcha check
        hcaptcha_success, hcaptcha_message = verify_captcha(
            request.form.get('h-captcha-response'),
            captcha_type='hcaptcha'
        )
        if not hcaptcha_success:
            return render_template(message=hcaptcha_message, **template_params)

        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template(message="Такой пользователь уже есть.", **template_params)

        user = User(name=form.name.data, email=form.email.data)
        user.set_default_img()
        user.set_password(form.password.data)

        db_sess.add(user)
        db_sess.commit()
        
        return redirect('/login')
    
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
        form.email.data = current_user.email
    
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        
        if user:
            user.name = form.name.data
            user.email = form.email.data
            db_sess.commit()
            return redirect('/profile')
    
    return render_template(**template_params)

@auth_bp.route("/change_password", methods=["GET", "POST"])
@login_required
@check_buffer
def change_password():
    form = ChangePasswordForm()
    template_params = {
        "template_name_or_list": "change_password.html",
        "title": "Смена пароля",
        "form": form
    }

    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template(message="Пароли не совпадают", **template_params)
        
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        
        if user and user.check_password(form.old_password.data):
            user.set_password(form.password.data)
            db_sess.commit()
            return redirect('/profile')
        
        return render_template(message="Неверный пароль", **template_params)
    
    return render_template(**template_params)

@auth_bp.route("/forgot_password", methods=["GET", "POST"])
@check_buffer
def forgot_password():
    form = ForgotPasswordForm()
    template_params = {
        "template_name_or_list": "forgot_password.html",
        "title": "Восстановление пароля",
        "form": form
    }

    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template(message="Пароли не совпадают", **template_params)
        
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        
        if not user:
            return render_template(message="Пользователь не найден", **template_params)
        
        if not form.code_verified():
            return render_template(message="Неверный код", **template_params)
        
        user.set_password(form.password.data)
        db_sess.commit()
        return redirect('/login')
    
    return render_template(**template_params)

@auth_bp.route("/send_verify_code", methods=["POST"])
def send_verify_code():
    email = request.json.get('email')
    subject = request.json.get('subject')

    if not email and subject != 'change_password':
        return jsonify({"success": False, "message": "Email не указан"})
    
    db_sess = db_session.create_session()
    
    if subject != 'register' and subject != 'forgot_password':
        user = db_sess.query(User).filter(User.email == email).first()
        
        if not user:
            return jsonify({"success": False, "message": "Пользователь не найден"})
    
    old_verify_code = db_sess.query(VerifyCode).filter(VerifyCode.email == email, VerifyCode.subject == subject).first()
    if old_verify_code:
        db_sess.delete(old_verify_code)
    
    code = ''.join([str(random.randint(0, 9)) for _ in range(20)])
    verify_code = VerifyCode(email=email, subject=subject)
    verify_code.set_verify_code(code)
    
    db_sess.add(verify_code)
    db_sess.commit()
    
    send_email(email, subject, code)
    
    return jsonify({"success": True}) 