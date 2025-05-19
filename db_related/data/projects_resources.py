import os
import zipfile
import io
from flask import jsonify, request
from flask_restful import Resource, abort

from .projects import Project
from . import db_session

def abort_if_project_not_found(project_id):
    session = db_session.create_session()
    project = session.query(Project).filter(Project.id == project_id).first()
    if not project:
        abort_params = {
            'error': '404',
            'message': f"Project {project_id} not found"
        }
        abort(404, **abort_params)


def abort_if_project_exists(project_id):
    """Bad request if project already exists"""
    session = db_session.create_session()
    project = session.query(Project).filter(Project.id == project_id).first()
    if project:
        abort_params = {
            'error': '400',
            'message': f"Project {project_id} already exists"
        }
        abort(400, **abort_params)


class ProjectsResource(Resource):
    def get(self, project_id):
        abort_if_project_not_found(project_id)
        session = db_session.create_session()
        project = session.query(Project).filter(Project.id == project_id).first()
        return jsonify({'project': project.to_dict(only=(
            'id', 'name', 'description', 'created_date', 'price', 'created_by_user_id', 'files', 'imgs'
        ))})
    
    def delete(self, project_id):
        abort_if_project_not_found(project_id)
        session = db_session.create_session()
        project = session.query(Project).filter(Project.id == project_id).first()
        session.delete(project)
        session.commit()
        return jsonify({'success': 'OK'})
    
    def put(self, project_id):
        abort_if_project_not_found(project_id)
        session = db_session.create_session()
        project = session.query(Project).filter(Project.id == project_id).first()
        # Update fields from form data
        if 'name' in request.form:
            project.name = request.form['name']
        if 'description' in request.form:
            project.description = request.form['description']
        if 'price' in request.form:
            project.price = request.form['price']
        if 'created_by_user_id' in request.form:
            project.created_by_user_id = request.form['created_by_user_id']
        if 'files' in request.files:
            files_file = request.files['files']
            project_dir = f"static/buffer/projects/{project.name}"
            os.makedirs(project_dir, exist_ok=True)
            files_path = f"{project_dir}/{project.name}.zip"
            with open(files_path, "wb") as f:
                f.write(files_file.read())
            project.files = files_path
        if 'imgs' in request.files:
            imgs_file = request.files['imgs']
            project_dir = f"static/buffer/projects/{project.name}"
            imgs_path = f"{project_dir}/preview_imgs"
            os.makedirs(project_dir, exist_ok=True)
            os.makedirs(imgs_path, exist_ok=True)
            with zipfile.ZipFile(io.BytesIO(imgs_file)) as zip_ref:
                zip_ref.extractall(imgs_path)
            project.imgs = imgs_path
        session.commit()
        return jsonify({'success': 'OK'})
    

class ProjectsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        projects = session.query(Project).all()
        return jsonify({'projects': [item.to_dict(only=(
            'id', 'name', 'description', 'created_date', 'price', 'created_by_user_id'
        )) for item in projects]})
