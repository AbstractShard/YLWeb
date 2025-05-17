s = """<!doctype html>
<html lang="ru">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">
        <link rel="stylesheet" href="../static/css/style.css">
        <link rel="stylesheet" href="../static/css/users.css">
        <link rel="stylesheet" href="../static/css/projects.css" >
        <link rel="stylesheet" href="../static/css/auth.css">

        <link rel="apple-touch-icon" sizes="180x180" href="../static/img/icon/apple-touch-icon.png">
        <link rel="icon" type="image/png" sizes="32x32" href="../static/img/icon/favicon-32x32.png">
        <link rel="icon" type="image/png" sizes="16x16" href="../static/img/icon/favicon-16x16.png">
        <link rel="manifest" href="../static/img/icon/site.webmanifest">
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com">
        
        <link href="https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,100;0,300;0,400;0,500;0,700;0,900;1,100;1,300;1,400;1,500;1,700;1,900&display=swap" rel="stylesheet">

        <title>{{ title }}</title>
    </head>

    <body>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

        <header>
            <div class="main-items">
                <h1 onclick="location.href='/'" title="На главную страницу">UltimateUnity</h1>

                {% if current_user.is_authenticated %}
                    <img
                            src="../static/img/add_project.png"
                            align="left"
                            width="70px"
                            height="70px"
                            title="В проекты"
                            onclick="location.href='/current_projects'"
                    >
                {% endif %}
            </div>

            <div class="user-items">
                {% if current_user.is_authenticated %}
                    <div onclick="location.href='/profile'" class="avatar" title="В профиль">
                        <img
                                src="../static/buffer/profile.png"
                                width="60px"
                                height="60px"
                                class="avatar-img"
                        >
                        <span class="avatar-caption">{{ current_user.name }}</span>
                    </div>
                    <div onclick="location.href='/currency'" class="currency" title="В отдел валют">
                        <img
                                src="../static/img/currency.png"
                                class="currency-img"
                                alt="Непрогруженная валюта"
                        >
                        <span class="currency-caption">{{ current_user.balance }}</span>
                    </div>
                    <div onclick="location.href='/message'" class="message" title="В уведомления">
                        <img
                                src="../static/img/notifications.png"
                                alt="Непрогруженные уведомления"
                        >
                    </div>
                {% else %}
                    <button onclick="location.href='/register'" class="btn btn-primary">Зарегистрироваться</button>
                    <button onclick="location.href='/login'" class="btn btn-success">Войти</button>
                {% endif %}
            </div>
        </header>

        <main role="main" class="bg-light">
            {% block content %}
            {% endblock %}

            <footer class="bg-dark text-white">
                <div class="container py-4">
                    <h5>О нас</h5>

                    <p>Мы — компания, предоставляющая лучшие услуги в своей области.
                        Наша цель — удовлетворение потребностей клиентов. Покупка, продажа и создание проектов —
                        всё, что требуется от вас. Отличный сайт, быстрая обратная связь — это к нам.
                    </p>

                    <div class="text-center py-3">
                        <small>&copy; 2025 UltimateUnity. Все права защищены.</small>
                    </div>
                </div>
            </footer>
        </main>
    </body>
</html>"""
import re
print(re.sub(r"\n", "", re.sub(r"^\s+", "", s, flags=re.MULTILINE), flags=re.MULTILINE))