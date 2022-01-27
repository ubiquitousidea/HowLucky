from discogs_identity import d
from util import just_try


@just_try
def get_entity(entity_id, entity):
    if entity == 'release':
        return d.release(entity_id)
    elif entity == 'artist':
        return d.artist(entity_id)
    elif entity == 'label':
        return d.label(entity_id)
