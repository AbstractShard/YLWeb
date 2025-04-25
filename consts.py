import random
from functools import wraps
import os
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage

from flask import render_template
from flask_login import current_user, AnonymousUserMixin
from db_related.data import db_session
from db_related.data.users import User, TempUser

# Load environment variables
load_dotenv('static/.env')

# Email configuration
SENDERS = os.getenv("SENDERS")

if not SENDERS:
    raise ValueError("Email credentials not configured in environment variables")
else:
    # Перевод строки в словарь
    SENDERS = {sender.split(':')[0]: sender.split(':')[1] for sender in SENDERS.split(',')}


DEFAULT_PROFILE_PATH = "static/img/profile.png"
CURRENT_PROFILE_PATH = "static/buffer/profile.png"


def check_buffer(func):
    @wraps(func)
    def body(*args, **kwargs):
        # Проверка на наличие папки "buffer"
        if not os.path.exists("static/buffer"):
            os.mkdir("static/buffer")

        # Проверка на наличие файла с изображением профиля
        if not os.path.exists(CURRENT_PROFILE_PATH):
            if not isinstance(current_user, AnonymousUserMixin):
                with open(CURRENT_PROFILE_PATH, mode="wb") as curr_img:
                    curr_img.write(current_user.img)

        return func(*args, **kwargs)

    return body


def send_email(email_receiver, subject, verification_code):
    if subject == "verify_email":
        subject = "Регистрация"

        # HTML-шаблон с кнопкой
        html_content = render_template('email/register.html', verification_code=verification_code)

    elif subject == "change_password":
        subject = "Смена пароля"

        html_content = render_template('email/change_password.html', verification_code=verification_code)

    elif subject == "forgot_password":
        subject = "Забыл пароль"

        html_content = render_template('email/forgot_password.html', verification_code=verification_code)

    random_senders = list(SENDERS.items())
    random.shuffle(random_senders)

    max_retries = 3
    timeout_seconds = 10
    for sender, password in random_senders:
        for attempt in range(max_retries):
            try:
                with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=timeout_seconds) as smtp:
                    msg = EmailMessage()
                    msg['From'] = sender
                    msg['Subject'] = subject
                    msg['To'] = email_receiver
                    msg.add_alternative(html_content, subtype='html')

                    smtp.login(sender, password)
                    smtp.send_message(msg)
                    print(f"{sender}: Sent email with subject '{subject}' to {email_receiver}")
                    return True
            except Exception as e:
                if attempt == max_retries - 1:  # Last attempt failed
                    print(f"{sender}: Failed to send email after {max_retries} attempts: {str(e)}.")

    return False


def user_exists(user_email, temp=False) -> bool:
    db_sess = db_session.create_session()
    if temp:
        return db_sess.query(TempUser).filter(TempUser.email == user_email).first()
    return db_sess.query(User).filter(User.email == user_email).first()


if __name__ == "__main__":
    print(send_email("6K3uGSGDFUIGubiudsfu8q45637462534regydf7^%^%F6sdg0@example.com", "verify_email", "1234567890"))
