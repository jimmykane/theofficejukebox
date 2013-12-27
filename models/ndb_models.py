'''
@author: Dimitrios Kanellopoulos
@contact: jimmykane9@gmail.com
'''
import logging

from google.appengine.ext import ndb


''' Class to help with dict conversions '''
class DictModel():

    '''
    From a dict make an entity. You need the parent
    First check if the properties are in the class definition
    Dictionary key names represent property names
    '''
    @classmethod
    def entity_from_dict(cls, parent_key, dict):
        valid_properties = {}
        for cls_property in cls._properties:
            if cls_property in dict:
                valid_properties.update({cls_property: dict[cls_property]})
        # Update the id from the dict
        if 'id' in dict: # if creating a new entity
                valid_properties['id'] = dict['id']
        # Add the parent
        valid_properties['parent'] = parent_key
        try:
            entity = cls(**valid_properties)
        except Exception as e:
            logging.exception('Could not create entity object\n' + repr(e))
            return False
        return entity


''' Class to help with shared model functions '''
class NDBCommonModel:

    '''
    Find if is the last child from the parent.
    Usefull if you want to check if it's last entry in a box,slide,post
    '''
    @classmethod
    def is_the_only_remaining_child(cls, key):
        related_keys_count = cls.query(ancestor=key.parent()).count(keys_only=True)
        if related_keys_count < 2:
            return True
        return False