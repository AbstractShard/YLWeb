from flask import jsonify
from flask_restful import Resource, abort

from .projects import Project
from . import db_session
from .project_parsers import parser_post, parser_put
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
        args = parser_put.parse_args()
        session = db_session.create_session()
        project = session.query(Project).filter(Project.id == project_id).first()
        if args['name']:
            project.name = args['name']
        if args['description']:
            project.description = args['description']
        if args['price']:
            project.price = args['price']
        if args['created_by_user_id']:
            project.created_by_user_id = args['created_by_user_id']
        if args['files']:
            project.files = args['files']
        if args['imgs']:
            project.imgs = args['imgs']
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
        args = parser_post.parse_args()
        abort_if_project_exists(args['name'])
        session = db_session.create_session()
        project = Project(
            name=args['name'],
            price=args['price'],
            files=args['files'],
            created_by_user_id=args['created_by_user_id'],
        )
        if args['description']:
            project.description = args['description']
        if args['imgs']:
            project.imgs = args['imgs']

        session.add(project)
        session.commit()
        return jsonify({'success': 'OK',
                        'id': project.id})