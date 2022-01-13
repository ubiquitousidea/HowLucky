"""
Connect to the Discogs API
See what info on records is available
Analyze the data
Display the data
"""

from util import (
    load_yaml,
    store_release_data,
    Randomize,
    sleep_random
)
import discogs_client
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('--limit', help='limit the number of releases to query', type=int, default=None)
args = parser.parse_args()


app_keys = load_yaml('keys/appdata.yaml')
token_info = load_yaml('keys/my_token.yaml')

d = discogs_client.Client(
    user_agent='HowLucky',
    consumer_key=app_keys['Consumer Key'],
    consumer_secret=app_keys['Consumer Secret'],
    token=token_info['token'],
    secret=token_info['secret']
)

me = d.identity()
collection = me.collection_folders[0].releases
wantlist = me.wantlist
release1 = wantlist[69].release

# -----------------------------------------------------------------------------
# - Store collection info -----------------------------------------------------
# -----------------------------------------------------------------------------

print('Analyzing record collection')
for item in Randomize(collection, limit=args.limit):
    release = item.release
    store_release_data(release, store_metadata=False)
    sleep_random()

print('Analyzing wantlist')
for item in Randomize(wantlist, limit=args.limit):
    release = item.release
    store_release_data(release, store_metadata=False)
    sleep_random()
