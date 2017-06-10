# Project: OAuth2.0
# Jon Hutter
# cs496-400 Spring 2017

# sources: oauth lecture and demo, others cited throughout

import webapp2
from google.appengine.api import urlfetch
from urllib import urlencode
import json
import logging

client = '387463041973-2j1noh0p0danoujlobm20q9378375b0n.apps.googleusercontent.com'
secret_str = 'Vgv_V2H9yTkXsmc-bK8VHy0g'
oauth_redir = 'https://final-project-496-400.appspot.com/oauth'

class RestPage(webapp2.RequestHandler):
    def get(self):
        self.response.write('Welcome...')
        self.response.out.write('Profile ID, ' + profile_id)
        

class ProfileIDPage(webapp2.RequestHandler):
    def get(self):
        self.response.write('Welcome...')
        self.response.out.write('Profile ID, ' + profile_id)

        

# source: http://webapp2.readthedocs.io/en/latest/guide/routing.html
app = webapp2.WSGIApplication([
    ('/profiles/<profile_id:([0-9]{1,8})>', ProfileIDPage),
    (r'/.*', RestPage)
], debug=True)
