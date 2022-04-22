from flask_restful import reqparse, abort, Resource
from flask import jsonify
from data.users import User
from data import db_session

parser = reqparse.RequestParser()
parser.add_argument('name', required=True)
parser.add_argument('email', required=True)
parser.add_argument('password', required=True)
parser.add_argument('rights', required=True)
parser.add_argument('about')


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")


class UserResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        return jsonify({'user': user.to_dict(only=('name', 'about', 'email', 'hashed_password',
                                                   'register_date', 'rights'))})

    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'users': [user.to_dict(
            only=('name', 'about', 'email', 'hashed_password', 'register_date', 'rights'))
            for user in users]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        user = User()
        user.name = args['name']
        user.email = args['email']
        user.set_password(args['password'])
        user.about = args['about']
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})
