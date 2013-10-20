'''
@author: Dimitrios Kanellopoulos
@contact: jimmykane9@gmail.com
'''
import logging
from controllers import person, server, admin, jukebox, queued_track
from models.person import *
from models.jukebox import *
from config import config
import webapp2



class SetupHandler(webapp2.RequestHandler):

	def get(self):

		person = Person.get_current()
		if not person: # its normal here
			self.response.out.write('Nope you won\'t')
			return

		if not users.is_current_user_admin():
			self.response.out.write('Nope you won\'t')
			return

		jukebox = Jukebox.get_or_insert(person.key.id()) #create same as person
		jukebox.title = 'Movenext'
		jukebox.owner_key = person.key
		jukebox.put()
		membership = JukeboxMembership.get_or_insert(person.key.id(),parent=jukebox.key)
		membership.type = 'owner'
		membership.put()
		if jukebox.player:
			self.response.out.write('done...')
			return
		#logging.info(jukebox.key)
		player_key = JukeboxPlayer(
				parent=jukebox.key,
				last_track_queued_on=datetime.datetime.now(),
				last_track_duration=0
		).put()
		self.response.out.write('done...')


# must fix list prio
app = webapp2.WSGIApplication([

		# Jukebox handlers
		("/AJAX/jukeboxes/get/", jukebox.GetJukeBoxesHandler),
		("/AJAX/jukebox/save/", jukebox.SaveJukeBoxeHandler),
		("/AJAX/jukebox/get/playing_track", jukebox.GetPlayingTrackHandler),
		("/AJAX/jukebox/get/queued_tracks", jukebox.GetJukeBoxQueuedTracksHandler),
		("/AJAX/jukebox/player/startplaying/", jukebox.StartPlayingHandler),
		("/AJAX/jukebox/player/stopplaying/", jukebox.StopPlayingHandler),
		("/AJAX/queued_track/save/", queued_track.AddSingleQueuedTrackHandler),
		("/AJAX/queued_track/remove/", queued_track.RemoveSingleQueuedTrackHandler),
		('/jukebox/.*', server.RootPage),
		# Essential handlers
		("/AJAX/person/get/current", person.GetCurrentPersonHanlder),
		("/login/", person.RegisterPersonHandler),
		("/register/", person.RegisterPersonHandler),
		("/setup/", SetupHandler),
		("/logout/", person.LogoutPersonHandler),
		('/', server.RootPage),

	],debug=True, config=config.config)




# Extra Hanlder like 404 500 etc
def handle_404(request, response, exception):
	logging.exception(exception)
	response.write('Oops! Naughty Mr. Jiggles (This is a 404)')
	response.set_status(404)

app.error_handlers[404] = handle_404
