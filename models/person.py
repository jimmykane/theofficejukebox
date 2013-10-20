'''
@author: Dimitrios Kanellopoulos
@contact: jimmykane9@gmail.com
'''
import logging

from models.jukebox import *
from google.appengine.ext import ndb
from google.appengine.api import users


class Person(ndb.Expando):

	registration_date = ndb.DateTimeProperty(auto_now_add=True)

	@property
	def info(self):
		info = PersonInfo.query(ancestor=self.key).get()
		return info

	@property
	def jukebox_memberships(self):
		jukebox_memberships = JukeboxMembership.query().filter(JukeboxMembership.person_key==self.key).fetch(30)
		return jukebox_memberships

	@property
	def jukebox_membership(self, jukebox):
		jukebox_membership_key = ndb.Key(Jukebox, jukebox.key.id(), JukeboxMembership, self.key.id())
		jukebox_membership_key.get()
		return jukebox_membership_key


	@classmethod
	def get_current(cls):
		user = users.get_current_user()
		if not user:
			return False
		person = ndb.Key(cls, user.user_id()).get()
		if not person:
			return False
		return person

	@classmethod
	def _pre_delete_hook(cls, key):
		# This needs urgent fixing. Should iterate in slides etc.
		person_info = PersonInfo.query(ancestor=key).get()
		if person_info:
			person_info.key.delete()
		#slides_keys = Slide.query(ancestor=key).fetch(1000, keys_only=True)
		#if slides_keys:
			#ndb.delete_multi(slides_keys)


class PersonInfo(ndb.Expando):

	email = ndb.StringProperty()
	nick_name = ndb.StringProperty()
	edit_date = ndb.DateTimeProperty(auto_now=True)
