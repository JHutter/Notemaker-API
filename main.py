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

# source: https://stackoverflow.com/questions/17190626/one-to-many-relationship-in-ndb
class Note(ndb.Model):
    owner = ndb.KeyProperty(kind=Profile)
    title = ndb.StringProperty()
    content = ndb.StringProperty()
    date_added = ndb.DateProperty()

    
# auth wrappers
# get user id: send req to google to trade token for user id
def getUserId(token):
    userid = 0
    try:
        # get it there
        url = 'https://www.googleapis.com/plus/v1/people/me'
        auth = {'Authorization': token}
        
        # check what we got back
        result = urlfetch.fetch(url, headers=auth)
        if result.status_code == 200:
            # if the status code says we're good, process the result
            usercontent = json.loads(result.content)
            if (usercontent['isPlusUser'] == True):
                userid = usercontent['id']
        else:
            userid = -1
    except urlfetch.Error:
        userid = -1
    return userid
    
# validateUserId, 
# send req to google with token, see if resulting g+ id matches what was passed to us by user originally
def validateUserId(id, token):
    google_userid = getUserId(token)
    if (id == google_userid):
        return True
    return False


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
        self.response.write('List profiles here ')
        
    def post(self):
        self.response.headers['Content-Type'] = 'application/json'  
        try:        # source: https://stackoverflow.com/questions/610883/how-to-know-if-an-object-has-an-attribute-in-python/610923#610923
            if ('Authorization' not in self.request.headers):   #source: https://groups.google.com/forum/#!topic/google-appengine/h-NlJm3mZx8
                raise AttributeError
            
            header = self.request.headers['Authorization']
            user_id = getUserId(header)
            
            if (user_id <= 0):
                raise Exception
            
            # get info sent in request
            handle = self.request.POST['handle']
            feeling = self.request.POST['feeling']
            bio = self.request.POST['bio']
            
            if (Profile.query(userid == user_id)): # trying to keep a uniqueness constraint here, even tho ndb doesn't support them
                #no don't add
                self.response.write('user already exists')
                status = '409 Conflict'
                message = 'profile already exists for this user'
                user = {}
                
            else:
                newProfile = Profile(userid=user_id, handle=handle, feeling=feeling, bio=bio)
                newProfile.put()
                status = '201 Created'
                message = 'user profile created'
                user = {'id': user_id,
                        'handle': handle,
                        'feeling': feeling,
                        'bio': bio}
        
        except AttributeError:
            #self.response.write('error')
            
            if ('Authorization' not in self.request.headers ):
                status = '401 Unauthorized'
                message = 'no authorization included'
                user = {}
            
            status = '400 Bad Request'
            message = 'missing parameters'
            user = {}
            # return error message to userStatus: 201 Created
        # except:
            # status = '403 Forbidden'
            # message = 'invalid authorization'
            # user = {self.request.POST}
            
        # return result to user
        response = {'status': status,
                    'message': message,
                    'user': user}
        self.response.out.write(json.dumps(response))
        


        

# source: http://webapp2.readthedocs.io/en/latest/guide/routing.html
app = webapp2.WSGIApplication([
    (r'/rest/profiles/(\d+)', ProfileIDPage),
    (r'/rest/profiles', ProfileListPage),
    (r'/rest.*', RestPage)
], debug=True)
