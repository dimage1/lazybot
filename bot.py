import telebot
from telebot import types
import random

import datetime
from datetime import datetime as dt
#from timezonefinderL import TimezoneFinder -- 350MB
from timezonefinderL import TimezoneFinder # -- 90MB, not so precise
#from tzwhere import tzwhere -- does not work with latest numpy

import requests
import json
import time
import os
import copy
import prettytable as pt # python -m pip install -U prettytable

from utils.geo import loadCityCoordinates
from blabla.carpooling import getTripsData

bot = telebot.TeleBot(os.environ.get('botID'))
apiKey = os.environ.get('blablaApiKey')

MONTH_MAP={'январь':'01', 'янв':'01', 'ферваль':'02', 'фев':'02', 'март':'03', 'мар':'03', 'апрель':'04', 'апр':'04', 'май':'05', 'июнь':'06', 'июль':'07', 'август':'08', 'авг':'08', 'сентябрь':'09',
    'сент':'09', 'октябрь':'10', 'окт':'10', 'ноябрь':'11', 'нояб':'11', 'декабрь':'12', 'дек':'12', 'january':'01', 'jan':'01', 'february':'02', 'feb':'02', 'march':'03', 'mar':'03', 'april':'04', 'apr':'04',
    'may':'05', 'june':'06', 'july':'07', 'august':'08', 'aug':'08', 'september':'09', 'sept':'09', 'october':'10', 'oct':'10', 'november':'11', 'nov':'11', 'december':'12', 'dec':'12'}

MONTH_MAP_REVERSE={'01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr', '05': 'May', '06': 'Jun', '07': 'Jul', '08': 'Aug', '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'}

DAYS_IN_MONTH=[31, 29, 31, 30, 31, 30, 31, 31, 31, 30, 31, 30]

CITY_COORD = loadCityCoordinates()

tf = TimezoneFinder()  # reuse
#tzw = tzwhere.tzwhere()

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

def scanFromTo(apiKey, seats, dateBegin, dateEnd, fromName, toName, radius):
    fromName = getCoordinatesByName(fromName.lower())
    toName = getCoordinatesByName(toName.lower())
    
    if 'T' not in dateBegin:
        dateBegin += 'T00:00:00'
    
    return getTripsData(apiKey, seats, fromName, toName, dateBegin, dateEnd, radius)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Helo Helo ! Be ready to ride")

@bot.message_handler(commands=['help'])
def send_help(message):
    now = datetime.date.today()
    day1 = (now.day + 1) % 30 + 1
    day2 = (now.day + 2) % 30 + 1
    day3 = (now.day + 5) % 30 + 1
    month1 = MONTH_MAP_REVERSE['%02d' % now.month].lower()
    month2 = MONTH_MAP_REVERSE['%02d' % (now.month + 1)].lower()
    examples = ['*trip* annecy chamonix %d %d' % (day1, day2), '*ride* annecy\+parmelan nice %d %d' % (day1, day3), '*ride* 2 turin milan %d' % day1, '*trip* prague vien %s 1 30' % month2, 
        '*ride* 3 annecy grenoble %d' % day1, '*ride* 4 ann lyon %d' % day1, '*ride* annecy aero %s %d' % (month1, day1), '*ride* annecy marseille %d %d' % (day1, day2) ]

    example = ' 🚗 `Blabla 🔎 examples`\n' + '\n'.join(examples)
    bot.send_message(message.chat.id, example, reply_markup=types.ReplyKeyboardRemove(), parse_mode='MarkdownV2')

    # markup = types.ReplyKeyboardMarkup(row_width=1)
    #itembtn1 = types.KeyboardButton('trip ann chamonix %d %d' % (day1, day2))
    #itembtn2 = types.KeyboardButton('ride 2 annecy+parmelan nice %d %d' % (day1, day3))
    #itembtn3 = types.KeyboardButton('ride 2 turin milan %d' % day1)
    #itembtn4 = types.KeyboardButton('trip prague vien %s 1 30' % month2)
    #itembtn5 = types.KeyboardButton('ride 3 ann grenoble %d' % day1)
    #itembtn6 = types.KeyboardButton('ride 4 ann lyon %d' % day1)
    #itembtn7 = types.KeyboardButton('ride ann aero %s %d' % (month1, day1))
    #itembtn8 = types.KeyboardButton('ride ann marseille %d %d' % (day1, day2))
    #itembtn9 = types.KeyboardButton('ride paris london %d 30' % day1)
    #itembtn10 = types.KeyboardButton('ride paris amsterdam %d %d' % (day1, day3))
    #itembtn11 = types.KeyboardButton('ride ann evian+france %d %d' % (day1, day2))
    #markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5, itembtn6, itembtn7, itembtn8, itembtn9, itembtn10, itembtn11)
    #bot.send_message(message.chat.id, "Choose an example:", reply_markup=markup)

