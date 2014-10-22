from google.appengine.ext import webapp

from functions.getlots import *

###
# Views to add:
# Vertical - relates vertical_num to an actual name (eg 1 = 'health')


###### Views ######


### Basic Views ###

class Cities(db.Model):
    city_num = db.IntegerProperty() # 1 = Silicon Valley, 2 = SF, 3 = Boston, 4 = DC
    city = db.StringProperty() # Relates number to name

class Verticals(db.Model):
    vertical_num = db.IntegerProperty() # 1 = health.  No others for now
    vertical = db.StringProperty() # Relates number to name
    
class Quarters(db.Model):
    quarter_num = db.IntegerProperty() # 1 = Spring, 2 = Summer, 3 = Fall, 4 = Winter
    quarter = db.StringProperty() # Relates number to name (spring / summer etc.)


### Proper Views ###

class Events(db.Model):
    event_num = db.IntegerProperty() # Turns an event, meaning MedHack vs Ignition, into a number.  1 = ignition, 2 = medhack, 3 = conversation, 99 = partner
    event_id = db.StringProperty() # Unique ID for each individual event. Will be used to populate event url.
    name = db.StringProperty() # Event name, MedHack or Ignition for now.
    vertical = db.StringProperty()
    address = db.StringProperty()
    city = db.StringProperty()
    city_num = db.IntegerProperty()
    state = db.StringProperty()
    venue = db.StringProperty()
    day = db.IntegerProperty()
    month = db.IntegerProperty()
    year = db.IntegerProperty()
    quarter = db.StringProperty()
    full_date = db.DateProperty()
    header = db.StringProperty()  #look into purpose of this
    subheader = db.StringProperty()  #look into purpose of this
    description = db.StringProperty()
    link = db.StringProperty() #event link
    ticketing = db.TextProperty() # eventbrite ticketing information
    companies = db.StringProperty()
    publish = db.BooleanProperty()

class Challenges(db.Model): #Used for Monthly Challenges
    challege_title = db.StringProperty()
    story = db.StringProperty()
    challenge = db.StringProperty()
    value = db.StringProperty()
    schedule = db.ListProperty(basestring, default=[]) #See what StringListProperty does and if it's the right thing to do here
    advantages = db.StringProperty()
    approaches = db.StringProperty()
    unique_id = db.StringProperty()
    wrapup = db.StringProperty()
    post_img = db.BlobProperty() #a place to upload a hero image of the event post-dinner. Check if working, left unfinished.
    publish = db.BooleanProperty()

    
    
class Mentors(db.Model):
    id = db.StringProperty() # Semi duct taped.  Currently firstname_lastname.  Could cause issues for 2 people of same name, but unlikely for a while.
    mentor_id = db.StringProperty()
    name = db.StringProperty()
    title = db.StringProperty()
    company = db.StringProperty()
    bio = db.StringProperty(multiline=False)
    homepage = db.StringProperty()
    img_file = db.BlobProperty()
    image = db.BlobProperty()
    img_alt = db.StringProperty()
    tags = db.StringProperty() # What a mentor is good at. Used mostly in MedHacks
    linkedin = db.StringProperty()
    twitter = db.StringProperty()
    designation = db.StringListProperty() # mentor, advisor, client, friend, prebacked
    
    order = db.IntegerProperty() #{~} Deprecated. Needs to be replaced with "importance", for auto-ordering
    vertical = db.StringProperty() #{~} Deprecated. Was when we had to put a new entry for each mentor for each event
    event = db.StringProperty() #{~} Deprecated. Was when we had to put a new entry for each mentor for each event
    img = db.StringProperty()  #{~} Deprecated.  Was used when I couldn't figure out the BlobPropoerty - now no longer needed.

class Problems(db.Model):
    problem_id = db.StringProperty()
    title = db.StringProperty()
    statement = db.StringProperty()
    statement_long = db.StringProperty()
    company = db.ListProperty(basestring, default=[])
    value = db.StringProperty()
    #city_num = db.IntegerProperty()
    #vertical_num = db.IntegerProperty()
    #quarter_num = db.IntegerProperty()
    
