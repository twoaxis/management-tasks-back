from flask import Blueprint, request, jsonify
import jwt, datetime
from werkzeug.security import check_password_hash
from config import Config
from db import cursor

auth_blueprint = Blueprint("auth", __name__)

@auth_blueprint.route("/login", methods=["POST"])
def login():
    if request.content_type == "application/json":
        try:
            Email = request.json["email"]
            password = request.json["password"]
        except KeyError:
            return jsonify({"msg": "Missing required fields"}), 400

        cursor.execute("SELECT * FROM Users WHERE Email = %s", (Email,))
        data_from_database = cursor.fetchone()
        if data_from_database and check_password_hash(data_from_database[6], password):
            token = jwt.encode(
                {"name": data_from_database[1], "exp": 
datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
                Config.SECRET_KEY,
                algorithm="HS256",
            )
            return jsonify({"Token": token}), 200
        else:
            return jsonify({"msg": "Invalid username or password"}), 401
    else:
        return jsonify({"msg": "Content-type should be json"}), 500

