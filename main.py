# Project: OAuth2.0
# Jon Hutter
# cs496-400 Spring 2017

# sources: oauth lecture and demo, others cited throughout
# source: https://cloud.google.com/appengine/docs/standard/python/ndb/queries

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
    visibile = ndb.BooleanProperty()

    
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
        try:
            # get auth, compare userid
            header = self.request.headers['Authorization']
            getID = getUserId(header)
            if (getID == 'None' or getID == 'Error'):
                auth = False
            else:
                auth = True
        except KeyError:
            auth = False
         
        query = Profile.query(Profile.userid == profile_id)
        if (query.get() is None):
            self.response.out.write(json.dumps({'profiles':[]}))
        elif (auth): 
            self.response.out.write(json.dumps({'profiles':[line.to_dict() for line in Profile.query().fetch()]}))
        else:    
            lines = Profile.query(Profile.userid == profile_id).iter()
            jsonline = []
            for line in lines:
                jsonline.append({'handle': line.handle, 'feeling': line.feeling, 'bio': line.bio}) # exclude userid
            self.response.out.write(json.dumps({'profiles':jsonline}))
            
    def patch(self, profile_id):
        try:
            header = self.request.environ['HTTP_AUTHORIZATION']
            auth = validateUserId(profile_id, header)
        except (KeyError, AttributeError):
            auth = False
        
        if (not auth):
            status = '401 Unauthorized'
            message = 'invalid or missing authorization'
            user = {}
            
        else:
            # prof = Profile.query(Profile.userid == profile_id).get()
            # prof.key.delete()
            
            newHandle = self.request.get('handle', default_value='same')
            newBio = self.request.get('bio', default_value='same')
            newFeeling = self.request.get('newFeeling', default_value='same')
            oldProfile = Profile.query(Profile.userid == profile_id).put()
            
            if (newHandle != 'same'):
                oldProfile.handle = newHandle
            if (newBio != 'same'):
                oldProfile.bio = newBio
            if (newFeeling != 'same'):
                oldProfile.feeling = newFeeling
            oldProfile.put()
            
            # query again so we know we actually made the changes
            newProfile = Profile.query(Profile.userid == profile_id).get()
            status = '200 OK'
            message = 'profile modified'
            user = {'id': profile_id,
                    'handle': newProfile.handle,
                    'bio': newProfile.bio,
                    'feeling': newProfile.feeling}
            
        self.response.out.write(json.dumps({'status': status, 'message': message, 'user': user}))
        
        
    def delete(self, profile_id):
        try:
            header = self.request.environ['HTTP_AUTHORIZATION']
            auth = validateUserId(profile_id, header)
        except (KeyError, AttributeError):
            auth = False
        
        if (not auth):
            status = '401 Unauthorized'
            message = 'invalid or missing authorization'
            
        else:
            prof = Profile.query(Profile.userid == profile_id).get()
            prof.key.delete()
            status = '200 OK'
            message = 'profile deleted'
            
        self.response.out.write(json.dumps({'status': status, 'message': message}))
     
# GET: all profiles
# POST:      
class ProfileListPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/json'  
        # source: https://stackoverflow.com/questions/13311363/appengine-making-ndb-models-json-serializable
        # exclude userid in projection ******
        lines = Profile.query().iter()
        jsonline = []
        for line in lines:
            jsonline.append({'handle': line.handle, 'feeling': line.feeling, 'bio': line.bio}) # exclude userid
        self.response.out.write(json.dumps({'profiles':jsonline}))
        
        #self.response.out.write(json.dumps({'profiles':[line.to_dict() for line in Profile.query().fetch(projection=[Profile.handle, Profile.feeling, Profile.bio])]}))
        
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
        
# get all visible notes
class NotesPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/json'  
        # source: https://stackoverflow.com/questions/13311363/appengine-making-ndb-models-json-serializable
        self.response.out.write(json.dumps({'notes':[line.to_dict() for line in Note.query(Note.visibile == True).fetch()]}))

# source: https://stackoverflow.com/questions/16280496/patch-method-handler-on-google-appengine-webapp2
allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods       

# source: http://webapp2.readthedocs.io/en/latest/guide/routing.html
app = webapp2.WSGIApplication([
    (r'/rest/notes', NotesPage),
    (r'/rest/profiles/(\d+)', ProfileIDPage),
    (r'/rest/profiles', ProfileListPage),
    (r'/rest.*', RestPage)
], debug=True)
