"""
update the releases table
"""

import argparse
from database.database_util import get_metadata, get_db_object, store_release_metadata
from discogs_search import get_entity, get_attribute
from scripts.update_field import update_field
from sql.schema import DB_CHOICE
from database.data_extractors import get_release_text, get_image_url
from util import sleep_random
from pandas import DataFrame


parser = argparse.ArgumentParser()

parser.add_argument(
    '--format_details',
    help='update release format details for releases already in table',
    type=int, default=0
)
parser.add_argument(
    '--find_missing',
    help='find missing releases present in marketplace data but not release table',
    type=int, default=0
)
parser.add_argument(
    '--artist_url',
    help='find missing artist image urls or update them when they change',
    type=int, default=0
)
parser.add_argument(
    '--release_url',
    help='find missing release image urls or update them when they change',
    type=int, default=0
)
args = parser.parse_args()

db = get_db_object(DB_CHOICE)

if args.format_details:
    update_field('releases', 'release_id', 'format_details', db_=db)
elif args.find_missing:
    r = db.read_rows('releases')
    m = db.read_rows('unique_releases')
    missing_releases = set(m['release_id']) - set(r['release_id'])
    for release_id in sorted(list(missing_releases)):
        release = get_entity(release_id, 'release_id')
        store_release_metadata(db, release)
        sleep_random()
elif args.artist_url:
    update_field('artists', 'artist_id', 'image', db_=db)
elif args.release_url:
    update_field('releases', 'release_id', 'image', db_=db)
else:
    pass



