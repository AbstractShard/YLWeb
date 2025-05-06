from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from db_related.data import db_session
from db_related.data.projects import Project
from db_related.data.users import User
from consts import check_buffer

# Initialize blueprint
projects_bp = Blueprint('projects', __name__)

# Routes
@projects_bp.route("/projects")
@check_buffer
def projects_list():
    db_sess = db_session.create_session()
    projects = db_sess.query(Project).all()
    return render_template("projects/list.html", title="Проекты", projects=projects)

@projects_bp.route("/projects/<int:project_id>")
@check_buffer
def project_detail(project_id):
    db_sess = db_session.create_session()
    project = db_sess.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        return redirect(url_for('projects.projects_list'))
    
    return render_template("projects/detail.html", title=project.name, project=project)

@projects_bp.route("/projects/create", methods=["GET", "POST"])
@login_required
@check_buffer
def project_create():
    if request.method == "POST":
        name = request.form.get('name')
        description = request.form.get('description')
        
        if not name:
            return render_template("projects/create.html", title="Создать проект", 
                                 error="Название проекта обязательно")
        
        db_sess = db_session.create_session()
        project = Project(
            name=name,
            description=description,
            creator_id=current_user.id
        )
        
        db_sess.add(project)
        db_sess.commit()
        
        return redirect(url_for('projects.project_detail', project_id=project.id))
    
    return render_template("projects/create.html", title="Создать проект")

@projects_bp.route("/projects/<int:project_id>/edit", methods=["GET", "POST"])
@login_required
@check_buffer
def project_edit(project_id):
    db_sess = db_session.create_session()
    project = db_sess.query(Project).filter(Project.id == project_id).first()
    
    if not project or project.creator_id != current_user.id:
        return redirect(url_for('projects.projects_list'))
    
    if request.method == "POST":
        name = request.form.get('name')
        description = request.form.get('description')
        
        if not name:
            return render_template("projects/edit.html", title="Редактировать проект",
                                 project=project, error="Название проекта обязательно")
        
        project.name = name
        project.description = description
        db_sess.commit()
        
        return redirect(url_for('projects.project_detail', project_id=project.id))
    
    return render_template("projects/edit.html", title="Редактировать проект", project=project)

@projects_bp.route("/projects/<int:project_id>/delete", methods=["POST"])
@login_required
@check_buffer
def project_delete(project_id):
    db_sess = db_session.create_session()
    project = db_sess.query(Project).filter(Project.id == project_id).first()
    
    if project and project.creator_id == current_user.id:
        db_sess.delete(project)
        db_sess.commit()
    
    return redirect(url_for('projects.projects_list'))

@projects_bp.route("/api/projects")
@check_buffer
def api_projects_list():
    db_sess = db_session.create_session()
    projects = db_sess.query(Project).all()
    
    return jsonify([{
        "id": p.id,
        "name": p.name,
        "description": p.description,
        "creator_id": p.creator_id,
        "created_date": p.created_date.isoformat()
    } for p in projects]) 