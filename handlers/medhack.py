from google.appengine.ext.webapp import util, template
import urllib2
from google.appengine.api import urlfetch

from functions.getlots import *
from functions.getSponsors import *
from operator import itemgetter

from handlers.basehandler import *
import datetime

class MedHackPagesHandler(BaseRequestHandler):
    def get(self, url="/"):
        
        # Declare variables
        template_values = {}
        filePath = ""
        judges = ""
        mid_content = ''
        prizes = []
        #vcs = getVCS("index")
        tier_one_sponsors = []
        tier_two_sponsors = []
        tier_three_sponsors = []
        featured_sponsors = []
        col1 = [] 
        col2 = [] 
        col3 = []
        faqs = []
        problems = {}
        mentors=[]
        judges = []
        panelists = []
        mlist=[]

        
        
        
        #Set filepath
        filePath = '../templates/medhack_event_pages.html'
            
        
        #{~} Duct-taped. Makes medhack.prebacked.com display the upcoming MedHack, eventually need to make a separate page for MedHack
        # similar to lean startup machine, but for now is fine.
        if url == "/":
            all_events = db.GqlQuery("SELECT * FROM Events Where event_num = :1 ORDER BY full_date DESC", 2) #Pulls last MedHack that was posted
            current_event = all_events.get()
        else:
            current_event = db.GqlQuery("SELECT * FROM Events Where event_num = :1 AND event_id = :2 ORDER BY full_date DESC", 2, url).get()
            if current_event is None: #Throw exception for protection.
                self.error(404)
                template_values = {}
                path = os.path.join(os.path.dirname(__file__), '../templates/404.html')
                self.response.out.write(template.render(path, template_values))
                return

        current_event_id = current_event.event_id
        
        #########
        # Need to populate all the event constants (date, location, etc.) right here.
        #########
        e = current_event # Don't hate, I was lazy and didn't want to type current_event 100 times.
        if current_event.address:
            address = current_event.address
        if current_event.city:
            city = current_event.city
        if current_event.state:
            state = current_event.state
        if current_event.venue:
            venue = current_event.venue
        day = current_event.day
        month = current_event.month
        year = current_event.year
        quarter = current_event.quarter
        full_date = current_event.full_date
        ticketing = current_event.ticketing
        
        
        
          #Used here on out
        
        # Gather mentors, judges, and panelists for this event
        
        #### Proper way, but not sorting correctly
        mentors_events = db.GqlQuery("SELECT * FROM Mentors_Events WHERE event_id = :1 ORDER BY mentor_type DESC, order ASC", current_event_id)
        for m in mentors_events:
            if m.mentor_type == 1:
                mentors.append(m)
            if m.mentor_type == 2:
                judges.append(m)
            if m.mentor_type == 3:
                panelists.append(m)
        ####
        

        
        all_faq_categories = Faq.gql("WHERE vertical = :1 ORDER BY order", "medhack").fetch(100) #Eventually will want to parse this out by city someone is looking at for event FAQs.
        
        #all_faqs = db.GqlQuery("SELECT * FROM Faq ORDER BY order ASC", vert)
        #Poll faq_events
        #Iterate faq_events over all_faqs to get all_faq_categories
        
        
        ### Below is code for multi-section FAQs. It's brittle and ugly and should be killed ###
        # if all_faq_categories:
        #     ################## Brittle ##################
        #     #iterate through list of all FAQs and return distinct categories
        #     for l in all_faq_categories:
        #        if (l.section == 'section1'):
        #            col1.append(l)
        #        elif (l.section == 'section2'):
        #            col2.append(l)
        #        elif (l.section == 'section3'):
        #            col3.append(l)
                   
        #     faqs = [
        #             [col1,"col1", "Event questions"],
        #             [col2,"col2", "Participant questions"],
        #             [col3,"col3", "Mentor questions"]
        #             ]
            
        #     ################################################
        sponsors = ""
        tier_one_sponsors = Sponsors_Events.gql("WHERE event_name = :1 AND subtype = :2", url, "corporate sponsor").fetch(20)

        try:
            tier_one_sponsors_count = len(tier_one_sponsors)
        except:
            tier_one_sponsors_count = 0
        
        tier_two_sponsors = Sponsors_Events.gql("WHERE event_name = :1 AND subtype = :2", url, "service provider sponsor").fetch(20)
        try:
            tier_two_sponsors_count = len(tier_two_sponsors)
        except:
            tier_two_sponsors_count = 0
        
        tier_three_sponsors = Sponsors_Events.gql("WHERE event_name = :1 AND subtype = :2", url,"api sponsor").fetch(20)

        media_partners = Sponsors_Events.gql("WHERE event_name = :1 AND subtype= :2", url, "media partner").fetch(20)
        
        featured_sponsors = tier_one_sponsors + tier_two_sponsors    
        all_sponsors = tier_one_sponsors + tier_two_sponsors + tier_three_sponsors
        
        date_is_passed = date_passed(year, month, day)
        event_over = date_is_passed
        
        template_values.update(locals())

        path = os.path.join(os.path.dirname(__file__), filePath)
        self.response.out.write(template.render(path, template_values))

class MedHackSponsorHandler(BaseRequestHandler): #sends requests to the /medhack/sponsor page, showing sponsorship options
    def get(self, url="/"):
        template_values={}
        filePath = '../templates/medhack_sponsors.html'
        path = os.path.join(os.path.dirname(__file__), filePath)
        self.response.out.write(template.render(path, template_values))
    


def date_passed(year = "2010", month = "1", day = "1"):
    test_day = datetime.date(year, month, day)
    todays_date = datetime.date.today()
    if todays_date >= test_day:
        return True
    else:
        return False
    
