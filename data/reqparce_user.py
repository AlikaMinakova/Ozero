from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument('surname', required=True)
parser.add_argument('name', required=True)
parser.add_argument('phone', required=True)
parser.add_argument('address', required=True)
parser.add_argument('email', required=True)