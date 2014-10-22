from google.appengine.ext.webapp import util, template
from google.appengine.api import images


from functions.getlots import *

from handlers.basehandler import *
import datetime

#  PDF stuff - not going to be used for a while, if ever
#from reportlab.pdfgen import canvas
#from reportlab.lib.pagesizes import A4

class AdminAddHandler(webapp2.RequestHandler):
    ### TODO ###
    # Build a way to update current mentors
    ############
    def get(self):
        mentor_id = None
        template_values = {}
        mentors = db.GqlQuery("SELECT * FROM Mentors ORDER BY name ASC")        
        events = db.GqlQuery("SELECT * FROM Events WHERE full_date >= :1 and event_num in :2 ORDER BY full_date ASC", datetime.date.today()-datetime.timedelta(days=2), [1,2,3,4,5,6,7,8,9])
        
        
        try:
            message = str(self.request.get('msg'))
        except:
            message = None
            
            
        ### fix title issue ###
        for m in mentors:
            string = str(m.title)
            sliced = string.split(':')
            if m.company is None:
                try:    
                    m.company = sliced[1]
                except:
                    m.company = m.company
            m.title = sliced[0]
            m.put()
        #######################
            
        template_values.update(locals())
        
        page = "../templates/mentor_add.html"
        path = os.path.join(os.path.dirname(__file__), page)
        self.response.out.write(template.render(path, template_values))
        
    def post(self):
        mentor = {}
        mentor_id = None
        template_values = {}
        mentors = db.GqlQuery("SELECT * FROM Mentors ORDER BY name ASC")
        events = db.GqlQuery("SELECT * FROM Events ORDER BY name ASC")
        url = "admin_add"
        
        template_values.update (mentors = mentors, events = events)
        
        ######
        
        message = ""
        tags = ""
        
        mentor_event = Mentors_Events()
        
            
        
        #Common to both
        if self.request.get('id'):
            mentor_id = str(self.request.get('id'))
            event_id = str(self.request.get('event'))
            
            mentor = Mentors(key_name = mentor_id)
            
            mentor.mentor_id = mentor_id
            mentor.id = mentor_id
            mentor_event.mentor_id = mentor_id # Depreciated (now use the reference property 'mentor')
            mentor_event.event_id = event_id
            
            
        if self.request.get('title') or self.request.get('company'):        # For adding a new mentor
            mentor_name = str(self.request.get('name'))
            if self.request.get('edit'):                #Check if intentionally editing
                mentor = Mentors.gql("WHERE name = :1", mentor_name).get()
            
            if Mentors.gql("WHERE name = :1", mentor_name).get() and not self.request.get('edit'):       # Make sure we're not saving a duplicate
                message = "Warning, duplicate detected!  Nothing saved"
            else:
                mentor.name = mentor_name
                title = str(self.request.get('title')).split(':')
                if title[0] == "None":
                    mentor.title = None
                else:
                    mentor.title = title[0]
                
                company = str(self.request.get('company'))
                if company == "None":
                    company = None
                mentor.company = company
                
                if (self.request.get('img')):
                    pic = self.request.get('img')
                    mentor.img_file = db.Blob(pic)

                try:
                    designation = self.request.get('designation', allow_multiple=True)
                except:
                    designation = {"friend"}
        
                bio = str(self.request.get('bio').replace(u'\ufeff', "").replace("\r\n","<br/>")) #replaces a very strange, non visible space w/ blank then replaces newlines with a <br/>
                
                mentor.bio = bio
                
                ## Capitalize first letter of each tag
                raw_tags = str(self.request.get('tags')).replace(',', ';')
                list_tags = raw_tags.split('; ')
                for t in list_tags[:-1]:
                    tags = tags + t.capitalize() + "; "
                tags = tags + list_tags[-1]
                ## End tags section
                
                mentor.tags = tags
                mentor.img = mentor.mentor_id + ".jpg"
                mentor.img_alt = mentor.name
                mentor.designation = designation
                #mentor.homepage = str(self.request.get('homepage'))
                #mentor.tags = str(self.request.get('tags'))
                #mentor.linkedin = str(self.request.get('linkedin'))
                #mentor.twitter = str(self.request.get('twitter'))
                mentor.order = int(self.request.get('order'))
                message = ("saved! " + str(mentor.name))
                mentor.put()
                
        elif self.request.get('id'):        #For connecting a mentor to an event
            if Mentors_Events.gql("WHERE mentor_id = :1 AND event_id = :2", mentor_id, event_id).get():       # Make sure we're not saving a duplicate
                message = "Warning, duplicate detected!  Nothing saved"
            else:    
                the_event = Events.gql("WHERE event_id = :1", event_id).get()
                the_mentor = Mentors.gql("WHERE mentor_id = :1", mentor_id).get()
                
                mentor_event.event = the_event
                mentor_event.event_id = event_id #Mostly depreciated, used to easily read entries
                mentor_event.mentor = the_mentor
                mentor_event.mentor_id = mentor_id #Mostly depreciated, used to easily read entries
                mentor_event.order = the_mentor.order
                mentor_event.mentor_type = int(self.request.get('mentor_type'))
                
                message = mentor.mentor_id + " added to " + mentor_event.event_id
                
                mentor_event.put()
        else:       #Triggered only if nothing is entered.
            message = "Error, nothing saved to database"
            
        ######
        
        
        page = "/admin_add?" + "msg=" + message
        self.redirect(page)


