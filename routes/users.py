from flask import Blueprint, request, jsonify
from database.db import db, cursor
from werkzeug.security import check_password_hash
import jwt, datetime
from config import SECRET_KEY  # Import your app's secret key


users_blueprint = Blueprint("users", __name__)


@users_blueprint.route("/auth/login", methods=["POST"])
def login():
    if request.content_type == "application/json":
        try:
            Email = request.json["email"]
            password = request.json["password"]
        except KeyError:
            return jsonify({"msg": "Missing required fields"}), 400
        
        cursor.execute("SELECT * FROM Users WHERE Email = %s", (Email,))
        data_from_database = cursor.fetchone()
        
        if data_from_database and check_password_hash(data_from_database[5], password):
            token = jwt.encode(
                {
                    "name": data_from_database[3],
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=3600)
                },
                SECRET_KEY
            )
            return jsonify({"Token": token}), 200
        else:
            # Catch brute-force attack or invalid credentials
            return jsonify({"msg": "Invalid username or password"}), 401
    else:
        return jsonify({"msg": "Content-type should be JSON"}), 500


@users_blueprint.route("/create", methods=["POST"])
def add_user():
    if request.content_type == "application/json":
        data = request.json
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        email = data.get("email")
        password = data.get("password")
        
        try:
            cursor.execute(
                "INSERT INTO Users (FirstName, LastName, Email, Password) VALUES (%s, %s, %s, %s)",
                (first_name, last_name, email, password)
            )
            db.commit()
            return jsonify({"msg": "User created successfully"}), 201
        except Exception as e:
            return jsonify({"msg": "Error creating user", "error": str(e)}), 500
    return jsonify({"msg": "Content type must be application/json"}), 415


@users_blueprint.route('/get', methods=['GET'])
def get_users():
    conn = db
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users")
    users = cursor.fetchall()
    return jsonify(users), 200



