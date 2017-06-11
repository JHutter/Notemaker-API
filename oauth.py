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

class MainPage(webapp2.RequestHandler):
    def get(self):
        base = 'https://accounts.google.com/o/oauth2/v2/auth?'
        client_id = 'client_id='+client
        redir = '&redirect_uri=' + oauth_redir
        scope = '&scope=email'
        response = '&response_type=code'
        secret = '&state=' + secret_str
        url = base + client_id + redir + scope + response + secret
        jstext = '<script type="text/javascript"> document.getElementById("signinButton").addEventListener("click", function(){ window.location = encodeURI("' + url + '");});    </script>'

        # write the response
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Final Project</title></head><body><p>Retrieve a token to use with final-project-496-400 API</p><button id="signinButton">Sign in with Google</button>' + jstext + '</body></html>');

class OauthHandler(webapp2.RequestHandler):
    def get(self):
        # source: http://webapp2.readthedocs.io/en/latest/guide/request.html
        code_value = self.request.get('code')
        secret_value = self.request.get('state')
        self.response.headers['Content-Type'] = 'text/plain'
        server_secret = secret_str
        
        # here should be a check that the secret in the get redir'ed from google matches the secret we have on our app's server
        if (secret_value != server_secret):
           self.response.write('That wasn\'t a very good secret. The secrets don\'t match.')
        else:
            # post to google
            # source: https://cloud.google.com/appengine/docs/standard/python/issue-requests
            try:
                # put secret, client, etc in here
                form_fields = {
                    'code': code_value,
                    'client_id': client,
                    'client_secret': server_secret,
                    'redirect_uri': oauth_redir,
                    'grant_type': 'authorization_code',
                    'access_type': 'offline'}
                post_data = urlencode(form_fields)
                headers = {'Content-Type': 'application/x-www-form-urlencoded'}
                result = urlfetch.fetch(url = 'https://www.googleapis.com/oauth2/v4/token', payload = post_data, method = urlfetch.POST, headers = headers)
                # parse the stuff we got
                jsonresults = json.loads(result.content)
                access_token = jsonresults['access_token']
                token_type = jsonresults['token_type']
                expires_in = jsonresults['expires_in']
                id_token = jsonresults['id_token']
                
                self.response.write(jsonresults)
                
                # now get stuff from google plus, with token as header
                try:
                    # get it there
                    url = 'https://www.googleapis.com/plus/v1/people/me'
                    auth = {'Authorization': 'Bearer ' + access_token}
                    
                    # check what we got back
                    result = urlfetch.fetch(url, headers=auth)
                    if result.status_code == 200:
                        # if the status code says we're good, process the result
                        usercontent = json.loads(result.content)
                        self.response.write('\n\n')
                        self.response.write(usercontent)
                        # if (usercontent['isPlusUser'] == True):
                            # name = usercontent['displayName']
                            # plusurl = usercontent['url']
                            # # display to user
                            # self.response.write('Hey, I know you. You\'re ' + name)
                            # self.response.write('\nAnd your google plus url is ' + plusurl)
                            # self.response.write('\n\nSecret ' + secret_value + ' used to get this information.')
                        # else:
                            # #name = usercontent
                            # self.response.write('You aren\'t a google plus user, so you don\'t have a url for google plus, and I don\'t have your name.')
                            # self.response.write('\n\nSecret ' + secret_value + ' used to get this information.')

                    else:
                        self.response.write('Error: status code ' + result.status_code)
                except urlfetch.Error:
                    logging.exception('Caught exception fetching url')
            except urlfetch.Error:
                logging.exception('Caught exception fetching url')
        
# source: https://stackoverflow.com/questions/16280496/patch-method-handler-on-google-appengine-webapp2
allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods
        
# source: http://webapp2.readthedocs.io/en/latest/guide/routing.html
app = webapp2.WSGIApplication([
    (r'/oauth', OauthHandler),
    (r'/.*', MainPage)
], debug=True)
