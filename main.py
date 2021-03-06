# Project: OAuth2.0
# Jon Hutter
# cs496-400 Spring 2017

# sources: oauth lecture and demo, others cited throughout
# source: https://cloud.google.com/appengine/docs/standard/python/ndb/queries
# source: https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html for status code

import webapp2
from google.appengine.api import urlfetch
from urllib import urlencode
import json
import logging
from google.appengine.ext import ndb
from google.appengine.datastore.datastore_query import Cursor
import datetime

client = '387463041973-2j1noh0p0danoujlobm20q9378375b0n.apps.googleusercontent.com'
secret_str = 'Vgv_V2H9yTkXsmc-bK8VHy0g'
oauth_redir = 'https://final-project-496-400.appspot.com/oauth'
# in production code where app.yaml has threading, use a mutex here to avoid a race condition.

# ndb entities, four properies each, with a one-to-many relationship (profile can have any number of notes)
# source: https://cloud.google.com/appengine/articles/modeling
# source: https://stackoverflow.com/questions/10077300/one-to-many-example-in-ndb
class AutoIncrement():
    
    def __init__(self):
        """ Create a new point at the origin """
        self.lastAutoInc = 0
        
    def getNextAutoInc(self):
        self.lastAutoInc += 1
        return self.lastAutoInc
        
noteidInc = AutoIncrement()

class Profile(ndb.Model):
    userid = ndb.StringProperty()
    handle = ndb.StringProperty()
    feeling = ndb.StringProperty()
    bio = ndb.StringProperty()
    notes = ndb.KeyProperty(kind='Note', repeated=True)

# source: https://stackoverflow.com/questions/17190626/one-to-many-relationship-in-ndb
class Note(ndb.Model):
    owner = ndb.KeyProperty(kind='Profile')
    noteid = ndb.StringProperty()
    title = ndb.StringProperty()
    content = ndb.StringProperty()
    date_added = ndb.DateProperty()
    visible = ndb.BooleanProperty()

    
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
    
def validateNote(noteid):
    result = Note.query(Note.noteid == noteid).get()
    
    if (result is not None):
            return True
    else:
        return False
  
# see if note's keyproperty matches the result for profile_id's key  
def validateProfileHasNoteId(profile_id, note_id):
    notesProfile = Note.query(Note.noteid == note_id).get().owner
    profile_key = Profile.query(Profile.userid == profile_id).get().key
    
    if notesProfile == profile_key:
        return True
    else:
        return False

class AutoIncrement():
    lastNoteNum = 0
    
    def getNextAutoInc(self):
        lastNoteNum += 1
        return lastNoteNum
            
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
            #self.response.out.write(json.dumps({'profiles':[line.to_dict() for line in Profile.query(Profile.userid == profile_id).fetch()]}))
            lines = Profile.query(Profile.userid == profile_id).iter()
            jsonline = []
            for line in lines:
                jsonline.append({'id': profile_id, 'handle': line.handle, 'feeling': line.feeling, 'bio': line.bio}) # exclude userid
            self.response.out.write(json.dumps({'profiles':jsonline}))
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
            newFeeling = self.request.get('feeling', default_value='same')
            oldProfile = Profile.query(Profile.userid == profile_id).get()
            
            keyid = oldProfile.key.get()
            
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
class NotesListPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/json'  
        # source: https://stackoverflow.com/questions/13311363/appengine-making-ndb-models-json-serializable
        #self.response.out.write(json.dumps({'notes':[line.to_dict() for line in Note.query(Note.visible == True).fetch()]})) 
        lines = Note.query(Note.visible == True).iter()
        jsonline = []
        for line in lines:
            jsonline.append({'title': line.title, 'date_added': str(line.date_added), 'content': line.content, 'visible': str(line.visible)})
        self.response.out.write(json.dumps({'notes':jsonline}))
        
        
    def post(self):
        #self.response.write(self.request.headers)
        try:
            header = self.request.headers['Authorization']
            userid = getUserId(header)
            
            if (userid == 'Error' or userid == 'None'):
                # bad userId or auth
                status = '403 Forbidden'
                message = 'invalid authorization'
                note = {}
            else:
                query = Profile.query(Profile.userid == userid).get()
                if (query is not None):
                    keyid = query.key
                    title = self.request.get('title', default_value='untitled')
                    content = self.request.get('content', default_value='[empty]')
                    date_added = datetime.date.today()
                    visible = self.request.get('visible', default_value='False')
                    noteid = str(noteidInc.getNextAutoInc())
                    
                    newNote = Note(owner=keyid, title=title, content=content, date_added=date_added, visible=(visible=='True'), noteid=noteid)
                    #newProfile = Profile(userid=user_id, handle=handle, feeling=feeling, bio=bio)
                    newKey = newNote.put()
                    status = '201 Created'
                    message = 'note created'
                    note = {'id':noteid, 'title': title, 'content': content, 'date_added': str(date_added), 'visible':str(visible)}
                    
                    
                else:
                    status = '404 Not Found'
                    message = 'no matching profile for authorization given'
                    note = {}
                
            
        except (KeyError, AttributeError):
            status = '401 Unauthorized'
            message = 'no authorization included'
            note = {}

        self.response.out.write(json.dumps({'status': status, 'message': message, 'note': note}))
        
