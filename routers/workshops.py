import os
import jwt
import psycopg2
import bcrypt
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

        connection.commit()
        for workshop in workshops:
            if workshop.get("workshop_date"):
                workshop["workshop_date"] = workshop["workshop_date"].isoformat()

            if workshop.get("start_time"):
                workshop["start_time"] = workshop["start_time"].strftime("%H:%M")


        return jsonify(workshops),200
    
    except Exception as err:
        return jsonify({"err": str(err)}), 500
    
    finally:
        if connection:
            connection.close()
        if cursor:
            connection.close()
