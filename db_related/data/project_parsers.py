from flask_restful import reqparse

parser_put = reqparse.RequestParser()
parser_put.add_argument("name", required=False, type=str)
parser_put.add_argument("description", required=False, type=str)
parser_put.add_argument("price", required=False, type=int)
parser_put.add_argument("created_by_user_id", required=False, type=int)
parser_put.add_argument("files", required=False, type=bytes)
parser_put.add_argument("imgs", required=False, type=bytes)


parser_post = reqparse.RequestParser()
parser_post.add_argument("name", required=True, type=str)
parser_post.add_argument("description", required=True, type=str)
parser_post.add_argument("price", required=True, type=int)
parser_post.add_argument("created_by_user_id", required=True, type=int)
parser_post.add_argument("files", required=True, type=bytes)
parser_post.add_argument("imgs", required=True, type=bytes)
