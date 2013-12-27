'''
@author: Dimitrios Kanellopoulos
@contact: jimmykane9@gmail.com
'''
import logging
from controllers import person, server, jukebox, queued_track
from config import config
import webapp2


# must fix list prio
app = webapp2.WSGIApplication([

		# Jukebox handlers
		("/AJAX/jukeboxes/get/", jukebox.GetJukeBoxesHandler),
		("/AJAX/jukebox/save/", jukebox.SaveJukeBoxeHandler),
		("/AJAX/jukebox/get/playing_track", jukebox.GetPlayingTrackHandler),
		("/AJAX/jukebox/get/memberships", jukebox.GetJukeBoxMembershipsHandler),
		("/AJAX/jukebox/save/membership", jukebox.SaveJukeBoxMembershipHandler),
		("/AJAX/jukebox/request/membership", jukebox.RequestJukeBoxMembershipHandler),
		("/AJAX/jukebox/get/queued_tracks", jukebox.GetJukeBoxQueuedTracksHandler),
		("/AJAX/jukebox/player/startplaying/", jukebox.StartPlayingHandler),
		("/AJAX/jukebox/player/stopplaying/", jukebox.StopPlayingHandler),
		("/AJAX/queued_track/save/", queued_track.AddSingleQueuedTrackHandler),
		("/AJAX/queued_track/remove/", queued_track.RemoveSingleQueuedTrackHandler),
		('/jukebox/.*', server.RootPage),
        ('/jukeboxes/.*', server.RootPage),
		# Essential handlers
		("/AJAX/person/get/current", person.GetCurrentPersonHanlder),
		("/login/", person.RegisterPersonHandler),
		("/register/", person.RegisterPersonHandler),
		("/logout/", person.LogoutPersonHandler),
		('/', server.RootPage),

	],debug=True, config=config.config)




# Extra Hanlder like 404 500 etc
def handle_404(request, response, exception):
	logging.exception(exception)
	response.write('Oops! Naughty Mr. Jiggles (This is a 404)')
	response.set_status(404)

app.error_handlers[404] = handle_404
