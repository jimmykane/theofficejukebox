'''
@author: Dimitrios Kanellopoulos
@contact: jimmykane9@gmail.com
'''
import logging
import hashlib
import json
from controllers.jsonhandler import *
from models.person import *
from models.jukebox import *
from models.tracks import *
from google.appengine.api import users


class LogoutPersonHandler(webapp2.RequestHandler):

	def get(self):
		try:
			return self.redirect(users.create_logout_url(self.request.get('return_url')))
		except Exception as e:
			logging.exception('Could not Logout user\n' + repr(e))
			self.redirect('/')
			return


class RegisterPersonHandler(webapp2.RequestHandler):

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


class GetCurrentPersonHanlder(webapp2.RequestHandler, JSONHandler):

	def post(self):
		person = Person.get_current()
		if not person: # its normal here
			response = {'status':self.get_status(status_code=404)}
			self.response.out.write(json.dumps(response))
			return

		# First convert to dict
		person_dict = Person._to_dict(person)
		# Then get info convert to dict and update person dict
		person_info = person.info
		person_info_dict = PersonInfo._to_dict(person_info)
		person_dict.update(person_info_dict)
		# Last get the memberships
		jukebox_memberships = person.jukebox_memberships
		member_ships = []
		for jukebox_membership in jukebox_memberships:
			jukebox_membership_dict = JukeboxMembership._to_dict(jukebox_membership)
			member_ships.append(jukebox_membership_dict)
		person_dict.update({'memberships': member_ships})

		response = response = {'data': person_dict}
		response.update({'status': self.get_status()})
		self.response.out.write(json.dumps(response))
