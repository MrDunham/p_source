import os
import webapp2
from google.appengine.ext import db

def pickVert():
    url = os.environ['HTTP_HOST'].split(':')[0];
    url2 = os.environ['HTTP_HOST'].split('.')[0];
    if (url == "prehack.prebacked.com") or (url == "medhack.prebacked.com") or (url2 == "medhack"):
        vert = 'medhack'
    elif (url == "education.prebacked.com"):
        vert = 'education'
    elif (url == "finance.prebacked.com"):
        vert = 'finance'
    elif (url == "data.prebacked.com") or (url2 == "data") or  (url == "ignition.prebacked.com") or (url == "health.ignition.prebacked.com"):
        vert = 'health'
    else:
        vert = "home"
    return vert;

# put '(url == "health.prebacked.com") or (url2 == "health") or'  back before data.prebacked.com when ready to go live

def pickCity(city):
#later on this should cross reference the city database to get number based on name
    if (city.lower() == "silicon valley"):
        city_num = 1
    elif (city.lower() == "sf"):
        city_num = 2
    elif (city.lower() == "boston"):
        city_num = 3
    elif (city.lower() == "washington dc"):
        city_num = 4
    elif (city.lower() == "mexico city"):
        city_num = 5
    return city_num