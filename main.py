# -*- coding: utf8 -*-

from flask import Flask, render_template
from data import db_session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'OZERO_secret_key'


def main():
    app.run()


@app.route('/')  # Главная
def index():
    return render_template('base.html')


if __name__ == '__main__':
    main()
