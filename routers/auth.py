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
    connection = None
    cursor = None
    try:
        new_user_data = request.get_json()
        connection = get_db_connection()
        cursor = connection.cursor(
            cursor_factory= psycopg2.extras.RealDictCursor)
        cursor.execute(" SELECT * FROM users WHERE username = %s ", (new_user_data["username"],))
        existing_username = cursor.fetchone()
        if existing_username:
            return jsonify({"err":"Username already taken"}),409
        
        cursor.execute(" SELECT * FROM users WHERE email = %s ", (new_user_data["email"],))
        existing_email = cursor.fetchone()

        if existing_email:
            return jsonify({"err": "Email alredy taken"}),409

        hashed_password = bcrypt.hashpw(
            bytes(new_user_data["password"], 'utf-8'), bcrypt.gensalt())
        
        cursor.execute("INSERT INTO users (username, email, password, role) VALUES (%s,%s, %s, %s) RETURNING id, username, role", (new_user_data["username"],new_user_data["email"], hashed_password.decode('utf-8'), new_user_data["role"]))
        create_user = cursor.fetchone()
        connection.commit()

        payload ={
            "username": create_user["username"], 
            "id": create_user["id"], 
            "role": create_user["role"]
        }
        
        token = jwt.encode({"payload":payload}, os.getenv('JWT_SECRET'))
        return jsonify({"token":token}),201
    
    except Exception as err:
        return jsonify({"err": str(err)}),401
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@auth_blueprint.route('/auth/sign-in', methods=["POST"])
def sign_in():

    connection = None
    cursor = None
    try:
        user_data = request.get_json()
        connection = get_db_connection()
        cursor = connection.cursor( cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("SELECT * FROM users WHERE username = %s ;", (user_data["username"],))

        existing_user= cursor.fetchone()
        if existing_user is None:
            return jsonify({"err": "Invalid credentials."}), 401
        password_is_valid = bcrypt.checkpw( bytes(user_data["password"], 'utf-8'), bytes(existing_user["password"], 'utf-8'))
        
        if not password_is_valid:
            return jsonify({"err": "Invalid credentials"}),401
        
        payload ={
            "username": existing_user["username"], 
            "id": existing_user["id"]
        }

        token = jwt.encode({"payload": payload}, os.getenv('JWT_SECRET'))


        return jsonify({"token": token}), 200
    
    except Exception as err:
        return jsonify({"err": str(err)}),401
    
    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()