from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from db import cursor , connection
from utils import jwt_required, get_priority_by_role
import jwt
from config import Config


user_blueprint = Blueprint("user", __name__)

@user_blueprint.route("/create", methods=["POST"])
@jwt_required
def create_user():
    if request.content_type == "application/json":
        try:
            Name = request.json["name"]
            Email = request.json["email"]
            password = request.json["password"]
            Role = request.json["role"]
            Prefix = request.json["prefix"]
        except KeyError:
            return jsonify({"msg": "Missing required fields"}), 400

        cursor.execute("SELECT * FROM Users WHERE Email = %s OR Name = %s", (Email, Name))
        is_acc_exists = cursor.fetchone()
        if is_acc_exists:
            return jsonify({"msg": "Choose Another Email OR Name"}), 400

        token = request.headers.get("Authorization")
        username = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])["name"]
        cursor.execute("SELECT Priority FROM Users WHERE Name = %s", (username,))
        user_priority = cursor.fetchone()

        if user_priority is None or user_priority[0] != 7:
            return jsonify({"msg": "You are not the admin, you cannot create an account"}), 403

        cursor.execute("SELECT UserID FROM Users WHERE Name = %s", (username,))
        parent_id = cursor.fetchone()
        parent_id = parent_id[0] if parent_id else None

        Priority = get_priority_by_role(Role)
        if Priority == "Bad_Choose":
            return jsonify({"msg": "Invalid Role"}), 400

        cursor.execute(
            "INSERT INTO Users (Name, Role, Prefix, ParentID, Email, Password, Priority) VALUES (%s, %s, %s, %s, %s, %s, %s)",(Name, Role, Prefix, parent_id, Email, generate_password_hash(password), Priority))
        connection.commit()

        return jsonify({"msg": "Account created successfully"}), 200
    else:
        return jsonify({"msg": "Content-type should be json"}), 500

