'''
@author: Dimitrios Kanellopoulos
@contact: jimmykane9@gmail.com
'''
import os
import re
import logging
import datetime
import json
from config import config
from userpage import *
from models.tracks import *
from models.jukebox import *
from controllers.jsonhandler import *

''' All responses must be JSON encoded '''

class RemoveSingleQueuedTrackHandler(UserPageHandler, JSONHandler):

	def post(self):
		person = Person.get_current()
		if not person:
			logging.warning('Unauthorized')
			response = {'status':self.get_status(status_code=401)}
			self.response.out.write(json.dumps(response))
			return
		try:
			data = json.loads(self.request.body)
			jukebox_id = data['jukebox_id']
			queued_track_id = data['queued_track_id']
			archive = data['archive']
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

		queued_track_key = ndb.Key(
			Jukebox, jukebox_id,
			QueuedTrack, queued_track_id
		)

		# should also be checking if it was ququed by that specific person
		# And also do something with the currently playing shit
		if archive:
			queued_track = queued_track_key.get()
			queued_track.archived = True
			queued_track.put()
			response = {'status': self.get_status()}
			self.response.out.write(json.dumps(response))
			return

		if not users.is_current_user_admin():
			logging.warning('Unauthorized')
			response = {'status':self.get_status(status_code=401)}
			self.response.out.write(json.dumps(response))
			return

		queued_track_key.delete()
		response = {'status': self.get_status()}
		self.response.out.write(json.dumps(response))
		return



class AddSingleQueuedTrackHandler(UserPageHandler, JSONHandler):

	def post(self):
		person = Person.get_current()
		#logging.info('here')
		if not person:
			logging.warning('Unauthorized')
			response = {'status':self.get_status(status_code=401)}
			self.response.out.write(json.dumps(response))
			return
		try:
			data = json.loads(self.request.body)
			#logging.info(data['jukebox']['id'])
			#logging.info(data['video_id'])
			jukebox_id = data['jukebox_id']
			video_id = data['video_id']
		except Exception as e:
			logging.error('Unconvertable request' + repr(e))
			response = {'status':self.get_status(status_code=400, msg=repr(e))}
			self.response.out.write(json.dumps(response))
			return

		# Get the jukebox
		jukebox = ndb.Key(Jukebox, jukebox_id).get()

		# First check if track exists etc
		# should have contect options
		logging.info(video_id)
		track = YouTubeTrack.get_or_insert(video_id)
		logging.info(track)

		# should be in trans
		# or maybe not since I can just check if they are set
		if not (track.duration and track.title):
			# Will try to get the info
			info = track.get_youtube_info
			if not info:
				track.key.delete()
				logging.info('Song doesnt have info or is restricted')
				response = {'status':self.get_status(status_code=403, msg='Song doesnt have info or is restricted')}
				self.response.out.write(json.dumps(response))
				return
			track.title = info[0]
			track.duration = info[1]
			if not (track.title and track.duration and track.duration < 900):
				track.key.delete()
				logging.info('Song doesnt have info or above 15 mins')
				response = {'status':self.get_status(status_code=403, msg='Song doesnt have info or above 15 mins')}
				self.response.out.write(json.dumps(response))
				return
			track.put()

		# I think this should be above the track.
		queued_track = ndb.Key(Jukebox, jukebox.key.id(), QueuedTrack, track.key.id()).get()
		if queued_track:
			logging.info('Track found unarchiving')
			queued_track.archived = False
		if not queued_track:
			logging.info('Track not found creating')
			queued_track = QueuedTrack(
				parent=jukebox.key,
				id=track.key.id(),
				duration=track.duration,
				title=track.title,
				video_id=video_id,
				queued_by_person_key=person.key
			)
		queued_track.put()
		# Maybe also favourites
		jukeboxes = [jukebox]
		jukeboxes = Jukebox.jukeboxes_and_queued_tracks_to_dict(jukeboxes)
		response = {'data': jukeboxes[0]['queued_tracks']}
		response.update({'status': self.get_status()})
		#logging.info(response)
		self.response.out.write(json.dumps(response))