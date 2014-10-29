#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

#################################################
######               Todo                 #######
#################################################
#  New database for sponsors broken out by location, date, vertical - update getSponsors function
#  Move homepage handler to it's own file
#  Move functions to their own files (functions in bottom of page)
#  Move views to their own respective files

#  Decouple medhack and ignition
#################################################
import os

from google.appengine.ext.webapp import util, template

import webapp2
# from webapp2 import redirect
# import json, base64
import base64
import json
#from google.appengine.api import images
from google.appengine.ext import db
from webapp2_extras import routes
from google.appengine.api import users

#from google.appengine.ext.webapp2 import util, template
#from google.appengine.ext.webapp2.template import render

from google.appengine.api import urlfetch
from google.appengine.api import mail
import urllib2


from functions.getlots import *
from handlers.medhack import *
from handlers.medhackfaq import *
from handlers.ignition_pages_handler import *
from handlers.admin_add import *

from datetime import date, timedelta

webapp.template.register_template_library('functions.templatefilters')

class HomepageHandler(BaseRequestHandler):
    def get(self):
        template_values = {}
        
        program_info = []
        x = 1

        
        template_values.update(locals())

        page = "homepage_alt_design_w2013.html"
        url = "templates/" + page
        path = os.path.join(os.path.dirname(__file__), url)
        self.response.out.write(template.render(path, template_values))
       

class PeopleHandler(BaseRequestHandler):
    def get(self):
        url = "People"
        template_values = {}
        dup_list = [] #list used to avoid duplicates for "friends"
        mentors = []
        clients = []
        friends = []

        # team = PrebackedTeam.gql("ORDER BY order").fetch(10)
        all_mentors = db.GqlQuery('SELECT * FROM Mentors ORDER BY order')

        for m in all_mentors:
            # four types: mentor, advisor, client, friend ## for this page "advisor" isn't very important. Should be on team pg
            if "mentor" in m.designation or "client" in m.designation:
                if "mentor" in m.designation:
                    mentors.append(m) # next: is a Prebacked Program mentor
                if "client" in m.designation:
                    clients.append(m) # next: Was / is a past / current client
            else:
                if not "prebacked" in m.designation:
                    friends.append(m) # next: is not Prebacked program mentor, previous client, nor Prebacked team member
        
        big_list = [
                    ["Program mentors", mentors], 
                    ["Company partners", clients], 
                    ["Friends of Prebacked", friends]
                    ]

            
        
        template_values.update(locals())
        path = os.path.join(os.path.dirname(__file__), 'templates/people.html')
        self.response.out.write(template.render(path, template_values))
        
