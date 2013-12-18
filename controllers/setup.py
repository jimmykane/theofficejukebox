'''
@author: Dimitrios Kanellopoulos
@contact: jimmykane9@gmail.com
'''
import logging
import webapp2
from models.person import *
from models.jukebox import *
from google.appengine.api import users


class SetupInitHandler(webapp2.RequestHandler):

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
        membership.person_key = person.key
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