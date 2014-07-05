import os
import webapp2
from google.appengine.ext import db

from handlers.basehandler import *
from functions.getlots import *

#
#
#class MedHackFaqHandler(BaseHandler):
#    def get(self):
#        vert = pickVert()
#        template_values = {}
#        template_values.update (self.event(), link_info = "current")
#        filePath = judges = col1 = col2 = col3 = corporate_sponsors = service_sponsors = api_sponsors = ''
#        main_content = mid_content = lower_content = ''
#        filePath = '../templates/faq.html'
#        col1 = Content.gql("WHERE vertical = :1 AND page='faq' AND subtype='col1'" "ORDER BY order", vert).fetch(20)
#        col2 = Content.gql("WHERE vertical = :1 AND page='faq' AND subtype='col2'" "ORDER BY order", vert).fetch(20)
#        col3 = Content.gql("WHERE vertical = :1 AND page='faq' AND subtype='col3'" "ORDER BY order", vert).fetch(20)
#        template_values.update(
#            main_content = main_content,
#            mid_content = mid_content,
#            col1 = col1,
#            col2 = col2,
#            col3 = col3
#        )
#        path = os.path.join(os.path.dirname(__file__), filePath)
#        self.response.out.write(template.render(path, template_values))