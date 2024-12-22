from flask import Blueprint, request, jsonify
from utils import jwt_required
from db import db
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
        username = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])['name']

        query = "SELECT Priority FROM Users WHERE Name = %s"
        result = db.execute(query, (username,))
        user = result.fetchone()

        if not user or user['Priority'] != 7:
            return jsonify({"msg": "You are not authorized to create a task"}), 403

        query = "INSERT INTO Tasks (TaskDescription, AssignedBy, AssignedTo, Deadline) VALUES (%s, %s, %s, %s)"
        db.execute(query, (TaskDescription, AssignedBy, AssignedTo, Deadline))
        db.commit()

        return jsonify({"msg": "Task created successfully"}), 201

    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500




@task_blueprint.route('/', methods=['GET'])
@jwt_required
def get_all_tasks():
    try:
        query = "SELECT * FROM Tasks"
        tasks = db.execute(query).fetchall()
        
        return jsonify({"tasks": [dict(task) for task in tasks]}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500




@task_blueprint.route('/<int:id>', methods=['GET'])
@jwt_required
def get_task_by_id(id):
    try:
        query = "SELECT * FROM Tasks WHERE TaskID = %s"
        task = db.execute(query, (id,)).fetchone()

        if not task:
            return jsonify({"msg": "Task not found"}), 404

        return jsonify({"task": dict(task)}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500




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

        query = "SELECT * FROM Tasks WHERE TaskID = %s"
        task = db.execute(query, (id,)).fetchone()

        if not task:
            return jsonify({"msg": "Task not found"}), 404

        query = """
            UPDATE Tasks SET
                TaskDescription = COALESCE(%s, TaskDescription),
                Status = COALESCE(%s, Status),
                Deadline = COALESCE(%s, Deadline)
            WHERE TaskID = %s
        """
        db.execute(query, (TaskDescription, Status, Deadline, id))
        db.commit()

        return jsonify({"msg": "Task updated successfully"}), 200

    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500




@task_blueprint.route('/<int:id>', methods=['DELETE'])
@jwt_required
def delete_task(id):
    try:
        query = "SELECT * FROM Tasks WHERE TaskID = %s"
        task = db.execute(query, (id,)).fetchone()

        if not task:
            return jsonify({"msg": "Task not found"}), 404

        query = "DELETE FROM Tasks WHERE TaskID = %s"
        db.execute(query, (id,))
        db.commit()

        return jsonify({"msg": "Task deleted successfully", "id": id}), 200

    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500




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

        query = "SELECT * FROM Tasks WHERE TaskID = %s"
        task = db.execute(query, (TaskID,)).fetchone()

        if not task:
            return jsonify({"msg": "Task not found"}), 404

        query = "UPDATE Tasks SET AssignedTo = %s WHERE TaskID = %s"
        db.execute(query, (AssignedTo, TaskID))
        db.commit()

        return jsonify({"msg": "Task assigned successfully"}), 200

    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500




@task_blueprint.route('/user/<int:id>', methods=['GET'])
@jwt_required
def get_tasks_by_user(id):
    try:
        query = "SELECT * FROM Tasks WHERE AssignedTo = %s"
        tasks = db.execute(query, (id,)).fetchall()

        return jsonify({"tasks": [dict(task) for task in tasks]}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
