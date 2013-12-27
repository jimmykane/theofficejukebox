'''
@author: Dimitrios Kanellopoulos
@contact: jimmykane9@gmail.com
'''
import logging
import json
from config import config
from models.ndb_models import *
from google.appengine.ext import ndb
from google.appengine.api import urlfetch



class Track(ndb.Expando, DictModel, NDBCommonModel):

    title = ndb.StringProperty()
    duration = ndb.IntegerProperty()
    creation_date = ndb.DateTimeProperty(auto_now_add=True)
    edit_date = ndb.DateTimeProperty(auto_now=True)
    available = ndb.BooleanProperty(default=True)

class YouTubeTrack(Track):

    #video_id = ndb.StringProperty(required=True)
    #lets make it the key
    pass

    @property
    def get_youtube_info(self):
        logging.info(self.key.id())
        video_id = self.key.id() #since it's the key id
        logging.info('Getting youtube data')
        title = False
        duration = False
        url = 'http://gdata.youtube.com/feeds/api/videos/'\
            + video_id + '?v=2&alt=jsonc&key='\
            + config.config.get('api_keys').get('youtube')
        #logging.info(url)
        result = urlfetch.fetch(url)
        #logging.info(result.status_code)
        if not (result.status_code == 200):
            return False

        data = json.loads(result.content)
        #logging.info(result.content)
        #logging.info(data['data']['title'])
        try:
            title = data['data']['title']
            duration = data['data']['duration']
        except Exception as e:
            logging.error('Error converting Youtube data' + repr(e))
            return False

        # if it doesnt allow embeding
        if data['data']['accessControl']['embed'] != 'allowed':
            return False

        # Try to see if there are restrictions
        try:
            for restriction in data['data']['restrictions']:
                logging.info(restriction)
                if restriction['type'] == 'country':# maybe just check more?
                    # if there are country restricitons we don't want these vids probably
                    if 'NL' in restriction['countries']:
                        logging.warning("Video has country restrictions to Netherlands")
                        return False
        except Exception as e:
            logging.warning('Video does not have restrictions')
            # has no restrictions let it pass
            pass

        return title, duration

class QueuedTrack(ndb.Expando, DictModel, NDBCommonModel):

    creation_date = ndb.DateTimeProperty(auto_now_add=True)
    edit_date = ndb.DateTimeProperty(auto_now=True)
    # track key can be used as this class key!!!
    queued_by_person_key = ndb.KeyProperty()
    archived = ndb.BooleanProperty(default=False)
    duration = ndb.IntegerProperty(required=True)
    title= ndb.StringProperty(required=True)
    play_count = ndb.IntegerProperty(required=True, default=0)

    @property
    def track(self):
        track = ndb.Key(Track, self.key.id()).get()
        return track;

    @classmethod
    def _to_dict(cls, queued_track):
        nick_name = 'Unknown'
        queued_track_id = queued_track.key.id()
        person = queued_track.queued_by_person_key.get()
        if person:
            nick_name = person.info.nick_name
        queued_track_dict = queued_track.to_dict(
            exclude=[
                'queued_by_person_key',
                'creation_date', 'edit_date'
            ]
        )
        queued_track_dict.update({
            'id': queued_track_id,
            'queuedby_nick_name': nick_name,
            'creation_date': queued_track.creation_date.isoformat(),
            'edit_date': queued_track.edit_date.isoformat(),
        })
        return queued_track_dict


    '''
    Hooks go here
    '''

    @classmethod
    def _pre_delete_hook(cls, key):
        return