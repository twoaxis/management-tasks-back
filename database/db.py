import pymysql

db = pymysql.connect(
    host='127.0.0.1',
    user='root',
    password = '',
    db='FCI'
)
cursor = db.cursor()