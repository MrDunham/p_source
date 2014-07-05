from google.appengine.ext.webapp import util, template
import datetime

from functions.getlots import *
from functions.getSponsors import *

from handlers.basehandler import *
from google.appengine.api import users



######
# To make this really robust, I need to have:
# - no more using a special html page (eg ignition_bcbs) but using the template and populating it
# - all queries go off something other than Vert (event_id likely)
# - Problems pulled from the problem database. Problem database needs updating
# - Details populated into the template based on a database call
# - Update to pick judges based on the event(s) they're associated with.
# - Need a new database called mentors_events to link two, and a third of just events
# - sponsors(), found in 'getlots.py' needs to be updated to check based on event
# - a sponsor_add page would be nice
# - an Section database to refer section_num and the section name for an FAQ.
# -- Also need to actually use section numbers vs current sort by section1, section2, ect.




class IgnitionPagesHandler(BaseRequestHandler):
    def get(self, url="/"):
        vert = pickVert()
        event_type = "ignition"
        event_num = 1
        template_values = {}
        filePath = judges = mid_content = ''
        
        mentors = ""
        col1 = [] 
        col2 = [] 
        col3 = []
        faqs = []
        problems = {}
        
        
        if url == "bcbs":
            path = "ignition_bxbs.html"
        else:
            current_event = db.GqlQuery("SELECT * FROM Events Where event_num = :1 AND event_id = :2 ORDER BY full_date DESC", event_num, url).get()
            if current_event is None:
                self.error(404)
            else:
                current_event_id = current_event.event_id
                ## remove quickly
            
            if current_event.header is None:
                current_event.header = "Start a startup and become revenue generating in one week."
                current_event.subheader = "Devise solutions to health tech's most pressing problems and earn a $25,000 revenue stipend, an enterprise LOI, and an invitation to join the Prebacked Foundry."
                current_event.put()
        
        
        #########
        # Need to populate all the event constants (date, location, etc.) right here.
        #########
        #if current_event is not None:  # /ignition/bcbs was hard coded, until we've held several we wanted to keep it around
        if url != "bcbs":
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
            company = current_event.companies
            
            start_day = full_date.strftime('%b %d')
            d = datetime.timedelta(days=1)
            t = full_date + d
            day_two = t.strftime('%b %d')
            d = datetime.timedelta(days=7)
            t = full_date + d
            judge_day = t.strftime('%b %d')
            
            
            #datetime.strptime('2012-06-25 01:17:40.273000','%Y-%m-%d %H:%M:%S.%f')


        all_faq_categories = db.GqlQuery("SELECT * FROM Faq WHERE vertical = :1 ORDER BY order ASC", event_type)
        


        ################## Brittle ##################
        #iterate through list of all FAQs and return distinct categories
        for l in all_faq_categories:
           if (l.section == 'section1'):
               col1.append(l)
           elif (l.section == 'section2'):
               col2.append(l)
           elif (l.section == 'section3'):
               col3.append(l)
               
        faqs = [
                [col1,"col1", "Event questions"],
                [col2,"col2", "Program questions"],
                [col3,"col3", "General questions"]
                ]
        
        all_faq_categories = Faq.gql("WHERE vertical = :1 ORDER BY order", event_type).fetch(100) #Eventually will want to parse this out by city someone is looking at for event FAQs.
        
        ##############################################
        
        
        #if current_event is not None:
        if url != "bcbs":
            problems_events = db.GqlQuery("SELECT * FROM Problems_Events WHERE event_name = :1", current_event_id)
            problems = {}
            
            problems = [{
                    "header": p.problem.title,
                    "statement": p.problem.statement,
                    "value": p.problem.value
                    } for p in problems_events]
            
            
        else:   # These are the old /bcbs problems.  Can be removed in 2-3 events.
            problems = [
                {
                    "header": "Consumer Apathy",
                    "statement": """How do we get our members to engage in preventative care?  What apps, tools or technologies
                                    can you build that can be adopted, scaled and actively utilized by our members?""",
                    "statement_long": """How do we get our members to engage in preventative care?  What apps, tools or technologies
                                    can you build that can be adopted, scaled and actively utilized by our members? Not only will
                                    your tool provide us valuable member engagement data, it could reduce member visits to providers, \
                                    reducing overall health spend.""",
                    "value": "$75,000",
                }
                ,{
                    "header": "Price Transparency",
                    "statement": """Different providers often charge different rates for the same procedure.
                                    Members are unaware since they only pay a flat co-pay per visit and there's no 
                                    incentive to 'shop around'.""",
                    "statement_long": """Different providers often charge different rates for the same procedure.
                                        Members are unaware since they only pay a flat co-pay per visit.
                                        There is no incentive to 'shop around', contributing to excess health spend.
                                        What technologies can you build to:
                                        1) increase transparency of  costs to our members,
                                        2) actively engage them to 'shop around'?""",
                    "value": "$100,000",
                },
                {
                    "header": "Medical Coding",
                    "statement": "ICD-10 standards have changed. Let's discover new opportunities within this transition.",
                    "statement_long":"""Every procedure is classified into a medical code, called an ICD.
                                        There are over 14,000 codes in our system, and they're
                                        currently being revised to the 10th revision, ICD-10.
                                        What analytic tools and technologies can you
                                        build to help us identify and forecast unique opportunities within the
                                        changing data set?""",
                    "value": "$50,000",
                }
            ]
        ################################################
        
        if url == "bcbs":
            sponsors = getSponsors()
            corporate_sponsors = sponsors['corporate_sponsors']
            service_sponsors = sponsors['service_sponsors']
            api_sponsors = sponsors['api_sponsors']
            sponsor_lists = corporate_sponsors + service_sponsors  
        else:                                                      
            sponsors = ""
            corporate_sponsors = Sponsors_Events.gql("WHERE event_name = :1 AND subtype = :2", url, "corporate sponsor").fetch(10)
            corporate_sponsors_count = len(corporate_sponsors)
            service_sponsors = Sponsors_Events.gql("WHERE event_name = :1 AND subtype = :2", url, "service provider sponsor").fetch(20)
            api_sponsors = Sponsors_Events.gql("WHERE event_name = :1 AND subtype = :2", url, "api sponsor").fetch(20)
            media_partners = Sponsors_Events.gql("WHERE event_name = :1 AND subtype = :2", url, "media partner").fetch(20)
            sponsor_lists = ""


        if url == "bcbs":
            judges = db.GqlQuery("SELECT * FROM Mentors WHERE vertical = 'health' ORDER BY order ASC") #right now statically picks all from vert = "health", bad bad bad
        else:
            all_partners = db.GqlQuery("SELECT * FROM Mentors_Events WHERE event_id = :1 ORDER BY mentor_type DESC, mentor_id ASC", current_event_id)
            fix_order(all_partners)
            
            execs = db.GqlQuery("SELECT * FROM Mentors_Events WHERE event_id = :1 AND mentor_type = :2 ORDER BY order ASC, mentor_id ASC", current_event_id, 3)

            judges = db.GqlQuery("SELECT * FROM Mentors_Events WHERE event_id = :1 AND mentor_type = :2 ORDER BY order ASC, mentor_id ASC", current_event_id, 2)
            mentors = db.GqlQuery("SELECT * FROM Mentors_Events WHERE event_id = :1 AND mentor_type = :2 ORDER BY order ASC, mentor_id ASC", current_event_id, 1)
            #mentors_judges = db.GqlQuery("SELECT * FROM Mentors_Events WHERE event_id = :1 AND mentor_type = :2 OR mentor_type = :3 ORDER BY order ASC, mentor_id ASC", current_event_id, 1, 2)
            mentors_judges = list(judges) + list(mentors)
            
            vip_list = [
                [execs, "Executive Panel"],
                [mentors_judges, "Mentors and Judges"]
            ]

            
        template_values.update(locals())
        
        if url == "bcbs":
            filePath ="../templates/ignition_bxbs.html"
        else:
            filePath = '../templates/ignition_base.html'
        
        path = os.path.join(os.path.dirname(__file__), filePath)
        self.response.out.write(template.render(path, template_values))
        
        
def fix_order(gql_query):
    for g in gql_query:
        g.order = g.mentor.order
        g.put()