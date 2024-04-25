import datetime
from datetime import datetime as dt
import json
from os import environ
import sys

from utils.geo import getCoordinatesByName, getAllCoordinates
from blabla.carpooling import getTripsData

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId

apiKey = environ.get('blablaApiKey')
dbKey = environ.get('dbKey')
dbName = environ.get('dbName', "lazydbdev")
dbCollection = "blablascan"

def scanFromTo(apiKey, seats, dateBegin, dateEnd, fromName, toName, radius):
    fromName = getCoordinatesByName(fromName.lower())
    toName = getCoordinatesByName(toName.lower())
    
    if 'T' not in dateBegin:
        dateBegin += 'T00:00:00'
    
    return getTripsData(apiKey, seats, fromName, toName, dateBegin, dateEnd, radius)


cityFrom = len(sys.argv) > 2 and sys.argv[1] or 'Annecy'
cityTo = len(sys.argv) > 2 and sys.argv[2] or 'Mulhouse'

if cityTo == 'all':
    citysTo = getAllCoordinates()
else:
    citysTo = [cityTo]

for cityTo in citysTo:
    try:
        srcdst = cityFrom + '_' + cityTo

        start = datetime.date.today() + datetime.timedelta(days=1)
        end = datetime.date.today() + datetime.timedelta(days=120)
        dateStart = '%d-%02d-%02d' % (start.year, start.month, start.day) + 'T00:00:00'
        dateEnd = '%d-%02d-%02d' % (end.year, end.month, end.day) + 'T23:59:59'

        trips = scanFromTo(apiKey, 1, dateStart, dateEnd, cityFrom, cityTo, 5000)

        if len(trips) > 0:
            uri = dbKey
            client = MongoClient(uri, server_api=ServerApi('1'))

            for t in trips:
                t['price']['amount'] = float(t['price']['amount'])
                t['srcdst'] = srcdst
                #t['linkid'] = t['link'].split('id=')[1].split('&')[0]

            query = {"srcdst": srcdst}
            #newvalues = {"$set": trips}
            #mycol.update_many(query, newvalues)

            mydb = client[dbName]
            mycol = mydb[dbCollection]

            d = mycol.delete_many(query)
            i = mycol.insert_many(trips)
            print('deleted', d.deleted_count)
            print('inserted', len(i.inserted_ids))
    except Exception as e:
        print(e)
    
