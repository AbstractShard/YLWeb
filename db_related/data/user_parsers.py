from flask_restful import reqparse

parser_post = reqparse.RequestParser()
parser_post.add_argument('name', required=True)
parser_post.add_argument('about', required=False)
parser_post.add_argument('img', required=False)
parser_post.add_argument('email', required=True)
parser_post.add_argument('password', required=True)
parser_post.add_argument('verify_code', required=True)


parser_put = reqparse.RequestParser()
parser_put.add_argument('name', required=False)
parser_put.add_argument('about', required=False)
parser_put.add_argument('img', required=False)


parser_verify_code = reqparse.RequestParser()
parser_verify_code.add_argument('email', required=True)
parser_verify_code.add_argument('subject', required=True)
