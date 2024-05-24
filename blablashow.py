import datetime
from datetime import datetime as dt
import json
from os import environ
import sys

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bottle import post, route, run, template, request, response, static_file, error, redirect

# json float precision
from json import encoder
encoder.FLOAT_REPR = lambda o: format(o, '.2f')

dbKey = environ.get('dbKey')
dbName = environ.get('dbName', "lazydbdev")
dbCollection = "blablascan"

uri = dbKey
client = MongoClient(uri, server_api=ServerApi('1'))
mydb = client[dbName]
mycol = mydb[dbCollection]

@route('/search')
def index():
    response.content_type = 'html'
    return template('show.html');

@route('/')
def index():
    response.content_type = 'html'
    return "<body><ul><li><a href='/search?fn=annecy'>Annecy</a></li><li><a href='/search?fn=ekb'>Ekb</a></li></ul></body>";

'''
"[{\"_id\": {\"$oid\": \"6610f6cc48bd4e9ce765c888\"}, 
\"link\": \"https://www.blablacar.fr/trip?source=CARPOOLING&id=4POCp58VRoe_gRx5FVIxcQSNcR9rE6TpKcYrdyHnXKiQ\", 
\"waypoints\": [{\"date_time\": \"2024-05-03T11:40:00\", 
\"place\": {\"city\": \"Annecy\", \"address\": \"16 Av. de Chev\\u00e9ne, Annecy\", \"latitude\": 45.901199, \"longitude\": 6.117875, \"country_code\": \"FR\"}}, 
{\"date_time\": \"2024-05-03T17:10:00\", \"place\": 
{\"city\": \"Milan\", \"address\": \"Viale Alcide de Gasperi, 2, Milano MI\", \"latitude\": 45.488908, \"longitude\": 9.141483, \"country_code\": \"IT\"}}], 
\"price\": {\"amount\": 41.49, \"currency\": \"EUR\"}, \"vehicle\": null, 
\"distance_in_meters\": 351650, 
\"duration_in_seconds\": 19800}, 


'''
@route('/data')
def new():
    response.content_type = 'application/json'
    src = request.query['fn'].lower()
    x = src and mycol.find({"src": src}) or []
    res = []
    for data in x:
        dt = data['waypoints'][0]['date_time'].split('T')
        tm = dt[1].split(':')
        dt = dt[0].split('-')

        #origin = str(data['waypoints'][0]['place']['latitude']) + ',' + str(data['waypoints'][0]['place']['longitude'])
        #destination = str(data['waypoints'][-1]['place']['latitude']) + ',' + str(data['waypoints'][-1]['place']['longitude'])
        res += [{'month': dt[1], 'day': dt[2], 'time': tm[0] + ':' + tm[1], 'from': data['waypoints'][0]['place']['city'], 'to': data['waypoints'][1]['place']['city'],
            #'origin': origin, 'destination': destination,
            'path': data['waypoints'],
            'price': data['price']['amount'], "distance_in_km": int(data['distance_in_meters'] / 1000), "duration_in_hours": round(float(data['duration_in_seconds']) / 3600, 1),
            'link' : data['link'] }]
    #res += '}'
    j = json.dumps(res)
    print('send %d data' % len(j))
    return j

@error(404)
def error404(error):
    return 'Nothing here, sorry'

@error(505)
def error505(error):
    return 'Nothing here, sorry, hehe'

run(host='0.0.0.0', port=8080, debug=True)

    
