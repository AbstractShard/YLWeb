from flask import Blueprint, render_template, request, redirect, abort, send_from_directory
from flask_login import login_required, current_user
from db_related.data.users import User
from db_related.data import db_session
from db_related.data.projects import Project
from forms import EditProjectForm
from consts import check_buffer, project_to_dict, check_zip
import os
import zipfile
import io
import shutil

# Initialize blueprint
projects_bp = Blueprint('projects', __name__)

# Routes
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
        project_name = form.name.data
        
        # 1. Проверяем, что имя проекта уникально
        project = db_sess.query(Project).filter(Project.name == project_name).first()
        if project:
            return render_template(message="Проект с таким именем уже существует", **template_params)
        
        # 2. Проверяем, что файлы проекта и изображения загружены
        imgs_file = form.imgs.data
        files_file = form.files.data
        if not imgs_file:
            return render_template(message="У проекта нет изображений", **template_params)
        if not files_file:
            return render_template(message="А где собственно, сами файлы проекта?", **template_params)
        imgs_data = imgs_file.read()
        if not check_zip(imgs_data):
            return render_template(message="Изображения - не ZIP-файл", **template_params)
        files_data = files_file.read()
        if not check_zip(files_data):
            return render_template(message="Файлы проекта - не ZIP-файл", **template_params)

        # 1. Сохраняем файлы на диск
        project_dir = f"static/buffer/projects/{project_name}"
        os.makedirs(project_dir, exist_ok=True)
        os.mkdir(f"{project_dir}/preview_imgs")
        imgs_path = f"{project_dir}/preview_imgs"
        files_path = f"{project_dir}/{project_name}.zip"

        with open(files_path, "wb") as f:
            f.write(files_data)
        with zipfile.ZipFile(io.BytesIO(imgs_data)) as zip_ref:
            zip_ref.extractall(imgs_path)
                        
        # 2. Создаём проект
        project = Project(
            name=project_name,
            description=form.description.data,
            price=form.price.data,
            imgs=imgs_path,
            files=files_path,
            created_by_user_id=current_user.id
        )

        # 3. Добавляем проект в базу данных
        db_sess.add(project)
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
    
    print(user_projects)

    template_params = {
        "template_name_or_list": "user_projects.html",
        "title": "Проекты",
        "projects": user_projects
    }

    return render_template(**template_params)


@projects_bp.route("/edit_project/<string:name>", methods=["GET", "POST"])
@login_required
@check_buffer
def edit_project(name: str):
    form = EditProjectForm()

    db_sess = db_session.create_session()
    project = db_sess.query(Project).filter(Project.name == name, Project.created_by_user == current_user).first()
    if not project:
        abort(404)
        
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
        project_new_name = form.name.data
        project_old_name = project.name
        project_old_imgs = project.imgs
        project_old_files = project.files
        
        # 1. Проверяем, что имя проекта уникально
        project_by_other = db_sess.query(Project).filter(Project.name == project_new_name, Project.created_by_user != current_user).first()
        if project_by_other:
            return render_template(message="Проект с таким именем уже существует", **template_params)
        
        # Если имя изменилось, переименовываем папку и файлы
        if project_new_name != project_old_name:
            old_dir = f"static/buffer/projects/{project_old_name}"
            new_dir = f"static/buffer/projects/{project_new_name}"
            if os.path.exists(old_dir):
                os.rename(old_dir, new_dir)
            # Обновляем пути к preview_imgs и .zip
            project.imgs = f"{new_dir}/preview_imgs"
            project.files = f"{new_dir}/{project_new_name}.zip"
        else:
            new_dir = f"static/buffer/projects/{project_new_name}"
            project.imgs = f"{new_dir}/preview_imgs"
            project.files = f"{new_dir}/{project_new_name}.zip"
        project.name = project_new_name
        project.description = form.description.data
        project.price = form.price.data

        # 2. Проверяем, что файлы проекта и изображения загружены и обновляем их
        imgs_file = form.imgs.data
        files_file = form.files.data
        project_dir = new_dir
        os.makedirs(project_dir, exist_ok=True)
        if imgs_file:
            imgs_data = imgs_file.read()
            if not check_zip(imgs_data):
                return render_template(message="Изображения - не ZIP-файл", **template_params)
            imgs_path = f"{project_dir}/preview_imgs"
            if os.path.exists(imgs_path):
                shutil.rmtree(imgs_path)
            os.makedirs(imgs_path, exist_ok=True)
            with zipfile.ZipFile(io.BytesIO(imgs_data)) as zip_ref:
                zip_ref.extractall(imgs_path)
            project.imgs = imgs_path
        if files_file:
            files_data = files_file.read()
            if not check_zip(files_data):
                return render_template(message="Файлы проекта - не ZIP-файл", **template_params)
            files_path = f"{project_dir}/{project_new_name}.zip"
            with open(files_path, "wb") as f:
                f.write(files_data)
            project.files = files_path
        
        # 3. Обновляем проект в базе данных
        db_sess.merge(project)
        db_sess.commit()
        return redirect("/current_projects")

    return render_template(**template_params)


@projects_bp.route("/project/<string:name>", methods=["GET", "POST"])
@check_buffer
def project_info(name: str):
    db_sess = db_session.create_session()
    
    # Проверяем, что проект существует
    project = db_sess.query(Project).filter(Project.name == name).first()
    if not project:
        abort(404)
        
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
            return redirect("/project/" + project.name)
        else:
            return render_template(
                "project_info.html",
                title=project.name,
                project=project_to_dict(project),
                project_btn=project_btn,
                message="Недостаточно GEF's"
            )

    return render_template(
        "project_info.html",
        title=project.name,
        project=project_to_dict(project),
        project_btn=project_btn
    )


@projects_bp.route("/delete_project/<string:name>")
@login_required
@check_buffer
def delete_project(name: str):
    db_sess = db_session.create_session()
    project = db_sess.query(Project).filter(Project.name == name, Project.created_by_user == current_user).first()

    db_sess.delete(project)
    db_sess.commit()

    return redirect("/current_projects")


@projects_bp.route("/download/<string:name>")
@check_buffer
def download_project(name: str):
    db_sess = db_session.create_session()
    project = db_sess.query(Project).filter(Project.name == name).first()
    if not project or not os.path.isfile(project.files):
        abort(404)
    return send_from_directory(os.path.dirname(project.files), os.path.basename(project.files), as_attachment=True)
