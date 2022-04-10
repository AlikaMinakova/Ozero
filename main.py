# -*- coding: utf8 -*-

from flask import Flask, render_template
from flask_login import login_user, login_required, logout_user
from flask_restful import Api
from werkzeug.utils import redirect

from data import db_session
from data.loginform import LoginForm
from data.user import User
from forms.user import RegisterForm
from flask_login import LoginManager

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
    return render_template('base.html')


@app.route('/index')
def index2():
    db_sess = db_session.create_session()
    return render_template('index.html')


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


if __name__ == '__main__':
    main()