def sendBack(message, text, encode=True):
    toId = message.chat.id # message['from'].i
    bot.send_message(toId, encode and text.encode("utf-8") or text, disable_web_page_preview=True, parse_mode='MarkdownV2')

def scanForDate(message, seats, dateBegin, dateEnd, fromCity, toCity, radius):
    data = scanFromTo(apiKey, seats, dateBegin, dateEnd, fromCity, toCity, radius)
    infos = ''
    datePrev = ''

    seatsStr = '웃' # '👤' '웃' '🧍' 🚶 #seats > 1 and 'seats' or 'seat'
    direction = '🚗 *' + fromCity.replace('+', "\+").replace('-', "\-") + ' \- ' + toCity.replace('+', "\+").replace('-', "\-") + 
        ' *\(*' + str(seats) + seatsStr + '*'

    for d in data:
        dateCurrent, timeCurrent = d['waypoints'][0]['date_time'].split('T')
        year, month, day = dateCurrent.split('-')
        month = MONTH_MAP_REVERSE[month]
        timeCurrent = timeCurrent.split(':')
        distance = int(d['distance_in_meters']) // 1000
        duration = int(d['duration_in_seconds']) // 60
        minutes = duration % 60
        hours = duration / 60
        if direction:
            infos += (direction + ',' + str(distance) + 'km,' + ('%dh%02d' % (hours, minutes)) + '\)\n').replace('.', "\.")
            direction = ''
        dateInfo = '      '
        if dateCurrent != datePrev:
            datePrev = dateCurrent
            #city = d['waypoints'][1]['place']['city']
            #infos += '*' + day + ' ' + month + direction + '*\n'#'__ 💡 *' + fromCity.replace('+', "\+") + ' \- ' + toCity.replace('+', "\+") + '*\n'
            #direction = ''
            dateInfo = day + ' ' + month
        amount = d['price']['amount'].split('.')[0]
        infos += ('`%s` → [%s:%s](%s) - %s €\n' % (dateInfo, timeCurrent[0], timeCurrent[1], d['link'], amount)).replace('.', "\.").replace('-', "\-")
        if len(infos) > 3200:
            sendBack(message, infos)
            infos = ''

    infos and sendBack(message, infos)

def getElevation(message, cities):
    table = pt.PrettyTable()
    table.padding_width=0
    table.align = "r"
    table.vrules=2
    table.field_names = ['Place', ' Elevation']

    url = "https://api.open-meteo.com/v1/elevation?"
    latitude = ''
    longitude = ''
    citiesOrder = []
    for city in cities:
        coord = getCoordinatesByName(city)
        if coord:
            citiesOrder += [city]
            coords = coord.split(',')
            latitude += (latitude and ',' or '') + coords[0]
            longitude += (longitude and ',' or '') + coords[1]

    response = requests.get(url + 'latitude=' + latitude +  '&longitude=' + longitude)
    response_json = response.json()
    print(response_json)

    info = ''
    for i in range(0, len(response_json["elevation"])):
        info += info and ', ' or ''
        info += citiesOrder[i] + ': ' + str(round(response_json["elevation"][i])) + 'м'

        table.add_row([citiesOrder[i], str(round(response_json["elevation"][i])) + ' м'])

    sendBack(message, f'```{table}```', True) #info.replace('-', '\-'), True)

def showRandom(message, options):
    if options:
        sendBack(message, random.choice(options))
    else:
        sendBack(message, random.choice(['🥕', '🥖', '🧀','🥦','🌶','🍳','🌭','🍔','🍟','🌮','🧆','🥙','🥪','🫔','🍹']), True)

