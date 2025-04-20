from functools import wraps
import os
import random
import smtplib
from email.message import EmailMessage
from flask_login import current_user, AnonymousUserMixin

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
        email_sender = "ultimateunitysender@gmail.com"
        email_password = "xeku ltag tolv rtrs"  # Для Gmail нужен пароль приложения

        subject = "Ваш верификационный код"
        # HTML-шаблон с кнопкой
        html_content = f"""
        <html>
        <body>
            <div style="background: #f9f9f9; padding: 20px; border-radius: 10px;">
                <h2 style="color: #333;">Ваш код подтверждения</h2>
                <br>
                <div style="text-align: center; margin: 0 auto; border: 2px solid #ccc; padding: 10px; border-radius: 5px;">
                    <h1>{verification_code}</h1>
                </div>
                <br>
                <p style="font-size: 17px;">Этот код действителен в течение 15 минут.</p>
    
                <p style="color: #777; font-size: 14px;">
                    Если вы не запрашивали этот код, проигнорируйте это письмо. Просто какой-то
                     <strike>даун</strike> слабоумный вашу почту вписал и теперь отправляет вам коды верификации.
                </p>
            </div>
        </body>
        </html>
        """

        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = email_sender
        msg['To'] = email_receiver
        msg.add_alternative(html_content, subtype='html')

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(email_sender, email_password)
            smtp.send_message(msg)

    elif subject == "change_password":
        email_sender = "ultimateunitysender@gmail.com"
        email_password = "xeku ltag tolv rtrs"  # Для Gmail нужен пароль приложения

        subject = "Смена пароля"
        # HTML-шаблон с кнопкой
        html_content = f"""
        <html>
        <body>
            <div style="background: #f9f9f9; padding: 20px; border-radius: 10px;">
                <h2 style="color: #333;">Ваш код подтверждения</h2>
                <br>
                <div style="text-align: center; margin: 0 auto; border: 2px solid #ccc; padding: 10px; border-radius: 5px;">
                    <h1>{verification_code}</h1>
                </div>
                <br>
                <p style="font-size: 17px;">Этот код действителен в течение 15 минут.</p>
    
                <p style="color: #777; font-size: 14px;">
                    Если вы не запрашивали этот код, проигнорируйте это письмо. Просто какой-то
                     <strike>даун</strike> слабоумный вашу почту вписал и теперь отправляет вам коды смены пароля.
                </p>
            </div>
        </body>
        </html>
        """

        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = email_sender
        msg['To'] = email_receiver
        msg.add_alternative(html_content, subtype='html')

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(email_sender, email_password)
            smtp.send_message(msg)
