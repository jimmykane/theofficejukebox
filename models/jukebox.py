'''
@author: Dimitrios Kanellopoulos
@contact: jimmykane9@gmail.com
'''
import datetime
import random
from google.appengine.ext import ndb
from google.appengine.api import users
from models.tracks import *
from models.ndb_models import *


class Jukebox(ndb.Expando, DictModel, NDBCommonModel):

	title = ndb.StringProperty()
	creation_date = ndb.DateTimeProperty(auto_now_add=True)
	edit_date = ndb.DateTimeProperty(auto_now=True)
	owner_key = ndb.KeyProperty()


	@property
	def owner(self):
		owner = owner_key.get()
		return queued_tracks


	@property
	def archived_queued_tracks(self):
		queued_tracks = QueuedTrack.query(ancestor=self.key).filter(QueuedTrack.archived==True).order(QueuedTrack.creation_date).fetch(1000)
		return queued_tracks


	@property
	def queued_tracks(self):
		queued_tracks = QueuedTrack.query(ancestor=self.key).filter(QueuedTrack.archived==False).order(QueuedTrack.edit_date).fetch(1000)
		return queued_tracks


	@property
	def track_playing(self):
		# if it's not on
		if not self.player.on:
			return False
		# Well its a mess here should have opts to buffer player
		queued_track = ndb.Key(Jukebox, self.key.id(), QueuedTrack, self.player.track_key.id()).get()
		return queued_track


	@property
	def player(self):
		player = JukeboxPlayer.query(ancestor=self.key).get()
		return player


	@property
	def random_archived_queued_track(self):
		queued_track_keys = QueuedTrack.query(ancestor=self.key)\
			.filter(QueuedTrack.archived==True)\
			.order(QueuedTrack.creation_date).fetch(1000,keys_only=True)
		if not queued_track_keys:
			return False
		random_key = random.choice(queued_track_keys)
		return random_key.get()


	@classmethod
	def _to_dict(cls, jukebox):
		jukebox_id = jukebox.key.id()
		jukebox_dict = jukebox.to_dict(
			exclude=[
				'creation_date',
				'edit_date',
				'on_datetime',
				'owner_key'
			]
		)
		jukebox_dict.update({
			'id': jukebox_id,
			'owner_key_id': jukebox.owner_key.id()
		})
		return jukebox_dict


class JukeboxPlayer(ndb.Expando, DictModel, NDBCommonModel):

	creation_date = ndb.DateTimeProperty(auto_now_add=True)
	edit_date = ndb.DateTimeProperty(auto_now=True)
	on = ndb.BooleanProperty(default=False)
	time_since_on = ndb.DateTimeProperty()
	status = ndb.StringProperty()
	track_queued_on = ndb.DateTimeProperty()
	track_duration = ndb.IntegerProperty()
	# can also be used as key
	track_key = ndb.KeyProperty()

	@property
	def duration_on(self):
		if not self.on:
			return False
		duration_on = datetime.datetime.now() - self.track_queued_on
		return duration_on.total_seconds()

	'''
	All Hooks etc go here
	'''

	#@classmethod
	#def _pre_delete_hook(cls, key):
		#should delete all the queue tracks