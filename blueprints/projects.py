from flask import Blueprint, render_template, request, redirect, abort
from flask_login import login_required, current_user, AnonymousUserMixin
from db_related.data import db_session
from db_related.data.projects import Project
from forms import EditProjectForm
from consts import check_buffer, project_to_dict, check_zip, add_project_files

# Initialize blueprint
projects_bp = Blueprint('projects', __name__)

# Routes
@projects_bp.route("/projects")
@check_buffer
def projects_list():
    db_sess = db_session.create_session()
    projects = db_sess.query(Project).all()
    return render_template("projects/list.html", title="Проекты", projects=projects)

@projects_bp.route("/add_project", methods=["GET", "POST"])
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


@projects_bp.route("/current_projects")
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


@projects_bp.route("/edit_project/<int:id>", methods=["GET", "POST"])
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


@projects_bp.route("/project_info/<int:id>", methods=["GET", "POST"])
@check_buffer
def project_info(id: int):
    db_sess = db_session.create_session()
    try:
        # Получаем объекты в текущей сессии
        project = db_sess.query(Project).get(id)
        if not project:
            abort(404)
        from db_related.data.users import User
        user = db_sess.query(User).get(current_user.id) if current_user.is_authenticated else None

        project_btn = "login"
        if user:
            if project in user.created_projects or project in user.purchased_projects:
                project_btn = "download"
            else:
                project_btn = "buy"

        if request.method == "POST" and user:
            if user.balance >= project.price:
                # Обновляем балансы
                user.balance -= project.price
                project.created_by_user.balance += project.price
                
                # Добавляем связь через текущую сессию
                user.purchased_projects.append(project)
                
                db_sess.commit()

        return render_template(
            "project_info.html",
            title=project.name,
            project=project_to_dict(project),
            project_btn=project_btn
        )
    finally:
        db_sess.close()


@projects_bp.route("/delete_project/<int:id>")
@login_required
@check_buffer
def delete_project(id: int):
    db_sess = db_session.create_session()
    project = db_sess.query(Project).filter(Project.id == id, Project.created_by_user == current_user).first()

    db_sess.delete(project)
    db_sess.commit()

    return redirect("/current_projects")