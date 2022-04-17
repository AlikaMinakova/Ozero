from flask import jsonify
from data import db_session
from flask_restful import abort, Resource
from .reqparce_user import parser
from .user import User


def abort_if_products_not_found(user_id):
    session = db_session.create_session()
    users = session.query(User).get(user_id)
    if not users:
        abort(404, message=f"User {user_id} not found")


class UsersResource(Resource):
    def get(self, user_id):
        abort_if_products_not_found(user_id)
        session = db_session.create_session()
        users = session.query(User).get(user_id)
        return jsonify({'users': users.to_dict(
            only=('name', 'surname', 'email', 'phone', 'address'))})

    def delete(self, user_id):
        abort_if_products_not_found(user_id)
        session = db_session.create_session()
        users = session.query(User).get(user_id)
        session.delete(users)
        session.commit()
        return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'users': [item.to_dict(
            only=('id', 'name', 'surname')) for item in users]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        users = User(
            name=args['name'],
            surname=args['surname'],
            email=args['email'],
            phone=args['phone'],
            address=args['address'],
        )
        session.add(users)
        session.commit()
        return jsonify({'success': 'OK'})
