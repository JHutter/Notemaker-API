# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import webapp2
from google.appengine.api import urlfetch
from urllib import urlencode
import json
# import urllib3

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
			#self.response.write(result.content)
			#access_token = result.access_token
			#bearer = result.token_type
			#expires_in = result.expires_in
			#id_token = result.id_token
			
			self.response.write('I got something back. ' + result.error)
			
			# source: http://urllib3.readthedocs.io/en/latest/user-guide.html
			#r = http.request(
			#	'POST',
			#	'https://www.googleapis.com/oauth2/v4/token',
			#	fields=form_fields)
		except urlfetch.Error:
			logging.exception('Caught exception fetching url')
		
		self.response.write('I got the code: ' + code_value)

# source: http://webapp2.readthedocs.io/en/latest/guide/routing.html
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/oauth', OauthHandler)
], debug=True)
