from flask import Flask, request, render_template, redirect
from flask_login import current_user
import requests
from forms import RegisterForm

app = Flask(__name__)
from dotenv import load_dotenv
import os

load_dotenv('static/.env')
app.secret_key = 'dsfsdf'

HCAPTCHA_SECRET_KEY = os.getenv('HCAPTCHA_SECRET_KEY')

@app.route('/', methods=['GET'])
def form():
    form = RegisterForm()
    params = {
        'HCAPTCHA_SECRET_KEY': os.getenv('HCAPTCHA_SECRET_KEY'),
        'form': form,
        "title": "Регистрация",
        "current_user": current_user
    }
    if form.validate_on_submit():
        return redirect("/submit")
    return render_template('register.html', **params)

@app.route('/submit', methods=['POST'])
def submit():
    # Проверка hCaptcha
    data = {
        'secret': os.getenv('HCAPTCHA_SECRET_KEY'),
        'response': request.form.get('h-captcha-response')
    }
    result = requests.post('https://hcaptcha.com/siteverify', data=data).json()
    
    if not result['success']:
        return "Капча не пройдена!", 400
    
    return "Форма отправлена успешно!"

if __name__ == '__main__':
    app.run()