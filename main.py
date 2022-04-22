from flask import Flask
from flask import render_template, redirect, request, abort, escape
from data import db_session
from data.users import User
from data.recipes import Recipe
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
import users_resource
import recipes_resource
from flask_restful import Api
from forms.login import LoginForm
from forms.register import RegisterForm
from forms.edit_recipe import EditRecipeForm
from forms.add_recipe import AddRecipeForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

db_session.global_init("recipe.db")

api = Api(app)
api.add_resource(users_resource.UsersListResource, '/api/users')
api.add_resource(users_resource.UserResource, '/api/user/<int:user_id>')
api.add_resource(recipes_resource.RecipesListResource, '/api/recipes')
api.add_resource(recipes_resource.RecipeResource, '/api/recipe/<int:recipe_id>')

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def home():
    db_sess = db_session.create_session()
    recipes = []
    for recipe in db_sess.query(Recipe).all():
        recipes.append({"author_name": recipe.author.name,
                        "recipe_title": recipe.recipe_title,
                        "recipe_id": recipe.id})
    return render_template('home.html', css_file="home.css", recipes=recipes)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', css_file="login.css",
                               message="Неправильный логин или пароль", form=form)
    return render_template('login.html', css_file="login.css", form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', form=form, css_file="register.css",
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', form=form, css_file="register.css",
                                   message="Такой пользователь уже есть")
        user = User()
        user.name = form.name.data
        user.email = form.email.data
        user.about = form.about.data
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()

        return redirect('/login')
    return render_template('register.html', css_file="register.css", form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/admin_panel')
@login_required
def admin_panel():
    if current_user.rights:
        db_sess = db_session.create_session()
        recipes = []
        for recipe in db_sess.query(Recipe).all():
            recipes.append({"author_name": recipe.author.name,
                            "recipe_title": recipe.recipe_title,
                            "creation_date": str(recipe.creation_date).split()[0],
                            "recipe_id": recipe.id})
        return render_template('admin_panel.html', css_file="admin_panel.css", recipes=recipes)
    else:
        abort(403)


@app.route('/recipe/<int:recipe_id>')
def view_recipe(recipe_id):
    db_sess = db_session.create_session()
    recipe = db_sess.query(Recipe).filter(Recipe.id == recipe_id).first()
    if recipe:
        recipe_data = {"author_name": recipe.author.name,
                       "recipe_title": recipe.recipe_title,
                       "recipe_content": recipe.recipe_content.split("\n"),
                       "creation_date": str(recipe.creation_date).split()[0],
                       "recipe_id": recipe.id}
        return render_template('recipe_view.html', css_file="recipe_view.css",
                               recipe_data=recipe_data)
    else:
        abort(404)


@app.route('/my_recipes')
@login_required
def view_my_recipes():
    db_sess = db_session.create_session()
    recipes = []
    for recipe in db_sess.query(Recipe).filter(Recipe.author_id == current_user.id).all():
        recipes.append({"author_name": recipe.author.name,
                        "recipe_title": recipe.recipe_title,
                        "creation_date": str(recipe.creation_date).split()[0],
                        "recipe_id": recipe.id})
    return render_template('my_recipes.html', css_file="my_recipes.css", recipes=recipes)


@app.route('/add_recipe', methods=['GET', 'POST'])
@login_required
def add_recipe():
    form = AddRecipeForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        recipe = Recipe()
        recipe.author_id = current_user.id
        recipe.recipe_title = form.recipe_title.data
        recipe.recipe_content = form.recipe_content.data

        db_sess.add(recipe)
        db_sess.commit()
        return redirect('/')
    return render_template('add_recipe.html', css_file="add_recipes.css", form=form)


@app.route('/edit_recipe/<int:recipe_id>', methods=['GET', 'POST'])
@login_required
def edit_recipe(recipe_id):
    form = EditRecipeForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        recipe = db_sess.query(Recipe).filter(Recipe.id == recipe_id, (
                (Recipe.author_id == current_user.id) | current_user.rights)).first()
        if recipe:
            form.recipe_title.data = recipe.recipe_title
            form.recipe_content.data = recipe.recipe_content
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        recipe = db_sess.query(Recipe).filter(Recipe.id == recipe_id, (
                (Recipe.author_id == current_user.id) | current_user.rights)).first()
        if recipe:
            recipe.recipe_title = form.recipe_title.data
            recipe.recipe_content = form.recipe_content.data
        db_sess.commit()
        return redirect('/my_recipes')
    return render_template('edit_recipe.html', css_file="edit_recipe.css", form=form)


@app.route('/delete_recipe/<int:recipe_id>', methods=['GET', 'POST'])
@login_required
def delete_recipe(recipe_id):
    db_sess = db_session.create_session()
    recipe = db_sess.query(Recipe).filter(Recipe.id == recipe_id, (
            (Recipe.author_id == current_user.id) | current_user.rights)).first()
    if recipe:
        db_sess.delete(recipe)
        db_sess.commit()
    return redirect('/my_recipes')


if __name__ == '__main__':
    app.run(port=5000, host='127.0.0.1')