class NotesIDPage(webapp2.RequestHandler):
    def get(self, profile_id, note_id):
        # if the note is visibl
        self.response.headers['Content-Type'] = 'application/json'  
        try:
            header = self.request.headers['Authorization']
            auth = validateUserId(profile_id, header)
        except (KeyError, AttributeError):
            auth = False
            
        
        noteExist = validateNote(str(note_id))
        validProfile = True if (Profile.query(Profile.userid == profile_id).get() is not None) else False
        
        
        if (not noteExist):
            status = '404 Not Found'
            message = 'no matching note found'
            note = {}
        else:
            if (not validProfile):  
                status = '404 Not Found'
                message = 'no matching profile found'
                note = {}
            else:
                if (not auth):
                    # only ret if public
                    lines = Note.query(Note.visible == True, Note.noteid == note_id).iter()
                    jsonline = []
                    for line in lines:
                        jsonline.append({'title': line.title, 'date_added': str(line.date_added), 'content': line.content, 'visible': str(line.visible)})
                    
                else:
                    # ret anyway
                    lines = Note.query(Note.noteid == note_id).iter()
                    jsonline = []
                    for line in lines:
                        jsonline.append({'title': line.title, 'id': note_id, 'date_added': str(line.date_added), 'content': line.content, 'visible': str(line.visible)})
                status = '200 OK'
                message = 'note returned'
                note = jsonline

        self.response.write(json.dumps({'status': status, 'message': message, 'note': note}))
            
    def delete(self, profile_id, note_id):  
        #delete the given note (must match profile)
        try:
            header = self.request.environ['HTTP_AUTHORIZATION']
            auth = validateUserId(profile_id, header)
            comboValid = validateProfileHasNoteId(str(profile_id), str(note_id))
            if (auth and comboValid):   
                #delete the note
                noteDel = Note.query(Note.noteid == note_id).get()
                noteDel.key.delete()
                
                #self.response.write('delete the note')
                status = '200 OK'
                message = 'note deleted'
            else:
                raise Exception
        except (KeyError, AttributeError):
            status = '403 Forbidden'
            message = 'No access to delete this note'
        except (Exception):
            status = '404 Not Found'
            message = 'No matching profile/note combination'
            
        self.response.out.write(json.dumps({'status': status, 'message':message}))
        
        
    def patch(self, profile_id, note_id):
        #patch the given note (must match profile)
        try:
            header = self.request.environ['HTTP_AUTHORIZATION']
            auth = validateUserId(profile_id, header)
            comboValid = validateProfileHasNoteId(str(profile_id), str(note_id))
            if (auth and comboValid):   
                # get and patch the note
                newTitle = self.request.get('title', default_value='same')
                newContent = self.request.get('content', default_value='same')
                newVisible = self.request.get('feeling', default_value='same')
                
                oldNote = Note.query(Note.noteid == note_id).get()
                
                if (newTitle != 'same'):
                    oldNote.title = newTitle
                if (newContent != 'same'):
                    oldNote.content = newContent
                if (newVisible != 'same'):
                    oldNote.visible = newVisible
                oldNote.put()
                
                #self.response.write('delete the note')
                status = '200 OK'
                message = 'note modified'
                
            else:
                raise Exception
        except (KeyError, AttributeError):
            status = '403 Forbidden'
            message = 'No access to modify this note'
            
        except (Exception):
            status = '404 Not Found'
            message = 'No matching profile/note combination'
            
            
        self.response.out.write(json.dumps({'status': status, 'message':message}))
 

class NotesForUserPage(webapp2.RequestHandler):
    def get(self, profile_id):
        # get all notes for a given profile
        self.response.headers['Content-Type'] = 'application/json'  
        try:
            header = self.request.headers['Authorization']
            auth = validateUserId(profile_id, header)
            user = Profile.query(Profile.userid == profile_id).get()
            if (user is None):
                raise Exception
        except (KeyError, AttributeError):
            auth = False
        except (Exception):
            status = '404 Not Found'
            message = 'No such profile'
            notes = []
        
        profileKey = Profile.query(Profile.userid == profile_id).get().key
        
        if (not auth):
            # only ret if public
            lines = Note.query(Note.visible == True).iter()
            jsonline = []
            for line in lines:
                if (line.owner == profileKey):
                    jsonline.append({'title': line.title, 'date_added': str(line.date_added), 'content': line.content, 'visible': str(line.visible)})
            
        else:
            # ret anyway
            note_id = noteidInc.getNextAutoInc()
            lines = Note.query().iter()
            jsonline = []
            for line in lines:
                if (line.owner == profileKey):
                    jsonline.append({'title': line.title, 'id': note_id, 'date_added': str(line.date_added), 'content': line.content, 'visible': str(line.visible)})
        
        status = '200 OK'
        message = 'note returned'
        notesArr = jsonline

        self.response.write(json.dumps({'status': status, 'message': message, 'notes': notesArr}))
        

# source: https://stackoverflow.com/questions/16280496/patch-method-handler-on-google-appengine-webapp2
allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods       

# source: http://webapp2.readthedocs.io/en/latest/guide/routing.html
app = webapp2.WSGIApplication([
    (r'/rest/profiles/(\d+)/notes/(\d+)', NotesIDPage),
    (r'/rest/profiles/(\d+)/notes', NotesForUserPage),
    (r'/rest/notes', NotesListPage),
    (r'/rest/profiles/(\d+)', ProfileIDPage),
    (r'/rest/profiles', ProfileListPage),
    (r'/rest.*', RestPage)
], debug=True)
