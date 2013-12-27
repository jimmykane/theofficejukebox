'''
Created on Dec 15, 2012

@author: jimmykane
'''
import os
import re
from google.appengine.ext import db

class Utitlities ():

    @classmethod
    def prefetch_refprops(cls, entities, *props):
        '''Dereference Reference Properties to reduce Gets.  See:
        http://blog.notdot.net/2010/01/ReferenceProperty-prefetching-in-App-Engine
        '''
        fields = [(entity, prop) for entity in entities for prop in props]
        ref_keys = [prop.get_value_for_datastore(x) for x, prop in fields]
        ref_entities = dict((x.key(), x) for x in db.get(set(ref_keys)))
        for (entity, prop), ref_key in zip(fields, ref_keys):
            prop.__set__(entity, ref_entities[ref_key])
        return entities

    @classmethod
    def validate_url(cls, url):
        if not re.match("\A[A-Za-z]+\Z", url) or len(url) < 4 or len(url) > 20:
            return True
        return False