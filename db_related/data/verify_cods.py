import datetime
import os
import random
import re
import smtplib
import socket
from email.message import EmailMessage
from time import sleep
from flask import render_template
from dotenv import load_dotenv
import sqlalchemy
from sqlalchemy import Column, Integer, String
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase


# Load environment variables
load_dotenv('static/.env')

# Email configuration
SENDERS = os.getenv("SENDERS")

if not SENDERS:
    raise ValueError("Email credentials not configured in environment variables")
else:
    # Перевод строки в словарь
    SENDERS = {sender.split(':')[0]: sender.split(':')[1] for sender in SENDERS.split(',')}


TEMPLATES = {
    "change_password": "Смена пароля",
    "forgot_password": "Восстановление пароля",
    "register": "Регистрация"
}

MAX_RETRIES = 3
TIMEOUT = 10
RETRY_DELAY = 1  # Задержка между попытками в секундах


def get_plain_text(verification_code, subject):
    return f"""
{subject}
Ваш код подтверждения: {verification_code}

Этот код действителен 15 минут. Если вы не запрашивали его, проигнорируйте это письмо.

Если вы не запрашивали этот код, проигнорируйте это письмо.
© 2025 UltimateUnity. Все права защищены.
    """


def check_email(email: str) -> bool:
    return re.match(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', email) is not None


def send_email(email_receiver: str, subject: str, verification_code: str) -> bool:
    """
    Отправляет электронное письмо с использованием случайного отправителя из SENDERS.

    Args:
        email_receiver: Email получателя
        subject: Тип письма (определяет шаблон)
        verification_code: Код для вставки в шаблон

    Returns:
        bool: True если отправка успешна, иначе False
    """

    if not check_email(email_receiver):
        raise ValueError(f"Invalid email: {email_receiver}")

    if subject not in TEMPLATES:
        raise ValueError(f"Unknown subject type: {subject}")

    subject = TEMPLATES[subject]
    html_content = render_template('email.html', verification_code=verification_code, subject=subject)

    type_of_mail = email_receiver.split('@')[1]

    # Перемешиваем отправителей для балансировки нагрузки
    senders = list(SENDERS.items())
    random.shuffle(senders)
    senders = list(filter(lambda sender: sender[0].endswith(type_of_mail), senders)) + \
              list(filter(lambda sender: not sender[0].endswith(type_of_mail), senders))
    for sender, password in senders:
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                # Определяем SMTP-сервер
                host = "smtp.gmail.com" if sender.endswith("gmail.com") else "smtp.yandex.ru"

                # Создаём сообщение и добавляем HTML-контент
                msg = EmailMessage()
                msg['From'] = 'UltimateUnity <' + sender + '>'
                msg['To'] = email_receiver
                msg['Subject'] = subject + ' | Код подтверждения'
                msg.set_content(get_plain_text(verification_code, subject))
                msg.add_alternative(html_content, subtype='html')

                # Устанавливаем соединение с таймаутом
                with smtplib.SMTP_SSL(host, 465, timeout=TIMEOUT) as smtp:
                    smtp.login(sender, password)
                    smtp.send_message(msg)
                    print(f"Success: {sender} → {email_receiver} | {subject}")
                    return True

            except smtplib.SMTPException as e:
                print(f"Attempt {attempt} failed for {sender}: {str(e)}")
                if attempt < MAX_RETRIES:
                    sleep(RETRY_DELAY)  # Задержка перед повторной попыткой
                continue
            except (socket.timeout, ConnectionError) as e:
                print(f"Connection error for {sender} → {email_receiver} | {subject}: {str(e)}")
                if attempt < MAX_RETRIES:
                    sleep(RETRY_DELAY * 2)  # Увеличенная задержка для сетевых ошибок
                continue
            except Exception as e:
                print(f"Unexpected error for {sender} → {email_receiver} | {subject}: {str(e)}")
                break  # Переходим к следующему отправителю

    return False


class VerifyCode(SqlAlchemyBase):
    __tablename__ = "verify_cods"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(sqlalchemy.String, nullable=False)
    time_sent = Column(sqlalchemy.DateTime, default=datetime.datetime.now())
    subject = Column(sqlalchemy.String, nullable=False)
    verify_code = Column(String, nullable=False)

    time_to_live = datetime.timedelta(minutes=15)

    def set_verify_code(self, code: str):
        self.verify_code = generate_password_hash(code)

    def check_verify_code(self, code: str) -> bool:
        if datetime.datetime.now() - self.time_sent > self.time_to_live:
            return False
        return check_password_hash(self.verify_code, code)

    def update(self, subject):
        self.time_sent = datetime.datetime.now()
        self.subject = subject
