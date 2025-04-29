from flask import jsonify
from flask_restful import Resource, abort


from .users import User
from .verify_cods import VerifyCode
from . import db_session
from .api_parsers import parser_post, parser_put


def abort_if_user_not_found(user_email):
    session = db_session.create_session()
    user = session.query(User).filter(User.email == user_email).first()
    if not user:
        abort_params = {
            'error': '404',
            'message': f"User {user_email} not found"
        }
        abort(404, **abort_params)


def abort_if_user_exists(user_email):
    """Bad request if user already exists"""
    session = db_session.create_session()
    user = session.query(User).filter(User.email == user_email).first()
    if user:
        abort_params = {
            'error': '400',
            'message': f"User {user_email} already exists"
        }
        abort(400, **abort_params)


class UsersResource(Resource):
    def get(self, user_email):
        abort_if_user_not_found(user_email)
        session = db_session.create_session()
        user = session.query(User).filter(User.email == user_email).first()
        return jsonify({'user': user.to_dict(only=(
            'id', 'name', 'about', 'balance', 'email'
        ))})

    def delete(self, user_email):
        abort_if_user_not_found(user_email)
        session = db_session.create_session()
        user = session.query(User).filter(User.email == user_email).first()
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})

    def put(self, user_email):
        abort_if_user_not_found(user_email)
        args = parser_put.parse_args()
        session = db_session.create_session()
        user = session.query(User).filter(User.email == user_email).first()
        if args['name']:
            user.name = args['name']
        if args['about']:
            user.about = args['about']
        if args['img']:
            user.img = args['img']
        session.commit()
        return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'users': [user.to_dict(only=(
            'id', 'name', 'about', 'balance', 'email'
        )) for user in users]})

    def post(self):
        args = parser_post.parse_args()
        abort_if_user_exists(args['email'])
        session = db_session.create_session()
        verify_code = session.query(VerifyCode).filter(VerifyCode.email == args['email']).first()
        if not verify_code:
            abort_params = {
                'error': '404',
                'message': f"Ask for verify_code at first"
            }
            abort(400, **abort_params)
        if not verify_code.check_verify_code(args['verify_code']):
            abort_params = {
                'error': '404',
                'message': f"Not valid verify_code"
            }
            abort(400, **abort_params)
        user = User(
            name=args['name'],
            email=args['email']
        )
        if args['img']:
            user.img = args['img']
        else:
            user.set_default_img()

        if args['about']:
            user.about = args['about']

        user.set_password(args['password'])
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK',
                        'id': user.id})
    