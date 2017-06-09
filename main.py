# Project: OAuth2.0
# 



import webapp2
from google.appengine.api import urlfetch
from urllib import urlencode
import json

class MainPage(webapp2.RequestHandler):
    def get(self):
        base = 'https://accounts.google.com/o/oauth2/v2/auth?'
	client_id = 'client_id=171910885128-t2c20dlngoajvamvpasrs8m7e9bvgf1m.apps.googleusercontent.com'
	redir = '&redirect_uri=https://oauth-assignment.appspot.com/oauth'
	scope = '&scope=email'
	response = '&response_type=code'
	# put this in a more secret place if real production code
	secret = '&state=u8WHIiKGuqiRxFu6leks8p83'
	url = base + client_id + redir + scope + response + secret
	jstext = '<script type="text/javascript"> document.getElementById("signinButton").addEventListener("click", function(){ window.location = encodeURI("' + url + '");});    </script>'

	# write the response
	self.response.headers['Content-Type'] = 'text/html'
        self.response.write('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>OAuth2.0 Assignment</title></head><body><p>Content?</p><button id="signinButton">Sign in with Google</button>' + jstext + '</body></html>');

class OauthHandler(webapp2.RequestHandler):
	def get(self):
		# source: http://webapp2.readthedocs.io/en/latest/guide/request.html
		code_value = self.request.get('code')
		secret_value = self.request.get('status')
		
		# compare to our secret?
		
		# post to google
		# source: https://cloud.google.com/appengine/docs/standard/python/issue-requests
		try:
			# put secret, client, etc in here
			form_fields = {
				'code': code_value,
				'client_id': '171910885128-t2c20dlngoajvamvpasrs8m7e9bvgf1m.apps.googleusercontent.com',
				'client_secret': 'u8WHIiKGuqiRxFu6leks8p83',
				'redirect_uri': 'https://oauth-assignment.appspot.com/oauth',
				'grant_type': 'authorization_code',
				'access_type': 'offline'}
			
			post_data = urlencode(form_fields)
			headers = {'Content-Type': 'application/x-www-form-urlencoded'}
			result = urlfetch.fetch(
				url = 'https://www.googleapis.com/oauth2/v4/token',
				payload = post_data,
				method = urlfetch.POST,
				headers = headers)
			
			# parse the stuff we got
			jsonresults = json.loads(result.content)
			access_token = jsonresults['access_token']
			token_type = jsonresults['token_type']
			expires_in = jsonresults['expires_in']
			id_token = jsonresults['id_token']
			
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
					if (usercontent['isPlusUser'] == True):
						name = usercontent['displayName']
						plusurl = usercontent['url']
						# display to user
						self.response.write('Hey, I know you. You\'re ' + name)
						self.response.write('And your google plus url is ' + plusurl)
					else:
						#name = usercontent
						self.response.write('You aren\'t a google plus user, so you don\'t have a url for google plus')
				else:
					self.response.write('Error: status code ' + result.status_code)
			except urlfetch.Error:
				logging.exception('Caught exception fetching url')
		except urlfetch.Error:
			logging.exception('Caught exception fetching url')
		

# source: http://webapp2.readthedocs.io/en/latest/guide/routing.html
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/oauth', OauthHandler)
], debug=True)
