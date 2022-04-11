import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Bag(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'bag'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id_bag = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    product_id_bag = sqlalchemy.Column(sqlalchemy.Integer,
                                       sqlalchemy.ForeignKey("products.id"))
    user_bag = orm.relation('User')
    product_bag = orm.relation('Products')