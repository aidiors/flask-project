from flask_restful import reqparse, abort, Resource
from flask import jsonify
from data.recipes import Recipe
from data import db_session

add_parser = reqparse.RequestParser()
add_parser.add_argument('recipe_title', required=True)
add_parser.add_argument('recipe_content', required=True)
add_parser.add_argument('author_id', required=True, type=int)

edit_parser = reqparse.RequestParser()
edit_parser.add_argument('recipe_title')
edit_parser.add_argument('recipe_content')


def abort_if_job_not_found(recipe_id):
    session = db_session.create_session()
    recipe = session.query(Recipe).get(recipe_id)
    if not recipe:
        abort(404, message=f"Recipe {recipe_id} not found")


class RecipeResource(Resource):
    def get(self, recipe_id):
        abort_if_job_not_found(recipe_id)
        session = db_session.create_session()
        recipe = session.query(Recipe).get(recipe_id)
        return jsonify(
            {'recipe': recipe.to_dict(only=('recipe_title', 'recipe_content', 'author.name'))})

    def delete(self, recipe_id):
        abort_if_job_not_found(recipe_id)
        session = db_session.create_session()
        recipe = session.query(Recipe).get(recipe_id)
        session.delete(recipe)
        session.commit()
        return jsonify({'success': 'OK'})

    def put(self, recipe_id):
        args = edit_parser.parse_args()
        abort_if_job_not_found(recipe_id)
        session = db_session.create_session()
        recipe = session.query(Recipe).get(recipe_id)
        if args.get('recipe_title'):
            recipe.recipe_title = args['recipe_title']
        if args.get('recipe_content'):
            recipe.recipe_content = args['recipe_content']
        session.commit()
        return jsonify({'success': 'OK'})


class RecipesListResource(Resource):
    def get(self):
        session = db_session.create_session()
        recipes = session.query(Recipe).all()
        return jsonify({'recipes': [recipe.to_dict(only=('recipe_title', 'recipe_content',
                                                         'author.name')) for recipe in recipes]})

    def post(self):
        args = add_parser.parse_args()
        session = db_session.create_session()
        recipe = Recipe()
        recipe.recipe_title = args['recipe_title']
        recipe.recipe_content = args['recipe_content']
        recipe.author_id = args['author_id']
        session.add(recipe)
        session.commit()
        return jsonify({'success': 'OK'})