class FaqAddHandler(webapp2.RequestHandler):
    def get(self):
        template_values = {}
        page = "../templates/faqadd.html"
        path = os.path.join(os.path.dirname(__file__), page)
        self.response.out.write(template.render(path, template_values))
        
    def post(self):
        template_values = {}
        
        faq = Faq()
        
        faq.question = str(self.request.get('question'))
        faq.answer = str(self.request.get('answer'))
        faq.vertical = str(self.request.get('vert'))
        faq.language = str(self.request.get('language')) 
        faq.section = str(self.request.get('section'))
        faq.subsection = str(self.request.get('subsection'))
        faq.link = str(self.request.get('link'))
        
        faq.order = int(self.request.get('order'))
        faq.put()

        
        message = ("saved! " + str(faq.question))
        template_values.update (message = message)
        redir = "/admin_add/faq_add" + "#saved_" + str(faq.question)
        
        self.redirect(redir)




class EventAddHandler(webapp2.RequestHandler):
    def get(self):
        template_values = {}
        
        try:
            event_edit = Events.gql("WHERE full_date >= :1 ORDER BY full_date", datetime.date.today()-datetime.timedelta(days=2))
        except:
            event_edit = {}
        
        try:
            past_events = Events.gql("WHERE full_date < :1 ORDER BY full_date", datetime.date.today()-datetime.timedelta(days=2))
        except:
            past_events = {}    
            
            
        message = ""
        if self.request.get('msg'):  # Pass a message back from the post
            msg = self.request.get('msg')
            message = msg
            
        if self.request.get('eventLink'):  # Grab the event link from post
            eventLink = self.request.get('eventLink')
            message = msg
            
        
        template_values.update (locals())
        page = "../templates/eventadd.html"
        path = os.path.join(os.path.dirname(__file__), page)
        self.response.out.write(template.render(path, template_values))
        
    def post(self):
        template_values = {}
        event_num = 0
        
        #city_event = Cities_Events()
        
        if str(self.request.get('edit')):
            event = Events.gql("WHERE event_id = :1", str(self.request.get('event_id'))).get()
        else:
            event = Events()
        
        event.vertical = str(self.request.get('vertical'))
        
        if self.request.get('type'):
            event_type = str(self.request.get('type'))
        else:
            event_num = int(self.request.get('event_num'))
            event_type = event_num
        
        if self.request.get('header'):
            event.header = str(self.request.get('header'))
        else:
            event.header = ""
        if self.request.get('description'):
            event.description = str(self.request.get('description'))
        else:
            event.description = ""
        
        if self.request.get("ticketing"):
            event.ticketing = str(self.request.get("ticketing"))
        
        #Name handling
        if (event_type == "ignition" or event_type == "medhack"):
            event.name = event_type
        elif (event_type == "conversations" or event_num == 3):
            event.name = "conversations" + " - " + event.header
        else:
            event.name = str(self.request.get('name')) # Catches partner events, which have varying names
            
        if self.request.get('link'):
            event.link = str(self.request.get('link')) # Saves the event link for a partner event
                #should have it make sure it begins w/ http://

        if event_type == "conversations":
            event.link = "/conversations"
        event.state = str(self.request.get('state'))
        event.venue = str(self.request.get('venue'))
        event.address = str(self.request.get('address'))
        event.day = int(self.request.get('day'))
        
        month = int(self.request.get('month'))
        event.month = month
        
        event.year = int(self.request.get('year'))
        
        # select quarter for event
        quarter = None
        if (1 <= month <= 3):
            quarter = "winter"
        elif (4 <= month <= 6):
            quarter = "spring"
        elif (7 <= month <= 9):
            quarter = "summer"
        elif (10 <= month <= 12):
            quarter = "fall"
        event.quarter = quarter
        
        #if self.request.get('quarter'):
        #    event.quarter = str(self.request.get('quarter'))
        
        
        
        if self.request.get('publish'):
            event.publish = True
        else:
            event.publish = False
        full_datetime = datetime.date(event.year, event.month, event.day)
        event.full_date = full_datetime
        city = str(self.request.get('city'))
        event.city = city
        
        
