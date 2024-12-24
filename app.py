from flask import Flask
from auth_routes import auth_blueprint
from user_routes import user_blueprint
from task_routes import task_blueprint
from request_routes import request_blueprint
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

app.register_blueprint(auth_blueprint, url_prefix="/auth")
app.register_blueprint(user_blueprint, url_prefix="/api/user")
app.register_blueprint(task_blueprint, url_prefix='/api/tasks')
app.register_blueprint(request_blueprint, url_prefix="/api/requests")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)

