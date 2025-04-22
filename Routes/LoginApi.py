from flask import Blueprint, request, jsonify
from DBUtility.DataBase import Database

login_app = Blueprint('login', __name__)

# Create User
@login_app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    query = """
        INSERT INTO public.login (user_id, username, password)
        VALUES (%s, %s, %s) RETURNING user_id;
    """
    Database.execute_query(query, (data['user_id'], data['username'], data['password']), fetch=False)
    return jsonify({'message': 'User created successfully'}), 201


# Get All Users
@login_app.route('/users', methods=['GET'])
def get_users():
    query = "SELECT user_id, username FROM public.login;"
    users = Database.execute_query(query)
    return jsonify(users)


# User Authentication
@login_app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    query = "SELECT * FROM public.login WHERE username = %s AND password = %s;"
    user = Database.execute_query(query, (data['username'], data['password']))
    if user:
        return jsonify({'message': 'Routes successful', 'user': user})
    else:
        return jsonify({'message': 'Invalid credentials'}), 401
