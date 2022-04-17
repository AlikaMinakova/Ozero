from flask import jsonify

from data import db_session
from .product import Products
from flask_restful import Resource, abort
from .reqparse import parser


def abort_if_products_not_found(products_id):
    session = db_session.create_session()
    products = session.query(Products).get(products_id)
    if not products:
        abort(404, message=f"Product {products_id} not found")


class ProductsResource(Resource):
    def get(self, products_id):
        abort_if_products_not_found(products_id)
        session = db_session.create_session()
        products = session.query(Products).get(products_id)
        return jsonify({'products': products.to_dict(
            only=('title', 'content', 'user_id', 'is_private', 'price', 'category'))})

    def delete(self, products_id):
        abort_if_products_not_found(products_id)
        session = db_session.create_session()
        products = session.query(Products).get(products_id)
        session.delete(products)
        session.commit()
        return jsonify({'success': 'OK'})


class ProductsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        products = session.query(Products).all()
        return jsonify({'products': [item.to_dict(
            only=('id', 'title')) for item in products]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        products = Products(
            title=args['title'],
            content=args['content'],
            user_id=args['user_id'],
            is_private=args['is_private'],
            price=args['price'],
            url_img=args['url_img'],
            category=args['category']
        )
        session.add(products)
        session.commit()
        return jsonify({'success': 'OK'})


