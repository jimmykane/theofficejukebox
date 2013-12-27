'''
@author: Dimitrios Kanellopoulos
@contact: jimmykane9@gmail.com
'''
import os
import re
import logging
import datetime
import json
import webapp2

from config import config
from models.tracks import *
from models.jukebox import *
from models.person import *
from controllers.jsonhandler import *

''' All responses must be JSON encoded '''

class RemoveSingleQueuedTrackHandler(webapp2.RequestHandler, JSONHandler):

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
			queued_track_key = ndb.Key(
				Jukebox, jukebox_id, QueuedTrack, queued_track_id
			)
		except Exception as e:
			logging.error('Unconvertable request' + repr(e))
			response = {'status':self.get_status(status_code=400, msg=repr(e))}
			self.response.out.write(json.dumps(response))
			return

		membership = ndb.Key(Jukebox, jukebox_id, JukeboxMembership, person.key.id()).get()
		if not membership:
			response = {'status':self.get_status(status_code=401)}
			self.response.out.write(json.dumps(response))
			return

		if membership.type not in Jukebox.membership_types()['members']:
			response = {'status':self.get_status(status_code=401)}
			self.response.out.write(json.dumps(response))
			return

		# I am not sure if this should be allowed
		# also def arg should br archive not delete see js
		if archive:
			queued_track = queued_track_key.get()
			queued_track.archived = True
			queued_track.put()
			response = {'status': self.get_status()}
			self.response.out.write(json.dumps(response))
			return

		# Only owner and admins can do go on
		if membership.type not in Jukebox.membership_types()['admins']:
			response = {'status':self.get_status(status_code=401)}
			self.response.out.write(json.dumps(response))
			return

		queued_track_key.delete()
		response = {'status': self.get_status()}
		self.response.out.write(json.dumps(response))
		return



class AddSingleQueuedTrackHandler(webapp2.RequestHandler, JSONHandler):

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
			jukebox_id = data['jukebox_id']
			video_id = data['video_id']
			jukebox = ndb.Key(Jukebox, jukebox_id).get()
		except Exception as e:
			logging.error('Unconvertable request' + repr(e))
			response = {'status':self.get_status(status_code=400, msg=repr(e))}
			self.response.out.write(json.dumps(response))
			return

		# Only members admins and owners can do go on
		membership = ndb.Key(Jukebox, jukebox_id, JukeboxMembership, person.key.id()).get()
		if not membership:
			response = {'status':self.get_status(status_code=401)}
			self.response.out.write(json.dumps(response))
			return

		if membership.type not in Jukebox.membership_types()['members']:
			response = {'status':self.get_status(status_code=401)}
			self.response.out.write(json.dumps(response))
			return

		track = YouTubeTrack.get_or_insert(video_id)

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
				queued_by_person_key=person.key
			)

		queued_track.put()
		queued_track_dict = QueuedTrack._to_dict(queued_track)
		response = {'data': queued_track_dict}
		response.update({'status': self.get_status()})
		#logging.info(response)
		self.response.out.write(json.dumps(response))