def weatherCodeToText(code, precipitation=0):
    precipitation = float(precipitation)

    if code in [0,1]:
        return '🌞' #'☀'
    elif code in [63, 65] or (code == 61 and precipitation >= 0.1):
        return '🌧'#'☔'
    elif code in [80, 81]:
        return '💦' #'☔'#'🌧']
    elif code == 82:
        return  '⛈'
    elif code in [2,3,61]:
        return  '⛅️'#☁🌥⛅
    elif code == 77:
        return ''#'❄'
    elif code in [71,73]:
        return  '❄'#'🌨']
    elif code == 75:
        return  '❄'#'🌨']
    elif code in [95, 96, 99]:
        return  '⚡'
    else:
        return '🌥'

def preparePreciseWeather(t, weatherCode, pressure, wind, humidity):
    temp = round(t)
    weatherPic = weatherCodeToText(weatherCode)
    humidity = int(humidity)
    wind = round(wind)
    pressure = round(float(pressure) * 0.75006375541921) #surface_pressure

    pressureSign = '🌡'
    if pressure > 770:
        pressureSign = '📈'
    elif pressure < 750:
        pressureSign = '📉'

    windSign = '💨' 
    if wind > 25:
        windSign = '‼️🌪' # ‼️
    if wind > 18:
        windSign = '🌪' # ‼️
    elif wind > 9:
        windSign = '🚩'

    humiditySign = '💧'
    if humidity > 60:
        humiditySign = '💦'

    return f'{weatherPic}*{temp}°* {windSign}{wind}м {pressureSign}{pressure} {humiditySign}{humidity}%'

def prepareShortWeather(hourlyData, shift):
    hourlyTemp = hourlyData['temperature_2m']
    hourlyCode = hourlyData['weathercode']
    hourlyPrec = hourlyData['precipitation']

    return weatherCodeToText(hourlyCode[shift], hourlyPrec[shift]) + str(round(hourlyTemp[shift])) + '°'

def prepareHourlyWeather(hourlyData, shift):
    return prepareShortWeather(hourlyData, shift + 9) + '  ' + prepareShortWeather(hourlyData, shift + 14) + ' ' + prepareShortWeather(hourlyData, shift + 20)

def showPreciseWeather(message, city, json):
    current = json['current']
    now = current['time'].split('T')[1]

    curWeather = preparePreciseWeather(current['temperature_2m'], current['weather_code'], current['pressure_msl'], current['wind_speed_10m'], current['relative_humidity_2m'])

    hourly = json['hourly']
    days = ['mon', 'tue', 'wed', 'thr', 'fra', 'sat', 'sun']
    dayOfTheWeek = datetime.datetime.now().isoweekday() - 1

    d1 = prepareHourlyWeather(hourly, 0)
    d2 = prepareHourlyWeather(hourly, 24)
    d3 = prepareHourlyWeather(hourly, 48)
    d4 = prepareHourlyWeather(hourly, 72)
    d5 = prepareHourlyWeather(hourly, 96)

    day1 = '' + days[dayOfTheWeek] + ' ' + d1
    dayOfTheWeek = (dayOfTheWeek + 1) % 7
    day2 = '' + days[dayOfTheWeek] + ' '+ d2
    dayOfTheWeek = (dayOfTheWeek + 1) % 7
    day3 = '' + days[dayOfTheWeek] + ' '+ d3
    dayOfTheWeek = (dayOfTheWeek + 1) % 7
    day4 = '' + days[dayOfTheWeek] + ' '+ d4
    dayOfTheWeek = (dayOfTheWeek + 1) % 7
    day5 = '' + days[dayOfTheWeek] + ' '+ d5

    cityShort = (city[0:3])

    # *{now}* 🌞{sunrise} - {sunset}
    # \n```......9:00...14:00...20:00\n{day1}\n{day2}\n{day3}\n{day4}\n{day5}```
    sendBack(message, (f'__{cityShort}__ ' + curWeather + '\n' +
        f'```......9:00...14:00...20:00\n{day1}\n{day2}\n{day3}\n{day4}\n{day5}```').replace('-', '\-'), True)

