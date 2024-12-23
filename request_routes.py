from flask import Blueprint, request, jsonify
from db import connection, cursor

requests_blueprint = Blueprint('requests', __name__)

@requests_blueprint.route("/create", methods=["POST"])
def create_request():
    if request.content_type == "application/json":
        data = request.json
        request_description = data.get("request_description")
        sent_by = data.get("sent_by")
        sent_to = data.get("sent_to")

        if not request_description:
            return jsonify({"msg": "Request description is required"}), 400
        if not sent_by:
            return jsonify({"msg": "SentBy (user ID) is required"}), 400
        if not sent_to:
            return jsonify({"msg": "SentTo (user ID) is required"}), 400

        try:
            cursor.execute("SELECT COUNT(*) FROM Users WHERE UserID = %s", (sent_by,))
            
            if cursor.fetchone()[0] == 0:
                return jsonify({"msg": "SentBy does not exist"}), 400

            cursor.execute("SELECT COUNT(*) FROM Users WHERE UserID = %s", (sent_to,))

            if cursor.fetchone()[0] == 0:
                return jsonify({"msg": "SentTo does not exist"}), 400

            cursor.execute(
                """
                INSERT INTO Requests (RequestDescription, SentBy, SentTo, Status, RequestDate)
                VALUES (%s, %s, %s, %s, NOW())
                """,
                (request_description, sent_by, sent_to, "Pending")
            )
            connection.commit()

            return jsonify({"msg": "Request created successfully"}), 201

        except Exception as e:
            return jsonify({"msg": "An error occurred while creating the request"}), 500
        
    return jsonify({"msg": "Content type must be application/json"}), 415


@requests_blueprint.route("/", methods=["GET"])
def get_all_requests():
    try:
        cursor.execute("SELECT * FROM Requests")
        requests = cursor.fetchall()

        return jsonify(requests), 200
    
    except Exception as e:
        return jsonify({"msg": "Error retrieving requests", "error": str(e)}), 500


@requests_blueprint.route("/<int:request_id>", methods=["GET"])
def get_request_by_id(request_id):
    try:
        cursor.execute("SELECT * FROM Requests WHERE RequestID = %s", (request_id,))
        request_data = cursor.fetchone()

        if not request_data:
            return jsonify({"msg": "Request not found"}), 404
        
        return jsonify(request_data), 200
    
    except Exception as e:
        return jsonify({"msg": "Error retrieving request", "error": str(e)}), 500


@requests_blueprint.route("/<int:request_id>", methods=["PUT"])
def update_request(request_id):
    if request.content_type == "application/json":
        data = request.json
        
        if "status" in data and data["status"] not in ["Pending", "Approved", "Rejected"]:
            return jsonify({"msg": "Invalid status"}), 400

        updatable_columns = ["RequestDescription", "SentBy", "SentTo", "Status"]
        updates = {key: value for key, value in data.items() if key in updatable_columns}

        if not updates:
            return jsonify({"msg": "No valid fields to update"}), 400

        set_clause = ", ".join([f"{col} = %s" for col in updates.keys()])
        values = list(updates.values())
        values.append(request_id)

        query = f"UPDATE Requests SET {set_clause} WHERE RequestID = %s"

        try:
            cursor.execute(query, values)
            connection.commit()

            if cursor.rowcount == 0:
                return jsonify({"msg": "Request not found"}), 404
            
            return jsonify({"msg": "Request updated successfully"}), 200
        
        except Exception as e:
            return jsonify({"msg": "Error updating request", "error": str(e)}), 500

    return jsonify({"msg": "Content type must be application/json"}), 415


@requests_blueprint.route("/<int:request_id>", methods=["DELETE"])
def delete_request(request_id):
    try:
        cursor.execute("DELETE FROM Requests WHERE RequestID = %s", (request_id,))
        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"msg": "Request not found"}), 404
        
        return jsonify({"msg": "Request deleted successfully"}), 200
    
    except Exception as e:
        return jsonify({"msg": "Error deleting request", "error": str(e)}), 500


@requests_blueprint.route("/assign", methods=["POST"])
def assign_request():
    if request.content_type == "application/json":
        data = request.json
        request_id = data.get("request_id")
        sent_to = data.get("sent_to")

        if not request_id or not sent_to:
            return jsonify({"msg": "Missing required fields"}), 400

        try:
            cursor.execute("SELECT COUNT(*) FROM Requests WHERE RequestID = %s", (request_id,))
            result = cursor.fetchone()

            if result[0] == 0:
                return jsonify({"msg": "Request ID does not exist"}), 404

            cursor.execute(
                "UPDATE Requests SET SentTo = %s WHERE RequestID = %s",
                (sent_to, request_id)
            )

            connection.commit()

            if cursor.rowcount == 0:
                return jsonify({"msg": "Request not found"}), 404
            
            return jsonify({"msg": "Request assigned successfully"}), 200
        
        except Exception as e:
            return jsonify({"msg": "Error assigning request", "error": str(e)}), 500
            
    return jsonify({"msg": "Content type must be application/json"}), 415


@requests_blueprint.route("/user/<int:user_id>", methods=["GET"])
def get_requests_by_user(user_id):
    try:
        cursor.execute(
            "SELECT * FROM Requests WHERE SentBy = %s OR SentTo = %s",
            (user_id, user_id)
        )
        
        requests = cursor.fetchall()
        return jsonify(requests), 200
    
    except Exception as e:
        return jsonify({"msg": "Error retrieving requests", "error": str(e)}), 500
