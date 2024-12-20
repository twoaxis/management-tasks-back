from flask import Flask
from routes.users import users_blueprint
from routes.tasks import tasks_blueprint
from routes.requests import requests_blueprint
import config

#------------------------------------------
app = Flask(__name__)
#------------------------------------------
#to do :
#implement csrf protection
#pbkdf2:sha256:600000$o1inp7vOzppEoQqs$a894447ecbe355c71bf158a386551ed508d3ace66e74e177eed8e42b769ab250
#regix for password complexity
#------------------------------------------

app.config['SECRET_KEY'] = config.SECRET_KEY


app.register_blueprint(users_blueprint, url_prefix="/users")
app.register_blueprint(tasks_blueprint, url_prefix="/tasks")
app.register_blueprint(requests_blueprint, url_prefix="/requests")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)