def showForecast(message, city, json):
    days = ['mo', 'tu', 'we', 'th', 'fr', 'sa', 'su']
    dayOfTheWeek = datetime.datetime.now().isoweekday() - 1

    '''
    day1 = '' + days[dayOfTheWeek] + '  ' + d1
    dayOfTheWeek = (dayOfTheWeek + 1) % 7
    day2 = '' + days[dayOfTheWeek] + '  '+ d2
    dayOfTheWeek = (dayOfTheWeek + 1) % 7
    day3 = '' + days[dayOfTheWeek] + '  '+ d3
    dayOfTheWeek = (dayOfTheWeek + 1) % 7
    day4 = '' + days[dayOfTheWeek] + '  '+ d4
    dayOfTheWeek = (dayOfTheWeek + 1) % 7
    day5 = '' + days[dayOfTheWeek] + '  '+ d5
    '''
    daily = json['daily']
    sunset = daily['sunset'][0].split('T')[1]
    sunrise = daily['sunrise'][0].split('T')[1]
    
    weatherCodes = daily['weathercode']
    temp = daily['temperature_2m_max']
    times = daily['time']

    day1 = weatherCodeToText(weatherCodes[0]) + str(round(temp[0])) + '°'
    d1 = days[dayOfTheWeek]
    dayOfTheWeek = (dayOfTheWeek + 1) % 7

    day2 = weatherCodeToText(weatherCodes[1]) + str(round(temp[1])) + '°'
    d2 = days[dayOfTheWeek]
    dayOfTheWeek = (dayOfTheWeek + 1) % 7

    day3 = weatherCodeToText(weatherCodes[2]) + str(round(temp[2])) + '°'
    d3 = days[dayOfTheWeek]
    dayOfTheWeek = (dayOfTheWeek + 1) % 7

    day4 = weatherCodeToText(weatherCodes[3]) + str(round(temp[3])) + '°'
    d4 = days[dayOfTheWeek]
    dayOfTheWeek = (dayOfTheWeek + 1) % 7

    day5 = weatherCodeToText(weatherCodes[4]) + str(round(temp[4])) + '°'
    d5 = days[dayOfTheWeek]
    dayOfTheWeek = (dayOfTheWeek + 1) % 7
    
    day6 = weatherCodeToText(weatherCodes[5]) + str(round(temp[5])) + '°'
    d6 = days[dayOfTheWeek]
    dayOfTheWeek = (dayOfTheWeek + 1) % 7

    day7 = weatherCodeToText(weatherCodes[6]) + str(round(temp[6])) + '°'
    d7 = days[dayOfTheWeek]
    dayOfTheWeek = (dayOfTheWeek + 1) % 7

    day8 = weatherCodeToText(weatherCodes[7]) + str(round(temp[7])) + '°'
    d8 = days[dayOfTheWeek]
    dayOfTheWeek = (dayOfTheWeek + 1) % 7

    day9 = weatherCodeToText(weatherCodes[8]) + str(round(temp[8])) + '°'
    d9 = days[dayOfTheWeek]
    dayOfTheWeek = (dayOfTheWeek + 1) % 7

    day10 = weatherCodeToText(weatherCodes[9]) + str(round(temp[9])) + '°'
    d10 = days[dayOfTheWeek]
    dayOfTheWeek = (dayOfTheWeek + 1) % 7

    day11 = weatherCodeToText(weatherCodes[10]) + str(round(temp[10])) + '°'
    d11 = days[dayOfTheWeek]
    dayOfTheWeek = (dayOfTheWeek + 1) % 7

    day12 = weatherCodeToText(weatherCodes[11]) + str(round(temp[11])) + '°'
    d12 = days[dayOfTheWeek]
   
    cityShort = (city[0:7])

    # *{now}* 🌞{sunrise} - {sunset}
    # \n```......9:00...14:00...20:00\n{day1}\n{day2}\n{day3}\n{day4}\n{day5}```
    sendBack(message, (f'```{cityShort}..12..days..forecast\n{d1},{d2},{d3} {day1} {day2} {day3}\n{d4},{d5},{d6} {day4} {day5} {day6}\n{d7},{d8},{d9} {day7} {day8} {day9}\n{d10},{d11},{d12} {day10} {day11} {day12}\n```').replace('-', '\-'), True)

def getCityWeather(message, city):
    coord = getCoordinatesByName(city)
    if not coord:
        return
    
    city = city.replace('-', '\\-').replace('.', '\.')

    coords = coord.split(',')
    latitude = coords[0]
    longitude = coords[1]

    coordStr = 'latitude=' + latitude +  '&longitude=' + longitude
    #getHourlyWeather(citiesOrder, coordsStr)

    dayOfTheWeek = datetime.datetime.now().isoweekday() - 1
    print(dayOfTheWeek)

    #tz = tzw.tzNameAt(float(longitude), float(latitude))
    tz = tf.timezone_at(lng=float(longitude), lat=float(latitude))
    print(tz)

    url = "https://api.open-meteo.com/v1/forecast?"
    url = url + coordStr + ("&wind_speed_unit=ms&current=precipitation,temperature_2m,weather_code,relative_humidity_2m,wind_speed_10m,pressure_msl&" + 
        "hourly=weathercode,temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,pressure_msl")
    
    response = requests.get(url)
    cityJson = response.json()

    print(cityJson)
    showPreciseWeather(message, city, cityJson)

