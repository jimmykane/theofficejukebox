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
		# First lets try to get the data and then logic
		try:
			jukebox_id = self.request.get('jukebox_id')
			track_key_id = self.request.get('track_key_id')
			track_queued_on = self.request.get('track_queued_on')
			#Watch out track_queued_on is in iso format.
		except Exception as e:
			logging.error('Unconvertable request' + repr(e))
			return

		jukebox = ndb.Key(Jukebox, jukebox_id).get()

		if not jukebox:
			logging.info(jukebox_id)
			logging.warning('No jukebox found. Aborting')
			return

		if not jukebox.player.on:
			logging.info('Jukebox player is off. Aborting')
			return

		player = jukebox.player

		if not (player.track_key.id() == track_key_id and player.track_queued_on.isoformat() == track_queued_on) :
			logging.warning ('Change track request with changed state. Dropping')
			return

		track_playing = jukebox.track_playing
		if not track_playing:
			#wtf ?
			logging.warning('This is something I should notice')
			logging.warning(player)
			return

		# the next song is the first queued
		next_track = QueuedTrack.query(ancestor=jukebox.key)\
			.filter(QueuedTrack.archived==False)\
			.order(QueuedTrack.edit_date).get()

		if not next_track:
			logging.info('No next track queued. Queuing random...')
			next_track = jukebox.random_archived_queued_track
			if not next_track:
				# All is empty...?
				logging.info('No track found at all')
				return
			#logging.info('Title: ' + str(next_track_playing.title))
			logging.info('Random Track queued...')

		# It has completed lets move on...
		player.track_queued_on = datetime.datetime.now()
		player.track_duration = next_track.duration
		player.track_key = next_track.key #hehe gets confusing
		player.put()

		#logging.info(player)

		taskqueue.add(
			queue_name = "playercommands",
			url="/playercommands/next/",
			method='POST',
			eta=datetime.datetime.now() + datetime.timedelta(0, player.track_duration),
			target=(None if self.is_dev_server() else 'playercommands'),
			params= {
				'jukebox_id': jukebox.key.id(),
				'track_key_id': player.track_key.id(),
				'track_queued_on': player.track_queued_on.isoformat()
				# date will be in iso format 2013-10-09 07:54:56.871812
			},
			headers={"X-AppEngine-FailFast":"true"} # for now
		)

		#now archive the song
		next_track.archived = True
		next_track.put()
		#logging.info('Track autoloaded')
		#logging.info('Going from:' + str(track_playing.title))
		#logging.info('To')
		#logging.info('Title: ' + str(next_track.title))
		return



app = webapp2.WSGIApplication([
		("/playercommands/next/", NextTrackHandler),
	],debug=True)