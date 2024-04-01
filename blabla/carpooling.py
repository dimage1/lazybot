import datetime
from datetime import datetime as dt
import requests
import json
import time
import os
import copy

API_URL = 'https://public-api.blablacar.com/api/v3/trips'

def getTripsData(apiKey, seats, fromName, toName, dateBegin, dateEnd, radius=10000):
    headers = {'accept': 'application/json', 'key': apiKey} 
    params = {'from_coordinate': fromName, 'requested_seats': seats, 'to_coordinate': toName, 'start_date_local': dateBegin, 'count' : 100, 'sort': 'departure_datetime:asc', 'currency' : 'EUR'}
    if radius != 0: # default
        params['radius_in_meters'] = radius
    
    if dateEnd != '':
        params['end_date_local'] = dateEnd

    #'end_date_local': '2021-04-20T05:55:00'}#, 'start_date_local': dateBegin} #'2021-03-20T05:55:00'}

    print(params)
    r = requests.get(API_URL, params=params, headers=headers)

    try:
        data  = r.json()
        print(data)
    except ValueError as err:
        print(str(err))
        sys.exit(2)

    return data["trips"]