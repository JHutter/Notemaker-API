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
import urllib
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
		code_value = self.request.get('code') # 'what is this even?' # urequest.GET['code']
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
				'grant_type': 'authorization_code'}
			
			post_data = urllib.urlencode(UrlPostHandler.form_fields)
			headers = {'Content-Type': 'application/json'}
			#result = urlfetch.fetch(
			#	url = 'https://www.googleapis.com/oauth2/v4/token',
			#	payload = form_data,
			#	method = urlfetch.POST,
			#	headers = headers)
			#self.response.write(result.content)
			#self.response.write('I got the post back')
		except urlfetch.Error:
			logging.exception('Caught exception fetching url')
		
		self.response.write('I got the code: ' + code_value)


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/oauth', OauthHandler)
], debug=True)