class Teams(db.Model): #Used for winning teams in Monthly Challenges and MedHack
    team_id = db.StringProperty()
    name = db.StringProperty()
    homepage = db.StringProperty()
    img_file = db.BlobProperty() 
    blurb = db.StringProperty()

class Sponsors(db.Model):
    sponsor_id = db.StringProperty()
    name = db.StringProperty()
    homepage = db.StringProperty()
    img = db.StringProperty()
    img_file = db.BlobProperty() 
    img_alt = db.StringProperty()
    blurb = db.StringProperty()
    blurb_long = db.StringProperty()
    perk = db.StringProperty()

class Faq(db.Model):
    vertical = db.StringProperty()
    language = db.StringProperty()
    section = db.StringProperty()
    subsection = db.StringProperty()
    link = db.StringProperty()
    question = db.StringProperty()
    answer = db.StringProperty()
    order = db.IntegerProperty()
    created = db.DateTimeProperty(auto_now_add=True)

### Joiners ###    
class Mentors_Events(db.Model):
    mentor_id = db.StringProperty() #depreciated
    event_id = db.StringProperty() #depreciated
    mentor = db.ReferenceProperty(Mentors,
                                  required=False,
                                  collection_name='mentors')
    event = db.ReferenceProperty(Events,
                                  required=False,
                                  collection_name='events')
    mentor_type = db.IntegerProperty() # 1 = mentor, 2 = judge, 3 = both / panelist / VIP
    order = db.IntegerProperty() #used for sorting, is pulled from Mentor.order

class Cities_Events(db.Model):
    city_id = db.IntegerProperty() # 1 = Silicon Valley, 2 = SF, 3 = Boston, 4 = DC, 5 = mexico city
    event_id = db.StringProperty()
    
class Problems_Events(db.Model):
    problem_name = db.StringProperty()
    event_name = db.StringProperty()
    problem = db.ReferenceProperty(Problems,
                                  required=False,
                                  collection_name='problems')
    event = db.ReferenceProperty(Events,
                                  required=False,
                                  collection_name='problems_events')
    
class Sponsors_Events(db.Model):
    sponsor_name = db.StringProperty()
    event_name = db.StringProperty()
    subtype = db.StringProperty()
    sponsor = db.ReferenceProperty(Sponsors,
                                  required=False,
                                  collection_name='sponsors')
    event = db.ReferenceProperty(Events,
                                  required=False,
                                  collection_name='sponsors_events')
    
#######{~} "CMS"... ghetto CMS.  DEPRECATED - should be able to dump after Ignition re-write.  Double check Homepage stuff for dependancy too.
class Content(db.Model):
    vertical = db.StringProperty()
    page = db.StringProperty()
    subtype = db.StringProperty()
    header = db.StringProperty()
    content = db.StringProperty()
    content2 = db.StringProperty()
    link = db.StringProperty()
    img1 = db.StringProperty()
    alt1 = db.StringProperty()
    img2 = db.StringProperty()
    alt2 = db.StringProperty()
    order = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)

####### end "CMS"


class PrebackedTeam(db.Model):
    name = db.StringProperty()
    title = db.StringProperty()
    bio = db.StringProperty()
    homepage = db.StringProperty()
    pic = db.StringProperty()
    linkedin = db.StringProperty()
    twitter = db.StringProperty()
    order = db.IntegerProperty()


    
class BaseRequestHandler(webapp2.RequestHandler):
    def initialize(self, request, response):
        webapp.RequestHandler.initialize(self, request, response)
        if request.path.endswith("/") and not request.path == "/":
            redirect = request.path[:-1]
            if request.query_string:
                redirect += "?" + request.query_string
            return self.redirect(redirect, permanent=True)
        
        
        
        
        
        
        
        