def getCityWeatherOld(message, city, precise):
    table = pt.PrettyTable()
    table.padding_width=0
    table.align = "r"
    table.vrules=2
    table2 = ''

    #table.top_left_junction_char=''

    coord = getCoordinatesByName(city)
    if not coord:
        return
    
    city = city.replace('-', '\\-').replace('.', '\.')

    coords = coord.split(',')
    latitude = coords[0]
    longitude = coords[1]

    coordStr = 'latitude=' + latitude +  '&longitude=' + longitude
    #getHourlyWeather(citiesOrder, coordsStr)

    dayOfTheWeek = datetime.datetime.now().isoweekday() - 1
    print(dayOfTheWeek)

    
    #tz = tzw.tzNameAt(float(longitude), float(latitude))
    tz = tf.timezone_at(lng=float(longitude), lat=float(latitude))
    print(tz)

    url = "https://api.open-meteo.com/v1/forecast?"
    url = url + coordStr + ("&wind_speed_unit=ms&current=precipitation,temperature_2m,weather_code,relative_humidity_2m,wind_speed_10m,pressure_msl&" + 
        "hourly=weathercode,temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,pressure_msl&" + 
        "daily=sunrise,sunset,weathercode,temperature_2m_max&forecast_days=14" + "&timezone=" + str(tz))
    response = requests.get(url)

    cityJson = response.json()
    print(cityJson)
    table.field_names = ['🏠'] + ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']
    temps = cityJson['daily']['temperature_2m_max']
    weatherCodes = cityJson['daily']['weathercode']

    if precise:
        showPreciseWeather(message, city, cityJson)
        return
    
    showForecast(message, city, cityJson)
    return

    #city = (len(cities) == 1) and '   ' or city
    row = ['°C'] + [' ' for x in range(dayOfTheWeek)] #, ' ', ' ', ' ', ' ']
    row2 = ' 🗓 ' + ''.join(['✖️' for x in range(dayOfTheWeek)])
    for i in range(7 - dayOfTheWeek):
        row += [round(temps[i])]
        row2 += weatherCodeToText(weatherCodes[i])
    table.add_row(row)

    row3 = ['°C']
    row4 = ' 🗓 '
    for i in range(7 - dayOfTheWeek, 14 - dayOfTheWeek):
        row3 += [round(temps[i])]
        row4 += weatherCodeToText(weatherCodes[i])
    table.add_row(row3)


    row5 = ['°C']
    row6 = ' 🗓 '
    rangeEnd = (dayOfTheWeek < 5) and 16 or (14 - dayOfTheWeek + 7)
    for i in range(14 - dayOfTheWeek, rangeEnd):
        row5 += [round(temps[i])]
        row6 += weatherCodeToText(weatherCodes[i])
    emptyCells = dayOfTheWeek > 4 and 0 or (4 + 1 - dayOfTheWeek)
    row5 += [' ' for x in range(emptyCells)] #, ' ', ' ', ' ', ' ']
    row6 += ''.join(['✖️' for x in range(emptyCells)])
    table.add_row(row5)


    table2 += row2 + '\n'
    table2 += row4 + '\n'
    table2 += row6 + '\n'

    sendBack(message, f'_Forecast \(16 days\): {city}_\n```{table}```\n' + table2, True)

    #if result:
    #    sendBack(message, result.replace('.', '\\.').replace('-', '\\-'))

def getCityForecast(message, city):
    coord = getCoordinatesByName(city)
    if not coord:
        return
    
    city = city.replace('-', '\\-').replace('.', '\.')

    coords = coord.split(',')
    latitude = coords[0]
    longitude = coords[1]

    coordStr = 'latitude=' + latitude +  '&longitude=' + longitude
    #getHourlyWeather(citiesOrder, coordsStr)

    dayOfTheWeek = datetime.datetime.now().isoweekday() - 1
    print(dayOfTheWeek)

    tz = tf.timezone_at(lng=float(longitude), lat=float(latitude))
    print(tz)

    url = "https://api.open-meteo.com/v1/forecast?"
    url = url + coordStr + ("&wind_speed_unit=ms&daily=sunrise,sunset,weathercode,temperature_2m_max&forecast_days=12" + "&timezone=" + str(tz))
    response = requests.get(url)

    cityJson = response.json()
    print(cityJson)
    showForecast(message, city, cityJson)

