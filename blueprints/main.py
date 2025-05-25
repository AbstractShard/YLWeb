from flask import Blueprint, render_template, request
from flask_login import current_user

from db_related.data import db_session
from db_related.data.message import Message
from db_related.data.projects import Project

from consts import check_buffer, project_to_dict

import datetime

# Initialize blueprint
main_bp = Blueprint('main', __name__)

# Routes
@main_bp.route("/")
@check_buffer
def index():
    db_sess = db_session.create_session()
    projects = db_sess.query(Project).all()

    template_params = {
        "template_name_or_list": 'index.html',
        "title": 'UltimateUnity',
        "projects": [project_to_dict(proj) for proj in projects]
    }
    
    return render_template(**template_params)

@main_bp.route('/currency', methods=['GET', 'POST'])
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
            "title": "Оплата | UU",
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
        "title": "Валюта | UU",
        "balance": balance,
        "price": price,
        "transactions": transactions
    }
    return render_template(**template_params)

@main_bp.route('/message')
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
        "title": "Уведомления | UU",
        "messages": reversed(messages),
        "news": news
    }

    for i in messages_db:
        i.readability = True
    db_sess.commit()
    return render_template(**template_params)

