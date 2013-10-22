'''
@author: Dimitrios Kanellopoulos
@contact: jimmykane9@gmail.com
'''
import os
import re
import logging
import datetime
import json
import random
from models.person import *
from models.tracks import *
from models.jukebox import *
from controllers.jsonhandler import *

from google.appengine.api import taskqueue

import webapp2

''' All responses must be JSON encoded '''

class GetJukeBoxesHandler(webapp2.RequestHandler, JSONHandler):

	def post(self):

		# First lets try to get the data and then logic
		try:
			data = json.loads(self.request.body)
			jukebox_ids = data['jukebox_ids']
			filters = data['filters']
		except Exception as e:
			logging.error('Unconvertable request' + repr(e))
			response = {'status':self.get_status(status_code=400, msg=repr(e))}
			self.response.out.write(json.dumps(response))
			return
		if filters:
			# Needs implementation here
			pass
		if jukebox_ids:
			jukeboxes = ndb.get_multi([ndb.Key(Jukebox, id) for id in jukebox_ids])
		else:
			jukeboxes = Jukebox.query().order(Jukebox.creation_date).fetch(100)
		if not jukeboxes:
			response = {'status':self.get_status(status_code=404)}
			self.response.out.write(json.dumps(response))
			return

		jukeboxes_dict_list = []
		for jukebox in jukeboxes:
			player = jukebox.player
			# Quick convert to dict for now
			player = {
				"duration_on": player.duration_on,
				"on": player.on
			}
			jukebox_dict = Jukebox._to_dict(jukebox)
			jukebox_dict.update({'player': player})
			jukeboxes_dict_list.append(jukebox_dict)
		response = {'data': jukeboxes_dict_list}
		response.update({'status': self.get_status()})
		#logging.info(response)
		self.response.out.write(json.dumps(response))
		return


class GetJukeBoxQueuedTracksHandler(webapp2.RequestHandler, JSONHandler):

	def post(self):

		# First lets try to get the data and then logic
		try:
			data = json.loads(self.request.body)
			jukebox_id = data['jukebox_id']
			filters = data['filters']
		except Exception as e:
			logging.error('Unconvertable request' + repr(e))
			response = {'status':self.get_status(status_code=400, msg=repr(e))}
			self.response.out.write(json.dumps(response))
			return

		jukebox_key = ndb.Key(Jukebox, jukebox_id)

		# initialize a query instance
		query = QueuedTrack.query(ancestor=jukebox_key)
		#logging.info(filters)
		archived = False
		order = 'edit_date'
		amount = 15
		# This needs major rethink. Leaving it aside for now
		if filters:
			if 'amount' in filters:
				if not (filters['amount'] > 30):
					amount = filters['amount']
			if 'archived' in filters:
				query = query.filter(QueuedTrack.archived==filters['archived'])
			if 'order' in filters:
				if 'short_desc' in filters:
					query = query.order(-ndb.GenericProperty(filters['order']))
				else:
					query = query.order(ndb.GenericProperty(filters['order']))

		#logging.info(query)
		# only queued tracks and wrap it in a try. Might explode...
		try:
			queued_tracks = query.fetch(amount)
		except Exception as e:
			logging.error('Unconvertable Parameters' + repr(e))
			response = {'status':self.get_status(status_code=400, msg=repr(e))}
			self.response.out.write(json.dumps(response))
			return

		queued_tracks_list = []
		for queued_track in queued_tracks:
			queued_track_dict = QueuedTrack._to_dict(queued_track)
			queued_tracks_list.append(queued_track_dict)

		response = {'data': queued_tracks_list}
		#logging.info(response)
		response.update({'status': self.get_status()})
		self.response.out.write(json.dumps(response))
		return


