import datetime
from datetime import datetime as dt
import json
from os import environ
import sys

from bson import json_util
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bottle import post, route, run, template, request, static_file, error, redirect

dbKey = environ.get('dbKey')
dbName = environ.get('dbName', "lazydbdev")
dbCollection = "blablascan"

uri = dbKey
client = MongoClient(uri, server_api=ServerApi('1'))
mydb = client[dbName]
mycol = mydb[dbCollection]

@route('/')
def index():
    return template('show.html');

@route('/data')
def new():
    res = '{'
    x = mycol.find()
    #for data in x:
    #    res += str(data) + ','
    #res += '}'
    return json_util.dumps(x)

@error(404)
def error404(error):
    return 'Nothing here, sorry'

@error(505)
def error505(error):
    return 'Nothing here, sorry, hehe'

run(host='0.0.0.0', port=8080, debug=True)

    