class HomepagesCatchAllHandler(BaseRequestHandler):
    def get(self, url="", error=""):
        template_values = {}
        event_num = 0
        
        ## Later can remove all this and have it call another function to do this lookup.  Will clean it up.
        #Set event num for database calls
        if url == 'ignition':
            event_num = 1 # must be arrays due to "Where event_num IN :1" directly below
        elif url == 'medhack': 
            event_num = 2
        elif url == 'conversations': 
            event_num = 3
        elif url == 'monthly': 
            event_num = 4
        elif url == 'events' or url =='event_board': 
            event_num = 9 
        
        #populates MedHack and Ignition pages with event links.
        if (1 <= event_num <= 2):
            t1_sponsors = []
            t2_sponsors = []
            sponsor_t1 = []
            sponsor_t2 = []
            sponsor_t3 = []
            duplicate_sponsors_counter = 0
            featured_sponsors = []
            other_sponsors = []
            seen_sponsors = set()
            

            upcoming_events = db.GqlQuery("SELECT * FROM Events Where event_num = :1 AND full_date > :2 AND publish = :3 ORDER BY full_date DESC", event_num, datetime.date.today()-timedelta(days=2), True)
            previous_events = db.GqlQuery("SELECT * FROM Events Where event_num = :1 AND full_date <= :2 AND publish = :3 ORDER BY full_date DESC LIMIT 3", event_num, datetime.date.today()-timedelta(days=2), True)

            try:
                test = upcoming_events[0]
            except:    
                upcoming_events = None
            
            
            if upcoming_events:               
                for e in upcoming_events:  # Populates 'companies' string with current list of corporate sponsors
                    sponsor_t1 = Sponsors_Events.gql("WHERE event_name = :1 AND subtype = :2", e.event_id, "corporate sponsor").fetch(10)
                    sponsor_t2 = Sponsors_Events.gql("WHERE event_name = :1 AND subtype = :2", e.event_id, "service provider sponsor").fetch(10)
                    sponsor_t3 = Sponsors_Events.gql("WHERE event_name = :1 AND subtype = :2", e.event_id, "api sponsor").fetch(10)

                    if sponsor_t1:
                        
                    ###?? Why the F did I do this below? ??### -- I think this is just for Ignition, not MedHack
                        companies = sponsor_t1[0].sponsor.name
                        for s in sponsor_t1[1:]:
                            companies = companies + "<br/>" + s.sponsor.name
                        e.companies = companies
                        e.put()
                    elif not e.companies:
                        e.companies = "Coming soon"
                        e.put()
                    elif e.companies.lower() == "none":
                        e.companies = "Coming soon"
                        e.put()
                    else:
                        e.companies = "Coming soon"
                        e.put()
                    ###?? ??###

                    if sponsor_t1 or sponsor_t2:
                        if sponsor_t1:
                            for s in sponsor_t1:
                                if s.sponsor_name not in seen_sponsors:
                                    t1_sponsors.append(s)
                                    seen_sponsors.add(s.sponsor_name) # Creates a list of featured sponsors to be used in the /medhack welcome page, starting with tier 1 sponsors

                        if sponsor_t2:
                            for s in sponsor_t2:
                                if s.sponsor_name not in seen_sponsors:
                                    t2_sponsors.append(s) # Finishes list of featured sponsors
                                    seen_sponsors.add(s.sponsor_name)


                    if sponsor_t3:
                        for s in sponsor_t3:
                            if s.sponsor_name not in seen_sponsors:
                                    other_sponsors.append(s) # Creates list of tier_3 sponsors
                                    seen_sponsors.add(s.sponsor_name)

                    sponsor_t1 = []
                    sponsor_t2 = []
                    sponsor_t3 = []



                if t1_sponsors and t2_sponsors:
                    #create featured sponsors list
                    featured_sponsors = t1_sponsors + t2_sponsors
                elif t1_sponsors:
                    featured_sponsors = t1_sponsors
                elif t2_sponsors:
                    featured_sponsors = t2_sponsors


                upcoming_events_length = upcoming_events.count()

        ### Conversations            
        elif (event_num == 3): #code for conversations page
            try:
                upcoming_events = Events.gql("WHERE full_date > :1 AND publish = True AND event_num = :2 ORDER BY full_date", datetime.date.today(), event_num)
            except:
                upcoming_events = {}
            if upcoming_events:
                conversations = []
                for e in upcoming_events:
                    mentors = db.GqlQuery("SELECT * FROM Mentors_Events WHERE event_id = :1 ORDER BY mentor_type ASC, order ASC, mentor_id ASC", e.event_id)
                    conversations.append([e , mentors])
        ### Monthly
        elif (event_num == 4): #code for Monthly page
            problems_events = []
            a_challenge = []
            challenges = []
            past_challenges = []

            #Get wufoo json
            # wufoo_url = "https://prebackedforms.wufoo.com/api/v3/forms/w1rxchu30fkqngf/entries.json"
            try:
                result = urlfetch.fetch("https://prebackedforms.wufoo.com/api/v3/forms/w1rxchu30fkqngf/entries.json",headers={"Authorization": "Basic %s" % base64.b64encode("S6ZS-M87O-9CYQ-OH18:haxx")}) #Get wufoo url response
                json_data = json.loads(result.content) #get content of response from wufoo
                all_entries = json_data['Entries']
            except:
                result = ""
                json_data = ""
                all_entries = ""

            # Need to make the next line into a try / except
            upcoming_challenges = Events.gql("WHERE full_date > :1 AND publish = True AND event_num = :2 ORDER BY full_date", datetime.date.today(), event_num).fetch(10)
            # was trying to make it blank in case there were no upcoming challenges
            # if upcoming_challenges == {}:
            #     upcoming_challenges = None;
            prev_challenges = Events.gql("WHERE full_date <= :1 AND publish = True AND event_num = :2 ORDER BY full_date DESC", datetime.date.today(), event_num)

            if upcoming_challenges:
                for e in upcoming_challenges:
                    p_e = Problems_Events.gql("WHERE event_name = :1 LIMIT 1", e.event_id) #.fetch(1) # gather joiner about current event
                    p_e_info = p_e.get()
                    p_e = p_e.fetch(1)
                    s_e = Sponsors_Events.gql("WHERE event_name = :1 LIMIT 1", e.event_id).fetch(1)
                    try:
                        challenge_id = p_e_info.problem.problem_id
                    except:
                        challenge_id = ""
                    
                    challenge_entries = []
                    try:
                        for entry in all_entries: # Get challenge entries from Wufoo
                            if entry['Field115'] == challenge_id:
                                challenge_entries.append(entry)
                    except:
                        challenge_entries = []

                    a_challenge = [p_e + s_e + [challenge_entries]] #Create list of lists for one challenge
                    challenges = challenges + a_challenge #Append this challenge to a list of all upcoming challenges
            
            for e in prev_challenges:
                past_p_e = Problems_Events.gql("WHERE event_name = :1 LIMIT 1", e.event_id).fetch(1) # gather joiner about current event
                past_s_e = Sponsors_Events.gql("WHERE event_name = :1 LIMIT 1", e.event_id).fetch(1)
                a_past_challenge = [past_p_e + past_s_e]
                past_challenges = past_challenges + a_past_challenge


        elif (event_num == 9):
            try:
                upcoming_events = Events.gql("WHERE full_date > :1 AND publish = True ORDER BY full_date", datetime.date.today())
            except:
                upcoming_events = {}

            for e in upcoming_events:
                challenge = Problems_Events.gql("WHERE event_name = :1", e.event_id).fetch(10)
            
        
        ###
        template_values.update (locals())
        path_url = 'templates/home_' + url + '.html'

        
                        
