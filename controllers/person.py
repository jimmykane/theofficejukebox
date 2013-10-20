'''
@author: Dimitrios Kanellopoulos
@contact: jimmykane9@gmail.com
'''
import logging
import hashlib
import json
from google.appengine.api import users
from controllers.jsonhandler import *
from models.person import *
from models.jukebox import *
from models.tracks import *
from userpage import *


class LogoutPersonHandler(UserPageHandler):

	def get(self):
		try:
			return self.redirect(users.create_logout_url(self.request.get('return_url')))
		except Exception as e:
			logging.exception('Could not Logout user\n' + repr(e))
			self.redirect('/')
			return


class RegisterPersonHandler(UserPageHandler):

	def get(self):
		user = users.get_current_user()
		if not user:
			self.redirect(users.create_login_url(self.request.uri), abort=True)
			return
		person = Person.get_or_insert(user.user_id())
		if not self._register(person, user):
			# more logging is needed
			logging.warning('Warning registration failed')
			return
		# get the slide and then redirect him there
		self.redirect("/jukebox/")

	def post(self):
		self.view("No reason to be here Mr Jiggles ;-)")
		return

	@ndb.transactional()
	def _register(self, person, user):
		''' Registration process happens here
		'''
		# check if the person has info and if not create it
		info = PersonInfo.query(ancestor=person.key).get()
		if not info:
			info = PersonInfo(id=user.user_id(), parent=person.key)
			info.nick_name = user.nickname()
			info.email = user.email()
			info.put()
		return True


class GetCurrentPersonHanlder(UserPageHandler, JSONHandler):

	def post(self):
		person = Person.get_current()
		if not person: # its normal here
			response = {'status':self.get_status(status_code=404)}
			self.response.out.write(json.dumps(response))
			return
		person_id = person.key.id()
		jukebox_memberships = person.jukebox_memberships
		person = person.info.to_dict(exclude=['edit_date'])
		person.update({'id': person_id})
		person.update({'app_admin': users.is_current_user_admin()})
		response = response = {'data': person}
		response.update({'status': self.get_status()})
		self.response.out.write(json.dumps(response))