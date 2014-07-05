from google.appengine.ext.webapp import util, template

from functions.getlots import *

from handlers.basehandler import *

#  PDF stuff - not going to be used for a while, if ever
#from reportlab.pdfgen import canvas
#from reportlab.lib.pagesizes import A4

class AdminAddHandler(BaseHandler):
    def get(self, text=""):
        message = text
        template_values = {}
        mentors = db.GqlQuery("SELECT * FROM Mentors ORDER BY name ASC")
        events = db.GqlQuery("SELECT * FROM Events ORDER BY name ASC")
        url = "admin_add"
        
        template_values.update (mentors = mentors, events = events)
        
        page = "../templates/adminadd.html"
        template_values.update (message = message)
        path = os.path.join(os.path.dirname(__file__), page)
        self.response.out.write(template.render(path, template_values))
        
    def post(self):
        template_values = {}
        message = "error"
        
        mentor_event = Mentors_Events()
        mentor = Mentors()
        
        #Common to both
        mentor.id = str(self.request.get('id'))
        mentor_event.mentor_id = mentor.id
        mentor_event.event_id = str(self.request.get('event'))
        

        #For updating an existing mentor
        if self.request.get('id'):
            message = mentor.id + " added to " + mentor_event.event_id
            #mentor_event.mentor_id = 
            
        
        # For adding a new mentor
        if self.request.get('title'):
            mentor.name = str(self.request.get('name'))
            mentor.title = str(self.request.get('title'))
            mentor.bio = str(self.request.get('bio'))
            mentor.img = mentor.id + ".jpg"
            mentor.img_alt = mentor.name
            #mentor.homepage = str(self.request.get('homepage'))
            #mentor.tags = str(self.request.get('tags'))
            #mentor.linkedin = str(self.request.get('linkedin'))
            #mentor.twitter = str(self.request.get('twitter'))
            mentor.order = int(self.request.get('order'))
            message = ("saved! " + str(mentor.name))
            mentor.put()
            
        
        
        
        ### Damn blob thing.  This saves the file name, but not sure if it does anything else.
        #img_file = str(self.request.get('img_file'))
        #mentor.img_file = db.Blob(img_file)
        ### /

        if ((mentor_event.event_id != "") or (mentor.title != "")): #check to make sure one of the options was filled out
            mentor_event.put()
            
        
        
        template_values.update (message = message)
        page = "../templates/adminadd.html"
        path = os.path.join(os.path.dirname(__file__), page)
        #self.response.out.write(template.render(path, template_values))
        self.redirect("/admin_add", message)
        
        
class FaqAddHandler(BaseHandler):
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




class EventAddHandler(BaseHandler):
    def get(self):
        template_values = {}
        
        page = "../templates/eventadd.html"
        path = os.path.join(os.path.dirname(__file__), page)
        self.response.out.write(template.render(path, template_values))
        
    def post(self):
        template_values = {}
        
        template_values = {}
        
        event = Events()
        city_event = Cities_Events()
        
        event.name = str(self.request.get('name'))
        event.vertical = str(self.request.get('vertical'))
        event.state = str(self.request.get('state'))
        event.venue = str(self.request.get('venue'))
        event.address = str(self.request.get('address'))
        event.day = int(self.request.get('day'))
        event.month = int(self.request.get('month'))
        event.year = int(self.request.get('year'))
        event.quarter = str(self.request.get('quarter'))
        event.full_date = str(event.day) + "/" + str(event.month) + "/" + str(event.year)
        city = str(self.request.get('city'))
        event.city = city
        
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
        
        # Populates event_num. Ghetto, but there's only 2 events so... deal with it
        if (event.name == "prebacked_ignition"):
            event_num = 1
        elif (event.name == "medhack"):
            event_num = 2
        
        event.event_num = event_num
            
        eventID = event.name.lower().replace (" ", "_") + "_" + str(event.quarter).lower() + "_" + str(event.year)
        event.event_id = eventID
        
        city_event.event_id = eventID
        city_event.city_id = city_num
        
        event.put()
        city_event.put()
        
        #Let user know they successfully added an event.
        message = event.name + " added, to be held at " + event.venue + " on " + str(event.month) + "/" + str(event.day)  + "/" + str(event.year)
   
        template_values.update (message = message)
        page = "../templates/eventadd.html"
        path = os.path.join(os.path.dirname(__file__), page)
        self.response.out.write(template.render(path, template_values))



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