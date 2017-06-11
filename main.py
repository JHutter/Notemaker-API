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
    userid = ndb.StringProperty()
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
    userid = 'None'
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
            userid = 'Error'
    except urlfetch.Error:
        userid = 'Error'
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
        self.response.headers['Content-Type'] = 'application/json'  
        query = Profile.query()
        all = query.fetch()
        results = []
        
        for line in all:
            self.response.write(line.Profile.handle)
        self.response.out.write(json.dumps({'profiles': results}))
        
    def post(self):
        self.response.headers['Content-Type'] = 'application/json'  
        try:        # source: https://stackoverflow.com/questions/610883/how-to-know-if-an-object-has-an-attribute-in-python/610923#610923
            header = self.request.headers['Authorization']
            user_id = getUserId(header)
            
            if (user_id == 'Error' or user_id == 'None'):
                raise Exception
            
            # get info sent in request
            handle = self.request.get('handle', default_value='anon')
            feeling = self.request.get('feeling', default_value=' ')
            bio = self.request.get('bio', default_value='somebody')
            
            # source: https://stackoverflow.com/questions/12220653/get-ndb-query-length-using-python-on-google-app-engine
            query = Profile.query(Profile.userid == user_id)
            if (query.get() is not None): # trying to keep a uniqueness constraint here, even tho ndb doesn't support them
                #no don't add
                self.response.write('user already exists')
                status = '409 Conflict'
                message = 'profile already exists for this user'
                user = {}
                
            else:
                self.response.write('created')
                newProfile = Profile(userid=user_id, handle=handle, feeling=feeling, bio=bio)
                newProfile.put()
                status = '201 Created'
                message = 'user profile created'
                user = {'id': user_id,
                        'handle': handle,
                        'feeling': feeling,
                        'bio': bio}
                
        except KeyError:
            status = '401 Unauthorized'
            message = 'no authorization included'
            user_id = -1
            user = {}

        except:
            status = '403 Forbidden'
            message = 'invalid authorization'
            user = {}
            
        # return result to user
        response = {'status': status,
                    'message': message,
                    'user': user}
        self.response.out.write(json.dumps(response))
        
class ResetDB(webapp2.RequestHandler):
    def get(self):
        ndb.delete_multi(Note.query().fetch()
)
        

# source: http://webapp2.readthedocs.io/en/latest/guide/routing.html
app = webapp2.WSGIApplication([
    (r'/rest/resetDB', ResetDB),
    (r'/rest/profiles/(\d+)', ProfileIDPage),
    (r'/rest/profiles', ProfileListPage),
    (r'/rest.*', RestPage)
], debug=True)
