'''
@author: Dimitrios Kanellopoulos
@contact: jimmykane9@gmail.com
'''
import os
import logging
from google.appengine.api import users
import webapp2
import jinja2

from models.person import *


class UserPageHandler(webapp2.RequestHandler):

	def test():
		pass