# !!!!!   HUGE BUG ALERT!  Below is meant to catch 404's, but it uses the path_url above and throws only 500's.  Means if you're getting a 404
        # and know the file exists that it's throwing a 500 instead.  No idea how to fix.
        # Update 3/2/2014 - seems fixed?
        # Update again - nope, now it throws a 404 when it's supposed to toss a 500. Better than before though
        

        try:
            path = os.path.join(os.path.dirname(__file__), path_url)
            self.response.out.write(template.render(path, template_values))
        except:
            self.error(404)
            path = os.path.join(os.path.dirname(__file__), 'templates/404.html')
            self.response.out.write(template.render(path, template_values))
        
        
        ###



class PastMonthlyChallengesHandler(BaseRequestHandler):
    def get(self, challenge_id, team_id=""):
        template_values = {}
        url = "monthly"

        result = urlfetch.fetch("https://prebackedforms.wufoo.com/api/v3/forms/w1rxchu30fkqngf/entries.json",headers={"Authorization": "Basic %s" % base64.b64encode("S6ZS-M87O-9CYQ-OH18:haxx")}) #Get wufoo url response
        json_data = json.loads(result.content) #get content of response from wufoo
        all_entries = json_data['Entries']

        problems_events = []
        a_challenge = []
        challenges = []
        past_challenges = []
        # Need to make the next line into a try / except

        p_e = Problems_Events.gql("WHERE event_name = :1 LIMIT 1", challenge_id) # gather joiner about current event
        p_e_info = p_e.get() # export p_e into an object so we can get the challenge_id
        p_e = p_e.fetch(1)
        s_e = Sponsors_Events.gql("WHERE event_name = :1 LIMIT 1", challenge_id).fetch(1)
        
        challenge = [p_e + s_e]


        # check to make sure page exists
        if challenge <> [[]]:

            # check if the event is currently running
            if p_e_info.event.full_date >= datetime.date.today():
                live_event = True

            #check if we can find a matching past or current challenge
            #url looks like prebacked.com/monthly/<challenge_id>
            if not team_id:
                challenge_entries = []
                for entry in all_entries: # Get challenge entries from Wufoo
                    if entry['Field115'] == challenge_id:
                        challenge_entries.append(entry)

                winners = []
                for entry in all_entries:
                    if entry['Field115'] == challenge_id and entry['Field123'] == 'winner':
                        winners.append(entry)
                template_values.update (locals())
                path = os.path.join(os.path.dirname(__file__), 'templates/home_monthly_old_chal.html')
                self.response.out.write(template.render(path, template_values))
            #check if we can find a matching team
            #url looks like prebacked.com/monthly/<challenge_id>/<team>
            elif team_id and challenge_id:
                team = ""
                for entry in all_entries:
                    if entry['Field115'] == challenge_id and entry['EntryId'] == team_id:
                        team = entry

                path = os.path.join(os.path.dirname(__file__), 'templates/home_monthly_team.html')
                template_values.update (locals())
                self.response.out.write(template.render(path, template_values))
        # if page doesn't exist, throw a 404
        else:
            self.error(404)
            path = os.path.join(os.path.dirname(__file__), 'templates/404.html')
            self.response.out.write(template.render(path, template_values))

