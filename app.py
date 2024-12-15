from flask import *
import jwt , datetime
from werkzeug.security import check_password_hash
import pymysql

#------------------------------------------
app = Flask(__name__)
connection = pymysql.connect(host='127.0.0.1', user='root', password = '', db='FCI')
cursor = connection.cursor()
#------------------------------------------
app.config["SECRET_KEY"]='##@R3_Y0u_H3ck3r_r1ghT_?_Cr3ck_m3_1f_Y0u_c@N##'
#------------------------------------------
#to do :
#implement csrf protection
#pbkdf2:sha256:600000$o1inp7vOzppEoQqs$a894447ecbe355c71bf158a386551ed508d3ace66e74e177eed8e42b769ab250
#regix for password complexity
#catch brute force

@app.route("/auth/login",methods=["POST"])
def login():
    if request.content_type == "application/json":
        try:
            Email = request.json["email"]
            password = request.json["password"]
        except:
            return jsonify({"msg":"Missing required fields"}),400
        cursor.execute("SELECT * FROM Users WHERE email = %s", (Email))
        data_from_database = cursor.fetchone()
        if data_from_database and (check_password_hash(data_from_database[5],password)):
            token = jwt.encode({"name":data_from_database[3],"exp": (datetime.datetime.utcnow() + datetime.timedelta(minutes=3600))},app.config["SECRET_KEY"])
            return jsonify({"Token":token}),200
        else:
        #catch_brute_force_attack_here
            return jsonify({"msg":"invalid username or password"}),401
    else:
        return jsonify({"msg","Content-type should be json"}),500

app.run(host='0.0.0.0', port=80)