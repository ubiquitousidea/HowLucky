from util import Randomize, sleep_random
from database.database_util import store_release_data
from database.database_util_postgres import DBPostgreSQL
from sql.schema import DB_KEYS_POSTGRES
from discogs_identity import dclient
import argparse


parser = argparse.ArgumentParser()

parser.add_argument(
    "--store_meta",
    help="store metadata for each release",
    action="store_true",
    default=False,
)

parser.add_argument(
    "--sleep",
    help="expected value of sleep time (exponential distribution)",
    type=float,
    default=5,
)

args = parser.parse_args()

# -----------------------------------------------------------------------------
# - Store collection info -----------------------------------------------------
# -----------------------------------------------------------------------------

db = DBPostgreSQL(DB_KEYS_POSTGRES)

while True:
    wantlist = dclient.identity().wantlist
    collection = dclient.identity().collection_folders[0].releases
    for clx in (collection, wantlist):
        for item in Randomize(clx):
            store_release_data(
                db=db, release=item.release, store_metadata=args.store_meta
            )
            sleep_random(args.sleep)