###  Needs update on rebrand       
        # Populates event_num. Ghetto, but there's only 2 events so... deal with it
        # edit - more events, still ghetto
        
        # 1 - 8 = has own page and is a prebacked event
        # 9 is reserved
        # 11+ = posted to events board with link
        if (event.name == "ignition"):
            event_num = 1
        elif (event.name == "medhack" or event.name == "boost" or event.name == "boostmed"):
            event_num = 2
        elif (event_type == "conversations"):
            event_num = 3
        elif (event_type == "accelerator"):
            event_num = 11
        elif (event_type == "prebacked_other"):
            event_num = 12
        elif (event_type == "partner_event"):
            event_num = 99
        
        
        
        event.event_num = event_num
        
        #eventID is crucial.  URL and all joiners are dependent.  
        if (1 <= event_num <= 2):
            eventID = city.lower().replace (" ", "-") + "-" + str(event.quarter).lower() + "-" + str(event.year) # Traslated: /event-city-quarter-year    
        elif (event_num == 3):
            eventID = "conversations" + "-" + city.lower().replace (" ", "-") + "-" + str(event.month) + "-" + str(event.year) # Traslated: /conversations-city-month-year
        elif (event_num == 99):
            eventID = event.name.lower().replace (" ", "-") + "-" + city.lower().replace (" ", "-") + "-" + str(event.month) + "-" + str(event.day) + "-" + str(event.year) # Traslated: /conversations-city-month-day-year    
        
        event.event_id = eventID
        
        #  Cities_Events doesn't have much point.  No plan to have > 1 event per quarter per location.
        #city_event.event_id = eventID
        #city_event.city_id = city_num
        #city_event.put()
        
        

        # sets link to be shown on event_add page (for easy reference, not public facing)
        if (1 <= event_num <= 2):
            eventLink = "/" + event.name + "/" + eventID
            event.link = eventLink
        elif (event_num == 3):
            eventLink = "/conversations"
        elif 11<= event_num <=19 :
            eventLink = "/events"
        elif event_num == 99 :
            eventLink = "/events"    
        

        event.put()
        
        #Let user know they successfully added an event.    
        if event.publish:
            message = '"' + event.name + '"' + " was edited and is published"
            redir = "event_add?msg=" + message + "&eventLink=" + eventLink
        elif self.request.get('edit'):
            message = '"' + event.name + '"' + " was edited but isn't published"
            redir = "event_add?msg=" + message
        else:
            message = event.name + " added, to be held at " + event.venue + " on " + str(event.month) + "/" + str(event.day)  + "/" + str(event.year) + " but still needs to be published."
            redir = "event_add?msg=" + message
        
        template_values.update (message = message, eventLink = eventLink)
        self.redirect(redir)




