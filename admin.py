'''
@author: Dimitrios Kanellopoulos
@contact: jimmykane9@gmail.com
'''
from controllers import admin
from config import config
from google.appengine.ext import ndb
import webapp2

app =  ndb.toplevel(webapp2.WSGIApplication([
		("/admin/",admin.AdminPageHandler)
	],debug=True, config=config.config))