def getForecast(message, cities):
    for city in cities:
        getCityForecast(message, city)


def getWeather(message, cities):
    for city in cities:
    #if len(cities) == 1: cities[0]
        getCityWeather(message, city)

    return

    table = pt.PrettyTable()
    table.padding_width=0
    table.align = "r"
    table.vrules=2
    table2 = ''

    table3 = pt.PrettyTable()
    table3.padding_width=0
    table3.align = "r"
    table3.vrules=2
    table4 = ''

    table5 = pt.PrettyTable()
    table5.padding_width=0
    table5.align = "r"
    table5.vrules=2
    table6 = ''

    #table.top_left_junction_char=''

    latitude = ''
    longitude = ''
    citiesOrder = []
    tz = ''
    for city in cities:
        coord = getCoordinatesByName(city)
        if coord:
            city = city.replace('-', '\\-').replace('.', '\.')
            citiesOrder += [city]
            coords = coord.split(',')
            latitude += (latitude and ',' or '') + coords[0]
            longitude += (longitude and ',' or '') + coords[1]
            if not tz:
                tz = tf.timezone_at(lng=float(coords[0]), lat=float(coords[1]))

    coordStr = 'latitude=' + latitude +  '&longitude=' + longitude
    #getHourlyWeather(citiesOrder, coordsStr)

    dayOfTheWeek = datetime.datetime.now().isoweekday() - 1
    daysNumber = (14 - dayOfTheWeek + 1)

    url = "https://api.open-meteo.com/v1/forecast?"
    url = url + coordStr + "&hourly=weathercode,temperature_2m&daily=sunrise,sunset,weathercode,temperature_2m_max&forecast_days=16" + "&timezone=" + tz
    response = requests.get(url)
    response_json = response.json()
    if len(citiesOrder) == 1:
        response_json = [response_json]
    print(response_json)

    counter = 0
    for cityJson in response_json:
        city = citiesOrder[counter]
        counter += 1
        if not table.field_names:
            fields = ['🏠°'] + [dt.strptime(t, '%Y-%m-%d').strftime("%A")[0:2] for t in cityJson['daily']['time'][:7 - dayOfTheWeek]]
            table.field_names = fields
            table3.field_names = ['🏠°'] + ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']
            table5.field_names = ['🏠°'] + [dt.strptime(t, '%Y-%m-%d').strftime("%A")[0:2] for t in cityJson['daily']['time'][14 - dayOfTheWeek: 21 - dayOfTheWeek]]
            #print(table)
            #table2 = pt.PrettyTable()
            #table2.padding_width=0
            #table2.align = "r"
            #table2.vrules=2
            #table2.hrules=pt.NONE
            #table2.header = False

        #tempNow = round(cityJson['current']['temperature_2m'])
        temps = cityJson['daily']['temperature_2m_max']
        weatherCodes = weatherCode and cityJson['daily']['weathercode'] or []

        cityHeader = (len(response_json) == 1) and '\(' + city + '\)' or ''
        #city = (len(cities) == 1) and '   ' or city
        row = [city[0:3]]
        row2 = ' ' + city[0:3] + ' '
        for i in range(0,7 - dayOfTheWeek):
            row += [round(temps[i])]
            if weatherCode:
                row2 += weatherCodeToText(weatherCodes[i])
        table.add_row(row)

        row3 = [city[0:3]]
        row4 = ' ' + city[0:3] + ' '
        for i in range(7 - dayOfTheWeek, 14 - dayOfTheWeek):
            row3 += [round(temps[i])]
            if weatherCode:
                row4 += weatherCodeToText(weatherCodes[i])
        table3.add_row(row3)

        row5 = [city[0:3]]
        row6 = ' ' + city[0:3] + ' '
        for i in range(14 - dayOfTheWeek, 21 - dayOfTheWeek):
            row5 += [round(temps[i])]
            if weatherCode:
                row6 += weatherCodeToText(weatherCodes[i])
        table5.add_row(row5)

        if weatherCode:
            table2 += row2 + '\n'
            table4 += row4 + '\n'
            table6 += row6 + '\n'

    sendBack(message, f'_Forecast: week 1 {cityHeader}_\n```{table}```\n' + table2
        + f'\n_Forecast: week 2 {cityHeader}_\n```{table3}```\n' + table4
        + f'\n_Forecast: week 3 {cityHeader}_\n```{table5}```\n' + table6, True)


    #if result:
    #    sendBack(message, result.replace('.', '\\.').replace('-', '\\-'))

