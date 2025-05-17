import os
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
            'id', 'name', 'description', 'created_date', 'price', 'created_by_user_id'
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
            project_dir = f"static/buffer/projects/{project.id}"
            os.makedirs(project_dir, exist_ok=True)
            files_path = f"{project_dir}/{project.name}.zip"
            with open(files_path, "wb") as f:
                f.write(files_file.read())
            project.files = files_path
        if 'imgs' in request.files:
            imgs_file = request.files['imgs']
            project_dir = f"static/buffer/projects/{project.id}"
            os.makedirs(project_dir, exist_ok=True)
            imgs_path = f"{project_dir}/project_imgs.zip"
            with open(imgs_path, "wb") as f:
                f.write(imgs_file.read())
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
    
    def post(self):
        # Accept form data and files
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        created_by_user_id = request.form.get('created_by_user_id')
        files = request.files.get('files')
        imgs = request.files.get('imgs')
        session = db_session.create_session()
        project = Project(
            name=name,
            price=price,
            created_by_user_id=created_by_user_id,
            description=description or None,
            files='',
            imgs=''
        )
        session.add(project)
        session.flush()  # get project.id
        project_dir = f"static/buffer/projects/{project.id}"
        os.makedirs(project_dir, exist_ok=True)
        if imgs:
            imgs_path = f"{project_dir}/project_imgs.zip"
            with open(imgs_path, "wb") as f:
                f.write(imgs.read())
            project.imgs = imgs_path
        if files:
            files_path = f"{project_dir}/{project.name}.zip"
            with open(files_path, "wb") as f:
                f.write(files.read())
            project.files = files_path
        session.commit()
        return jsonify({'success': 'OK', 'id': project.id})