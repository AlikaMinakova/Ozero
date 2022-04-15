# -*- coding: utf8 -*-

import os

import requests
from flask_login import login_user, login_required, logout_user
from flask_restful import Api
from werkzeug.utils import redirect
from flask import Flask, render_template, request
from data.product import Products
from werkzeug.exceptions import abort

from data.bag import Bag

from data import db_session
from data.loginform import LoginForm
from data.user import User
from forms.products import ProductsForm
from forms.user import RegisterForm
from flask_login import LoginManager

from forms.user_set import SetForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'OZERO_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
api = Api(app)


@login_manager.user_loader  # функция для получения пользователя
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')  # мы «забываем» пользователя при помощи функции logout_user и перенаправляем его на главную страницу нашего приложения. Из интересного здесь — декоратор login_required (не забудьте это импортировать). Таким декоратором можно украшать обработчики страниц, на которые может попасть только авторизованный пользователь.
@login_required
def logout():
    logout_user()
    return redirect("/")


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


@app.route('/register', methods=['GET', 'POST'])  # регистрация
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            surname=form.surname.data,
            phone=form.phone.data,
            address=form.address.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])  # вход
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/product_info/<int:id>', methods=['GET', 'POST'])  # страница товара
def info_about_product(id):
    db_sess = db_session.create_session()
    product = db_sess.query(Products).filter(Products.id == id).first()
    same_product = db_sess.query(Products).filter((Products.category == product.category), (Products.id != id),
                                                  (Products.is_private != True))
    try:
        bag = db_sess.query(Bag).filter((Bag.user_id_bag == current_user.id),
                                        (Bag.product_id_bag == product.id)).first()
    except:
        bag = False
    try:
        geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={product.user.address}&format=json"  # Выполняем запрос.
        response = requests.get(geocoder_request)
        if response:  # Преобразуем ответ в json-объект
            json_response = response.json()  # Получаем первый топоним из ответа геокодера. # Согласно описанию ответа, он находится по следующему пути:
            toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0][
                "GeoObject"]  # Полный адрес топонима:
            toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]  # Координаты центра топонима:
            toponym_coodrinates = toponym["Point"]["pos"]  # Печатаем извлечённые из ответа поля:
            toponym_coodrinates = toponym_coodrinates.split()
    except:
        toponym_coodrinates = [37.617644, 55.755819]
    if bag:
        return render_template('info_about_product.html', products=product, same_product=same_product, have=True,
                               coor=toponym_coodrinates)
    return render_template('info_about_product.html', products=product, same_product=same_product, have=False,
                           coor=toponym_coodrinates)


@app.route('/account/<int:id>', methods=['GET', 'POST'])  # настройки аккаунта
@login_required
def edit_user(id):
    form = SetForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == id).first()
        if user:
            form.name.data = user.name
            form.surname.data = user.surname
            form.address.data = user.address
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == id).first()
        if user:
            user.name = form.name.data
            user.surname = form.surname.data
            user.address = form.address.data
            db_sess.commit()
            return redirect('/info/all')
        else:
            abort(404)
    return render_template('user_set.html',
                           form=form
                           )


@app.route('/account')  # Страница пользователя
def account():
    db_sess = db_session.create_session()
    products = db_sess.query(Products).filter(
        (Products.user == current_user), (Products.is_private != True))
    return render_template('name.html', products=products)


@app.route('/account_private')  # Страница пользователя с приватными записями
def account_private():
    db_sess = db_session.create_session()
    products = db_sess.query(Products).filter(
        (Products.user == current_user), (Products.is_private == True))
    return render_template('private.html', products=products)


@app.route('/user_prod/<int:id>', methods=['GET', 'POST'])  # Страница продавца
def user_prod(id):
    db_sess = db_session.create_session()
    products = db_sess.query(Products).filter(
        (Products.user_id == id), (Products.is_private != True))
    return render_template('seller.html', products=products)


@app.route('/add_product_bag/<int:user_id>/<int:product_id>')  # Добавление товара в корзину
def add_product_bag(user_id, product_id):
    db_sess = db_session.create_session()
    bag_bag = db_sess.query(Bag).filter((Bag.product_id_bag == product_id), (Bag.user_id_bag == user_id)).first()
    if not bag_bag:
        bag = Bag()
        bag.user_id_bag = user_id
        bag.product_id_bag = product_id
        db_sess.add(bag)
        db_sess.commit()
    db_sess = db_session.create_session()
    bag = db_sess.query(Bag).filter(
        (Bag.user_id_bag == user_id))
    return render_template('bag.html', bag=bag)


@app.route('/bag_delete/<int:id>', methods=['GET', 'POST'])  # Удаление товара из корзины
def bag_delete(id):
    db_sess = db_session.create_session()
    bag = db_sess.query(Bag).all()
    if bag:
        for item in bag:
            if item.id == id:
                db_sess.delete(item)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/info/all')


@app.route('/bag/<int:user_id>')  # Страница корзины
def bag(user_id):
    db_sess = db_session.create_session()
    bag = db_sess.query(Bag).filter(
        (Bag.user_id_bag == user_id))
    return render_template('bag.html', bag=bag)


@app.route('/products', methods=['GET', 'POST'])  # добавить товар
@login_required
def add_news():
    form = ProductsForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            products = Products()
            products.title = form.title.data
            products.content = form.content.data
            products.is_private = form.is_private.data
            products.price = form.price.data
            try:
                file1 = request.files['file1']
                path = os.path.join(app.config['UPLOAD_FOLDER'], file1.filename)
                file1.save(path)
                products.url_img = file1.filename
                products.category = form.category.data
                current_user.product.append(products)
                db_sess.merge(current_user)
                db_sess.commit()
                return redirect('/info/all')
            except:
                products.url_img = 'no_picture.png'
                products.category = form.category.data
                current_user.product.append(products)
                db_sess.merge(current_user)
                db_sess.commit()
                return redirect('/info/all')
    return render_template('products.html', title='Добавление товара',
                           form=form)


if __name__ == '__main__':
    main()
