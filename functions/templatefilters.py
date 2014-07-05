from google.appengine.ext import webapp
from datetime import date, timedelta

register = webapp.template.create_template_register()

def add_a_day(value):
    new_date = value + timedelta(days=1)
    return new_date

register.filter(add_a_day)