@bot.message_handler(func=lambda message: True)
def menu(message):
    try:
        parts = message.text.split(' ')
        now = datetime.date.today() + datetime.timedelta(days=1)
        cmd = parts[0].lower()
        #print(parts)
        #print(message)
        if cmd in ['/weather', 'weather', '/погода', 'погода', 'погда']:
            cities = (len(parts) > 1) and parts[1:] or ['Annecy']
            getWeather(message, cities)
        elif cmd in ['/forecast', 'forecast', '/прогноз', 'прогноз', 'прогноз']:
            cities = (len(parts) > 1) and parts[1:] or ['Annecy']
            getForecast(message, cities)
        elif cmd in ['/elevation', 'высота', 'elevation', '/высота']:
            getElevation(message, parts[1:])
        elif cmd in ['/random','random','/случайно','случайно']:
            showRandom(message, parts[1:])
        elif len(parts) > 2 and cmd in ['ride', 'trip', '/t', '/r', 'b', 'поездка', 'тур', '/trip', '/ride', 'r', 't', 'трип']:
            radius=5000

            pos = 1
            seats = 1
            # try to get seats
            try:
                seats = int(parts[pos])
                pos += 1
            except:
                pass

            fromCity = parts[pos]
            toCity = parts[pos + 1]

            if toCity in ['gva', 'aero', 'aeroport']:
                radius = 3000

            year, month, days = now.year, now.month, [now.day]
            if len(parts) == 3:
                now7 = datetime.date.today() + datetime.timedelta(days=7)
                dateStart = '%d-%02d-%02d' % (year, month, now.day) + 'T00:00:00'
                dateEnd = '%d-%02d-%02d' % (now7.year, now7.month, now7.day) + 'T23:59:59'
            else:
                pos += 2
                # try to get year
                try:
                    possibleYear = int(parts[pos])
                    if possibleYear > 2020:
                        year = possibleYear
                        pos += 1
                except:
                    pass
                
                possibleMonth = MONTH_MAP.get(parts[pos].lower(), '')
                if possibleMonth:
                    pos += 1
                    month = int(possibleMonth)
                    
                dayStr = parts[pos]
                dayInt = int(dayStr)
                days = [dayInt]
                if len(parts) > pos + 1:
                    dayLast = int(parts[pos + 1])
                    days += [dayLast]#[x for x in range(dayInt + 1, dayLast + 1)]
                else:
                    days += [dayInt] #⛅️
                
                dateStart = '%d-%02d-%02d' % (year, month, days[0]) + 'T00:00:00'
                dateEnd = '%d-%02d-%02d' % (year, month, days[1]) + 'T23:59:59'
                print(days)
            
            #if len(days) > 10:
            #    sendBack(message, '10 days max\, please\. Thank you \;\)')
            #    days = days[0:10]

            isTrip = cmd in ['/t', 'trip', '/trip', 'тур', 't', 'трип']
            scanForDate(message, seats, dateStart, dateEnd, fromCity, toCity, radius)
            if isTrip:
                scanForDate(message, seats, dateStart, dateEnd, toCity, fromCity, radius)

            #scanForDate(message, when + 'T11:00:00', '', toCity, fromCity, radius)
            #for d in days:
            #    when = '%d-%02d-%02d' % (year, month, d)
            #    dateStart = isTrip and when + 'T00:00:00' or when
            #    dateEnd = isTrip and when + 'T15:00:00' or ''
            #    scanForDate(message, dateStart, dateEnd, fromCity, toCity, radius)
            #    if isTrip:
            #        scanForDate(message, when + 'T11:00:00', '', toCity, fromCity, radius)
        #else:
        #   #sendBack(message, 'command error, try help')
    except Exception as e:
        sendBack(message, 'oops, wtf?')
        print(e)

bot.set_my_commands([
    telebot.types.BotCommand("weather", "Weather Forecast"),
])

bot.polling(none_stop=True)