class SponsorAddHandler(webapp2.RequestHandler):
    def get(self):
        template_values = {}
        page = "../templates/sponsor_add.html"
        message = ""
        if self.request.get('msg'):  # Pass a message back from the post
            msg = self.request.get('msg')
            message = msg
        
        sponsors = db.GqlQuery("SELECT * FROM Sponsors ORDER BY name ASC")
        events = Events.gql("WHERE full_date > :1 ORDER BY full_date ASC", datetime.date.today())
        
        template_values.update (locals())
        path = os.path.join(os.path.dirname(__file__), page)
        self.response.out.write(template.render(path, template_values))
        
    def post(self):
        template_values = {}
        page = "../templates/sponsor_add.html"
        
        ######
        
        message = ""
        
        sponsor_event = Sponsors_Events()
        sponsor = Sponsors()
            
        #Common to both

        sponsor_name = str(self.request.get('name'))
        sponsor_id = sponsor_name.lower().replace(" ", "_")
        event_id = str(self.request.get('event'))
        
        if self.request.get('blurb'):                                                   # For adding a new mentor
            sponsor.name = sponsor_name
            sponsor.sponsor_id = sponsor_id
            
            if Sponsors.gql("WHERE name = :1", sponsor_name).get() and not self.request.get('edit'): # Make sure we're not saving a duplicate
                message = "Warning, duplicate detected!  Nothing saved"
            else:
                if self.request.get('edit'):
                    sponsor = Sponsors.gql("WHERE name = :1", sponsor_name).get()
                
                sponsor.blurb = str(self.request.get('blurb')) #
                if str(self.request.get('blurb_long')) != "":
                    sponsor.blurb_long = str(self.request.get('blurb_long'))
                else:
                    sponsor.blurb_long = sponsor.blurb
                
                if (self.request.get('logo')):
                    pic = self.request.get('logo')
                    sponsor.img_file = db.Blob(pic)
                

                sponsor.img = sponsor.name.lower().replace (" ", "_") + ".png"
                sponsor.img_alt = "Sponsor " + sponsor.name
                if str(self.request.get('homepage')).split('www')[0]=='http://':
                    sponsor.homepage = str(self.request.get('homepage'))
                else:
                    sponsor.homepage = "http://" + str(self.request.get('homepage'))
                message = ("saved! " + str(sponsor.name))
                sponsor.put()
        elif self.request.get('event'):                                                 #For adding a mentor to an event
            
            the_event = Events.gql("WHERE event_id = :1", event_id).get()
            the_sponsor = Sponsors.gql("WHERE name = :1", sponsor_name).get()
            
            if Sponsors_Events.gql("WHERE event = :1 AND sponsor = :2", the_event, the_sponsor).get():  # Check for duplicates
                message = "Warning, duplicate detected!"
            else:
                sponsor_event.subtype = str(self.request.get('subtype'))
                sponsor_event.event = the_event
                sponsor_event.event_name = event_id #Mostly depreciated, used to easily read entries
                sponsor_event.sponsor = the_sponsor
                sponsor_event.sponsor_name = sponsor_id
                #Mostly depreciated, used to easily read entries
                
                sponsor_event.put()
                
                message = sponsor_name + " added to " + event_id
        else:
            message ="Nothing saved to database"
        
        self.redirect("sponsor_add?msg=" + message)