class GetPlayingTrackHandler(webapp2.RequestHandler, JSONHandler):

	def post(self):

		# First lets try to get the data and then logic
		try:
			data = json.loads(self.request.body)
			jukebox_id = data['jukebox_id']
			# inside the try due to wrong posts etc of id
			jukebox = ndb.Key(Jukebox, jukebox_id).get()
		except Exception as e:
			logging.error('Unconvertable request' + repr(e))
			response = {'status':self.get_status(status_code=400, msg=repr(e))}
			self.response.out.write(json.dumps(response))
			return

		#logging.info(jukebox)
		if not jukebox:
			response = {'status':self.get_status(status_code=404, msg='Sorry but no jukebox')}
			self.response.out.write(json.dumps(response))
			return

		player = jukebox.player

		if not player.track_key:
			response = {
				'status':self.get_status(
					status_code=403,
					msg='Sorry no track is playing atm..'
				)
			}
			self.response.out.write(json.dumps(response))
			return

		track_playing = player.track_key.get()

		if not track_playing:
			response = {
				'status':self.get_status(
					status_code=403,
					msg='Sorry no track is playing atm..'
				)
			}
			self.response.out.write(json.dumps(response))
			return

		duration = track_playing.duration
		elapsed = datetime.datetime.now() - player.track_queued_on
		start_seconds = elapsed.total_seconds()

		if start_seconds > track_playing.duration + 5:
			logging.info('Current song has ended for sure. now what?')
			response = {
				'status':self.get_status(
					status_code=403,
					msg='Last song ended? Jukebox is probable loading..'
				)
			}
			self.response.out.write(json.dumps(response))
			return

		track_playing_id = track_playing.key.id()
		nick_name = 'Unknown'
		person = track_playing.queued_by_person_key.get()
		if person:
			nick_name = person.info.nick_name
		track_playing = track_playing.to_dict(exclude=['queued_by_person_key','track_key','creation_date', 'edit_date'])
		track_playing.update({'id': track_playing_id})
		track_playing.update({'person_nick_name': nick_name})

		# Recalculate please to be more current
		elapsed = datetime.datetime.now() - player.track_queued_on
		start_seconds = elapsed.total_seconds()
		if (start_seconds < duration + 5) and (start_seconds > duration):
			start_seconds = start_seconds - 5
		track_playing.update({'start_seconds': start_seconds})

		response = {'data': track_playing}
		response.update({'status': self.get_status()})
		#logging.info(response)
		self.response.out.write(json.dumps(response))


'''
	This handler will queue the requested song and
	will fire a next track task with an eta.
'''
class StartPlayingHandler(webapp2.RequestHandler, JSONHandler):

	def post(self):

		person = Person.get_current()

		if not person: # its normal now
			response = {'status':self.get_status(status_code=404)}
			self.response.out.write(json.dumps(response))
			return

		try:
			data = json.loads(self.request.body)
			jukebox_id = data['jukebox_id']
			queued_track_id = data['queued_track_id']
			seek = data['seek']
			jukebox_key = ndb.Key(Jukebox, jukebox_id)
		except Exception as e:
			logging.error('Unconvertable request' + repr(e))
			response = {'status':self.get_status(status_code=400, msg=repr(e))}
			self.response.out.write(json.dumps(response))
			return

		# Only owner and admins can do go on
		membership = ndb.Key(Jukebox, jukebox_key.id(), JukeboxMembership, person.key.id()).get()
		if not membership:
			response = {'status':self.get_status(status_code=401)}
			self.response.out.write(json.dumps(response))
			return

		if (membership.type != 'owner') and (membership.type != 'admin'):
			response = {'status':self.get_status(status_code=401)}
			self.response.out.write(json.dumps(response))
			return

		queued_track_key = ndb.Key(
			Jukebox, jukebox_id,
			QueuedTrack, queued_track_id
		)

		started = self.start_playing(jukebox_key, queued_track_key, seek)
		if not started:
			response = {'status':self.get_status(status_code=400)}
			self.response.out.write(json.dumps(response))
			return

		logging.info('Added and player has started')

		response = {'status': self.get_status()}
		self.response.out.write(json.dumps(response))

		return

	@ndb.transactional()
	def start_playing(self, jukebox_key, queued_track_key, seek):

		queued_track = queued_track_key.get()

		if not queued_track:
			logging.warning('Start Playing with no queued track in bd')
			return False

		if not seek: #should also check if the seek is bigger than dur
			seek = 0

		player = JukeboxPlayer.query(ancestor=jukebox_key).get()
		player.on = True
		player.track_queued_on = datetime.datetime.now() - datetime.timedelta(0, seek)
		player.track_duration = queued_track.duration
		player.track_key = queued_track_key
		player.put()

		taskqueue.add(
			queue_name = "playercommands",
			url="/playercommands/next/",
			method='POST',
			eta=player.track_queued_on + datetime.timedelta(0, player.track_duration),
			target=(None if self.is_dev_server() else 'playercommands'),
			params= {
				'jukebox_id': jukebox_key.id(),
				'track_key_id': player.track_key.id(),
				'track_queued_on': player.track_queued_on.isoformat()
				# date will be in iso format 2013-10-09 07:54:56.871812
			},
			headers={"X-AppEngine-FailFast":"true"} # for now
		)

		queued_track.archived = True
		queued_track.put()

		return True