#This handler is used for ajax requests from the team page
class VoteHandler(BaseRequestHandler):
    def get(self, team_id):
        teamvotes = TeamVotes.gql("WHERE team_id = :1 ", team_id).get()
        if teamvotes:
            self.response.out.write(str(teamvotes.votes))
        else:
            self.response.out.write("0")

    def post(self, team_id):
        teamvotes = TeamVotes.gql("WHERE team_id = :1 ", team_id).get()
        if teamvotes:
            teamvotes.votes = teamvotes.votes + 1
            teamvotes.put()
            self.response.out.write(str(teamvotes.votes))
        else:
            votes = TeamVotes(team_id = team_id, votes = 1 )
            votes.put()
            self.response.out.write("1")


class Webapp2HandlerAdapter(webapp2.BaseHandlerAdapter):
    def __call__(self, request, response, exception):
        request.route_args = {}
        request.route_args['exception'] = exception
        handler = self.handler(request, response)
        return handler.get()
    
class NotFoundPageHandler(BaseRequestHandler):
    def get(self):
        self.error(404)
        template_values = {}
        path = os.path.join(os.path.dirname(__file__), 'templates/404.html')
        self.response.out.write(template.render(path, template_values))

class OtherEventsHandler(BaseRequestHandler):
    def get(self):
        template_values = {}
        path = os.path.join(os.path.dirname(__file__), 'templates/other_events.html')
        self.response.out.write(template.render(path, template_values))

class ImageHandler(BaseRequestHandler):
    def get(self):

        mentor_id = self.request.get('mentor_id')
        mentor = getMentor(mentor_id)
        
        if mentor is None:
            self.response.out.write("No Image")
        elif mentor.img_file:
            self.response.headers['Content-Type'] = 'image/jpeg'
            self.response.out.write(mentor.img_file)
        else:
            self.response.out.write("No Image")

class TeamImageHandler(BaseRequestHandler):
    def get(self):
        team_id = self.request.get('team_id')
        team = getTeam(team_id)
        
        if team is None:
            self.response.out.write("No Image")
        elif team.img_file:
            self.response.headers['Content-Type'] = 'image/jpeg'
            self.response.out.write(team.img_file)
        else:
            self.response.out.write("No Image")    

class CorporateImageHandler(BaseRequestHandler):
    def get(self):
        partner_id = self.request.get('partner_id')
        sponsor = getCorporate(partner_id)
        
        if sponsor is None:
            self.response.out.write("No Image")
        elif sponsor.img_file:
            self.response.headers['Content-Type'] = 'image/png'
            self.response.out.write(sponsor.img_file)
        else:
            self.response.out.write("No image found")
    
    

class MisspellHandler(BaseRequestHandler):
    def get(self):
        self.redirect('/ignition/silicon_valley_winter_2013', permanent=True)


####  Functions  ####


def getMentor(mentor_id):
    result = db.GqlQuery("SELECT * FROM Mentors WHERE mentor_id = :1 LIMIT 1",
                    mentor_id).fetch(1)
    if (len(result) > 0):
        return result[0]
    else:
        return None

def getCorporate(partner_id):
    result = db.GqlQuery("SELECT * FROM Sponsors WHERE sponsor_id = :1 LIMIT 1",
                    partner_id).fetch(1)
    if (len(result) > 0):
        return result[0]
    else:
        return None

def getTeam(team_id):  #Used to get startup information from Teams table
    result = db.GqlQuery("SELECT * FROM Teams WHERE team_id = :1 LIMIT 1",
                    team_id).fetch(1)
    if (len(result) > 0):
        return result[0]
    else:
        return None

def getVCS(page):  #another old function. Don't believe we're using Content table anymore
    vert = pickVert()
    vcs = Content.gql("WHERE vertical = :1 AND page= :2 AND subtype='vc'" "ORDER BY order", vert, page).fetch(15)
    return vcs