class ProblemAddHandler(webapp2.RequestHandler):
    def get(self):
        template_values = {}
        page = "../templates/problem_add.html"
        events = db.GqlQuery("SELECT * FROM Events WHERE event_num = :1 AND full_date > :2 ", 1, datetime.date.today())
        companies = db.GqlQuery("SELECT * FROM Sponsors ORDER BY name ASC")
        
        problems = db.GqlQuery("SELECT * FROM Problems")

        
        if self.request.get("msg"):
            message = self.request.get("msg")
        
        template_values.update(locals())
        path = os.path.join(os.path.dirname(__file__), page)
        self.response.out.write(template.render(path, template_values))
        
        
    def post(self):
        template_values = {}
        message = ""
        
        problem = Problems()
        problem_event = Problems_Events()
    
    
        if self.request.get('event_id'):                                        # Link a problem to an event
            problem_id = str(self.request.get("problem_id"))
            event_id = str(self.request.get("event_id"))
            
            if Problems_Events.gql("WHERE event_name = :1 AND problem_id = :2", event_id, problem_id).get():       # Make sure we're not saving a duplicate
                message = "Warning, duplicate detected!  Nothing saved"
            else:
    ############
                event_link = Events.gql("WHERE event_id = :1", event_id).get()
                problem_link = Problems.gql("WHERE problem_id = :1", problem_id).get()
                
                problem_event.problem = problem_link
                problem_event.event = event_link
                problem_event.problem_name = problem_id
                problem_event.event_name = event_id
                
                problem_event.put()
                message = "Linked " + problem_id + " to " + event_id
                
        elif self.request.get('statement'): #create a new problem or updates an old one
            
            
            title = str(self.request.get('title'))
            company_list = self.request.get_all('company')
            
            company = ""
            for c in company_list:  
                if company == "":
                    company = c
                else:
                    company = company + ';  ' + c
            
            # Determine if we're creating a new problem or updating an old one.
            if (Problems.gql("WHERE problem_id = :1", str(self.request.get("problem_id"))).get()) is not None:
                problem_id = str(self.request.get("problem_id"))
                problem = Problems.gql("WHERE problem_id = :1", problem_id).get()
                message = "Problem updated: " + title
            else:
                message = "New problem created: " + title + " " + company
            
            
            problem.title = title
            problem.statement = str(self.request.get('statement'))
            problem.company = company_list
            dollars = self.request.get("value").replace("$", "")
            problem.value = dollars
            
            
            problem_id = title.lower().replace(" ", "_") + "_" + company.lower().replace(" ", "_")
            problem.problem_id = problem_id
            
            problem.put()
            
        else:
            message = "There was an error"
    
        template_values.update (message = message)    
        self.redirect("/admin_add/problem_add?msg=" +  message)
        


class PrintNameHandler(webapp.RequestHandler):
    def get(self):
        template_values = {}
        page = "../templates/printtags.html"
        judges = db.GqlQuery("SELECT * FROM Mentors WHERE vertical = 'health' ORDER BY order ASC") #right now statically picks all from vert = "health", bad bad bad
        template_values.update (judges = judges)
        
        ##PDF stuff - too complex, use HTML to PDF API
        #self.response.headers['Content-Type'] = 'application/pdf'
        #self.response.headers['Content-Disposition'] = 'attachment; filename=my.pdf'
        #c = canvas.Canvas(self.response.out, pagesize=A4)
        #
        #c.drawString(100, 100, "Hello world")
        #c.showPage()
        #c.save()
        #end pdf
        
        path = os.path.join(os.path.dirname(__file__), page)
        self.response.out.write(template.render(path, template_values))
        
        
def split_name(self):
    the_name = self.split();
    return the_name[0] + '<br/>' + the_name[1];