'''
	This handler will fire next track tasks with an eta.
'''
#shoulb be moved again to seperate controller i think.
#no need to be here.
class StopPlayingHandler(webapp2.RequestHandler, JSONHandler):

	def post(self):

		person = Person.get_current()
		if not person: # its normal now
			response = {'status':self.get_status(status_code=404)}
			self.response.out.write(json.dumps(response))
			return
		# First lets try to get the data and then logic
		try:
			data = json.loads(self.request.body)
			jukebox_id = data['jukebox_id']
		except Exception as e:
			logging.error('Unconvertable request' + repr(e))
			response = {'status':self.get_status(status_code=400, msg=repr(e))}
			self.response.out.write(json.dumps(response))
			return
		# is there a jukebox ?
		jukebox = ndb.Key(Jukebox, jukebox_id).get()
		if not jukebox:
			response = {'status':self.get_status(status_code=404)}
			self.response.out.write(json.dumps(response))
			return

		# Only owner and admins can do go on
		membership = ndb.Key(Jukebox, jukebox.key.id(), JukeboxMembership, person.key.id()).get()
		if not membership:
			response = {'status':self.get_status(status_code=401)}
			self.response.out.write(json.dumps(response))
			return

		if (membership.type != 'owner') and (membership.type != 'admin'):
			response = {'status':self.get_status(status_code=401)}
			self.response.out.write(json.dumps(response))
			return

		#transaction here please!!!!!!!!!
		player = jukebox.player

		player.on = False

		player.put()
		#logging.info(player.track_key)
		#return
		logging.info('Player stopped')
		response = {'status': self.get_status()}
		self.response.out.write(json.dumps(response))
		return



class SaveJukeBoxeHandler(webapp2.RequestHandler, JSONHandler):

	def post(self):

		person = Person.get_current()
		if not person:
			logging.warning('Unauthorized')
			response = {'status': self.get_status(status_code=401)}
			self.response.out.write(json.dumps(response))
			return
		try:
			jukebox_to_save = json.loads(self.request.body)
			#logging.info(jukebox_to_save)
			if not jukebox_to_save:
				response = {'status':self.get_status(status_code=404)}
				self.response.out.write(json.dumps(response))
				return
		except Exception as e:
			logging.exception('Unconvertable request' + repr(e))
			response = {'status': self.get_status(status_code=400, msg=repr(e))}
			self.response.out.write(json.dumps(response))
			return

		jukebox = Jukebox.entity_from_dict(None, jukebox_to_save)
		jukebox.put()

		if not jukebox:
			response = {'status': self.get_status(status_code=404)}
			self.response.out.write(json.dumps(response))
			return

		# Only owner and admins can do go on
		membership = ndb.Key(Jukebox, jukebox.key.id(), JukeboxMembership, person.key.id()).get()
		if not membership:
			response = {'status':self.get_status(status_code=401)}
			self.response.out.write(json.dumps(response))
			return

		if (membership.type != 'owner') and (membership.type != 'admin'):
			response = {'status':self.get_status(status_code=401)}
			self.response.out.write(json.dumps(response))
			return

		player = jukebox.player
		# Quick convert to dict for now
		player = {
			"duration_on": player.duration_on,
			"on": player.on
		}
		jukebox_dict = Jukebox._to_dict(jukebox)
		jukebox_dict.update({'player': player})
		response = {'data': jukeboxes_dict_list}
		response.update({'status': self.get_status()})
		#logging.info(response)
		self.response.out.write(json.dumps(response))
		return