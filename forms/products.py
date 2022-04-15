from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField
from wtforms import BooleanField, SubmitField, IntegerField, FileField
from wtforms.validators import DataRequired


class ProductsForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    is_private = BooleanField("Личное")
    category = SelectField('Категория', choices=['Транспорт', 'Продукты', 'Одежда', 'Электроника', 'Недвижимость',
                                                 'Вакансии', 'Хобби', 'Техника', 'Другое'])
    url_image = FileField('Выберите фото')
    price = IntegerField("Цена")
    submit = SubmitField('Применить')