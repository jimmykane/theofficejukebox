'''
@author: Dimitrios Kanellopoulos
@contact: jimmykane9@gmail.com
'''
from google.appengine.ext import ndb
from google.appengine.api import users
import logging


class Person(ndb.Expando):

	registration_date = ndb.DateTimeProperty(auto_now_add=True)

	@property
	def info(self):
		info = PersonInfo.query(ancestor=self.key).get()
		return info


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
