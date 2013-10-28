'''
@author: Dimitrios Kanellopoulos
@contact: jimmykane9@gmail.com
'''
import logging
import webapp2
from controllers import setup
from config import config
from google.appengine.ext import ndb

app = webapp2.WSGIApplication([
		("/setup/init", setup.SetupInitHandler)
	],debug=True, config=config.config)


# Extra Hanlder like 404 500 etc
def handle_404(request, response, exception):
	logging.exception(exception)
	response.write('Oops! Naughty Mr. Admin (This is a 404)')
	response.set_status(404)

app.error_handlers[404] = handle_404