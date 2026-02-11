import psycopg2
from psycopg2 import errors
import psycopg2.extras
from flask import Blueprint,request, jsonify, g

from utils.geocoding import geocode_adress
from db.db_helpers import get_db_connection
from middleware.auth_middleware import token_required
from main import upload_image


workshops_blueprint = Blueprint('workshops_blueprint', __name__)


@workshops_blueprint.route('/workshops/', methods=["POST"])
@token_required
def create_workshops():
    connection = None
    cursor = None
    try:
        image = request.files.get("image")

        image_url = None
        if image:
            image_url = upload_image(image)
        
        title = request.form.get("title")
        description = request.form.get("description")
        art_type = request.form.get("art_type")
        level = request.form.get("level")

        workshop_date = request.form.get("workshop_date")
        start_time = request.form.get("start_time")
        duration_hours = request.form.get("duration_hours")

        address = request.form.get("address")
        city = request.form.get("city")
        state = request.form.get("state")

        latitude, longitude =  geocode_adress(address,city,state)

        max_capacity = request.form.get("max_capacity")
        materials_included = request.form.get("materials_included")
        materials_to_bring = request.form.get("materials_to_bring")

        required_fields = {
            "title": title,
            "description": description,
            "art_type": art_type,
            "level": level,
            "workshop_date": workshop_date,
            "start_time": start_time,
            "duration_hours": duration_hours,
            "address": address,
            "city": city,
            "state": state,
            "max_capacity": max_capacity
        }

        missing_fields = [field for field, value in required_fields.items() if not value]

        if missing_fields:
            return jsonify({
                "err": "Missing required fields",
                "fields": missing_fields
            }), 400

        user_id = g.user["id"]
        connection = get_db_connection()

        cursor = connection.cursor( 
            cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute(""" INSERT INTO workshops(user_id, title, description, art_type, level, workshop_date, start_time, duration_hours, address, city, state, latitude, longitude, max_capacity, materials_included, materials_to_bring, image_url) 
                        VALUES(%s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        RETURNING id
                        """,
                        (user_id, title, description, art_type, level, workshop_date, start_time, int(duration_hours), address, city, state,latitude, longitude, int(max_capacity), materials_included, materials_to_bring, image_url )
                        )

        workshops_id = cursor.fetchone()["id"]

        cursor.execute(""" SELECT workshops.id, workshops.title, workshops.description, workshops.art_type, 
                       workshops.level, workshops.workshop_date, workshops.start_time, workshops.duration_hours, 
                       workshops.address, workshops.city, workshops.state,workshops.latitude, workshops.longitude, workshops.max_capacity, workshops.materials_included, 
                       workshops.materials_to_bring, workshops.image_url, users.username AS instructor_username
                       FROM workshops
                       JOIN users ON workshops.user_id = users.id
                       WHERE  workshops.id = %s               
                       """, (workshops_id,) )
        
        created_workshop = cursor.fetchone()
        connection.commit()
        if created_workshop.get("workshop_date"):
            created_workshop["workshop_date"] = created_workshop["workshop_date"].isoformat()

        if created_workshop.get("start_time"):
            created_workshop["start_time"] = created_workshop["start_time"].strftime("%H:%M")

        return jsonify(created_workshop),201
    
    except errors.UniqueViolation:
        return jsonify({"err":"You are already registered for this workshop"}), 409
    
    except Exception as err:
        return jsonify({"err": str(err)}), 500
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()




@workshops_blueprint.route('/workshops/', methods=["GET"])
@token_required
def get_workshops():
    connection = None
    cursor = None
    try:
        connection=get_db_connection()
        cursor = connection.cursor( 
            cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute("""SELECT workshops.id, workshops.title, workshops.description, workshops.art_type, 
                       workshops.level, workshops.workshop_date, workshops.start_time, workshops.duration_hours, 
                       workshops.address, workshops.city, workshops.state,workshops.latitude, workshops.longitude, workshops.max_capacity, workshops.materials_included, 
                       workshops.materials_to_bring, workshops.image_url,workshops.current_registrations, users.username AS instructor_username
                       FROM workshops
                       JOIN users ON workshops.user_id = users.id """,)
        
        workshops = cursor.fetchall()

        for workshop in workshops:
            if workshop.get("workshop_date"):
                workshop["workshop_date"] = workshop["workshop_date"].isoformat()

            if workshop.get("start_time"):
                workshop["start_time"] = workshop["start_time"].strftime("%H:%M")


        return jsonify(workshops),200
    
    except Exception as err:
        return jsonify({"err": str(err)}), 500
    
    finally:
        if cursor:
            connection.close()
        if connection:
            connection.close()


@workshops_blueprint.route('/workshops/<workshop_id>', methods=["GET"])
@token_required
def get_workshop(workshop_id):
    connection = None
    cursor= None
    try:
        connection= get_db_connection()
        cursor = connection.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute(""" SELECT workshops.id, workshops.title, workshops.description, workshops.art_type, 
                       workshops.level, workshops.workshop_date, workshops.start_time, workshops.duration_hours, 
                       workshops.address, workshops.city, workshops.state,workshops.latitude, workshops.longitude, workshops.max_capacity, workshops.materials_included, 
                       workshops.materials_to_bring, workshops.image_url,workshops.current_registrations, users.username AS instructor_username
                       FROM workshops
                       JOIN users ON workshops.user_id = users.id
                       WHERE workshops.id = %s """,(workshop_id))
        
        workshop = cursor.fetchone()
        if workshop.get("workshop_date"):
                workshop["workshop_date"] = workshop["workshop_date"].isoformat()

        if workshop.get("start_time"):
                workshop["start_time"] = workshop["start_time"].strftime("%H:%M")

        return jsonify(workshop),200

    except Exception as err:
        return jsonify({"err": str(err)}),500
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()



@workshops_blueprint.route('/workshops/<workshop_id>', methods=['PUT'])
@token_required
def update_workshop(workshop_id):
    connection =None
    cursor = None
    try:
        image = request.files.get("image")

        image_url = None
        if image:
            image_url = upload_image(image)
        
        title = request.form.get("title")
        description = request.form.get("description")
        art_type = request.form.get("art_type")
        level = request.form.get("level")

        workshop_date = request.form.get("workshop_date")
        start_time = request.form.get("start_time")
        duration_hours = request.form.get("duration_hours")

        address = request.form.get("address")
        city = request.form.get("city")
        state = request.form.get("state")

        latitude, longitude =  geocode_adress(address,city,state)

        max_capacity = request.form.get("max_capacity")
        materials_included = request.form.get("materials_included")
        materials_to_bring = request.form.get("materials_to_bring")

        required_fields = {
            "title": title,
            "description": description,
            "art_type": art_type,
            "level": level,
            "workshop_date": workshop_date,
            "start_time": start_time,
            "duration_hours": duration_hours,
            "address": address,
            "city": city,
            "state": state,
            "max_capacity": max_capacity
        }

        missing_fields = [field for field, value in required_fields.items() if not value]

        if missing_fields:
            return jsonify({
                "err": "Missing required fields",
                "fields": missing_fields
            }), 400
        latitude, longitude = geocode_adress(address, city, state)

        connection = get_db_connection()

        cursor = connection.cursor(
            cursor_factory= psycopg2.extras.RealDictCursor)
        
        cursor.execute(""" SELECT * FROM workshops WHERE workshops.id = %s""", (workshop_id,))

        workshop_to_update = cursor.fetchone()

        if workshop_to_update is None:
            return jsonify({"err":"Workshop not found"}),404
        
        if workshop_to_update["user_id"] != g.user["id"]:
            return jsonify({"err":"Unauthorized"}), 401
        
        final_image_url = image_url if image_url else workshop_to_update.get(
            "image_url")
        
        cursor.execute(""" UPDATE workshops SET title =%s, description =%s, art_type =%s, level =%s, workshop_date =%s, start_time =%s, duration_hours=%s, address =%s, city=%s, state =%s, latitude =%s, longitude=%s, max_capacity=%s, materials_included=%s, materials_to_bring=%s, image_url=%s
                       WHERE id =%s 
                        RETURNING id""",                        
                        ( title, description, art_type, level, workshop_date, start_time, int(duration_hours), address, city, state,latitude, longitude, int(max_capacity), materials_included, materials_to_bring, final_image_url, workshop_id )
                        )
        updated_id = cursor.fetchone()["id"]

        cursor.execute(""" SELECT workshops.id, workshops.title, workshops.description, workshops.art_type, 
                       workshops.level, workshops.workshop_date, workshops.start_time, workshops.duration_hours, 
                       workshops.address, workshops.city, workshops.state,workshops.latitude, workshops.longitude, workshops.max_capacity, workshops.materials_included, 
                       workshops.materials_to_bring, workshops.image_url, users.username AS instructor_username
                       FROM workshops
                       JOIN users ON workshops.user_id = users.id
                       WHERE  workshops.id = %s               
                       """, (updated_id,) )
        
        updated_workshop = cursor.fetchone()
        connection.commit()

        if updated_workshop.get("workshop_date"):
            updated_workshop["workshop_date"] = updated_workshop["workshop_date"].isoformat()

        if updated_workshop.get("start_time"):
            updated_workshop["start_time"] = updated_workshop["start_time"].strftime("%H:%M")

        return jsonify(updated_workshop), 200
    
    except Exception as err:

        return jsonify({"err": str(err)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@workshops_blueprint.route('/workshops/<workshop_id>', methods=['DELETE'])
@token_required
def delete_workshop(workshop_id):
    
    connection = None
    cursor= None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(
            cursor_factory= psycopg2.extras.RealDictCursor)
        
        cursor.execute("SELECT * FROM workshops where workshops.id = %s", (workshop_id,))

        workshop_to_delete = cursor.fetchone()

        if workshop_to_delete is None:
            return jsonify({"err": "Workshop not found"}),404
        
        if workshop_to_delete["user_id"] is not g.user["id"]:
            return jsonify({"error":"Unauthorized"}),401
        
        cursor.execute("DELETE FROM workshops WHERE workshops.id = %s",(workshop_id,))

        connection.commit()

        return jsonify({"message": "Workshop successfully removed"}), 200
    
    except Exception as err:
        return jsonify({"err": str(err)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()





@workshops_blueprint.route('/workshops/<workshop_id>/registrations', methods=["POST"])
@token_required
def add_registration(workshop_id):
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor= connection.cursor(
            cursor_factory= psycopg2.extras.RealDictCursor)

        user_id = g.user["id"]

        cursor.execute("""SELECT id, max_capacity, current_registrations FROM workshops WHERE workshops.id = %s FOR UPDATE""", (workshop_id,))
        workshop_to_register= cursor.fetchone()
        

        if workshop_to_register is None:
            return jsonify({"err:", "Workshop not found"}),404                


        if workshop_to_register["current_registrations"] >= workshop_to_register["max_capacity"]:
            return jsonify({"err": "Workshop is full"}), 409


        cursor.execute(""" INSERT INTO registrations(user_id, workshop_id)
                       VALUES (%s,%s )
                       RETURNING *
                       """,(user_id, workshop_id))
        
        registration = cursor.fetchone()

        cursor.execute(""" UPDATE workshops SET current_registrations = current_registrations +1, updated_at = CURRENT_TIMESTAMP
                       WHERE id =%s
                        """,(workshop_id))

        connection.commit()
        return jsonify(registration),201


    except errors.UniqueViolation:
        if connection:
            connection.rollback()
        return jsonify({"error": "You are already registered for this workshop"}), 409

    except Exception as err:
        return jsonify({"err": str(err)}),500
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()




@workshops_blueprint.route('/workshops/<workshop_id>/registrations', methods = ["PUT"])
@token_required
def cancel_registration(workshop_id):
    connection = None
    cursor= None
    try:
        connection= get_db_connection()

        cursor = connection.cursor(
            cursor_factory= psycopg2.extras.RealDictCursor)
        
        user_id = g.user["id"]
        
        cursor.execute(""" SELECT * FROM registrations 
                       WHERE user_id = %s AND workshop_id = %s
                       """, (user_id,workshop_id))

        registration_to_cancel = cursor.fetchone()

        if registration_to_cancel is None:
            return jsonify({"err": "Registration not found"}),404
        

        if registration_to_cancel["status"] == "cancelled":
            return jsonify({"message": "Registration already cancelled"}), 200
        
        
        cursor.execute("""UPDATE registrations SET status= 'cancelled', cancelled_at = CURRENT_TIMESTAMP
                       WHERE registrations.id =%s
                       RETURNING *
                       """, (registration_to_cancel["id"],))


        cursor.execute(""" UPDATE workshops SET current_registrations = current_registrations -1, updated_at = CURRENT_TIMESTAMP
                       WHERE id =%s
                       """,(workshop_id))

        connection.commit()
        return jsonify({"message": "Registration cancellation successful"}),200

    except Exception as err:
        return jsonify({"err":err}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@workshops_blueprint.route('/workshops/<workshop_id>/registrations', methods=["GET"])
@token_required
def get_registrations(workshop_id):
    connection = None
    cursor = None
    try:
        connection= get_db_connection()
        cursor = connection.cursor(
            cursor_factory= psycopg2.extras.RealDictCursor)
        
        user_id= g.user["id"]

        cursor.execute (""" SELECT role FROM users WHERE id=%s""", (user_id,))

        user = cursor.fetchone()

        if user is None:
            return jsonify({"error": "User not found"}), 404
        

        if user["role"] != "instructor":
            return jsonify({"err": "Access for instructors only"}), 403
        
        cursor.execute(""" SELECT user_id FROM workshops 
                       WHERE id = %s
                       """, (workshop_id,))

        workshop = cursor.fetchone()

        if workshop is None:
            return jsonify({"error": "Workshop not found"}), 404

        if workshop["user_id"] != user_id:
            return jsonify({"err": "Unauthorized"}), 403
        
        cursor.execute(""" SELECT registrations.id, registrations.user_id, registrations.status, registrations.registered_at , users.email, users.username, users.full_name 
                       FROM registrations
                       JOIN users ON users.id = registrations.user_id 
                       WHERE registrations.workshop_id = %s 
                       ORDER BY registrations.registered_at DESC
                       """, (workshop_id,))
        
        registrations = cursor.fetchall()

        return jsonify(registrations), 200

    except Exception as err:
        return jsonify({"err":err}),500
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
