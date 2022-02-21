"""
update the releases table
"""

from database.database_util import get_metadata, get_db_object
from discogs_search import get_entity
from sql.schema import DB_CHOICE
from database.data_extractors import get_release_text
from util import sleep_random
from pandas import DataFrame


db = get_db_object(DB_CHOICE)

TBL = 'releases'
INDEX = 'release_id'

for idx, item in get_metadata(TBL).iterrows():
    release = get_entity(item[INDEX], 'release')
    df = DataFrame([
        {INDEX: item[INDEX],
         'format_details': get_release_text(release)}
    ], index=[0])
    db.update_rows(df, INDEX, TBL)
    sleep_random()
    if idx > 2:
        break
