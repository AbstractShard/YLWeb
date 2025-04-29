import random

import flask
from flask import jsonify
from flask_restful import abort, Resource

from . import db_session
from .verify_cods import VerifyCode, send_email
from .api_parsers import parser_verify_code

SUBJECTS = ['verify_email', 'change_password', 'forgot_password']


class VerifyCodeResource(Resource):
    def post(self):
        db_sess = db_session.create_session()
        args = parser_verify_code.parse_args()
        if args['subject'] not in SUBJECTS:
            abort_params = {
                'error': '404',
                'message': f"Not valid subject {args['subject']}. Possible subjects: [{', '.join(SUBJECTS)}]"
            }
            abort(400, **abort_params)

        verify_code = db_sess.query(VerifyCode).filter(args['email'] == VerifyCode.email).first()
        verify_code_generated = str(random.randint(10000000000000000000000,
                                                   99999999999999999999999))
        if not verify_code:
            verify_code = VerifyCode(
                email=args['email'],
                subject=args['subject']
            )
            verify_code.set_verify_code(verify_code_generated)
            db_sess.add(verify_code)
        else:
            verify_code.set_verify_code(verify_code_generated)
            verify_code.update(args['subject'])

        db_sess.commit()

        send_email(args['email'], args['subject'], verify_code_generated)
        print(verify_code_generated)
        return jsonify({"success": 'OK'})