def getSponsors():
    #This is very broken for scale - need a new database for sponsors broken out by location, date, vertical
    
    vert = pickVert()
    corporate_sponsors = []
    service_sponsors = []
    api_sponsors = []
    
    sponsors = Content.gql("WHERE vertical = :1 AND page='index'" "ORDER BY order", vert).fetch(100)
            
    for s in sponsors:
        if (s.subtype == 'corporate sponsor'):
            corporate_sponsors.append(s)
        elif (s.subtype == 'service provider sponsor'):
            service_sponsors.append(s)
        elif (s.subtype == 'api sponsor'):
            api_sponsors.append(s)
    
    return {'corporate_sponsors':corporate_sponsors, 'service_sponsors':service_sponsors, 'api_sponsors':api_sponsors}



def split_name(self):
    the_name = self.split();
    return the_name[0] + '<br/>' + the_name[1];

### Not sure if needed anymore ###
def getPrizes():
    vert = pickVert()
    prizes = Content.gql("WHERE vertical = :1 AND subtype='prize'" "ORDER BY order", vert).fetch(20)
    return prizes
######


    

# medhack_pages = [
#         webapp2.Route(r'/', handler=MedHackPagesHandler, name='medhack-main'),
#         webapp2.Route(r'/img', handler=ImageHandler),
#         webapp2.Route(r'/partners', handler=CorporateImageHandler),
#         webapp2.Route(r'/<:.*>', handler=MedHackPagesHandler, name='medhack-main-catchall'),
#         webapp2.Route(r'/404', handler=NotFoundPageHandler)
#     ]


application = webapp2.WSGIApplication([
    # routes.DomainRoute('medhack.<:[a-zA-Z0-9\-\_]+>.prebacked-hrd.appspot.com', MedHackForwarderHandler),
    # routes.DomainRoute('medhack.prebacked.com', MedHackForwarderHandler),
    # routes.DomainRoute('prehack.<:(dev|live)[0-9\-\_]+>.prebacked.com', MedHackForwarderHandler),
    # routes.DomainRoute('prehack.prebacked.com', MedHackForwarderHandler),
    webapp2.Route(r'/', handler=HomepageHandler, name='home-main'),
    webapp2.Route(r'/img', handler=ImageHandler),
    webapp2.Route(r'/partners', handler=CorporateImageHandler),
    webapp2.Route(r'/teams', handler=TeamImageHandler),
    webapp2.Route(r'/people', handler=PeopleHandler, name='home-people'),
    webapp2.Route(r'/ignition/sillicon_valley_winter_2013', handler=MisspellHandler, name='ignition-mispelling'),
    webapp2.Route(r'/ignition/<:.*>', handler=IgnitionPagesHandler, name='ignition-main-catchall'),
    #webapp2.Route(r'/ignition', handler=IgnitionHandler, name='ignition-home'),
    webapp2.Route(r'/medhack/sponsor', handler=MedHackSponsorHandler, name='medhack-sponsor-catchall'),
    webapp2.Route(r'/medhack/<:.*>', handler=MedHackPagesHandler, name='medhack-main-catchall'),
    webapp2.Route(r'/get_votes/<:.*>', handler=VoteHandler, name='get-votes'),
    webapp2.Route(r'/monthly/<:.*>/<:.*>', handler=PastMonthlyChallengesHandler, name='monthly-teams'),
    webapp2.Route(r'/monthly/<:.*>', handler=PastMonthlyChallengesHandler, name='past-monthly-main-catchall'),
    webapp2.Route(r'/admin_add', handler=AdminAddHandler, name='admin-add'),
    webapp2.Route(r'/admin_add/faq_add', handler=FaqAddHandler, name='faq-add'),
    webapp2.Route(r'/admin_add/event_add', handler=EventAddHandler, name='event-add'),
    webapp2.Route(r'/admin_add/sponsor_add', handler=SponsorAddHandler, name='sponsor-add'),
    webapp2.Route(r'/admin_add/problem_add', handler=ProblemAddHandler, name='ignition-add'),
    webapp2.Route(r'/admin_add/challenge', handler=ProblemAddHandler, name='problem-add'),
    webapp2.Route(r'/admin_add/print_names', handler=PrintNameHandler, name='print-name'),

    
    # webapp2.Route(r'/events', handler=TempEventsPageReroute, name='event-reroute'),
    webapp2.Route(r'/<:.*>', handler=HomepagesCatchAllHandler, name='homepage-main-catchall')
    ],
        debug=False)






application.error_handlers[404] = Webapp2HandlerAdapter(NotFoundPageHandler)
util.run_wsgi_app(application)

    
#if __name__ == '__main__':
#    main()
