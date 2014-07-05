#getSponsors function

from functions.getlots import *

from handlers.basehandler import *


def getSponsors(current_event_id = ""):
    
    vert = pickVert()  #no longer used
    corporate_sponsors = []
    service_sponsors = []
    api_sponsors = []
    
    sponsors = db.GqlQuery("SELECT * FROM Sponsors_Events WHERE event_name = :1", current_event_id).fetch(100)
    
    for s in sponsors:
        if (s.subtype == 'corporate sponsor'):
            corporate_sponsors.append(s)
        elif (s.subtype == 'service provider sponsor'):
            service_sponsors.append(s)
        elif (s.subtype == 'api sponsor'):
            api_sponsors.append(s)
    
    return {'corporate_sponsors':corporate_sponsors, 'service_sponsors':service_sponsors, 'api_sponsors':api_sponsors}