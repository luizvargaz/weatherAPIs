from time import gmtime
import requests
from pytz import timezone, utc
from datetime import datetime, timedelta
#import pandas as pd
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

import redis

app = Flask(__name__)
cache = redis.Redis(host='redis', port=6379)

@app.route('/', methods = ['GET', 'POST'])
def index():
    if request.method == 'POST':
        location = request.form.get('city')
        lat, lon = location.split(',')

        loc = {
            'lat': lat,
            'lon': lon
        }

    else:
        location = 'No method POST'

    if not location == 'No method POST':

        """url_coor = 'http://api.ipstack.com/check?access_key=005bdacb79427e7b7fb68b93342e0e07'
        r_coor = requests.get(url_coor).json()

        loc = {
            'latitude':r_coor['latitude'],
            'longitude':r_coor['longitude'],
            'city':r_coor['city'],
            'country': r_coor['country_name'],
        }"""

        ####################
        ##### OpenWeather

        url_OpenWeather = 'http://api.openweathermap.org/data/2.5/weather?{}&appid=9f84e8e5d7240be8ce15d4642864972f&units=metric&lang=es'
        #coordinates = 'lat='+str(loc['latitude'])+ '&lon=' + str(loc['longitude'])
        coordinates = 'lat=' + lat + '&lon=' + lon

        request_OpenWeather = requests.get(url_OpenWeather.format(coordinates)).json()

        OpenWeather = {
            'temperature': request_OpenWeather['main']['temp'],
            'description': request_OpenWeather['weather'][0]['description'],
            'icon': request_OpenWeather['weather'][0]['icon'],
            'wind_speed': request_OpenWeather['wind']['speed'],
            'wind_deg': request_OpenWeather['wind']['deg'],
            'humidity': request_OpenWeather['main']['humidity'],
            'pressure': request_OpenWeather['main']['pressure'],
            'visibility': request_OpenWeather['visibility'],
            'tem_max': request_OpenWeather['main']['temp_max'],
            'tem_min': request_OpenWeather['main']['temp_min'],
            'date': request_OpenWeather['dt'],
            'time_zone': request_OpenWeather['timezone'],
            'city': request_OpenWeather['name'],
            'country': request_OpenWeather['sys']['country'],
            'longitude': request_OpenWeather['coord']['lon'],
            'latitude': request_OpenWeather['coord']['lat']
        }

        correct_date = OpenWeather['date'] + OpenWeather['time_zone']
        dt_OpenWeather = '{}-{}-{} {}:{}:{}'.format(*gmtime(correct_date))
        #dt_OpenWeather = pd.to_datetime(correct_date, unit='s')

        OpenWeather.update({'dt': dt_OpenWeather})

        ##### /OpenWeather
        ####################

        ####################
        ##### Weatherbit

        url_Weatherbit = 'http://api.weatherbit.io/v2.0/current?&{}&key=dc88358548db4d728b5c1a9052e090b8'
        coordinates = 'lat=' + lat + '&lon=' + lon
        request_Weatherbit = requests.get(url_Weatherbit.format(coordinates)).json()

        Weatherbit = {
            'temperature': request_Weatherbit['data'][0]['app_temp'],
            'description': request_Weatherbit['data'][0]['weather']['description'],
            'icon': request_Weatherbit['data'][0]['weather']['icon'],
            'wind_speed': request_Weatherbit['data'][0]['wind_spd'],
            'wind_deg': request_Weatherbit['data'][0]['wind_cdir_full'],
            'precipitation': request_Weatherbit['data'][0]['precip'],
            'pressure': request_Weatherbit['data'][0]['pres'],
            'visibility': request_Weatherbit['data'][0]['vis'],
            'date': request_Weatherbit['data'][0]['ob_time'],
            'time_zone': request_Weatherbit['data'][0]['timezone'],
            'city': request_Weatherbit['data'][0]['city_name'],
            'country': request_Weatherbit['data'][0]['country_code'],
            'longitude': request_Weatherbit['data'][0]['lon'],
            'latitude': request_Weatherbit['data'][0]['lat'],
            'clouds': request_Weatherbit['data'][0]['clouds'],
            'solar_rad': request_Weatherbit['data'][0]['solar_rad'],
        }

        date_Weatherbit_noUTC = datetime.strptime(Weatherbit['date'], '%Y-%m-%d %H:%M')

        #print('date_Weatherbit_noUTC ', date_Weatherbit_noUTC , type(date_Weatherbit_noUTC ))
        date_Weatherbit = date_Weatherbit_noUTC.replace(tzinfo= utc)

        dt_Weatherbit = date_Weatherbit.astimezone(timezone(Weatherbit['time_zone']))

        # date_Weatherbit = pd.to_datetime(Weatherbit['date'])
        #date time conversion with pandas
        #tz_Weatherbit = Weatherbit['time_zone']
        #dt_Weatherbit = date_Weatherbit.tz_localize('UTC').tz_convert(tz_Weatherbit)

        Weatherbit.update({'dt': dt_Weatherbit})
        ##### /Weatherbit
        ####################

        ####################
        ##### darkSky

        url_DarkSky = 'https://api.darksky.net/forecast/45b194154f45f62b287e3a3e40dc2593/19.530508,-98.847903?units=si&lang=es'
        coordinates = 'lat=' + lat + ',lon=' + lon
        request_DarkSky = requests.get(url_DarkSky.format(coordinates)).json()

        DarkSky = {
            'temperature': request_DarkSky['currently']['temperature'],
            'description':request_DarkSky['currently']['summary'],
            'icon': request_DarkSky['currently']['icon'],
            'wind_speed': request_DarkSky['currently']['windSpeed'],
            'windGust': request_DarkSky['currently']['windGust'],
            'precipitation': request_DarkSky['currently']['precipIntensity'],
            'precip_probability': round(request_DarkSky['currently']['precipProbability']*100),
            'pressure': request_DarkSky['currently']['pressure'],
            'visibility': request_DarkSky['currently']['visibility'],
            'date': request_DarkSky['currently']['time'],
            'time_zone': request_DarkSky['timezone'],
            'longitude': request_DarkSky['longitude'],
            'latitude': request_DarkSky['latitude'],
            'clouds': round(request_DarkSky['currently']['cloudCover']*100),
            'humidity': round(request_DarkSky['currently']['humidity']*100)
        }

        date_DarkSky_noUTC = datetime.strptime('{}-{}-{} {}:{}:{}'.format(*gmtime(DarkSky['date'])), '%Y-%m-%y %H:%M:%S')
        date_DarkSky = date_DarkSky_noUTC.replace(tzinfo=utc)
        dt_DarkSky = date_DarkSky.astimezone(timezone(DarkSky['time_zone']))

        # Pandas convertion
        #date_DarkSky = pd.to_datetime(DarkSky['date'], unit='s')
        #tz_DarkSky = DarkSky['time_zone']
        #dt_DarkSky = date_DarkSky.tz_localize('UTC').tz_convert(tz_DarkSky)

        DarkSky.update({'dt': dt_DarkSky})

        #Weatherbit.update({'dt': dt_Weatherbit})

        ##### /darksky
        ####################

        return render_template('weather.html', OpenWeather = OpenWeather, Weatherbit = Weatherbit, DarkSky = DarkSky, loc = loc)

    else:

        return render_template('location.html')

if __name__ == '__main__':
    #app.run(host='0.0.0.0')
    app.run(debug=True)