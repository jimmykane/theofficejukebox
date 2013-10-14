'''
@author: Dimitrios Kanellopoulos
@contact: jimmykane9@gmail.com
'''
import logging
import cgi
from models.person import *
from userpage import *
from google.appengine.api import users


class AdminPageHandler(UserPageHandler):

	@ndb.toplevel
	def get(self):
		try:
			all_users = bool(cgi.escape(self.request.get('all')))
			delete_users = bool(cgi.escape(self.request.get('delete')))
			populate_users = bool(cgi.escape(self.request.get('populate')))
			sync_users = bool(cgi.escape(self.request.get('sync_users')))
		except:
			logging.info("Parameters not defined.")
			return


	def post(self):
		self.view("No reason to POST here Mr Jiggles ;-)")
		return
