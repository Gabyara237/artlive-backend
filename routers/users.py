import psycopg2
from psycopg2 import errors
import psycopg2.extras
from flask import Blueprint, jsonify, g
from db.db_helpers import get_db_connection
from middleware.auth_middleware import token_required
from middleware.role_middleware import instructor_required


users_blueprint = Blueprint('users_blueprint', __name__)

@users_blueprint.route('/users/me/registrations', methods=["GET"])
@token_required
def get_my_registrations():
    connection= None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor)
        
        user_id = g.user["id"]

        cursor.execute("""
            SELECT registrations.id AS registration_id, registrations.status,registrations.registered_at,registrations.cancelled_at,workshops.id AS workshop_id,
                workshops.title,workshops.art_type,workshops.level,workshops.workshop_date,workshops.start_time, workshops.duration_hours,workshops.image_url,
                workshops.address,workshops.city,workshops.state
            FROM registrations 
            JOIN workshops ON workshops.id = registrations.workshop_id
            WHERE registrations.user_id = %s
            ORDER BY workshops.workshop_date ASC, workshops.start_time ASC;
        """, (user_id,))

        registrations = cursor.fetchall()

        for registration in registrations:
            
            if registration.get("workshop_date"):
                registration["workshop_date"] = registration["workshop_date"].isoformat()

            if registration.get("start_time"):
                registration["start_time"] = registration["start_time"].strftime("%H:%M")

            if registration.get("registered_at"):
                registration["registered_at"] = registration["registered_at"].isoformat()

            if registration.get("cancelled_at"):
                registration["cancelled_at"] = registration["cancelled_at"].isoformat()


        return jsonify({"registrations": registrations}), 200

    except Exception as err:
        return jsonify({"err": str(err)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()



@users_blueprint.route('/users/me/workshops', methods=["GET"])
@token_required
@instructor_required
def get_my_workshops():
    connection= None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor)
        
        user_id = g.user["id"]

        cursor.execute("""
            SELECT *
            FROM workshops
            WHERE user_id = %s
            ORDER BY workshop_date ASC, start_time ASC;
        """, (user_id,))

        workshops = cursor.fetchall()

        for workshop in workshops:
            
            if workshop.get("workshop_date"):
                workshop["workshop_date"] = workshop["workshop_date"].isoformat()

            if workshop.get("start_time"):
                workshop["start_time"] = workshop["start_time"].strftime("%H:%M")

            if workshop.get("registered_at"):
                workshop["registered_at"] = workshop["registered_at"].isoformat()

            if workshop.get("cancelled_at"):
                workshop["cancelled_at"] = workshop["cancelled_at"].isoformat()


        return jsonify({"workshops": workshops}), 200

    except Exception as err:
        return jsonify({"err": str(err)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@users_blueprint.route("/users/me/registrations/workshops/<workshop_id>", methods=["GET"])
@token_required
def get_my_registration_for_workshop(workshop_id):
    connection= None
    cursor= None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        user_id = g.user["id"]

        cursor.execute("""
            SELECT id, user_id, workshop_id, status, registered_at, cancelled_at
            FROM registrations
            WHERE user_id = %s AND workshop_id = %s
            ORDER BY registered_at DESC
            LIMIT 1;
        """, (user_id, workshop_id))

        registration = cursor.fetchone()

        return jsonify({"registration": registration}), 200

    except Exception as err:
        return jsonify({"err": str(err)}), 500
    finally:
        if cursor: cursor.close()
        if connection: connection.close()



