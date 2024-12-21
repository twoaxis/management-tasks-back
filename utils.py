import jwt
from flask import request, jsonify
from config import Config
from functools import wraps
def jwt_required(func):
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error": "Missing token"}), 401
        try:
            decoded = jwt.decode(token, Config.SECRET_KEY,algorithms=["HS256"])
        except Exception as e:
            print(e)
            return jsonify({"error": "Invalid token"}), 401
        return func(*args, **kwargs)
    return wrapper


def get_priority_by_role(role):
    match role:
        case "JavaScript":
            return 6

        case "Python":
            return 5

        case "PHP":
            return 4

        case "Solidity":
            return 3

        case "Java":
            return 2
        case "hello":
            return 1
        case _:
            return "Bad_Choose"

