"""
Update a column in a table using the discogs API
"""
import argparse
from database.database_util import get_metadata, get_db_object, store_release_metadata
from discogs_search import get_entity, get_attribute
from util import sleep_random
from pandas import DataFrame


def update_field(tbl, index, field, db_):
    for idx_, item_ in get_metadata(tbl).iterrows():
        id_ = item_[index]
        entity = get_entity(id_, index)
        attr_ = get_attribute(entity, field)
        db_.update_rows(DataFrame([
            {index: id_,
             field: attr_}
        ], index=[0]), index, tbl)
        sleep_random()
    return None