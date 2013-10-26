'''
@author: Dimitrios Kanellopoulos
@contact: jimmykane9@gmail.com
'''
import os
import logging
import config
import webapp2
import datetime
from models.person import *
from models.tracks import *
from models.jukebox import *
from controllers.jsonhandler import *
from google.appengine.api import taskqueue


class NextTrackHandler(webapp2.RequestHandler, JSONHandler):
	def post(self):
		logging.info('Jukebox Player Going to next track')
		try:
			jukebox_id = self.request.get('jukebox_id')
			track_key_id = str(self.request.get('track_key_id'))
			track_queued_on = self.request.get('track_queued_on')
			jukebox_key = ndb.Key(Jukebox, jukebox_id)
			track_key = ndb.Key(Jukebox, jukebox_id, QueuedTrack, track_key_id)
		except Exception as e:
			logging.error('Unconvertable request' + repr(e))
			return

		started = self._start_playing(jukebox_key, track_key, track_queued_on)
		if not started:
			logging.warning('Track change skipped...')
			#and more to do
		return

	@ndb.transactional()
	def _start_playing(self, jukebox_key, track_key, track_queued_on):
		player = JukeboxPlayer.query(ancestor=jukebox_key).get()
		if not player.on:
			logging.info('Jukebox player is off. Aborting')
			return False
		if not (player.track_key == track_key and player.track_queued_on.isoformat() == track_queued_on) :
			logging.warning ('Change track request with changed state. Dropping')
			return False

		track_playing = player.track_key.get()
		if not track_playing:
			# This can happen if for example the track is playing
			# and someone deletes it. Then the key reference returns None
			logging.warning('This is something I should notice')
			logging.warning(player)
			return False

		# the next song is the first queued
		next_track = QueuedTrack.query(ancestor=jukebox_key)\
			.filter(QueuedTrack.archived==False)\
			.order(QueuedTrack.edit_date).get()
		if not next_track:
			logging.info('No next track queued. Queuing random...')
			next_track = Jukebox.random_archived_queued_track(jukebox_key)
			if not next_track:
				# All is empty...?
				logging.info('No track found at all')
				return False
			logging.info('Random Track queued...')
		else:
			next_track.play_count = next_track.play_count + 1
		next_track.archived = True

		player.track_queued_on = datetime.datetime.now()
		player.track_duration = next_track.duration
		player.track_key = next_track.key #hehe gets confusing

		ndb.put_multi([next_track, player])
		taskqueue.add(
			queue_name = "playercommands",
			url="/playercommands/next/",
			method='POST',
			eta=datetime.datetime.now() + datetime.timedelta(0, player.track_duration),
			target=(None if self.is_dev_server() else 'playercommands'),
			params= {
				'jukebox_id': jukebox_key.id(),
				'track_key_id': player.track_key.id(),
				'track_queued_on': player.track_queued_on.isoformat()
				# date will be in iso format 2013-10-09 07:54:56.871812
			},
			headers={"X-AppEngine-FailFast":"true"} # for now
		)
		return True


app = webapp2.WSGIApplication([
		("/playercommands/next/", NextTrackHandler),
	],debug=True, config=config.config)