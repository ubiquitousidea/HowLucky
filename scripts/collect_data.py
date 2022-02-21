"""
Connect to the Discogs API
See what info on records is available
Analyze the data
Display the data
"""

from util import Randomize, sleep_random
from database.database_util import store_release_data
from discogs_identity import collection, wantlist
import argparse
from sql.schema import DB_CHOICE

# -----------------------------------------------------------------------------
# - Argument parsing ----------------------------------------------------------
# -----------------------------------------------------------------------------

parser = argparse.ArgumentParser()
parser.add_argument(
    '--limit',
    help='limit the number of releases to query',
    type=int, default=None
)
parser.add_argument(
    '--store_meta',
    help='if 1, store metadata, else dont',
    type=int, default=0
)
parser.add_argument(
    '--store_prices',
    help='if 1, store prices, else dont',
    type=int, default=1
)
parser.add_argument(
    '--db',
    help='which database to use (mysql or postgres)',
    type=str, default=DB_CHOICE
)
args = parser.parse_args()

# -----------------------------------------------------------------------------
# - Store collection info -----------------------------------------------------
# -----------------------------------------------------------------------------

for clx in (collection, wantlist):
    for item in Randomize(clx, limit=args.limit):
        release = item.release
        store_release_data(
            release,
            store_metadata=args.store_meta,
            store_prices=args.store_prices,
        )
        sleep_random()
