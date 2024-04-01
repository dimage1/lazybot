import datetime
from datetime import datetime as dt
import json
from os import environ

from utils.geo import getCoordinatesByName
from blabla.carpooling import getTripsData

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId

apiKey = environ.get('blablaApiKey')
dbKey = environ.get('dbKey')

def scanFromTo(apiKey, seats, dateBegin, dateEnd, fromName, toName, radius):
    fromName = getCoordinatesByName(fromName.lower())
    toName = getCoordinatesByName(toName.lower())
    
    if 'T' not in dateBegin:
        dateBegin += 'T00:00:00'
    
    return getTripsData(apiKey, seats, fromName, toName, dateBegin, dateEnd, radius)


start = datetime.date.today() + datetime.timedelta(days=1)
end = datetime.date.today() + datetime.timedelta(days=120)
dateStart = '%d-%02d-%02d' % (start.year, start.month, start.day) + 'T00:00:00'
dateEnd = '%d-%02d-%02d' % (end.year, end.month, end.day) + 'T23:59:59'

trips = scanFromTo(apiKey, 1, dateStart, dateEnd, "Annecy", "Mulhouse", 5000)

if len(trips) > 0:
    uri = dbKey
    client = MongoClient(uri, server_api=ServerApi('1'))

    for t in trips:
        t['price']['amount'] = float(t['price']['amount'])
        #t['linkid'] = t['link'].split('id=')[1].split('&')[0]

    query = {}#{"linkid": trips[0]['linkid']}#{'$in': [t['linkid'] for t in trips]}}
    #newvalues = {"$set": trips}
    #mycol.update_many(query, newvalues)

    mydb = client["lazydb"]
    mycol = mydb["blablascan"]

    d = mycol.delete_many(query)
    i = mycol.insert_many(trips)
    print('deleted', d.deleted_count)
    print('inserted', len(i.inserted_ids))

    
