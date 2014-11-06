import os
import webapp2
from google.appengine.ext import db

def cleanString(string):
    # Cleans strings, removing typical characters that cause 500's when copying and pasting
    # .replace(u'\ufeff', "") = replaces a very strange, non visible space w/ blank
    # .replace("\r\n","<br/>")) = replaces newlines with a <br/>
    # .replace(u'\u201c', '\"') & .replace(u'\u201d', '\"') = replace forward and backward quotes with regular ones
    # .replace(u'\u2013', "-") = replace em dashes with regular dash
    result = string.replace(u'\ufeff', "").replace("\r\n","<br/>").replace(u'\u201c', '\"').replace(u'\u201d', '\"').replace(u'\u2013', "-").replace("& ", "&amp; ")
    return result