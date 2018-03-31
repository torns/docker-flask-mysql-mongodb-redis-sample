
import time

from flask import Flask
import MySQLdb as mdb
from pymongo import MongoClient
import redis


# SERVER, DATABASES, CACHE SETUP

# flask instance
app = Flask(__name__)

# mysql instance and settings
mysql_con = mdb.connect(
    host='mysql',
    user='root',
    passwd='example',
    db='test'
)
mysql_con.set_character_set('utf8')
mysql_cur = mysql_con.cursor(mdb.cursors.DictCursor)
mysql_cur.execute('SET NAMES utf8;')
mysql_cur.execute('SET CHARACTER SET utf8;')
mysql_cur.execute('SET character_set_connection=utf8;')

# mongo instance
mongo_client = MongoClient(
    host='mongo',
    port=27017
)

# redis instance
cache = redis.Redis(
    host='redis',
    port=6379
)


# METHODS

def get_mysql_data():
    with mysql_con:
        mysql_cur.execute("""
            SELECT *
            FROM test_table
        """)
        rows = mysql_cur.fetchall()
        return rows

def get_mongo_data():
    db = mongo_client.mongo_test_db
    collection = db.test_collection
    records = []
    for record in collection.find():
        records.append(record)
    return records

def get_hit_cache_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)


# ROUTES

@app.route('/get-mysql')
def get_mysql():
    mysql_data = get_mysql_data()
    return 'Here\'s the mysql datas:\n{}'.format(str(mysql_data))

@app.route('/get-mongo')
def get_mongo():
    mongo_data = get_mongo_data()
    return 'Here\'s the mongo datas:\n{}'.format(str(mongo_data))

@app.route('/get-cache')
def get_cache():
    count = get_hit_cache_count()
    return 'Hello World! I have been seen {} times.\n'.format(str(count))


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

