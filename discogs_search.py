from discogs_client import Release, Artist, Master, Label
from discogs_identity import d
from util import just_try
from database.data_extractors import *


@just_try
def get_entity(entity_id, index_field_name):
    if index_field_name == 'release_id':
        return d.release(entity_id)
    elif index_field_name == 'artist_id':
        return d.artist(entity_id)
    elif index_field_name == 'label_id':
        return d.label(entity_id)
    elif index_field_name == 'master_id':
        return d.master(entity_id)
    else:
        raise ValueError(f'unknown id: {index_field_name}')


def get_attribute(entity, field):
    """
    When the cached release data gets stale, use this function to refresh with values from the discogs API.
    :param entity: discogs object (artist, release, label, or master)
    :param field: name of the field in the table to update from API
    :return: attribute value
    """
    if type(entity) is Release:
        if field == 'title':
            output = get_title(entity)
        elif field == 'image':
            output = get_image_url(entity)
        else:
            raise NotImplemented(f'{field} - {entity} not implemented')
    elif type(entity) is Artist:
        if field == 'image':
            output = get_image_url(entity)
        else:
            raise NotImplemented(f'{field} - {entity} not implemented')
    elif type(entity) is Label:
        if field == 'image':
            output = get_image_url(entity)
        else:
            raise NotImplemented(f'{field} - {entity} not implemented')
    else:
        raise NotImplemented(f'{field} - {entity} not implemented')
    return output
