'''
@author: Dimitrios Kanellopoulos
@contact: jimmykane9@gmail.com
'''
import logging
import hashlib
import json
import webapp2
from controllers.jsonhandler import *
from models.person import *
from models.jukebox import *
from models.tracks import *
from google.appengine.ext import ndb
from google.appengine.api import users


class LogoutPersonHandler(webapp2.RequestHandler):

    def get(self):
        try:
            return self.redirect(users.create_logout_url(self.request.get('return_url')))
        except Exception as e:
            logging.exception('Could not Logout user\n' + repr(e))
            self.redirect('/')
            return


class RegisterPersonHandler(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()
        if not user:
            self.redirect(users.create_login_url(self.request.uri), abort=True)
            return

        person = Person.get_or_insert(user.user_id())
        if not self._register(person, user):
            # more logging is needed
            logging.warning('Warning registration failed')
            return

        # get the slide and then redirect him there
        self.redirect("/jukebox/")

    def post(self):
        self.view("No reason to be here Mr Jiggles ;-)")
        return

    @ndb.transactional(xg=True)
    def _register(self, person, user):

        # Register the info
        person_info = PersonInfo.query(ancestor=person.key).get()
        if not person_info:
            info = PersonInfo(id=user.user_id(), parent=person.key)
            info.nick_name = user.nickname()
            info.email = user.email()
            info.put()

        # Register a jukebox
        person_jukebox = ndb.Key(Jukebox, person.key.id()).get()
        if not person_jukebox:
            person_jukebox = Jukebox(id=person.key.id())
            person_jukebox.title = 'Jukebox Beta'
            person_jukebox.owner_key = person.key
            person_jukebox.put()

        # Add it's player
        person_jukebox_player = ndb.Key(Jukebox, person_jukebox.key.id(), JukeboxPlayer, person_jukebox.key.id()).get()
        if not person_jukebox_player:
            person_jukebox_player = JukeboxPlayer(id=person_jukebox.key.id(), parent=person_jukebox.key)
            person_jukebox_player.last_track_queued_on = datetime.datetime.now()
            person_jukebox_player.last_track_duration = 0
            person_jukebox_player.put()

        # Register a membership
        person_jukebox_membership = ndb.Key(Jukebox, person_jukebox.key.id(), JukeboxMembership, person.key.id()).get()
        if not person_jukebox_membership:
            person_jukebox_membership = JukeboxMembership(id=person.key.id(), parent=person_jukebox.key)
            person_jukebox_membership.type = 'owner'
            person_jukebox_membership.person_key = person.key
            person_jukebox_membership.put()

        return True


class GetCurrentPersonHanlder(webapp2.RequestHandler, JSONHandler):

    def post(self):
        person = Person.get_current()
        if not person: # its normal here
            response = {'status':self.get_status(status_code=404)}
            self.response.out.write(json.dumps(response))
            return

        # First convert to dict
        person_dict = Person._to_dict(person)
        # Then get info convert to dict and update person dict
        person_info = person.info
        person_info_dict = PersonInfo._to_dict(person_info)
        person_dict.update(person_info_dict)
        # Last get the memberships
        jukebox_memberships = person.jukebox_memberships
        member_ships = []
        for jukebox_membership in jukebox_memberships:
            jukebox_membership_dict = JukeboxMembership._to_dict(jukebox_membership)
            member_ships.append(jukebox_membership_dict)
        person_dict.update({'memberships': member_ships})
        response = response = {'data': person_dict}
        response.update({'status': self.get_status()})
        self.response.out.write(json.dumps(response))
