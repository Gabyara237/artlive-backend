import os
import jwt
import psycopg2
import bcrypt
import psycopg2.extras
from flask import Blueprint,request, jsonify
from db.db_helpers import get_db_connection


auth_blueprint = Blueprint('auth_blueprint',__name__)

@auth_blueprint.route('/auth/sign-up', methods=['POST'])
def sign_up():
    try:
        new_user_data = request.get_json()
        connection = get_db_connection()
        cursor = connection.cursor(
            cursor_factory= psycopg2.extras.RealDictCursor)
        cursor.execute(" SELECT * FROM users WHERE username = %s ", (new_user_data["username"],))
        existing_username = cursor.fetchone()
        if existing_username:
            cursor.close()
            connection.close()
            return jsonify({"err":"Username already taken"}),409
        
        
        hashed_password = bcrypt.hashpw(
            bytes(new_user_data["password"], 'utf-8'), bcrypt.gensalt())
        
        cursor.execute("INSERT INTO users (username, password, role) VALUES (%s,%s, %s) RETURNING id, username, role", (new_user_data["username"], hashed_password.decode('utf-8'), new_user_data["role"]))
        create_user = cursor.fetchone()
        connection.commit()
        connection.close()

        payload ={
            "username": create_user["username"], 
            "id": create_user["id"], 
            "role": create_user["role"]
        }
        
        token = jwt.encode({"payload":payload}, os.getenv('JWT_SECRET'))
        return jsonify({"token":token}),201
    

    except Exception as err:
        return jsonify({"err": str(err)}),401
