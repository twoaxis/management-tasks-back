from flask import Blueprint, request, jsonify
from utils import jwt_required
from db import connection, cursor
import jwt
from config import Config

task_blueprint = Blueprint('tasks', __name__)

@task_blueprint.route('/create', methods=['POST'])
@jwt_required
def create_task():
    if request.content_type != "application/json":
        return jsonify({"msg": "Content-type should be JSON"}), 400

    try:
        data = request.json
        TaskDescription = data.get("TaskDescription")
        AssignedBy = data.get("AssignedBy")
        AssignedTo = data.get("AssignedTo")
        Deadline = data.get("Deadline")

        if not all([TaskDescription, AssignedBy, AssignedTo, Deadline]):
            return jsonify({"msg": "Missing required fields"}), 400

        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"msg": "Missing token"}), 401

        decoded = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        username = decoded.get("name")

        if not username:
            return jsonify({"msg": "Invalid token"}), 401

        cursor.execute("SELECT Priority FROM Users WHERE Name = %s", (username,))
        user = cursor.fetchone()

        if not user or user[0] != 7:
            return jsonify({"msg": "You are not authorized to create a task"}), 403

        cursor.execute(
            "INSERT INTO Tasks (TaskDescription, AssignedBy, AssignedTo, Deadline) VALUES (%s, %s, %s, %s)",
            (TaskDescription, AssignedBy, AssignedTo, Deadline)
        )
        connection.commit()

        return jsonify({"msg": "Task created successfully"}), 201

    except Exception as e:
        return jsonify({"msg": "An error occurred while creating the task", "error": str(e)}), 500

@task_blueprint.route('/', methods=['GET'])
@jwt_required
def get_all_tasks():
    try:
        cursor.execute("SELECT * FROM Tasks")
        tasks = cursor.fetchall()

        # Convert tasks to a list of dictionaries
        task_list = []
        for task in tasks:
            task_dict = {
                "TaskID": task[0],
                "TaskDescription": task[1],
                "AssignedBy": task[2],
                "AssignedTo": task[3],
                "Status": task[4],
                "CreationDate": task[5],
                "Deadline": task[6]
            }
            task_list.append(task_dict)

        return jsonify({"tasks": task_list}), 200

    except Exception as e:
        return jsonify({"msg": "Error retrieving tasks", "error": str(e)}), 500

@task_blueprint.route('/<int:id>', methods=['GET'])
@jwt_required
def get_task_by_id(id):
    try:
        cursor.execute("SELECT * FROM Tasks WHERE TaskID = %s", (id,))
        task = cursor.fetchone()

        if not task:
            return jsonify({"msg": "Task not found"}), 404

        task_dict = {
            "TaskID": task[0],
            "TaskDescription": task[1],
            "AssignedBy": task[2],
            "AssignedTo": task[3],
            "Status": task[4],
            "CreationDate": task[5],
            "Deadline": task[6]
        }

        return jsonify({"task": task_dict}), 200

    except Exception as e:
        return jsonify({"msg": "Error retrieving task", "error": str(e)}), 500

@task_blueprint.route('/<int:id>', methods=['PUT'])
@jwt_required
def update_task(id):
    if request.content_type != "application/json":
        return jsonify({"msg": "Content-type should be JSON"}), 400

    try:
        data = request.json
        TaskDescription = data.get('TaskDescription')
        Status = data.get('Status')
        Deadline = data.get('Deadline')

        cursor.execute("SELECT * FROM Tasks WHERE TaskID = %s", (id,))
        task = cursor.fetchone()

        if not task:
            return jsonify({"msg": "Task not found"}), 404

        query = """
            UPDATE Tasks SET
                TaskDescription = %s,
                Status = %s,
                Deadline = %s
            WHERE TaskID = %s
        """
        cursor.execute(query, (TaskDescription, Status, Deadline, id))
        connection.commit()

        return jsonify({"msg": "Task updated successfully"}), 200

    except Exception as e:
        return jsonify({"msg": "Error updating task", "error": str(e)}), 500

@task_blueprint.route('/<int:id>', methods=['DELETE'])
@jwt_required
def delete_task(id):
    try:
        cursor.execute("SELECT * FROM Tasks WHERE TaskID = %s", (id,))
        task = cursor.fetchone()

        if not task:
            return jsonify({"msg": "Task not found"}), 404

        cursor.execute("DELETE FROM Tasks WHERE TaskID = %s", (id,))
        connection.commit()

        return jsonify({"msg": "Task deleted successfully", "id": id}), 200

    except Exception as e:
        return jsonify({"msg": "Error deleting task", "error": str(e)}), 500

@task_blueprint.route('/assign', methods=['POST'])
@jwt_required
def assign_task():
    if request.content_type != "application/json":
        return jsonify({"msg": "Content-type should be JSON"}), 400

    try:
        data = request.json
        TaskID = data.get("TaskID")
        AssignedTo = data.get("AssignedTo")

        if not all([TaskID, AssignedTo]):
            return jsonify({"msg": "Missing required fields"}), 400

        cursor.execute("SELECT * FROM Tasks WHERE TaskID = %s", (TaskID,))
        task = cursor.fetchone()

        if not task:
            return jsonify({"msg": "Task not found"}), 404

        cursor.execute("UPDATE Tasks SET AssignedTo = %s WHERE TaskID = %s", (AssignedTo, TaskID))
        connection.commit()

        return jsonify({"msg": "Task assigned successfully"}), 200

    except Exception as e:
        return jsonify({"msg": "Error assigning task", "error": str(e)}), 500

@task_blueprint.route('/user/<int:id>', methods=['GET'])
@jwt_required
def get_tasks_by_user(id):
    try:
        cursor.execute("SELECT * FROM Tasks WHERE AssignedTo = %s", (id,))
        tasks = cursor.fetchall()

        task_list = []
        for task in tasks:
            task_dict = {
                "TaskID": task[0],
                "TaskDescription": task[1],
                "AssignedBy": task[2],
                "AssignedTo": task[3],
                "Status": task[4],
                "CreationDate": task[5],
                "Deadline": task[6]
            }
            task_list.append(task_dict)

        return jsonify({"tasks": task_list}), 200

    except Exception as e:
        return jsonify({"msg": "Error retrieving tasks", "error": str(e)}), 500