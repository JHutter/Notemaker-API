# Project: OAuth2.0
# Jon Hutter
# cs496-400 Spring 2017

# sources: oauth lecture and demo, others cited throughout

import webapp2
from google.appengine.api import urlfetch
from urllib import urlencode
import json
import logging
from google.appengine.ext import ndb
from google.appengine.datastore.datastore_query import Cursor

client = '387463041973-2j1noh0p0danoujlobm20q9378375b0n.apps.googleusercontent.com'
secret_str = 'Vgv_V2H9yTkXsmc-bK8VHy0g'
oauth_redir = 'https://final-project-496-400.appspot.com/oauth'

# ndb entities, four properies each, with a one-to-many relationship (profile can have any number of notes)
# source: https://cloud.google.com/appengine/articles/modeling
class Profile(ndb.Model):
    userid = ndb.IntegerProperty()
    handle = ndb.StringProperty()
    feeling = ndb.StringProperty()
    bio = ndb.StringProperty()

class Note(ndb.Model):
    contact = ndb.ReferenceProperty(Profile,
                                   collection_name='notes')
    title = ndb.StringProperty()
    content = ndb.StringProperty()
    date_added = ndb.DateProperty()



class RestPage(webapp2.RequestHandler):
    def get(self):
        self.response.write('You shouldn\'t be here...')
        

class ProfileIDPage(webapp2.RequestHandler):
    def get(self, profile_id):
        self.response.headers['Content-Type'] = 'application/json'   
        obj = {
          'success': profile_id, 
          'payload': 'some var',
        } 
        self.response.out.write(json.dumps(obj))
        
class ProfileListPage(webapp2.RequestHandler):
    def get(self):
        self.response.write('List profiles here')
        
    def post(self):
        # scott = Contact(name='Scott')
        # scott.put()
        self.response.write('posted a new profile')

        

# source: http://webapp2.readthedocs.io/en/latest/guide/routing.html
app = webapp2.WSGIApplication([
    (r'/rest/profiles/(\d+)', ProfileIDPage),
    (r'/rest/profiles', ProfileListPage),
    (r'/rest.*', RestPage)
], debug=True)
