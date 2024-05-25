import datetime
from datetime import datetime as dt
from time import sleep
import json
import os
import sys

from utils.geo import getCoordinatesByName, getAllCoordinates
from blabla.carpooling import getTripsData

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId

#from dotenv import load_dotenv
#load_dotenv() 

apiKey = os.getenv('blablaApiKey')
dbKey = os.getenv('dbKey')
dbName = os.getenv('dbName', "lazydbdev")
dbCollection = "blablascan"

def scanFromTo(apiKey, seats, dateBegin, dateEnd, fromName, toName, radius):
    fromName = getCoordinatesByName(fromName.lower())
    toName = getCoordinatesByName(toName.lower())

    if fromName and toName:
        if 'T' not in dateBegin:
            dateBegin += 'T00:00:00'
        
        return getTripsData(apiKey, seats, fromName, toName, dateBegin, dateEnd, radius)


cityFrom = len(sys.argv) > 2 and sys.argv[1] or 'Annecy'
cityTo = len(sys.argv) > 2 and sys.argv[2] or 'Mulhouse'

#if cityTo == 'all':
#    citysTo = getAllCoordinates()
#else:
if ',' in cityTo:
    citysTo = cityTo.split(',')
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

        if trips and len(trips) > 0:
            uri = dbKey
            client = MongoClient(uri, server_api=ServerApi('1'))

            for t in trips:
                t['price']['amount'] = float(t['price']['amount'])
                t['srcdst'] = srcdst
                t['src'] = cityFrom
                t['dst'] = cityTo
                t['start_time'] = t['waypoints'][0]['date_time']
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
        sleep(0.1)
    except Exception as e:
        print(e)
    
