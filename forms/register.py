from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, EmailField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length


class RegisterForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired(), Length(min=3, max=20)])
    email = EmailField('Почта', validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6, max=30)])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired(),
                                                                   Length(min=6, max=30)])
    about = TextAreaField('О себе')
    submit = SubmitField('Зарегестрироваться')
