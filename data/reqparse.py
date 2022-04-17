from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument('title', required=True)
parser.add_argument('content', required=True)
parser.add_argument('is_private', required=True, type=bool)
parser.add_argument('user_id', required=True, type=int)
parser.add_argument('price', required=True, type=int)
parser.add_argument('url_img', required=True)
parser.add_argument('category', required=True)