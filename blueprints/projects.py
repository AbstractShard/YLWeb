from flask import Blueprint, render_template, request, redirect, abort
from flask_login import login_required, current_user
from db_related.data import db_session
from db_related.data.projects import Project
from forms import EditProjectForm
from consts import check_buffer, project_to_dict, check_zip, add_project_files
import os

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

        # Save uploaded files to disk
        imgs_file = form.imgs.data
        files_file = form.files.data
        if not imgs_file:
            return render_template(message="У проекта нет изображений", **template_params)
        imgs_data = imgs_file.read()
        if not check_zip(imgs_data):
            return render_template(message="Изображения - не ZIP-файл", **template_params)
        if not files_file:
            return render_template(message="А где собственно, сами файлы проекта?", **template_params)
        files_data = files_file.read()
        if not check_zip(files_data):
            return render_template(message="Файлы проекта - не ZIP-файл", **template_params)

        db_sess.add(project)
        db_sess.flush()  # Get project.id before commit
        project_dir = f"static/buffer/projects/{project.id}"
        os.makedirs(project_dir, exist_ok=True)
        imgs_path = f"{project_dir}/project_imgs.zip"
        files_path = f"{project_dir}/{project.name}.zip"
        with open(imgs_path, "wb") as f:
            f.write(imgs_data)
        with open(files_path, "wb") as f:
            f.write(files_data)
        project.imgs = imgs_path
        project.files = files_path

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

        imgs_file = form.imgs.data
        files_file = form.files.data
        project_dir = f"static/buffer/projects/{project.id}"
        os.makedirs(project_dir, exist_ok=True)
        if imgs_file:
            imgs_data = imgs_file.read()
            if check_zip(imgs_data):
                imgs_path = f"{project_dir}/project_imgs.zip"
                with open(imgs_path, "wb") as f:
                    f.write(imgs_data)
                project.imgs = imgs_path
            else:
                return render_template(message="Изображения - не ZIP-файл", **template_params)
        if files_file:
            files_data = files_file.read()
            if check_zip(files_data):
                files_path = f"{project_dir}/{project.name}.zip"
                with open(files_path, "wb") as f:
                    f.write(files_data)
                project.files = files_path
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
                add_project_files(project)
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