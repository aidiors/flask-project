from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


class AddRecipeForm(FlaskForm):
    recipe_title = StringField('Название рецепта', validators=[DataRequired(),
                                                               Length(min=3, max=75)])
    recipe_content = TextAreaField('Рецепт', validators=[DataRequired(), Length(min=10, max=20000)])
    submit = SubmitField('Добавить')
