# -*- coding: utf8 -*-

from flask import Flask, render_template, request
from data import db_session
from data.product import Products

app = Flask(__name__)
app.config['SECRET_KEY'] = 'OZERO_secret_key'


def main():
    db_session.global_init("db/shop.db")
    app.run()


@app.route('/')  # Главная
def index():
    db_sess = db_session.create_session()
    products = db_sess.query(Products).filter((Products.is_private != True))
    return render_template('index.html', products=products[:4], new=products[-4:])


@app.route('/info/<string:category>', methods=['GET', 'POST'])  # каталог
def info(category):
    db_sess = db_session.create_session()
    message = ''
    count = 0
    if category == 'all':
        products = db_sess.query(Products).filter((Products.is_private != True))
    elif category == 'inp_txt':
        if len(request.form['name']):
            products = db_sess.query(Products).filter(((Products.title.like(f"%{request.form['name'].lower()}%")) |
                                                       (Products.title.like(f"%{request.form['name'].upper()}%")) |
                                                       (Products.title.like(f"%{request.form['name'].capitalize()}%"))
                                                       | (Products.content.like(f"%{request.form['name'].upper()}%")) |
                                                       (Products.content.like(f"%{request.form['name'].capitalize()}%"))
                                                       | (Products.content.like(f"%{request.form['name'].lower()}%"))),
                                                      (Products.is_private != True))
        else:
            products = db_sess.query(Products).filter((Products.is_private != True))
    else:
        products = db_sess.query(Products).filter((Products.category.like(category.lower())
                                                   | (Products.category.like(category.upper()))
                                                   | (Products.category.like(category.capitalize()))),
                                                  (Products.is_private != True))
    for _ in products:
        count += 1
    if count == 0:
        message = 'Товары не найдены'
    return render_template("info.html", products=products, message=message)


if __name__ == '__main__':
    main()
