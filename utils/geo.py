
import requests

def loadCityCoordinates():
    coords = {}

    f = open('utils/stops.txt', 'r')
    for l in f:
        parts = l.split(',')
        if len(parts) > 4 and len(parts[0]) == 3:
            shortName = parts[0]
            name = parts[2].split(' ')[0]
            if len(name) > 3:
                geo = parts[4] + ',' + parts[5]
                coords[name.lower()] = geo
                coords[shortName.lower()] = geo
    f.close()


    return coords | {'annecy': '45.9160,6.1330', 'a': '45.9160,6.1330', 'ann': '45.9160,6.1330', '.': '45.9160,6.1330',
        'lyon': '45.764043,4.835659', 'paris': '48.8566,2.3522', 'nimes': '43.8380,4.3610',
        'aix-les-bains': '45.6923,5.9090', 'aix': '45.6923,5.9090',
        'rumilly': '45.8671,5.9424', 'albertville': '45.6755,6.3927', 'torino': '45.0703,7.6869', 'turin': '45.0703,7.6869',
        'montpellier': '43.6108,3.8767', 'milan': '45.4642,9.1900', 'lausanne': '46.5197,6.6323', 'lau': '46.5197,6.6323',
        'avignon': '43.5654,4.4832', 'grenoble': '45.1885,5.7245', 'toulouse': '43.6045,1.4440',
        'antibes': '43.3580,7.6290', 'chamonix': '45.9237,6.8694', 'marseille': '43.2965,5.3698', 'cannes' : '43.5528,7.0174',
        'barcelona': '41.3851,2.1734', 'nice': '43.7102,7.2620', 'le-grand-saconnex': '46.2332,6.1232', 'aeroport': '46.2332,6.1232', 'aero': '46.2332,6.1232', 'gva': '46.2332,6.1232', 'baar': '47.1954,8.5261',
        'bonneville': '46.0775797,6.4086189', 'mont-blanc': '45.8327056,6.865170', 'мон-блан' : '45.8327056,6.865170', 
        'питер':  '59.938732,30.316229', 'санкт-петербург':  '59.938732,30.316229', 'saint-petersburg':  '59.938732,30.316229',
        'mulhouse': '47.7467233,7.3389937'}



CITY_COORD = loadCityCoordinates()

def getCoordinatesByName(name):
    try:
        return CITY_COORD[name.lower()]
    except Exception as e:
        print(e)
        url = "https://nominatim.openstreetmap.org/search?format=json&addressdetails=0&limit=1&q=" + name

        try:
            response = requests.get(url)
            response_json = response.json()
            print(response_json)

            lat = response_json[0]['lat']
            lon = response_json[0]['lon']

            CITY_COORD[name.lower()] = lat + ',' + lon
            print(CITY_COORD[name.lower()])
            return lat + ',' + lon
        except Exception as e:
            print(e)
            return ''

def getAllCoordinates():
    return CITY_COORD