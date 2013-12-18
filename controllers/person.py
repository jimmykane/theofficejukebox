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

        # All get or inserts please
        person = Person.get_or_insert(user.user_id())
        person_info = PersonInfo.get_or_insert(user.user_id(), parent=person.key)
        jukebox = Jukebox.get_or_insert(person.key.id())
        membership = JukeboxMembership.get_or_insert(person.key.id(), parent=jukebox.key)

        if not self._register(person, person_info , user, jukebox, membership):
            # more logging is needed
            logging.warning('Warning registration failed')
            return

        # get the slide and then redirect him there
        self.redirect("/jukebox/")

    def post(self):
        self.view("No reason to be here Mr Jiggles ;-)")
        return

    @ndb.transactional(xg=True)
    def _register(self, person, person_info ,user, jukebox, membership):
        ''' Registration process happens here
        '''
        if not person_info.creation_date:
            person_info = PersonInfo(id=user.user_id(), parent=person.key)
            person_info.nick_name = user.nickname()
            person_info.email = user.email()
            person_info.put()
        #@todo
        # I assume here that the owner key or user_id from the openid will always be unique
        if not jukebox.owner_key:
            jukebox.title = 'Jukebox Beta'
            jukebox.owner_key = person.key
            jukebox.put()
        if not membership.type:
            membership.type = 'owner'
            membership.person_key = person.key
            membership.put()
        #@todo Move player registration here.
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
